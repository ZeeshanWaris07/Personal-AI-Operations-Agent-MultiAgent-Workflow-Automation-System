from langgraph.graph import StateGraph,START,END
from app.state import AgentState,MainState
from app.nodes.supervisor import supervisor

from app.nodes.output_gaurdrails import output_guardrail
from app.agents.research_graph import build_research_graph
from app.agents.email_graph import build_email_graph
from app.agents.planning_graph import build_planner_graph
from langgraph.checkpoint.sqlite import SqliteSaver
from app.nodes.final_response import final_response
from app.nodes.input_gaurdrails import input_gaurdrail
from langchain_core.messages import AIMessage
from app.nodes.save_chat_history import save_chat_history

planning_graph = build_planner_graph()
email_graph = build_email_graph()

def make_run_research(research_graph):

    async def run_research(state: MainState, runtime):
        prompt_content = f"OBJECTIVE: {state['objective']}"

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

        return {
            "research_results": research_results
        }

    return run_research


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


from langchain_core.messages import AIMessage


async def run_email(state: MainState, runtime):

    email_input = {
        "recipients": state["recipients"],
        "purpose": state["objective"],
        "drafts": [],
        "approved": None,
        "send_result": None,
        "messages": []
    }

    result = await email_graph.ainvoke(
        email_input,
        context=runtime.context
    )

    messages = result.get("messages", [])

    email_result = messages[-1] if messages else None

    return {
        "email_drafts": result.get("drafts"),
        "email_approved": result.get("approved"),
        "email_send_result": result.get("send_result"),
        "messages": [email_result] if email_result else []
    }

def route_supervisor(state: MainState):
    return state['next_agent']

def route_after_guardrail(state:MainState):
    decision = state["gaurdrail_decision"]

    if decision.allowed:
        return "supervisor"

    return "blocked"

def gaurdrail_response(state):

    decision = state["gaurdrail_decision"]

    response = (
        "I can't process this request because it was blocked by "
        f"the input guardrail: {decision.reason}"
    )

    return {
        "messages": [AIMessage(content=response)],
        "final_response": response,
    }

def route_after_output_guardrail(state: MainState):

    if state["output_guardrail_passed"]:
        return "passed"

    return "blocked"

def output_guardrail_blocked(state: MainState):

    response = (
        "I couldn't safely return the generated response."
    )

    return {
        "messages": [AIMessage(content=response)],
        "final_response": response,
    }

def build_graph(rag_pipeline):

    builder = StateGraph(MainState)

    research_graph = build_research_graph(rag_pipeline)

    run_research = make_run_research(research_graph)

    builder.add_node('input_gaurdrails',input_gaurdrail)
    builder.add_node('supervisor', supervisor)
    builder.add_node('research', run_research)
    builder.add_node('planning', run_planning)
    builder.add_node('email', run_email)
    builder.add_node('final', final_response)
    builder.add_node('blocked',gaurdrail_response)
    builder.add_node('output_guardrail',output_guardrail)
    builder.add_node("output_guardrail_blocked",output_guardrail_blocked)
    builder.add_node('save_chat_history',save_chat_history)

    builder.add_edge(START, 'input_gaurdrails')

    builder.add_conditional_edges(
        'input_gaurdrails',
        route_after_guardrail,
        {
            'supervisor':'supervisor',
            'blocked':'blocked'
        }
    )

    builder.add_edge('blocked',END)

    builder.add_conditional_edges(
        'supervisor',
        route_supervisor,
        {
            'research': 'research',
            'planning': 'planning',
            'email': 'email',
            'final': 'final'
        }
    )

    builder.add_edge('research', 'supervisor')
    builder.add_edge('planning', 'supervisor')
    builder.add_edge('email', 'supervisor')
    builder.add_edge('final', 'output_guardrail')
    builder.add_conditional_edges(
        'output_guardrail',
        route_after_output_guardrail,
        {
            'passed':'save_chat_history',
            'blocked':'output_guardrail_blocked'
        }
    )
    builder.add_edge('output_guardrail_blocked',END)
    builder.add_edge('save_chat_history',END)

    return builder