"""Quick end-to-end test: reads the latest unread email, classifies it, prints the reply. Does NOT send anything."""
import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 55)
print("FULL PIPELINE TEST (read → classify → reply preview)")
print("=" * 55)

# Step 1: Fetch latest unread email
print("\n[1] Fetching latest unread email from Gmail...")
import imaplib, email
from email.header import decode_header

def decode_str(value):
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"))
    mail.select("inbox")
    _, ids = mail.search(None, "UNSEEN")
    all_ids = ids[0].split()
    print(f"    Unread emails found: {len(all_ids)}")

    if not all_ids:
        print("    No unread emails. Mark the Game Hu email as unread in Gmail first.")
        exit()

    # Get the most recent one
    uid = all_ids[-1]
    _, msg_data = mail.fetch(uid, "(BODY.PEEK[])")
    raw = msg_data[0][1]
    msg = email.message_from_bytes(raw)

    sender  = decode_str(msg.get("From", ""))
    subject = decode_str(msg.get("Subject", ""))
    body    = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

    print(f"    From   : {sender}")
    print(f"    Subject: {subject}")
    print(f"    Body   : {body[:200].strip()}")
    mail.logout()
except Exception as e:
    print(f"    IMAP ERROR: {e}")
    exit()

# Step 2: Classify
print("\n[2] Classifying with Groq AI...")
from groq import Groq
from config import GROQ_API_KEY, DEPARTMENTS

client = Groq(api_key=GROQ_API_KEY)
dept_list = "\n".join(f"- {n}: {d['description']}" for n, d in DEPARTMENTS.items())

try:
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Classify this email into one of: {dept_list}\n\nSubject: {subject}\nBody: {body[:800]}\n\nReply with ONLY the department name."}],
        temperature=0, max_tokens=10,
    )
    department = r.choices[0].message.content.strip().lower()
    if department not in DEPARTMENTS:
        department = "general"
    print(f"    Department: {department.upper()}")
except Exception as e:
    print(f"    GROQ ERROR: {e}")
    exit()

# Step 3: Generate reply preview
print("\n[3] Generating reply (preview only, not sending)...")
from config import COMPANY_NAME
try:
    r2 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Write a short auto-reply for {COMPANY_NAME} {department} team. Acknowledge their email and say someone will follow up in 24-48h. Under 80 words. Body only."}],
        temperature=0.7, max_tokens=150,
    )
    reply = r2.choices[0].message.content.strip()
    print(f"\n    --- REPLY PREVIEW ---")
    print(f"    {reply}")
    print(f"    ---------------------")
except Exception as e:
    print(f"    GROQ ERROR: {e}")
    exit()

print("\n✓ Full pipeline works! Run 'python main.py' to start the live bot.")
print("=" * 55)
