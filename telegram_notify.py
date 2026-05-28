import requests
import logging
from datetime import datetime
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    TELEGRAM_CHAT_SALES, TELEGRAM_CHAT_ACCOUNT, TELEGRAM_CHAT_SUPPORT,
    COMPANY_NAME
)

logger = logging.getLogger(__name__)

DEPT_EMOJI = {
    "sales":   "💰",
    "account": "📋",
    "support": "🔧",
    "general": "💬",
}

# Department → which extra chat ID to notify (if configured)
DEPT_CHAT = {
    "sales":   TELEGRAM_CHAT_SALES,
    "account": TELEGRAM_CHAT_ACCOUNT,
    "support": TELEGRAM_CHAT_SUPPORT,
    "general": "",
}


def _send(chat_id: str, message: str):
    """Send a message to a single chat ID. Skips silently if ID is empty."""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
    except Exception as e:
        logger.warning(f"Telegram notify failed for chat {chat_id}: {e}")


def notify_email_processed(sender: str, subject: str, department: str):
    """Notify owner always. Also notify department team if their chat ID is set."""
    emoji = DEPT_EMOJI.get(department, "📧")
    time_str = datetime.now().strftime("%H:%M")

    if "<" in sender:
        name = sender.split("<")[0].strip().strip('"')
        email_addr = sender.split("<")[1].replace(">", "").strip()
    else:
        name = sender
        email_addr = sender

    message = (
        f"📧 *New Email — {COMPANY_NAME}*\n"
        f"{'─' * 30}\n"
        f"👤 *From:* {name}\n"
        f"✉️ *Email:* {email_addr}\n"
        f"📌 *Subject:* {subject[:60]}\n"
        f"{emoji} *Department:* {department.upper()}\n"
        f"✅ *Auto-reply sent*\n"
        f"⏰ *Time:* {time_str}"
    )

    # Always notify the owner
    _send(TELEGRAM_CHAT_ID, message)

    # Also notify the department team if they have their own chat ID
    dept_chat = DEPT_CHAT.get(department, "")
    if dept_chat and dept_chat != TELEGRAM_CHAT_ID:
        _send(dept_chat, message)


def notify_daily_summary(total: int, skipped: int, counts: dict):
    """Send daily report to owner only."""
    if not TELEGRAM_CHAT_ID:
        return
    today = datetime.now().strftime("%A, %B %d")
    lines = [f"📊 *Daily Report — {COMPANY_NAME}*", f"_{today}_", "─" * 30]
    lines.append(f"✅ Total processed: *{total}*")
    lines.append(f"⏭ Skipped: *{skipped}*")
    lines.append("")
    for dept, count in counts.items():
        emoji = DEPT_EMOJI.get(dept, "📧")
        bar = "█" * min(count, 10)
        lines.append(f"{emoji} {dept.upper():<10} *{count}*  {bar}")

    _send(TELEGRAM_CHAT_ID, "\n".join(lines))
