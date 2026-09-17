
def output_guardrail(state):
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

    print("[Output Guardrail] Passed.")

    return {
        "output_guardrail_passed": True,
        "output_guardrail_reason": None
    }
