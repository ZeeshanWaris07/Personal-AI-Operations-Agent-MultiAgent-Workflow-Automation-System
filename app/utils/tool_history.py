def create_tool_signature(
    tool_name: str,
    arguments: dict,
) -> str:

    args = ",".join(
        f"{key}={value}"
        for key, value in sorted(arguments.items())
    )

    return f"{tool_name}:{args}"


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
    signature: str,
    status: str,
    **extra,
):

    history.append(
        {
            "tool": tool_name,
            "signature": signature,
            "status": status,
            **extra,
        }
    )