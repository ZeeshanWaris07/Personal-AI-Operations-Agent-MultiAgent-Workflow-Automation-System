from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict,Literal
from app.utils.tool_result import ToolExecutionResult
from app.models.models import Plan,PlanReview,EmailDraft

class AgentState(TypedDict):
    messages : Annotated[list,add_messages]

    next_agent : Literal[
        "research",
        "planning",
        "email",
        "final"
    ]

    final_response : str

    allowed_tool_calls : list[dict]

    tool_result: ToolExecutionResult | None


class PlanningState(TypedDict):

    objective: str

    research_results: str

    plan: Plan | None

    review: PlanReview | None

    num_iterations : int = 0


class EmailState(TypedDict):
    recipient: str
    subject: str
    purpose: str

    draft: EmailDraft | None

    approved: bool | None

    send_result: str | None

class MainState(TypedDict):
    objective: str

    next_agent: str | None

    research_results: str | None

    plan: Plan | None

    email_draft: EmailDraft | None
    email_approved: bool | None
    email_send_result: str | None

    final_response: str | None