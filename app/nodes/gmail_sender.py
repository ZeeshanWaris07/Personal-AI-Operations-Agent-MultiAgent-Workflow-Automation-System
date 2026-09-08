from email.mime.text import MIMEText
import base64

from app.services.gmail_auth import get_gmail_service
from app.state import EmailState


def send_email(state: EmailState):

    drafts = state["drafts"]

    service = get_gmail_service()

    results = []

    for draft in drafts:

        message = MIMEText(draft.body)

        message["to"] = draft.recipient
        message["subject"] = draft.subject

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        body = {
            "raw": encoded_message
        }

        result = service.users().messages().send(
            userId="me",
            body=body
        ).execute()

        results.append(
            f"Email sent to {draft.recipient}. Message ID: {result['id']}"
        )

    return {
        "send_result": results
    }