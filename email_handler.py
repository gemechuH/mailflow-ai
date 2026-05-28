import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import logging
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, IMAP_SERVER, IMAP_PORT, SMTP_SERVER, SMTP_PORT

logger = logging.getLogger(__name__)

# Process at most this many emails per cycle to avoid rate limits
BATCH_SIZE = 5

# Skip emails from these senders — automated, marketing, or no-reply
SKIP_SENDER_PATTERNS = [
    "noreply", "no-reply", "no_reply", "donotreply", "do-not-reply",
    "notifications@", "notification@", "alerts@", "alert@",
    "mailer@", "bounce@", "postmaster@", "daemon@", "mailer-daemon",
    # Social media
    "facebookmail.com", "linkedin.com", "twitter.com", "instagram.com",
    "pinterest.com", "tiktok.com", "youtube.com",
    # Learning platforms
    "pluralsight", "coursera", "udemy", "mailchimp",
    # Shopping / ecommerce promotional senders
    "aliexpress", "amazon", "ebay", "shein", "temu", "wish.com",
    "ae-market", "market.ae", "ae3@mail",
    # Common marketing keywords in sender addresses
    "promo@", "promotions@", "deals@", "offers@", "news@",
    "newsletter@", "updates@", "info@", "hello@", "marketing@",
    "team@", "support-noreply", "reply-noreply",
]


SKIP_SUBJECT_PATTERNS = [
    "unsubscribe", "newsletter", "weekly digest", "monthly digest",
    "job alert", "new jobs", "training program", "tutorial session",
    "% off", "sale ends", "limited time", "flash sale", "just landed",
    "new arrivals", "don't miss", "exclusive offer", "free shipping",
    "verify your email", "confirm your", "activate your account",
    "invitation:", "you're invited", "digest", "notification",
]


def is_automated_email(from_address: str, reply_to: str, subject: str = "") -> bool:
    """Return True if this looks like a newsletter, promo, or no-reply automated email."""
    combined = (from_address + " " + reply_to).lower()
    if any(pattern in combined for pattern in SKIP_SENDER_PATTERNS):
        return True
    subject_lower = subject.lower()
    if any(pattern in subject_lower for pattern in SKIP_SUBJECT_PATTERNS):
        return True
    return False


def decode_str(value):
    if value is None:
        return ""
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and part.get("Content-Disposition") is None:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return body.strip()


def fetch_unread_emails():
    """Connect to Gmail via IMAP and return up to BATCH_SIZE unread emails.
    Uses PEEK so emails are NOT marked as read during fetch — only marked
    read after successful processing in main.py."""
    emails = []
    try:
        print("  Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        _, message_ids = mail.search(None, "UNSEEN")
        all_ids = message_ids[0].split()
        total_unread = len(all_ids)

        # Take the NEWEST BATCH_SIZE emails (reversed so recent emails are processed first)
        batch = list(reversed(all_ids[-BATCH_SIZE:]))

        print(f"  Unread in inbox: {total_unread}  |  Processing this batch: {len(batch)}")

        for uid in batch:
            # PEEK = fetch without marking as read
            _, msg_data = mail.fetch(uid, "(BODY.PEEK[])")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            emails.append({
                "uid": uid,
                "mail_conn": mail,   # keep connection open to mark read later
                "from": decode_str(msg.get("From", "")),
                "subject": decode_str(msg.get("Subject", "(No Subject)")),
                "body": get_email_body(msg),
                "reply_to": msg.get("Reply-To") or msg.get("From", ""),
            })

    except Exception as e:
        logger.error(f"IMAP fetch error: {e}")
        print(f"  ERROR during fetch: {e}")

    return emails


def mark_as_read(mail_conn, uid):
    """Mark an email as read after we have successfully processed it."""
    try:
        mail_conn.store(uid, "+FLAGS", "\\Seen")
    except Exception as e:
        logger.warning(f"Could not mark email {uid} as read: {e}")


def close_connection(mail_conn):
    try:
        mail_conn.logout()
    except Exception:
        pass


def send_reply(to_address: str, subject: str, plain_body: str, html_body: str = None):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address

        # Plain text fallback first, then HTML (email clients prefer last part)
        msg.attach(MIMEText(plain_body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())

        logger.info(f"Reply sent to {to_address}")
        print(f"  Reply sent to: {to_address}")
    except Exception as e:
        logger.error(f"SMTP send error: {e}")
        print(f"  ERROR sending reply: {e}")


def forward_email(to_address: str, original_from: str, subject: str, body: str, department: str):
    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"[{department.upper()}] {subject}"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address

        forward_body = f"--- Forwarded from {original_from} ---\n\n{body}"
        msg.attach(MIMEText(forward_body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())

        logger.info(f"Forwarded to {department} at {to_address}")
        print(f"  Forwarded to {department} team")
    except Exception as e:
        logger.error(f"Forward error: {e}")
        print(f"  ERROR forwarding: {e}")
