from langgraph.graph import StateGraph,START,END
from app.state import AgentState
from app.nodes.supervisor import supervisor
from app.nodes.placeholders import (
    planning_placeholder,
    email_placeholder,
)
from app.nodes.tool_executor import tool_node
from langgraph.prebuilt import ToolNode
from app.agents.research_graph import build_research_graph

research_graph = build_research_graph()

def route_supervisor(state:AgentState):
    return state.next_agent

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node('supervisor',supervisor)
    builder.add_node('research',research_graph)
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
    builder.add_edge('planning',END)
    builder.add_edge('email',END)

    return builder.compile()