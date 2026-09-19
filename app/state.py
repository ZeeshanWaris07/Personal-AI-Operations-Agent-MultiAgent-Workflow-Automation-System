from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict,Literal
from app.utils.tool_result import ToolExecutionResult
from app.models.models import Plan,PlanReview,EmailDraft
from app.models.models import FinalResponse
from app.gaurdrails.schemas import GaurdrailDecision

class AgentState(TypedDict):
    messages : Annotated[list,add_messages]

    final_response : str

    allowed_tool_calls : list[dict]

    tool_result: list[ToolExecutionResult] | None


class PlanningState(TypedDict):

    objective: str

    research_results: str

    plan: Plan | None

    review: PlanReview | None

    num_iterations : int


class EmailState(TypedDict):
    messages : Annotated[list,add_messages]

    recipient: list[str]
    purpose: str

    drafts: list[EmailDraft] | None

    approved: bool | None

    send_result: str | None

class MainState(TypedDict):

    chat_history : list

    messages : Annotated[list,add_messages]

    objective: str

    next_agent : Literal[
            "research",
            "planning",
            "email",
            "final"
        ]

    email_required: bool
    multiple_emails: bool

    recipients: list[str]

    research_results: str | None

    plan: Plan | None


    email_drafts: list[EmailDraft] | None
    email_approved: bool | None
    email_send_result: str | None

    final_response: FinalResponse

    gaurdrail_decision : GaurdrailDecision | None = None

    output_guardrail_passed: bool | None
    output_guardrail_reason: str | None