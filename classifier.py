from groq import Groq
from config import GROQ_API_KEY, DEPARTMENTS

client = Groq(api_key=GROQ_API_KEY)

DEPARTMENT_LIST = "\n".join(
    f"- {name}: {info['description']}" for name, info in DEPARTMENTS.items()
)


def classify_email(subject: str, body: str) -> str:
    """Use Groq/LLaMA to classify an email into one of the defined departments."""
    prompt = f"""You are an email routing assistant for an ecommerce company.

Classify this incoming email into exactly ONE of these departments:
{DEPARTMENT_LIST}

Email Subject: {subject}
Email Body: {body[:1500]}

Reply with ONLY the department name (e.g. sales, support, hr, billing, general). No explanation."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10,
    )

    department = response.choices[0].message.content.strip().lower()

    if department not in DEPARTMENTS:
        department = "general"

    return department
