from langgraph.graph import StateGraph,START,END
from app.state import AgentState,MainState
from app.nodes.supervisor import supervisor

from app.nodes.tool_executor import tool_node
from langgraph.prebuilt import ToolNode
from app.agents.research_graph import build_research_graph
from app.agents.email_graph import build_email_graph
from app.agents.planning_graph import build_planner_graph
from langgraph.checkpoint.sqlite import SqliteSaver
from app.nodes.final_response import final_response

research_graph = build_research_graph()
planning_graph = build_planner_graph()
email_graph = build_email_graph()

async def run_research(state: MainState, runtime):
    prompt_content = f"OBJECTIVE: {state['objective']}"
    
    # Pass previous findings if this is a follow-up research attempt
    if state.get("research_results"):
        prompt_content += f"""

PREVIOUS RESEARCH FINDINGS:
{state['research_results']}

INSTRUCTIONS FOR RESEARCH AGENT:
The previous research did not fully satisfy the objective.
- Do NOT repeat searches you have already performed.
- Perform targeted follow-up queries for missing details (e.g., search specific company websites or contact pages for HR emails).
- If information is genuinely not publicly available after trying, state that clearly in your final response so the workflow can proceed.
"""

    result = await research_graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt_content
                }
            ]
        },
        config={"configurable": {"context": runtime.context}}
    )

    research_results = result["messages"][-1].content
    return {"research_results": research_results}


async def run_planning(state: MainState, runtime):

    planning_input = {
        "objective": state["objective"],
        "research_results": state["research_results"],
        "plan": None,
        "review": None,
        "num_iterations": 0
    }

    result = await planning_graph.ainvoke(
        planning_input,
        context=runtime.context
    )

    return {
        "plan": result["plan"]
    }


async def run_email(state: MainState, runtime):

    recipient = state["recipients"][0]

    email_input = {
        "recipient": recipient,
        "subject": "",
        "purpose": state["objective"],
        "draft": None,
        "approved": None,
        "send_result": None,
    }

    result = await email_graph.ainvoke(
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
    builder.add_node('final',final_response)

    builder.add_edge(START,'supervisor')

    builder.add_conditional_edges(
        'supervisor',
        route_supervisor,
        {
            'research' : 'research',
            'planning' : 'planning',
            'email' : 'email',
            'final' : 'final'
        }
    )
    builder.add_edge('research','supervisor')
    builder.add_edge('planning','supervisor')
    builder.add_edge('email','supervisor')
    builder.add_edge('final',END)

    return builder