"""
Tool: draft_supplier_email
Prepares structured context for drafting a follow-up email for a flagged purchase order.
The LLM uses this context to compose the actual email text.
Milestone M4 is instrumented here.
"""
import logging
from opentelemetry import trace
from langchain_core.tools import tool

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@tool
def draft_supplier_email(
    purchase_order_number: str,
    purchase_order_item: str,
    supplier_name: str,
    short_text: str,
    net_amount: float,
    currency: str,
    schedule_delivery_date: str,
    days_overdue: int,
    flags: list,
) -> dict:
    """Prepare the context needed to draft a follow-up email for a flagged purchase order.
    Returns structured PO data and a drafting instruction for the agent to use when composing
    the email. The agent must then write a short, polite DRAFT email using this context.
    Always mark the output as DRAFT for buyer review — never send it."""
    with tracer.start_as_current_span("M4_draft_supplier_email"):
        try:
            flag_descriptions = {
                "OVERDUE": f"delivery was due on {schedule_delivery_date} and is now {days_overdue} day(s) overdue",
                "DUE_SOON": f"delivery is due on {schedule_delivery_date} (within the next 3 days)",
                "MISSING_ACK": "no order acknowledgement has been received from the supplier",
                "MISSING_GR": f"no goods receipt has been posted despite the delivery date of {schedule_delivery_date} having passed",
            }

            flag_list = flags if isinstance(flags, list) else list(flags)
            issues = [flag_descriptions.get(f, f) for f in flag_list]
            issues_text = "; ".join(issues) if issues else "requires follow-up"

            draft_instruction = (
                f"Draft a short, polite email to {supplier_name} regarding "
                f"Purchase Order {purchase_order_number}, item {purchase_order_item} "
                f"({short_text}, {net_amount} {currency}). "
                f"The issue(s): {issues_text}. "
                "Request a status update and estimated resolution date. "
                "Tone: professional and collaborative, not threatening. "
                "Keep the email under 150 words. "
                "Start with 'DRAFT — FOR BUYER REVIEW' on the first line."
            )

            result = {
                "po_number": purchase_order_number,
                "item": purchase_order_item,
                "supplier": supplier_name,
                "description": short_text,
                "amount": net_amount,
                "currency": currency,
                "delivery_date": schedule_delivery_date,
                "days_overdue": days_overdue,
                "flags": flag_list,
                "draft_instruction": draft_instruction,
            }

            logger.info(
                "M4.achieved: Draft email generated for PO %s — reason: %s",
                purchase_order_number,
                ", ".join(flag_list),
            )
            return result
        except Exception as e:
            logger.error(
                "M4.missed: Email draft could not be generated for PO %s — %s",
                purchase_order_number,
                str(e),
            )
            raise
