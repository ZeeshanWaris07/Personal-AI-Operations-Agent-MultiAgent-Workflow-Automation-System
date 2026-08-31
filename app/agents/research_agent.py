from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.state import AgentState
from app.tools import TOOLS


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


research_llm = llm.bind_tools(TOOLS)


RESEARCH_PROMPT = """
You are the Research Agent in a Personal AI Operations Agent.

Your job is to gather accurate information for the user.

You have access to tools that can help you perform your work.

Use tools when external information or calculations are required.

Do not invent information.

When you have enough information, provide a useful answer.
"""


def research_agent(state: AgentState):

    messages = [
        SystemMessage(content=RESEARCH_PROMPT),
        *state["messages"],
    ]

    response = research_llm.invoke(messages)

    return {
        "messages": [response]
    }