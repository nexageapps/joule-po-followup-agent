"""
Tool: rank_purchase_orders
Sorts flagged purchase orders by urgency (days overdue) and monetary value.
Milestone M3 is instrumented here.
"""
import logging
from datetime import date
from opentelemetry import trace
from langchain_core.tools import tool

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def _days_overdue(item: dict, today: date) -> int:
    raw = item.get("ScheduleDeliveryDate") or ""
    try:
        delivery_date = date.fromisoformat(raw[:10]) if raw else None
    except ValueError:
        delivery_date = None
    if delivery_date and delivery_date < today:
        return (today - delivery_date).days
    return 0


@tool
def rank_purchase_orders(flagged_purchase_orders: list[dict]) -> list[dict]:
    """Sort flagged purchase orders by urgency (days overdue, descending) and monetary value
    (net amount, descending). Returns the ranked list with 'rank' and 'days_overdue' fields added.
    Use this after flag_purchase_orders to present results to the buyer in priority order."""
    with tracer.start_as_current_span("M3_rank_purchase_orders"):
        try:
            today = date.today()

            enriched = []
            for item in flagged_purchase_orders:
                enriched.append({
                    **item,
                    "days_overdue": _days_overdue(item, today),
                })

            ranked = sorted(
                enriched,
                key=lambda x: (-(x["days_overdue"]), -(x.get("NetAmount") or 0)),
            )

            for idx, item in enumerate(ranked, start=1):
                item["rank"] = idx

            logger.info(
                "M3.achieved: Ranked results ready — %d flagged POs presented to buyer",
                len(ranked),
            )
            return ranked
        except Exception as e:
            logger.error("M3.missed: Ranking did not complete — %s", str(e))
            raise
