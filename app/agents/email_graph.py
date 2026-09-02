from langgraph.graph import StateGraph,START,END
from app.state import EmailState
from app.agents.email_agent import generate_email_draft
from app.nodes.human_approval import human_approval
from langgraph.checkpoint.sqlite import SqliteSaver

def make_email_decision(state:EmailState):

    flag = state['approved']

    if flag:
        return 'send'

    return 'reject'

def build_email_graph():

    builder = StateGraph(EmailState)

    checkpointer = SqliteSaver.from_conn_string('email_checkpoints.db')

    builder.add_node('email_drafting',generate_email_draft)
    builder.add_node('approval',human_approval)

    builder.add_edge(START,'email_drafting')
    builder.add_edge('email_drafting','approval')
    builder.add_conditional_edges(
        'approval',
        make_email_decision,
        {
            'send' : 'send_mail',
            'reject' : END
        }
    )

    return builder.compile(
        checkpointer=checkpointer
    )

