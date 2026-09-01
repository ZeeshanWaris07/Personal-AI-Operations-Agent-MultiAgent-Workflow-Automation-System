from dataclasses import dataclass, field


@dataclass
class AgentContext:

    user_id: str

    num_iterations: int = 0

    max_iterations: int = 10

    retry_count: int = 0

    max_retries: int = 2

    tool_call_history: list[dict] = field(
        default_factory=list
    )
@dataclass
class PlannerContext:

    max_iterations : int = 0