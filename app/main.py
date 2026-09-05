import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.context import AgentContext
from app.graph import build_graph

def handle_event(event):

    event_type = event["event"]

    if event_type == "on_chain_start":

        print(f"\n[START] {event['name']}")

    elif event_type == "on_chain_end":

        print(f"\n[END] {event['name']}")

    elif event_type == "on_tool_start":

        print(f"\n[TOOL] {event['name']}")

    elif event_type == "on_tool_end":

        print(f"\n[TOOL COMPLETE] {event['name']}")

    elif event_type == "on_chat_model_stream":

        chunk = event["data"]["chunk"]

        content = chunk.content

        if isinstance(content, str):
            print(content, end="", flush=True)

        elif isinstance(content, list):

            for block in content:

                if isinstance(block, dict):

                    text = block.get("text")

                    if text:
                        print(text, end="", flush=True)



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

    async with AsyncSqliteSaver.from_conn_string(
        "checkpoints.db"
    ) as checkpointer:

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


                    async for event in graph.astream_events(
                        Command(resume=True),
                        config=config,
                        context=context,
                        version="v2"
                    ):

                        handle_event(event)

                    print("\n\nEmail approved.")

                else:


                    async for event in graph.astream_events(
                        Command(resume=False),
                        config=config,
                        context=context,
                        version="v2"
                    ):

                        handle_event(event)

                    print("\n\nEmail rejected.")

                continue


            user_input = input("\n\nYou: ")

            if user_input.lower() in {"exit", "quit"}:
                break


            async for event in graph.astream_events(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ],
                    "objective": user_input
                },
                config=config,
                context=context,
                version="v2"
            ):

                handle_event(event)



            snapshot = await graph.aget_state(config)

            if snapshot.interrupts:
                continue


            final_state = snapshot.values

            if final_state.get("messages"):

                print(
                    "\n\nAI:",
                    final_state["messages"][-1].content
                )



if __name__ == "__main__":
    asyncio.run(main())
