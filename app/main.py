from langchain_core.messages import HumanMessage
from app.context import AgentContext
from app.graph import build_graph

context = AgentContext(
    user_id='zeeshan'
)

graph = build_graph()


def main():

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ],
                "final_response": None,
            },
            context=context
        )

        print("\nAI:", result["messages"][-1].content)


if __name__ == "__main__":
    main()