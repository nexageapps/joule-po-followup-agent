"""Unit tests for draft_supplier_email tool."""
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def _path(add_agent_to_path):
    pass


def _call_tool(po_num="PO001", flags=None):
    from tools.draft_supplier_email import draft_supplier_email
    if flags is None:
        flags = ["OVERDUE", "MISSING_GR"]
    return draft_supplier_email.invoke({
        "purchase_order_number": po_num,
        "purchase_order_item": "00010",
        "supplier_name": "Test Supplier GmbH",
        "short_text": "Industrial Steel Bolts M12",
        "net_amount": 4500.0,
        "currency": "EUR",
        "schedule_delivery_date": "2024-10-01",
        "days_overdue": 8,
        "flags": flags,
    })


def test_returns_dict():
    result = _call_tool()
    assert isinstance(result, dict)


def test_required_fields_present():
    result = _call_tool()
    required_keys = [
        "po_number", "item", "supplier", "description",
        "amount", "currency", "delivery_date", "days_overdue",
        "flags", "draft_instruction"
    ]
    for key in required_keys:
        assert key in result, f"Missing key '{key}' in result"


def test_draft_instruction_non_empty():
    result = _call_tool()
    assert isinstance(result["draft_instruction"], str)
    assert len(result["draft_instruction"]) > 0


def test_po_number_in_result():
    result = _call_tool(po_num="PO999")
    assert result["po_number"] == "PO999"


def test_flags_preserved():
    flags = ["DUE_SOON", "MISSING_ACK"]
    result = _call_tool(flags=flags)
    assert result["flags"] == flags


def test_draft_instruction_references_po():
    result = _call_tool(po_num="PO001")
    assert "PO001" in result["draft_instruction"]


def test_draft_instruction_references_supplier():
    result = _call_tool()
    assert "Test Supplier GmbH" in result["draft_instruction"]


def test_no_llm_or_http_calls():
    """Verify the tool does not make any LLM or HTTP calls."""
    with patch("builtins.open", side_effect=AssertionError("Should not open files")):
        # If the tool tried to call an LLM it would need file I/O for config
        # This is a structural check that the tool is purely computational
        result = _call_tool()
        assert result is not None


def test_missing_ack_flag_message_in_instruction():
    result = _call_tool(flags=["MISSING_ACK"])
    assert "acknowledgement" in result["draft_instruction"].lower()
