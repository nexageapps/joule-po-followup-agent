"""
Tool: flag_purchase_orders
Applies follow-up rules to a list of purchase orders and returns only those that require action.
Milestone M2 is instrumented here.
"""
import logging
from datetime import date
from typing import Any
from opentelemetry import trace
from langchain_core.tools import tool

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

_DUE_SOON_DAYS = 3


def _flag_item(item: dict, today: date) -> list[str]:
    """Return a list of flag codes for a single PO item."""
    flags = []
    raw_date = item.get("ScheduleDeliveryDate") or ""
    try:
        delivery_date = date.fromisoformat(raw_date[:10]) if raw_date else None
    except ValueError:
        delivery_date = None

    if delivery_date:
        if delivery_date < today:
            flags.append("OVERDUE")
            # MISSING_GR: delivery date passed and no goods receipt posted
            if item.get("GoodsReceiptStatus", "").upper() == "OPEN":
                flags.append("MISSING_GR")
        elif (delivery_date - today).days <= _DUE_SOON_DAYS:
            flags.append("DUE_SOON")

    # MISSING_ACK: no order acknowledgement number
    ack = item.get("OrderAcknowledgmentNumber")
    if not ack:
        flags.append("MISSING_ACK")

    return flags


@tool
def flag_purchase_orders(purchase_orders: list[dict]) -> list[dict]:
    """Apply follow-up rules to a list of purchase orders and return only those that require action.
    Each flagged item includes a 'flags' list explaining why it needs follow-up.
    Flags: OVERDUE (delivery date passed), DUE_SOON (due within 3 days),
    MISSING_ACK (no supplier acknowledgement), MISSING_GR (delivery passed, no goods receipt).
    POs with no flags are excluded from the result."""
    with tracer.start_as_current_span("M2_flag_purchase_orders"):
        try:
            today = date.today()
            total = 0
            flagged_items = []

            for po in purchase_orders:
                for item in po.get("items", []):
                    total += 1
                    flags = _flag_item(item, today)
                    if flags:
                        flagged_item = {**po, **item}
                        # Remove nested items list to flatten the record
                        flagged_item.pop("items", None)
                        flagged_item["flags"] = flags
                        flagged_items.append(flagged_item)

            logger.info(
                "M2.achieved: Flagging logic applied — %d POs flagged out of %d",
                len(flagged_items),
                total,
            )
            return flagged_items
        except Exception as e:
            logger.error("M2.missed: Flagging logic did not complete — %s", str(e))
            raise
