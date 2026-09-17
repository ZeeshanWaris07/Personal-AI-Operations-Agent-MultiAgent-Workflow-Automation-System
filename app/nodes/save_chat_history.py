
from app.state import MainState


def save_chat_history(state: MainState):

    history = state.get("chat_history", [])

    new_turn = [
        {
            "role": "user",
            "content": state["objective"]
        },
        {
            "role": "assistant",
            "content": state["final_response"]
        }
    ]

    return {
        "chat_history": history + new_turn
    }