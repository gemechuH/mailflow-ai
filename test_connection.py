"""Run this to diagnose connection issues before running the main bot."""
import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL = os.getenv("GMAIL_ADDRESS")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GROQ_KEY = os.getenv("GROQ_API_KEY")

print("=" * 50)
print("STEP 1: Checking .env values loaded correctly")
print(f"  Gmail address : {GMAIL}")
print(f"  App password  : {'SET ✓' if PASSWORD else 'MISSING ✗'}")
print(f"  Groq key      : {'SET ✓' if GROQ_KEY else 'MISSING ✗'}")
print()

print("=" * 50)
print("STEP 2: Testing Gmail IMAP connection...")
try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(GMAIL, PASSWORD)
    print("  Login: SUCCESS ✓")

    mail.select("inbox")

    # Check ALL emails (read + unread)
    _, all_ids = mail.search(None, "ALL")
    total = len(all_ids[0].split()) if all_ids[0] else 0

    # Check only UNSEEN (unread)
    _, unseen_ids = mail.search(None, "UNSEEN")
    unread = len(unseen_ids[0].split()) if unseen_ids[0] else 0

    print(f"  Total emails in inbox : {total}")
    print(f"  Unread emails         : {unread}")

    if unread == 0 and total > 0:
        print()
        print("  ⚠ Emails exist but 0 unread.")
        print("  → Gmail marks emails you send to YOURSELF as already-read.")
        print("  → Fix: Open Gmail in browser, find your test emails, mark them as UNREAD.")
    elif total == 0:
        print()
        print("  ⚠ Inbox appears empty via IMAP.")
        print("  → Make sure IMAP is enabled in Gmail settings.")

    mail.logout()
except imaplib.IMAP4.error as e:
    print(f"  Login FAILED ✗ → {e}")
    print()
    print("  Possible fixes:")
    print("  1. Make sure IMAP is enabled: Gmail → Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP")
    print("  2. Use the App Password (not your real Gmail password)")
    print("  3. Make sure 2-Step Verification is ON in your Google account")
except Exception as e:
    print(f"  Error: {e}")

print()
print("=" * 50)
print("STEP 3: Testing Groq API...")
try:
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Reply with only the word: working"}],
        max_tokens=5,
    )
    result = response.choices[0].message.content.strip()
    print(f"  Groq API: SUCCESS ✓  (response: '{result}')")
except Exception as e:
    print(f"  Groq API FAILED ✗ → {e}")
    print("  → Check your GROQ_API_KEY in .env is correct")

print()
print("=" * 50)
