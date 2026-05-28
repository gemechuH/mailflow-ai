import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
COMPANY_NAME = os.getenv("COMPANY_NAME", "Our Company")
SUMMARY_HOUR = int(os.getenv("SUMMARY_HOUR", 8))
SUMMARY_EMAIL = os.getenv("SUMMARY_EMAIL", GMAIL_ADDRESS)
BRAND_COLOR = os.getenv("BRAND_COLOR", "#1a1a2e")
BRAND_LOGO_URL = os.getenv("BRAND_LOGO_URL", "")  # paste your logo image URL here

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Each department has: a forward-to email and a short description for the AI
DEPARTMENTS = {
    "sales": {
        "email": "gamehu892@gmail.com",
        "description": "Product inquiries, pricing, bulk orders, wholesale, new orders, partnerships, quotes, purchasing",
        "reply_tone": "enthusiastic and helpful",
    },
    "account": {
        "email": "misganachala385@gmail.com",
        "description": "Existing client accounts, account management, renewals, upgrades, invoices, billing, payments, subscriptions",
        "reply_tone": "professional and detail-oriented",
    },
    "support": {
        "email": "gamebus2025@gmail.com",
        "description": "Order issues, refunds, returns, damaged items, complaints, tracking, technical problems, general help",
        "reply_tone": "empathetic and solution-focused",
    },
    "general": {
        "email": "gamebus2025@gmail.com",
        "description": "Everything else that does not fit sales, account, or support",
        "reply_tone": "friendly and professional",
    },
}
