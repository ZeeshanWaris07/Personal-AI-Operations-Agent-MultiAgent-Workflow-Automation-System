from dataclasses import dataclass

@dataclass
class AgentContext:
    user_id : str
    num_iterations:int = 0