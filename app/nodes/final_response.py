from langchain_core.messages import AIMessage
from app.state import MainState
from app.models.models import FinalResponse
from app.llm import llm


async def final_response(state: MainState):

    structured_llm = llm.with_structured_output(FinalResponse)

    prompt = f"""
You are the final response agent.

Create a concise final response summarizing what the
Personal AI Operations Agent accomplished.

USER OBJECTIVE:
{state["objective"]}

RESEARCH RESULTS:
{state.get("research_results")}

PLAN:
{state.get("plan")}

EMAIL DRAFT:
{state.get("email_draft")}

EMAIL APPROVED:
{state.get("email_approved")}

EMAIL SEND RESULT:
{state.get("email_send_result")}

Summarize:
1. What was accomplished.
2. Important research findings.
3. The resulting plan.
4. Email status, if an email workflow was requested.

Do not claim that an email was sent unless
EMAIL SEND RESULT confirms it.

Return the result using the required structured format.
"""

    response = await structured_llm.ainvoke(prompt)

    return {
        "final_response": response.model_dump_json(),
        "messages": [
            AIMessage(
                content=response.model_dump_json()
            )
        ]
    }