from langgraph.types import interrupt

from app.models.models import EmailDraft
from app.state import EmailState


def human_approval(state: EmailState):

    last_message = state["messages"][-1]

    drafts = [
        EmailDraft(
            recipient=call["args"]["recipient"],
            subject=call["args"]["subject"],
            body=call["args"]["body"]
        )
        for call in last_message.tool_calls
        if call["name"] == "send_mail"
    ]

    decision = interrupt({
        "type": "email_approval",
        "message": "Please review these emails before they are sent.",
        "drafts": [draft.model_dump() for draft in drafts]
    })

    if isinstance(decision, dict):

        drafts = [
            EmailDraft(**draft)
            for draft in decision.get("drafts", [
                draft.model_dump()
                for draft in drafts
            ])
        ]

        return {
            "drafts": drafts,
            "approved": decision["approved"]
        }

    return {
        "drafts": drafts,
        "approved": decision
    }