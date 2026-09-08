import asyncio

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


def edit_draft(draft):

    print("\nCurrent email:")
    print(f"\nTo: {draft['recipient']}")
    print(f"Subject: {draft['subject']}")
    print("\nBody:")
    print(draft["body"])

    print("\nWhat would you like to edit?")
    print("1. Recipient")
    print("2. Subject")
    print("3. Body")
    print("4. Nothing")

    choice = input("\nChoice: ")

    if choice == "1":
        draft["recipient"] = input("New recipient: ")

    elif choice == "2":
        draft["subject"] = input("New subject: ")

    elif choice == "3":
        print("\nEnter the new body:")
        draft["body"] = input("> ")

    return draft


def handle_email_approval(interrupt_data):

    drafts = interrupt_data["drafts"]

    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)

    print(f"\n{len(drafts)} email(s) are ready to send.")

    for index, draft in enumerate(drafts, start=1):

        print("\n" + "-" * 60)
        print(f"EMAIL {index}")
        print("-" * 60)

        print(f"To: {draft['recipient']}")
        print(f"Subject: {draft['subject']}")
        print("\nBody:")
        print(draft["body"])

    while True:

        print("\n" + "-" * 60)
        print("1. Approve all")
        print("2. Edit an email")
        print("3. Reject all")

        choice = input("\nChoice: ")

        if choice == "1":

            return {
                "approved": True,
                "drafts": drafts
            }

        elif choice == "2":

            if len(drafts) == 1:
                index = 0

            else:
                try:
                    index = int(
                        input(
                            f"Email number (1-{len(drafts)}): "
                        )
                    ) - 1

                    if index < 0 or index >= len(drafts):
                        print("Invalid email number.")
                        continue

                except ValueError:
                    print("Please enter a valid number.")
                    continue

            drafts[index] = edit_draft(drafts[index])

            print("\nEmail updated.")

            print("\nUpdated email:")
            print(f"To: {drafts[index]['recipient']}")
            print(f"Subject: {drafts[index]['subject']}")
            print("\nBody:")
            print(drafts[index]["body"])

        elif choice == "3":

            return {
                "approved": False,
                "drafts": drafts
            }

        else:
            print("Invalid choice.")


context = AgentContext(
    user_id="zeeshan"
)


async def main():

    thread_id = "test_2"

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

                if interrupt_data["type"] == "email_approval":

                    decision = handle_email_approval(
                        interrupt_data
                    )

                    async for event in graph.astream_events(
                        Command(resume=decision),
                        config=config,
                        context=context,
                        version="v2"
                    ):
                        handle_event(event)

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