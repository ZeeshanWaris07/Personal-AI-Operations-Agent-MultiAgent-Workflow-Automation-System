from app.agents.planning_agent import Planner , reviewer
from langgraph.graph import StateGraph,START,END
from app.state import PlanningState
from app.context import PlannerContext
from langgraph.runtime import Runtime

def route_reviewer(state:PlanningState,runtime):

    iterations = state.get('num_iterations',0)

    if iterations >= runtime.context.max_iterations:
        return 'final'

    review = state.get('review',None)

    if review is None:
        return 'final'

    if review.approved:
        return 'final'

    return 'plan'


def build_planner_graph():

    builder = StateGraph(PlanningState)

    builder.add_node('planner',Planner)
    builder.add_node('reviewer',reviewer)

    builder.add_edge(START,'planner')
    builder.add_edge('planner','reviewer')
    builder.add_conditional_edges(
        'reviewer',
        route_reviewer,
        {
            'plan' : 'planner',
            'final' : END
        }
    )

    return builder.compile()