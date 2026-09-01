from langgraph.graph import StateGraph , START,END
from langgraph.prebuilt import tools_condition

from app.state import AgentState
from app.context import AgentContext
from app.nodes.tool_executor import tool_node
from app.agents.research_agent import research_agent
from app.nodes.tool_controller import tool_controller
from app.nodes.filter_tool_calls import create_filter_ai_message
def route_research(state: AgentState,runtime:AgentContext):

    if runtime.context.num_iterations >= runtime.context.max_iterations:
        print(
            f"[Research Graph] "
            f"Max iterations reached: {runtime.context.num_iterations}"
        )
        return "end"
    
    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        [],
    )



    if tool_calls:
        return "tool_controller"

    return "end"

def route_filter(state:AgentState):

    last_message = state['messages'][-1]

    if last_message.tool_calls:
        return 'filter'

    return 'end'

def build_research_graph():
    builder = StateGraph(AgentState)

    builder.add_node('research',research_agent)
    builder.add_node('tools',tool_node)
    builder.add_node('tool_controller',tool_controller)
    builder.add_node('filter',create_filter_ai_message)

    builder.add_edge(START,'research')
    builder.add_conditional_edges(
        'research',
        route_research,
        {
            'tool_controller' : 'tool_controller',
            'end' : END
        }
    )
    builder.add_conditional_edges(
        'tool_controller',
        route_filter,
        {
            'filter' : 'filter',
            'end' : END
        }
    )
    builder.add_edge('filter','tools')
    builder.add_edge(
        'tools',
        'research'
    )

    return builder.compile()