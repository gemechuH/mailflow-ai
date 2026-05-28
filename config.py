import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
COMPANY_NAME = os.getenv("COMPANY_NAME", "Our Company")

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Each department has: a forward-to email and a short description for the AI
DEPARTMENTS = {
    "sales": {
        "email": GMAIL_ADDRESS,   # change to e.g. sales@megaplc.com when you have a real team
        "description": "Product inquiries, pricing, bulk orders, wholesale, partnerships, quotes",
        "reply_tone": "enthusiastic and helpful",
    },
    "support": {
        "email": GMAIL_ADDRESS,   # change to support@megaplc.com
        "description": "Order issues, refunds, returns, damaged items, tracking, complaints",
        "reply_tone": "empathetic and solution-focused",
    },
    "hr": {
        "email": GMAIL_ADDRESS,   # change to hr@megaplc.com
        "description": "Job applications, career inquiries, internships, employment questions",
        "reply_tone": "professional and welcoming",
    },
    "billing": {
        "email": GMAIL_ADDRESS,   # change to billing@megaplc.com
        "description": "Invoices, payment problems, subscription changes, charge disputes",
        "reply_tone": "clear and reassuring",
    },
    "general": {
        "email": GMAIL_ADDRESS,
        "description": "Everything else that doesn't fit above",
        "reply_tone": "friendly and professional",
    },
}
