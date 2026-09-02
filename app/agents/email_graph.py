from langgraph.graph import StateGraph,START,END
from app.state import EmailState
from app.agents.email_agent import generate_email_draft
def build_email_graph():

    builder = StateGraph(EmailState)

    builder.add_node('email_drafting',generate_email_draft)