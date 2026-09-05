from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver
import uuid

from app.context import AgentContext
from app.graph import build_graph


context = AgentContext(
    user_id="zeeshan"
)


def main():

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    builder = build_graph()

    with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:

        graph = builder.compile(
            checkpointer=checkpointer
        )

        while True:

            snapshot = graph.get_state(config)

            if snapshot.interrupts:

                interrupt_data = snapshot.interrupts[0].value

                print("\n" + "=" * 50)
                print("HUMAN APPROVAL REQUIRED")
                print("=" * 50)

                print("\nMessage:")
                print(interrupt_data["message"])

                draft = interrupt_data["draft"]

                print("\nTo:", draft["recipient"])
                print("Subject:", draft["subject"])
                print("\nBody:")
                print(draft["body"])

                answer = input(
                    "\nApprove this email? (yes/no): "
                )

                if answer.lower() in {"yes", "y"}:

                    graph.invoke(
                        Command(resume=True),
                        config=config,
                        context=context
                    )

                    print("\nEmail approved.")

                else:

                    graph.invoke(
                        Command(resume=False),
                        config=config,
                        context=context
                    )

                    print("\nEmail rejected.")

                continue

            user_input = input("\nYou: ")

            if user_input.lower() in {"exit", "quit"}:
                break

            result = graph.invoke(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=config,
                context=context
            )

            snapshot = graph.get_state(config)

            if snapshot.interrupts:
                continue

            print(
                "\nAI:",
                result["messages"][-1].content
            )


if __name__ == "__main__":
    main()