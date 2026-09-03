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

def run_email(state:MainState,runtime):




def route_supervisor(state:AgentState):
    return state.next_agent

def build_graph():
    builder = StateGraph(MainState)

    builder.add_node('supervisor',supervisor)
    builder.add_node('research',research_graph)
    builder.add_node('planning',planning_graph)
    builder.add_node('email',email_graph)


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