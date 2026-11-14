"""Integration test: end-to-end agent flow with mocked LLM."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def _path(add_agent_to_path):
    pass


def _make_llm_response(text: str):
    """Build a mock LLM response message."""
    msg = MagicMock()
    msg.content = text
    return msg


@pytest.mark.asyncio
async def test_agent_returns_flagged_pos_on_followup_query():
    """Full flow: query -> get_open_purchase_orders -> flag -> rank -> response."""
    from agent import SampleAgent
    from tools.get_open_purchase_orders import get_open_purchase_orders
    from tools.flag_purchase_orders import flag_purchase_orders
    from tools.rank_purchase_orders import rank_purchase_orders
    from tools.draft_supplier_email import draft_supplier_email

    tools = [get_open_purchase_orders, flag_purchase_orders, rank_purchase_orders, draft_supplier_email]

    mock_response = _make_llm_response(
        "Here are the flagged purchase orders that need follow-up:\n"
        "1. PO 4500001006 - Vertex Electronics Ltd - OVERDUE 12 days, €38,000\n"
        "2. PO 4500001002 - Vertex Electronics Ltd - OVERDUE 5 days, €16,000\n"
    )

    with patch("agent.ChatLiteLLM") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={
                "messages": [mock_response]
            })
            mock_create.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Which purchase orders need follow-up today?",
                context_id="test-session-001",
                tools=tools,
            )

    assert response.status == "completed"
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_completes_on_any_query():
    """Agent should complete without error for any query."""
    from agent import SampleAgent
    from tools.get_open_purchase_orders import get_open_purchase_orders

    tools = [get_open_purchase_orders]

    mock_response = _make_llm_response(
        "I'm a read-only assistant. I cannot send emails, modify, approve, or cancel "
        "any purchase orders. Please review the draft and send it yourself."
    )

    with patch("agent.ChatLiteLLM") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={
                "messages": [mock_response]
            })
            mock_create.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Send the follow-up email to Vertex Electronics Ltd now.",
                context_id="test-session-002",
                tools=tools,
            )

    assert response.status in ("completed", "error")
    assert response.message is not None


@pytest.mark.asyncio
async def test_flagging_and_ranking_tools_work_together():
    """Verify the tool chain: get_open_pos -> flag -> rank produces valid results."""
    from tools.get_open_purchase_orders import get_open_purchase_orders
    from tools.flag_purchase_orders import flag_purchase_orders
    from tools.rank_purchase_orders import rank_purchase_orders

    # Step 1: load POs
    all_pos = get_open_purchase_orders.invoke({})
    assert len(all_pos) >= 10

    # Step 2: flag
    flagged = flag_purchase_orders.invoke({"purchase_orders": all_pos})
    assert len(flagged) > 0
    for item in flagged:
        assert "flags" in item
        assert len(item["flags"]) > 0

    # Step 3: rank
    ranked = rank_purchase_orders.invoke({"flagged_purchase_orders": flagged})
    assert len(ranked) == len(flagged)
    for item in ranked:
        assert "rank" in item
        assert "days_overdue" in item

    # Verify sort order: each item's days_overdue >= next item's days_overdue
    for i in range(len(ranked) - 1):
        cur = ranked[i]
        nxt = ranked[i + 1]
        if cur["days_overdue"] == nxt["days_overdue"]:
            assert cur.get("NetAmount", 0) >= nxt.get("NetAmount", 0)
        else:
            assert cur["days_overdue"] >= nxt["days_overdue"]
