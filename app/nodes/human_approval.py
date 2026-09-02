from langgraph.types import interrupt
from app.state import EmailState

def human_approval(state:EmailState):

    draft = state['draft']

    decision = interrupt({
        "type": "email_approval",
        "message": "Please review this email before it is sent.",
        "draft": draft.model_dump(),
    })

    return {
        'approved' : decision
    }