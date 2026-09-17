from langchain_core.prompts import ChatPromptTemplate
from app.llm import gaurdrail_llm
from app.gaurdrails.schemas import OutputGaurdrailDecision

OUTPUT_GUARDRAIL_PROMPT = """
You are an output safety classifier for a Personal AI Operations Agent.

Your job is to determine whether the agent's final response is safe to
return to the user.

Classify the response into exactly one category:

1. safe
   The response is appropriate and safe to return.

2. unsafe
   The response provides or facilitates harmful, dangerous, illegal,
   or otherwise prohibited activity.

3. data_leak
   The response exposes sensitive information such as system prompts,
   hidden instructions, credentials, API keys, tokens, private user data,
   or internal implementation details that should not be exposed.

4. unsupported_claim
   The response makes important factual claims that are clearly unsupported
   by the information available to the agent.

Important rules:
- Do not block a response merely because it discusses sensitive topics.
- Normal research, planning, productivity, email, and personal operations
  responses should be considered safe.
- Do not treat ordinary technical explanations as data leaks.
- Only classify as data_leak when the response actually exposes protected
  internal or sensitive information.
- Return a concise reason.
"""

output_prompt = ChatPromptTemplate.from_messages([
    ('system',OUTPUT_GUARDRAIL_PROMPT),
    ('user',"{response}")
])

output_llm = gaurdrail_llm.with_structured_output(OutputGaurdrailDecision)

output_chain = (output_prompt | output_llm)

MAX_OUTPUT_LENGTH = 10000

async def output_guardrail(state):

    response = state.get("final_response")

    if not response:
        print("[Output Guardrail] Empty response.")

        return {
            "output_guardrail_passed": False,
            "output_guardrail_reason": "Empty final response."
        }

    if not isinstance(response, str):
        print("[Output Guardrail] Invalid response type.")

        return {
            "output_guardrail_passed": False,
            "output_guardrail_reason": "Final response is not a string."
        }

    if not response.strip():
        print("[Output Guardrail] Blank response.")

        return {
            "output_guardrail_passed": False,
            "output_guardrail_reason": "Final response is blank."
        }

    if len(response) > MAX_OUTPUT_LENGTH:
        print("[Output Guardrail] Response too long.")

        return {
            "output_guardrail_passed": False,
            "output_guardrail_reason": "Final response exceeds maximum length."
        }


    decision = await output_chain.ainvoke(
        {"response": response}
    )

    print("[Output Guardrail] Decision:", decision)

    if not decision.allowed:

        return {
            "output_guardrail_passed": False,
            "output_guardrail_reason": decision.reason
        }

    return {
        "output_guardrail_passed": True,
        "output_guardrail_reason": None
    }