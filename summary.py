import smtplib
import json
import os
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, SMTP_SERVER, SMTP_PORT, COMPANY_NAME, SUMMARY_EMAIL, DEPARTMENTS

logger = logging.getLogger(__name__)

DATA_FILE = "daily_counts.json"


class DailySummary:
    def __init__(self):
        self._load()

    def _load(self):
        """Load today's counts from file. If file is from a previous day, reset."""
        today = str(date.today())
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                if data.get("date") == today:
                    self.date = date.today()
                    self.counts = data.get("counts", {dept: 0 for dept in DEPARTMENTS})
                    self.skipped = data.get("skipped", 0)
                    self.errors = data.get("errors", 0)
                    return
            except Exception:
                pass
        self.reset()

    def _save(self):
        """Persist current counts to file."""
        try:
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "date": str(self.date),
                    "counts": self.counts,
                    "skipped": self.skipped,
                    "errors": self.errors,
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save daily counts: {e}")

    def reset(self):
        self.date = date.today()
        self.counts = {dept: 0 for dept in DEPARTMENTS}
        self.skipped = 0
        self.errors = 0
        self._save()

    def record(self, department: str):
        if department in self.counts:
            self.counts[department] += 1
        self._save()

    def record_skip(self):
        self.skipped += 1
        self._save()

    def record_error(self):
        self.errors += 1
        self._save()

    @property
    def total_processed(self):
        return sum(self.counts.values())

    def print_status(self):
        """Print current day's stats to terminal on startup."""
        print(f"\n{'='*55}")
        print(f"  TODAY ({self.date.strftime('%A %b %d')}) — Loaded from saved data")
        print(f"  Processed : {self.total_processed}  |  Skipped: {self.skipped}  |  Errors: {self.errors}")
        for dept, count in self.counts.items():
            bar = "█" * min(count, 15)
            print(f"  {dept.upper():<10} {count:>3}  {bar}")
        print(f"{'='*55}\n")

    def send(self):
        report_date = self.date.strftime("%A, %B %d %Y")
        total = self.total_processed

        dept_rows = ""
        for dept, count in self.counts.items():
            team_email = DEPARTMENTS[dept]["email"]
            bar = "█" * min(count, 20)
            dept_rows += f"  {dept.upper():<12} {count:>4}  emails   →  {team_email}\n"
            if count > 0:
                dept_rows += f"              {bar}\n"

        body = f"""
{'='*55}
  {COMPANY_NAME} — Daily Email Report
  {report_date}
{'='*55}

SUMMARY
  Total processed : {total}
  Skipped (auto)  : {self.skipped}
  Errors          : {self.errors}

BREAKDOWN BY DEPARTMENT
{dept_rows}
{'='*55}
  Report generated at {datetime.now().strftime("%H:%M")} by MailFlow AI Bot
{'='*55}
""".strip()

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{COMPANY_NAME}] Daily Email Report — {self.date.strftime('%b %d')}"
            msg["From"] = GMAIL_ADDRESS
            msg["To"] = SUMMARY_EMAIL
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_ADDRESS, SUMMARY_EMAIL, msg.as_string())

            logger.info(f"Daily summary sent to {SUMMARY_EMAIL}")
            print(f"\n  Daily summary report sent to {SUMMARY_EMAIL}")
            print(f"  Total processed today: {total} | Skipped: {self.skipped}")
        except Exception as e:
            logger.error(f"Failed to send summary: {e}")
            print(f"  ERROR sending summary: {e}")

        # Also push summary to Telegram
        try:
            from telegram_notify import notify_daily_summary
            notify_daily_summary(total, self.skipped, self.counts)
        except Exception:
            pass

        self.reset()
