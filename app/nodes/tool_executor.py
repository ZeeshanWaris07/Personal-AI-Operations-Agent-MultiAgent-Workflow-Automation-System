from app.tools import TOOLS
from langgraph.prebuilt import ToolNode


def create_tool_node(rag_tools):
    return ToolNode([
        *TOOLS,
        *rag_tools
    ])