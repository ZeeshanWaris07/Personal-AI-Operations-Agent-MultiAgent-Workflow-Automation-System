import json

def create_tool_signature(tool_name: str, arguments: dict) -> str:
    try:
        serialized_args = json.dumps(arguments, sort_keys=True)
    except TypeError:
        serialized_args = str(arguments)
    return f"{tool_name}:{serialized_args}"


def find_previous_call(
    history: list[dict],
    signature: str,
) -> dict | None:

    for entry in reversed(history):

        if entry["signature"] == signature:
            return entry

    return None


def record_tool_call(
    history: list[dict],
    *,
    tool_name: str,
    tool_call_id: str,
    signature: str,
    status: str,
    **extra,
):

    history.append(
        {
            "tool": tool_name,
            "tool_call_id": tool_call_id,
            "signature": signature,
            "status": status,
            **extra,
        }
    )

def update_tool_call(
    history: list[dict],
    tool_call_id: str,
    *,
    status: str,
    **updates,
):

    for entry in reversed(history):

        if entry["tool_call_id"] == tool_call_id:

            entry["status"] = status
            entry.update(updates)

            return