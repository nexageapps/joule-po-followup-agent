"""Unit tests for rank_purchase_orders tool."""
import pytest
from datetime import date, timedelta


@pytest.fixture(autouse=True)
def _path(add_agent_to_path):
    pass


def _make_flagged(po_num, delivery_date, net_amount, flags):
    return {
        "PurchaseOrder": po_num,
        "Supplier": "SUPP_TEST",
        "SupplierName": "Test Supplier",
        "PurchaseOrderItem": "00010",
        "ShortText": "Test Item",
        "NetAmount": net_amount,
        "Currency": "EUR",
        "ScheduleDeliveryDate": delivery_date,
        "flags": flags,
    }


def test_most_overdue_ranked_first():
    from tools.rank_purchase_orders import rank_purchase_orders
    po1 = _make_flagged("PO001", (date.today() - timedelta(days=2)).isoformat(), 1000.0, ["OVERDUE"])
    po2 = _make_flagged("PO002", (date.today() - timedelta(days=10)).isoformat(), 1000.0, ["OVERDUE", "MISSING_GR"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1, po2]})
    assert result[0]["PurchaseOrder"] == "PO002"


def test_higher_value_ranked_first_when_equal_overdue():
    from tools.rank_purchase_orders import rank_purchase_orders
    past = (date.today() - timedelta(days=5)).isoformat()
    po1 = _make_flagged("PO001", past, 500.0, ["OVERDUE"])
    po2 = _make_flagged("PO002", past, 9000.0, ["OVERDUE"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1, po2]})
    assert result[0]["PurchaseOrder"] == "PO002"


def test_rank_field_added():
    from tools.rank_purchase_orders import rank_purchase_orders
    po1 = _make_flagged("PO001", (date.today() - timedelta(days=3)).isoformat(), 1000.0, ["OVERDUE"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1]})
    assert "rank" in result[0]
    assert result[0]["rank"] == 1


def test_days_overdue_field_added():
    from tools.rank_purchase_orders import rank_purchase_orders
    past = (date.today() - timedelta(days=4)).isoformat()
    po1 = _make_flagged("PO001", past, 1000.0, ["OVERDUE"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1]})
    assert "days_overdue" in result[0]
    assert result[0]["days_overdue"] == 4


def test_due_soon_has_zero_days_overdue():
    from tools.rank_purchase_orders import rank_purchase_orders
    soon = (date.today() + timedelta(days=2)).isoformat()
    po1 = _make_flagged("PO001", soon, 1000.0, ["DUE_SOON"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1]})
    assert result[0]["days_overdue"] == 0


def test_empty_input_returns_empty():
    from tools.rank_purchase_orders import rank_purchase_orders
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": []})
    assert result == []


def test_rank_is_sequential():
    from tools.rank_purchase_orders import rank_purchase_orders
    po1 = _make_flagged("PO001", (date.today() - timedelta(days=1)).isoformat(), 1000.0, ["OVERDUE"])
    po2 = _make_flagged("PO002", (date.today() - timedelta(days=5)).isoformat(), 2000.0, ["OVERDUE"])
    po3 = _make_flagged("PO003", (date.today() + timedelta(days=1)).isoformat(), 500.0, ["DUE_SOON"])
    result = rank_purchase_orders.invoke({"flagged_purchase_orders": [po1, po2, po3]})
    ranks = [r["rank"] for r in result]
    assert ranks == [1, 2, 3]
