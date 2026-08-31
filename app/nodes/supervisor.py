from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from app.state import AgentState
from typing import Literal
from pydantic import BaseModel,Field
import asyncio 

class SupervisorDecision(BaseModel):
    next_agent : Literal[
        "research",
        "planning",
        "email",
        "final"
    ] = Field(
        description = "The next agent that should handle the request"
    )

llm = ChatGoogleGenerativeAI(
    model = 'gemini-3.6-flash'
)

decision_llm = llm.with_structured_output(SupervisorDecision)

SUPERVISOR_PROMPT = """
You are the Supervisor Agent of a Personal AI Operations Agent.

Your job is to decide which specialized agent should handle
the user's request.

Available agents:

research:
Use when the user needs information gathered from external sources.

planning:
Use when the user needs a plan, strategy, prioritization,
or structured set of actions.

email:
Use when the user wants to draft or send an email.

final:
Use when no specialized agent is required and the request
can be answered directly.

Choose the most appropriate destination.
"""

async def supervisor(state:AgentState):

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        *state["messages"],
    ]

    decision = await decision_llm.ainvoke(state['messages'])

    return {
        'next_agent' : decision.next_agent
    }
