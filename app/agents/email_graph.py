from langgraph.graph import StateGraph,START,END
from app.state import EmailState
from app.agents.email_agent import generate_email_draft
from app.nodes.human_approval import human_approval
from langgraph.checkpoint.sqlite import SqliteSaver
from app.nodes.gmail_sender import send_email
def make_email_decision(state:EmailState):

    flag = state['approved']

    if flag:
        return 'send'

    return 'reject'

def build_email_graph():

    builder = StateGraph(EmailState)

    builder.add_node('email_drafting',generate_email_draft)
    builder.add_node('approval',human_approval)
    builder.add_node('send_email',send_email)

    builder.add_edge(START,'email_drafting')
    builder.add_edge('email_drafting','approval')
    builder.add_conditional_edges(
        'approval',
        make_email_decision,
        {
            'send' : 'send_email',
            'reject' : END
        }
    )
    builder.add_edge('send_email',END)
    
    return builder.compile()

