import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.context import AgentContext
from app.graph import build_graph


context = AgentContext(
    user_id="zeeshan"
)


async def main():

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    builder = build_graph()

    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:

        graph = builder.compile(
            checkpointer=checkpointer
        )

        while True:

            snapshot = await graph.aget_state(config)

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

                    await graph.ainvoke(
                        Command(resume=True),
                        config=config,
                        context=context
                    )

                    print("\nEmail approved.")

                else:

                    await graph.ainvoke(
                        Command(resume=False),
                        config=config,
                        context=context
                    )

                    print("\nEmail rejected.")

                continue

            user_input = input("\nYou: ")

            if user_input.lower() in {"exit", "quit"}:
                break

            result = await graph.ainvoke(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ],
                    'objective' : user_input
                },
                config=config,
                context=context
            )

            snapshot = await graph.aget_state(config)

            if snapshot.interrupts:
                continue

            print(
                "\nAI:",
                result["messages"][-1].content
            )


if __name__ == "__main__":
    asyncio.run(main())