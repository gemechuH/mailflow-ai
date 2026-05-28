from groq import Groq
from config import GROQ_API_KEY, COMPANY_NAME, DEPARTMENTS  # DEPARTMENTS used for tone only

client = Groq(api_key=GROQ_API_KEY)


def generate_reply(department: str, sender_name: str, subject: str, body: str) -> str:
    """Generate a personalized auto-reply using Groq/LLaMA."""
    dept_info = DEPARTMENTS.get(department, DEPARTMENTS["general"])
    tone = dept_info["reply_tone"]

    prompt = f"""You are a customer-facing assistant for {COMPANY_NAME}.

Write a short, professional auto-reply email. Tone: {tone}.

Rules:
- Greet the sender by first name if detectable, otherwise use "there"
- Acknowledge what they wrote about in 1 sentence
- Tell them their message has been received and our team will follow up within 12-24 hours
- Do NOT mention any email address, phone number, or direct contact details
- Do NOT say "reply to this email" or "contact us at"
- Sign off as "{COMPANY_NAME} Team"
- Keep it under 100 words
- Do NOT make up specific answers, prices, policies, or order details

Sender name hint: {sender_name}
Subject: {subject}
Their message: {body[:800]}

Write only the email body text, no subject line."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()
