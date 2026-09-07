from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime
from app.state import AgentState
from app.tools import TOOLS
from app.llm import llm


research_llm = llm.bind_tools(TOOLS)


RESEARCH_PROMPT = """
You are an autonomous Research Agent.
Your goal is to gather complete information for the user's request.

ITERATION & TOOL INSTRUCTIONS:
1. You can call tools repeatedly in sequence.
2. If your initial search returns partial results (e.g. company names but no emails), issue follow-up tool calls to gather the missing details.
3. Only produce a final text response when you have gathered ALL required information or exhausted search options.
4. When finished, summarize your findings clearly in text WITHOUT generating any tool calls.
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

    print('-'*60)
    print(response)

    return {
        "messages": [response]
    }