from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime
from app.state import AgentState
from app.tools import TOOLS
from app.llm import llm


research_llm = llm.bind_tools(TOOLS)


RESEARCH_PROMPT = """
You are an autonomous Research Agent.

Your goal is to gather complete and accurate information for the user's request.

You have access to web research tools.

IMPORTANT TOOL EXECUTION RULE:

When you identify multiple independent pieces of information that need
to be researched, generate MULTIPLE TOOL CALLS IN THE SAME RESPONSE
whenever possible.

Do NOT unnecessarily perform independent searches one at a time.

For example, if you need information about five different companies,
generate five independent tool calls together:

- search_web(company_1)
- search_web(company_2)
- search_web(company_3)
- search_web(company_4)
- search_web(company_5)

These independent calls can then be executed concurrently.

Only perform sequential tool calls when the next search depends on
the result of a previous search.

RESEARCH PROCESS:

1. Understand the user's request.
2. Perform an initial discovery search if necessary.
3. Identify the information or entities that need further research.
4. Group independent research tasks together and issue their tool
   calls in the same response.
5. After receiving the tool results, determine whether additional
   research is necessary.
6. When sufficient information has been gathered, stop calling tools
   and produce the final answer.

Do not invent information.

Do not claim to have researched a source unless the relevant tool
was actually used.

When you have sufficient information, return a final text response
without tool calls.
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