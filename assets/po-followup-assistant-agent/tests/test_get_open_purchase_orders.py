"""Unit tests for get_open_purchase_orders tool."""
import pytest


@pytest.fixture(autouse=True)
def _path(add_agent_to_path):
    pass


def test_returns_non_empty_list():
    from tools.get_open_purchase_orders import get_open_purchase_orders
    result = get_open_purchase_orders.invoke({})
    assert isinstance(result, list)
    assert len(result) > 0


def test_each_record_has_required_header_fields():
    from tools.get_open_purchase_orders import get_open_purchase_orders
    records = get_open_purchase_orders.invoke({})
    required_fields = ["PurchaseOrder", "Supplier", "SupplierName", "DocumentDate", "items"]
    for record in records:
        for field in required_fields:
            assert field in record, f"Missing field '{field}' in record {record.get('PurchaseOrder')}"


def test_each_record_has_items():
    from tools.get_open_purchase_orders import get_open_purchase_orders
    records = get_open_purchase_orders.invoke({})
    for record in records:
        assert isinstance(record["items"], list)
        assert len(record["items"]) > 0


def test_items_have_required_fields():
    from tools.get_open_purchase_orders import get_open_purchase_orders
    records = get_open_purchase_orders.invoke({})
    item_fields = [
        "PurchaseOrderItem", "ShortText", "NetAmount", "Currency",
        "ScheduleDeliveryDate", "GoodsReceiptStatus"
    ]
    for record in records:
        for item in record["items"]:
            for field in item_fields:
                assert field in item, f"Item missing field '{field}' in PO {record.get('PurchaseOrder')}"


def test_returns_at_least_10_records():
    from tools.get_open_purchase_orders import get_open_purchase_orders
    records = get_open_purchase_orders.invoke({})
    assert len(records) >= 10
