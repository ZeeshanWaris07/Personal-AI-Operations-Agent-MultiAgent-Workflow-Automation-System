from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime
from app.state import AgentState
from app.tools import TOOLS
from app.llm import llm


research_llm = llm.bind_tools(TOOLS)


RESEARCH_PROMPT = """
You are the Research Agent in a Personal AI Operations Agent.

Your job is to gather accurate information for the user.

You have access to tools that can help you perform your work.

Use tools when external information or calculations are required.

Do not invent information.

When you have enough information, provide a useful answer.
"""


def research_agent(state: AgentState,runtime:Runtime):
    
    runtime.context.num_iterations += 1

    print(
        f"Iteration: {runtime.context.num_iterations}"
    )

    messages = [
        SystemMessage(content=RESEARCH_PROMPT),
        *state["messages"],
    ]

    response = research_llm.invoke(messages)

    return {
        "messages": [response]
    }