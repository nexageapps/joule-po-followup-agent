"""
Mock purchase order data shaped like the SAP S/4HANA API_PURCHASEORDER_PROCESS_SRV OData schema.
Dates are computed dynamically relative to today so the data never becomes stale.
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

TODAY = date.today


def _iso(d: date) -> str:
    return d.isoformat()


def get_open_purchase_orders() -> list[dict]:
    """Return a list of open purchase order records shaped like API_PURCHASEORDER_PROCESS_SRV."""
    today = TODAY()

    pos = [
        # --- Scenario 1: OVERDUE + MISSING_GR (delivery passed, no GR) ---
        {
            "PurchaseOrder": "4500001001",
            "Supplier": "SUPP_ACME",
            "SupplierName": "Acme Industrial Supplies GmbH",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=30)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-10021",
                    "ShortText": "Industrial Steel Bolts M12 (Box of 500)",
                    "OrderQuantity": 10.0,
                    "NetPriceAmount": 450.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 4500.0,
                    "ScheduleDeliveryDate": _iso(today - timedelta(days=8)),
                    "ConfirmationDeliveryDate": _iso(today - timedelta(days=10)),
                    "OrderAcknowledgmentNumber": "ACK-20241001",
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 10.0,
                }
            ],
        },
        # --- Scenario 2: OVERDUE + MISSING_ACK + MISSING_GR ---
        {
            "PurchaseOrder": "4500001002",
            "Supplier": "SUPP_VERTEX",
            "SupplierName": "Vertex Electronics Ltd",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=45)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-30044",
                    "ShortText": "Industrial Microcontroller Board Rev 3",
                    "OrderQuantity": 50.0,
                    "NetPriceAmount": 320.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 16000.0,
                    "ScheduleDeliveryDate": _iso(today - timedelta(days=5)),
                    "ConfirmationDeliveryDate": None,
                    "OrderAcknowledgmentNumber": None,
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 50.0,
                }
            ],
        },
        # --- Scenario 3: DUE_SOON (delivery in 2 days) + MISSING_ACK ---
        {
            "PurchaseOrder": "4500001003",
            "Supplier": "SUPP_NORDIC",
            "SupplierName": "Nordic Packaging Solutions AB",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=20)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-20010",
                    "ShortText": "Cardboard Shipping Boxes 60x40x30 cm (Pallet)",
                    "OrderQuantity": 5.0,
                    "NetPriceAmount": 1200.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 6000.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=2)),
                    "ConfirmationDeliveryDate": None,
                    "OrderAcknowledgmentNumber": None,
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 5.0,
                }
            ],
        },
        # --- Scenario 4: DUE_SOON (delivery tomorrow) ---
        {
            "PurchaseOrder": "4500001004",
            "Supplier": "SUPP_CHEM",
            "SupplierName": "ChemFlow Industries SA",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=15)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-50002",
                    "ShortText": "Industrial Solvent IPA 99% (200L drum)",
                    "OrderQuantity": 3.0,
                    "NetPriceAmount": 2800.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 8400.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=1)),
                    "ConfirmationDeliveryDate": _iso(today + timedelta(days=1)),
                    "OrderAcknowledgmentNumber": "ACK-20241105",
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 3.0,
                }
            ],
        },
        # --- Scenario 5: MISSING_ACK only (delivery in 10 days) ---
        {
            "PurchaseOrder": "4500001005",
            "Supplier": "SUPP_PRECISION",
            "SupplierName": "Precision Parts Manufacturing Co.",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=10)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-11033",
                    "ShortText": "CNC Machined Aluminium Bracket Type-A",
                    "OrderQuantity": 100.0,
                    "NetPriceAmount": 85.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 8500.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=10)),
                    "ConfirmationDeliveryDate": None,
                    "OrderAcknowledgmentNumber": None,
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 100.0,
                }
            ],
        },
        # --- Scenario 6: OVERDUE + MISSING_GR (high value) ---
        {
            "PurchaseOrder": "4500001006",
            "Supplier": "SUPP_VERTEX",
            "SupplierName": "Vertex Electronics Ltd",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=60)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-30099",
                    "ShortText": "High-Performance Server GPU Module",
                    "OrderQuantity": 4.0,
                    "NetPriceAmount": 9500.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 38000.0,
                    "ScheduleDeliveryDate": _iso(today - timedelta(days=12)),
                    "ConfirmationDeliveryDate": _iso(today - timedelta(days=14)),
                    "OrderAcknowledgmentNumber": "ACK-20240920",
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 4.0,
                }
            ],
        },
        # --- Scenario 7: DUE_SOON (today + 3 days exactly) + MISSING_ACK ---
        {
            "PurchaseOrder": "4500001007",
            "Supplier": "SUPP_LOGIX",
            "SupplierName": "Logix Freight & Logistics GmbH",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=25)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-70001",
                    "ShortText": "Pallet Wrapping Film 500mm x 300m",
                    "OrderQuantity": 20.0,
                    "NetPriceAmount": 95.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 1900.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=3)),
                    "ConfirmationDeliveryDate": None,
                    "OrderAcknowledgmentNumber": None,
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 20.0,
                }
            ],
        },
        # --- Scenario 8: Clean PO — on time, ACK received, no GR yet (not overdue) ---
        {
            "PurchaseOrder": "4500001008",
            "Supplier": "SUPP_ACME",
            "SupplierName": "Acme Industrial Supplies GmbH",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=5)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-10050",
                    "ShortText": "Safety Gloves EN388 (Box of 10 pairs)",
                    "OrderQuantity": 50.0,
                    "NetPriceAmount": 25.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 1250.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=14)),
                    "ConfirmationDeliveryDate": _iso(today + timedelta(days=14)),
                    "OrderAcknowledgmentNumber": "ACK-20241110",
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 50.0,
                }
            ],
        },
        # --- Scenario 9: Clean PO — delivered and GR posted ---
        {
            "PurchaseOrder": "4500001009",
            "Supplier": "SUPP_NORDIC",
            "SupplierName": "Nordic Packaging Solutions AB",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=40)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-20020",
                    "ShortText": "Stretch Film Rolls (Box of 6)",
                    "OrderQuantity": 30.0,
                    "NetPriceAmount": 48.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 1440.0,
                    "ScheduleDeliveryDate": _iso(today - timedelta(days=10)),
                    "ConfirmationDeliveryDate": _iso(today - timedelta(days=10)),
                    "OrderAcknowledgmentNumber": "ACK-20241001",
                    "GoodsReceiptStatus": "RECEIVED",
                    "PurchaseOrderQuantity": 30.0,
                }
            ],
        },
        # --- Scenario 10: Clean PO — future delivery, ACK present ---
        {
            "PurchaseOrder": "4500001010",
            "Supplier": "SUPP_CHEM",
            "SupplierName": "ChemFlow Industries SA",
            "PurchasingOrganization": "1010",
            "DocumentDate": _iso(today - timedelta(days=3)),
            "items": [
                {
                    "PurchaseOrderItem": "00010",
                    "Material": "MAT-50010",
                    "ShortText": "Laboratory Reagent Kit Type-B",
                    "OrderQuantity": 10.0,
                    "NetPriceAmount": 340.0,
                    "NetPriceQuantity": 1.0,
                    "Currency": "EUR",
                    "NetAmount": 3400.0,
                    "ScheduleDeliveryDate": _iso(today + timedelta(days=21)),
                    "ConfirmationDeliveryDate": _iso(today + timedelta(days=21)),
                    "OrderAcknowledgmentNumber": "ACK-20241112",
                    "GoodsReceiptStatus": "OPEN",
                    "PurchaseOrderQuantity": 10.0,
                }
            ],
        },
    ]

    logger.info("Mock PO data loaded: %d records", len(pos))
    return pos
