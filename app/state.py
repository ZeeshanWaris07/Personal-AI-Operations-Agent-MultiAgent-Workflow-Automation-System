from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict,Literal

class AgentState(TypedDict):
    messages : Annotated[list,add_messages]

    next_agent = Literal[
        "research",
        "planning",
        "email",
        "final"
    ]

    final_respponse : str

    allowed_tool_calls : list[dict]