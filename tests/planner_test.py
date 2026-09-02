from app.agents.planning_graph import build_planner_graph
from app.context import PlannerContext

graph = build_planner_graph()

context = PlannerContext(
    user_id="zeeshan",
    max_iterations=3
)

initial_state = {
    "objective": "Find five suitable ML engineering companies",
    "research_results": """
    Company A is hiring an ML Engineer.
    Company B is hiring a Machine Learning Engineer.
    Company C is hiring a Data Scientist.
    Company D is hiring an ML Engineer.
    Company E is hiring an AI Engineer.
    """,
    "plan": None,
    "review": None,
    "num_iterations": 0,
}


result = graph.invoke(
    initial_state,
    context=context
)


print("\nFINAL PLAN:")
print(result["plan"])

print("\nFINAL REVIEW:")
print(result["review"])

print("\nITERATIONS:")
print(result["num_iterations"])