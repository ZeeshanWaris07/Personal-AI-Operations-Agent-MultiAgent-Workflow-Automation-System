from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict,Literal
from app.utils.tool_result import ToolExecutionResult
from app.agents.planning_agent import Plan,PlanReview

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