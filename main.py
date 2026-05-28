import time
import logging
from datetime import datetime
from config import CHECK_INTERVAL, DEPARTMENTS, SUMMARY_HOUR
from email_handler import fetch_unread_emails, send_reply, forward_email, mark_as_read, close_connection, is_automated_email
from classifier import classify_email
from reply_generator import generate_reply
from summary import DailySummary
from email_log import log_email
from email_template import build_html_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("email_auto.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

daily = DailySummary()
summary_sent_today = False


def extract_first_name(from_field: str) -> str:
    if "<" in from_field:
        name_part = from_field.split("<")[0].strip().strip('"')
    else:
        name_part = from_field.split("@")[0]
    first = name_part.split()[0] if name_part else "there"
    return first.capitalize()


def check_and_send_summary():
    """Send daily summary at SUMMARY_HOUR and reset for the new day."""
    global summary_sent_today
    now = datetime.now()

    # Reset flag at midnight so we can send again the next day
    if now.hour == 0 and summary_sent_today:
        summary_sent_today = False

    if now.hour == SUMMARY_HOUR and not summary_sent_today:
        print(f"\n  Sending daily summary report...")
        daily.send()
        summary_sent_today = True


def process_email(email_data: dict):
    subject = email_data["subject"]
    body = email_data["body"]
    sender = email_data["from"]
    reply_to = email_data["reply_to"]
    uid = email_data["uid"]
    mail_conn = email_data["mail_conn"]

    # Skip newsletters, notifications, and no-reply automated emails
    if is_automated_email(sender, reply_to, subject):
        print(f"\n  SKIPPED (automated/no-reply): '{subject[:50]}'")
        mark_as_read(mail_conn, uid)
        daily.record_skip()
        return

    print(f"\n  Processing: '{subject[:60]}' from {sender}")

    # Step 1: Classify
    print("  Classifying...")
    department = classify_email(subject, body)
    print(f"  → Department: {department.upper()}")

    # Step 2: Generate reply
    print("  Generating reply...")
    sender_name = extract_first_name(sender)
    reply_body = generate_reply(department, sender_name, subject, body)

    # Step 3: Build HTML and send branded reply
    html_body = build_html_email(department, reply_body)
    send_reply(reply_to, subject, reply_body, html_body)

    # Step 4: Forward to department
    dept_email = DEPARTMENTS[department]["email"]
    from config import GMAIL_ADDRESS
    if dept_email and dept_email != GMAIL_ADDRESS:
        forward_email(dept_email, sender, subject, body, department)

    # Step 5: Mark as read
    mark_as_read(mail_conn, uid)

    # Step 6: Record in daily summary and history log
    daily.record(department)
    log_email(sender, subject, department, reply_to)

    print(f"\n{'='*55}")
    print(f"  FROM      : {sender}")
    print(f"  SUBJECT   : {subject[:55]}")
    print(f"  DEPARTMENT: {department.upper()}")
    print(f"  REPLIED TO: {reply_to}")
    print(f"  TODAY     : {daily.total_processed} processed | {daily.skipped} skipped")
    print(f"{'='*55}")


def run():
    logger.info("Email Auto-Reply Bot started")
    logger.info(f"Checking inbox every {CHECK_INTERVAL}s | Daily report at {SUMMARY_HOUR}:00")
    print(f"\nEmail Auto-Reply Bot is running. Daily report sends at {SUMMARY_HOUR}:00 AM.")
    print("Press Ctrl+C to stop.")
    daily.print_status()

    cycle = 0
    while True:
        try:
            cycle += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n[Cycle #{cycle} at {now}] Checking inbox...")

            check_and_send_summary()

            emails = fetch_unread_emails()

            if not emails:
                print("  No new unread emails found.")
            else:
                for email_data in emails:
                    try:
                        process_email(email_data)
                    except Exception as e:
                        logger.error(f"Error processing email: {e}")
                        print(f"  ERROR: {e}")
                        daily.record_error()

                close_connection(emails[0]["mail_conn"])

            print(f"  Waiting {CHECK_INTERVAL}s before next check...")

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"  ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
