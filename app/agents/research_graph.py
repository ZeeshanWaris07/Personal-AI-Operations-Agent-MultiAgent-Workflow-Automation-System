from langgraph.graph import StateGraph , START,END
from langgraph.prebuilt import tools_condition

from app.state import AgentState
from app.context import AgentContext
from app.nodes.tool_executor import tool_node
from app.agents.research_agent import research_agent
from app.nodes.tool_controller import tool_controller
from app.nodes.filter_tool_calls import create_filter_ai_message
from app.nodes.tool_result_processor import handle_tool_result
from app.nodes.handle_duplicates import handle_duplicate_tools_node
from langgraph.runtime import Runtime

def route_research(state: AgentState,runtime:AgentContext):

    if runtime.context.num_iterations >= runtime.context.max_iterations:

        print(
            f"[Research Graph] "
            f"Max iterations reached: {runtime.context.num_iterations}"
        )
        return "end"

    print("Valid")
    
    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        [],
    )



    if tool_calls:
        print("There are tool calls")
        return "tool_controller"

    return "end"

def route_filter(state:AgentState):

    if state.get('allowed_tool_calls'):
        return 'filter'

    return 'handle_duplicates'

def route_tool_result(
    state: AgentState,
    runtime: Runtime[AgentContext],
):
    results = state.get("tool_result")

    if not results:
        return "end"


    all_successful = all(getattr(r, "status", None) == "success" for r in results)
    if all_successful:
        return "research"


    has_non_retryable = any(
        getattr(r, "status", None) == "failed" and not getattr(r, "retryable", False)
        for r in results
    )
    if has_non_retryable:
        return "end"


    if runtime.context.retry_count >= runtime.context.max_retries:
        return "end"

    return "research"


def build_research_graph():
    builder = StateGraph(AgentState)

    builder.add_node('research',research_agent)
    builder.add_node('tools',tool_node)
    builder.add_node('tool_controller',tool_controller)
    builder.add_node('filter',create_filter_ai_message)
    builder.add_node('handle_duplicates',handle_duplicate_tools_node)
    builder.add_node('tool_result_handler',handle_tool_result)



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
            'handle_duplicates' : 'handle_duplicates'
        }
    )
    builder.add_edge('handle_duplicates','research')
    builder.add_edge('filter','tools')
    builder.add_edge(
        'tools',
        'tool_result_handler'
    )
    builder.add_conditional_edges(
        'tool_result_handler',
        route_tool_result,
        {
            'research' : 'research',
            'end' : END
        }
    )

    return builder.compile()