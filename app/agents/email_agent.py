from app.llm import llm
from app.models.models import EmailDraft
from app.state import EmailState

def generate_email_draft(state:EmailState):

    recipient = state["recipient"]
    subject = state["subject"]
    purpose = state["purpose"]

    email_agent = llm.with_structured_output(EmailDraft)

    prompt = f"""
You are an email drafting agent.

Create a professional email based on the information below.

RECIPIENT:
{recipient}

SUBJECT:
{subject}

PURPOSE:
{purpose}

Requirements:
- Keep the email professional and concise.
- Clearly communicate the purpose.
- Do not invent facts.
- Return only the structured email draft.
"""

    draft = email_agent.invoke(prompt)

    return {
        "draft": draft
    }
