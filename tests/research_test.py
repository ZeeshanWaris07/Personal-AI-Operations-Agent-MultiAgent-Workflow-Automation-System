import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.context import AgentContext
from app.state import AgentState
from app.utils.tool_result import ToolExecutionResult
from app.utils.tool_history import create_tool_signature, record_tool_call
from app.nodes.tool_controller import tool_controller
from app.nodes.filter_tool_calls import create_filter_ai_message
from app.nodes.tool_result_processor import handle_tool_result
from app.nodes.handle_duplicates import handle_duplicate_tools_node


@pytest.fixture
def mock_context():
    """Provides a fresh AgentContext for each test."""
    return AgentContext(user_id="test_user_123")


class TestToolControllerAndHistory:

    def test_new_tool_call_recorded_as_pending(self, mock_context):
        """Verify new tool calls are marked as pending and added to allowed_tool_calls."""
        state: AgentState = {
            "messages": [
                AIMessage(
                    content="Searching for info...",
                    tool_calls=[{
                        "name": "web_search",
                        "args": {"query": "LangGraph tutorial"},
                        "id": "call_1"
                    }]
                )
            ],
            "allowed_tool_calls": []
        }

        # Mock Runtime wrapper expected by tool_controller
        class RuntimeMock:
            context = mock_context

        result = tool_controller(state, RuntimeMock())

        # Check allowed calls output
        assert len(result["allowed_tool_calls"]) == 1
        assert result["allowed_tool_calls"][0]["id"] == "call_1"

        # Check history recording
        assert len(mock_context.tool_call_history) == 1
        history_entry = mock_context.tool_call_history[0]
        assert history_entry["status"] == "pending"
        assert history_entry["tool_call_id"] == "call_1"

    def test_duplicate_successful_tool_call_skipped(self, mock_context):
        """Verify previously successful tool calls are skipped by tool_controller."""
        sig = create_tool_signature("web_search", {"query": "LangGraph tutorial"})

        # Pre-seed history with a successful call
        record_tool_call(
            mock_context.tool_call_history,
            tool_name="web_search",
            tool_call_id="call_0",
            signature=sig,
            status="success"
        )

        state: AgentState = {
            "messages": [
                AIMessage(
                    content="Retrying same search...",
                    tool_calls=[{
                        "name": "web_search",
                        "args": {"query": "LangGraph tutorial"},
                        "id": "call_1"
                    }]
                )
            ],
            "allowed_tool_calls": []
        }

        class RuntimeMock:
            context = mock_context

        result = tool_controller(state, RuntimeMock())

        # Should be filtered out
        assert len(result["allowed_tool_calls"]) == 0

    def test_handle_duplicate_tools_node_generates_synthetic_tool_message(self):
        """Verify skipped duplicate tools receive synthetic ToolMessages to avoid hanging calls."""
        state: AgentState = {
            "messages": [
                AIMessage(
                    content="Need duplicate data",
                    tool_calls=[{
                        "name": "web_search",
                        "args": {"query": "LangGraph tutorial"},
                        "id": "call_duplicate_99"
                    }]
                )
            ]
        }

        res = handle_duplicate_tools_node(state)

        assert "messages" in res
        assert len(res["messages"]) == 1
        synthetic_msg = res["messages"][0]

        assert isinstance(synthetic_msg, ToolMessage)
        assert synthetic_msg.tool_call_id == "call_duplicate_99"
        assert "[System Notice]" in synthetic_msg.content


class TestBatchToolResultProcessing:

    def test_batch_tool_execution_updates_all_history_entries(self, mock_context):
        """Verify handle_tool_result updates history status for ALL parallel calls in a batch."""
        # 1. Simulate 2 pending tool calls in history
        sig1 = create_tool_signature("search", {"q": "python"})
        sig2 = create_tool_signature("search", {"q": "langgraph"})

        record_tool_call(
            mock_context.tool_call_history,
            tool_name="search",
            tool_call_id="id_1",
            signature=sig1,
            status="pending",
        )
        record_tool_call(
            mock_context.tool_call_history,
            tool_name="search",
            tool_call_id="id_2",
            signature=sig2,
            status="pending",
        )

        # 2. Simulate batch tool execution results (Added 'tool="search"')
        tool_results = [
            ToolExecutionResult(
                tool="search",
                tool_call_id="id_1",
                status="success",
                result="Python docs...",
                error_type=None,
                message=None,
                retryable=False,
            ),
            ToolExecutionResult(
                tool="search",
                tool_call_id="id_2",
                status="success",
                result="LangGraph docs...",
                error_type=None,
                message=None,
                retryable=False,
            ),
        ]

        state: AgentState = {"tool_result": tool_results}

        class RuntimeMock:
            context = mock_context

        handle_tool_result(state, RuntimeMock())

        # 3. Verify BOTH entries transitioned from pending -> success
        assert mock_context.tool_call_history[0]["status"] == "success"
        assert mock_context.tool_call_history[0]["result"] == "Python docs..."

        assert mock_context.tool_call_history[1]["status"] == "success"
        assert mock_context.tool_call_history[1]["result"] == "LangGraph docs..."


class TestFilterAIMessage:

    def test_filter_creates_clean_message_without_id_collision(self):
        """Verify create_filter_ai_message constructs a new AIMessage with allowed calls."""
        original_msg = AIMessage(
            id="msg_original_123",
            content="I will search both terms",
            tool_calls=[
                {"name": "search", "args": {"q": "A"}, "id": "id_1"},
                {"name": "search", "args": {"q": "B"}, "id": "id_2"}
            ]
        )

        state: AgentState = {
            "messages": [original_msg],
            "allowed_tool_calls": [
                {"name": "search", "args": {"q": "A"}, "id": "id_1"}
            ]
        }

        result = create_filter_ai_message(state)

        filtered_msg = result["messages"][0]
        assert len(filtered_msg.tool_calls) == 1
        assert filtered_msg.tool_calls[0]["id"] == "id_1"
        # Ensure we do not reuse the message ID to avoid state overwrite bugs
        assert filtered_msg.id != "msg_original_123"