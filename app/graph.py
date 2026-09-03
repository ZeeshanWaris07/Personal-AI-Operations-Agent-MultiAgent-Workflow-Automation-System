from langgraph.graph import StateGraph,START,END
from app.state import AgentState,MainState
from app.nodes.supervisor import supervisor

from app.nodes.tool_executor import tool_node
from langgraph.prebuilt import ToolNode
from app.agents.research_graph import build_research_graph
from app.agents.email_graph import build_email_graph
from app.agents.planning_graph import build_planner_graph

research_graph = build_research_graph()
planning_graph = build_planner_graph()
email_graph = build_email_graph()

def run_research(state:MainState,runtime):

    result = research_graph.invoke(
        {
            'messages' : [{
                'role' : 'user',
                'content' : state['objective']
            }]
        },
        context=runtime.context
    )

    return {
        'research_results' : result['research_results']
    }



def run_planning(state:MainState,runtime):

    planning_input = {
        'objective' : state['objective'],
        'research_results' : state['research_results'],
        'plan' : None,
        'review' : None,
        'num_iterations' : 0
    }

    result = planning_graph.invoke(
        planning_input,
        context=runtime.context
    )

    return {
        'plan' : result['plan']
    }

def run_email(state: MainState, runtime):

    recipient = state["recipients"][0]

    email_input = {
        "recipient": recipient,
        "subject": state.get("email_subject", ""),
        "purpose": state["objective"],
        "draft": None,
        "approved": None,
        "send_result": None,
    }

    result = email_graph.invoke(
        email_input,
        context=runtime.context
    )

    return {
        "email_draft": result.get("draft"),
        "email_approved": result.get("approved"),
        "email_send_result": result.get("send_result"),
    }

def route_supervisor(state: MainState):
    return state['next_agent']

def build_graph():
    builder = StateGraph(MainState)

    builder.add_node('supervisor',supervisor)
    builder.add_node('research',run_research)
    builder.add_node('planning',run_planning)
    builder.add_node('email',run_email)


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
    builder.add_edge('research','supervisor')
    builder.add_edge('planning','supervisor')
    builder.add_edge('email','supervisor')

    return builder.compile()