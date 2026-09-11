from langchain_core.tools import tool
from app.services.gmail_auth import get_gmail_service
import json

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


@tool
def search_mail(query: str):
    """
    Search the user's Gmail mailbox using a Gmail search query.
    Returns matching email message IDs and basic metadata.
    """

    service = get_gmail_service()

    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=10
    ).execute()

    messages = result.get("messages", [])

    if not messages:
        return {
            "query": query,
            "results": []
        }

    results = []

    for message in messages:
        message_id = message["id"]

        email = service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()

        headers = {
            header["name"]: header["value"]
            for header in email.get("payload", {}).get("headers", [])
        }

        results.append({
            "id": message_id,
            "thread_id": message.get("threadId"),
            "from": headers.get("From"),
            "to": headers.get("To"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date")
        })

    return {
        "query": query,
        "results": results
    }