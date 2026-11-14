"""
Tool: get_open_purchase_orders
Retrieves all open purchase orders from the mock data source.
Milestone M1 is instrumented here.
"""
import logging
from opentelemetry import trace
from langchain_core.tools import tool

from mock_po_data import get_open_purchase_orders as _fetch

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@tool
def get_open_purchase_orders() -> list[dict]:
    """Retrieve all open purchase orders from the data source.
    Returns a list of PO records including header and line item details.
    Use this as the first step before flagging or ranking purchase orders."""
    with tracer.start_as_current_span("M1_po_data_load"):
        try:
            records = _fetch()
            count = len(records)
            logger.info("M1.achieved: PO data loaded successfully — %d records available", count)
            return records
        except Exception as e:
            logger.error("M1.missed: PO data could not be loaded — %s", str(e))
            raise
