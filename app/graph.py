from langgraph.graph import StateGraph,START,END
from app.state import AgentState
from app.nodes.supervisor import supervisor
from app.nodes.placeholders import (
    planning_placeholder,
    email_placeholder,
    research_placeholder
)



def route_supervisor(state:AgentState):
    return state.next_agent

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node('supervisor',supervisor)
    builder.add_node('research',research_placeholder)
    builder.add_node('planning',planning_placeholder)
    builder.add_node('email',email_placeholder)

    builder.add_edge(START,'supervisor')

    builder.add_conditional_edges(
        'supervisor',
        route_supervisor,
        {
            'research' : 'resarch',
            'planning' : 'planning',
            'email' : 'email',
            'final' : END
        }
    )

    builder.add_edge('research',END)
    builder.add_edge('planning',END)
    builder.add_edge('email',END)

    return builder.compile()