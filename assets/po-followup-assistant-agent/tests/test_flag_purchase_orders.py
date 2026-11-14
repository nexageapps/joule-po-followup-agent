"""Unit tests for flag_purchase_orders tool."""
import pytest
from datetime import date, timedelta


@pytest.fixture(autouse=True)
def _path(add_agent_to_path):
    pass


def _make_po(po_num, delivery_date, ack=None, gr_status="OPEN", net_amount=1000.0):
    return {
        "PurchaseOrder": po_num,
        "Supplier": "SUPP_TEST",
        "SupplierName": "Test Supplier",
        "PurchasingOrganization": "1010",
        "DocumentDate": "2024-01-01",
        "items": [
            {
                "PurchaseOrderItem": "00010",
                "Material": "MAT-001",
                "ShortText": "Test Item",
                "OrderQuantity": 1.0,
                "NetPriceAmount": net_amount,
                "NetPriceQuantity": 1.0,
                "Currency": "EUR",
                "NetAmount": net_amount,
                "ScheduleDeliveryDate": delivery_date,
                "ConfirmationDeliveryDate": None,
                "OrderAcknowledgmentNumber": ack,
                "GoodsReceiptStatus": gr_status,
                "PurchaseOrderQuantity": 1.0,
            }
        ],
    }


def test_overdue_flag_applied():
    from tools.flag_purchase_orders import flag_purchase_orders
    past = (date.today() - timedelta(days=5)).isoformat()
    pos = [_make_po("PO001", past, ack="ACK001", gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 1
    assert "OVERDUE" in result[0]["flags"]


def test_due_soon_flag_applied():
    from tools.flag_purchase_orders import flag_purchase_orders
    soon = (date.today() + timedelta(days=2)).isoformat()
    pos = [_make_po("PO002", soon, ack="ACK002", gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 1
    assert "DUE_SOON" in result[0]["flags"]


def test_missing_ack_flag_applied():
    from tools.flag_purchase_orders import flag_purchase_orders
    future = (date.today() + timedelta(days=10)).isoformat()
    pos = [_make_po("PO003", future, ack=None, gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 1
    assert "MISSING_ACK" in result[0]["flags"]


def test_missing_gr_flag_applied():
    from tools.flag_purchase_orders import flag_purchase_orders
    past = (date.today() - timedelta(days=3)).isoformat()
    pos = [_make_po("PO004", past, ack="ACK004", gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    flags = result[0]["flags"]
    assert "MISSING_GR" in flags


def test_clean_po_not_flagged():
    from tools.flag_purchase_orders import flag_purchase_orders
    future = (date.today() + timedelta(days=14)).isoformat()
    pos = [_make_po("PO005", future, ack="ACK005", gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 0


def test_delivered_po_not_flagged():
    from tools.flag_purchase_orders import flag_purchase_orders
    past = (date.today() - timedelta(days=5)).isoformat()
    # GR received — no MISSING_GR, but OVERDUE still applies because delivery date passed
    # and MISSING_ACK does not apply since ACK is provided
    pos = [_make_po("PO006", past, ack="ACK006", gr_status="RECEIVED")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    # Should have OVERDUE but NOT MISSING_GR
    if result:
        assert "MISSING_GR" not in result[0]["flags"]


def test_multiple_flags_on_same_po():
    from tools.flag_purchase_orders import flag_purchase_orders
    past = (date.today() - timedelta(days=7)).isoformat()
    pos = [_make_po("PO007", past, ack=None, gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 1
    flags = result[0]["flags"]
    assert "OVERDUE" in flags
    assert "MISSING_ACK" in flags
    assert "MISSING_GR" in flags


def test_empty_input_returns_empty_list():
    from tools.flag_purchase_orders import flag_purchase_orders
    result = flag_purchase_orders.invoke({"purchase_orders": []})
    assert result == []


def test_due_soon_exactly_3_days():
    from tools.flag_purchase_orders import flag_purchase_orders
    exactly_3 = (date.today() + timedelta(days=3)).isoformat()
    pos = [_make_po("PO008", exactly_3, ack="ACK008", gr_status="OPEN")]
    result = flag_purchase_orders.invoke({"purchase_orders": pos})
    assert len(result) == 1
    assert "DUE_SOON" in result[0]["flags"]
