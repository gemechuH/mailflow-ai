import json
import os
from datetime import datetime

LOG_FILE = "email_history.json"
MAX_ENTRIES = 500


def log_email(sender: str, subject: str, department: str, replied_to: str, status: str = "replied"):
    """Append a processed email to the history log."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": sender,
        "subject": subject,
        "department": department,
        "replied_to": replied_to,
        "status": status,
    }

    history = _load()
    history.insert(0, entry)          # newest first
    history = history[:MAX_ENTRIES]   # keep max 500
    _save(history)


def get_history(limit: int = 100):
    return _load()[:limit]


def _load():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)
