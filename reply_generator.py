from groq import Groq
from config import GROQ_API_KEY, COMPANY_NAME, DEPARTMENTS

client = Groq(api_key=GROQ_API_KEY)


def generate_reply(department: str, sender_name: str, subject: str, body: str) -> str:
    """Generate a personalized auto-reply using Groq/LLaMA."""
    dept_info = DEPARTMENTS.get(department, DEPARTMENTS["general"])
    tone = dept_info["reply_tone"]
    dept_email = dept_info["email"]

    prompt = f"""You are a customer-facing assistant for {COMPANY_NAME}.

Write a short, professional auto-reply email. Tone: {tone}.

Rules:
- Greet the sender by first name if detectable, otherwise use "there"
- Acknowledge what they wrote about in 1 sentence
- Tell them their message has been routed to the {department} team and someone will follow up within 24-48 hours
- If useful, mention they can reply to this email or contact {dept_email} directly
- Sign off as "{COMPANY_NAME} Team"
- Keep it under 120 words
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
