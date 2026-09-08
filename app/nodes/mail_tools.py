from langchain_core.tools import tool
from app.services.gmail_auth import get_gmail_service

@tool
def get_mail(query: str = "", limit: int = 10):
    """
    Search the user's Gmail messages and return matching emails.
    """

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=limit
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for message in messages:
        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        # Parse the Gmail response here
        emails.append(email)

    return emails

from langchain_core.tools import tool


@tool
def send_mail(
    recipient: str,
    subject: str,
    body: str
):
    """
    Send an email to a recipient.

    Use this tool when the user explicitly wants an email sent.
    The email will go through the approval workflow before being sent.
    """

    return {
        "action": "send_mail",
        "recipient": recipient,
        "subject": subject,
        "body": body
    }