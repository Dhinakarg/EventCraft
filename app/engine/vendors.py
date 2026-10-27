"""Pure deterministic vendor checklist and booking deadline engine."""

from datetime import date, timedelta

from app.constants import DEFAULT_VENDOR_BUDGET_RATIO
from app.engine.data.vendor_specs import VENDOR_SPECS_BY_EVENT_TYPE, VendorSpec
from app.models import BudgetResponse, EventRequest, EventType, VendorChecklistItem


def _get_vendor_specs(event_type: EventType) -> list[VendorSpec]:
    """Dispatch vendor templates by event category."""
    specs = VENDOR_SPECS_BY_EVENT_TYPE.get(event_type, VENDOR_SPECS_BY_EVENT_TYPE[EventType.WEDDING])
    return list(specs)


def _match_vendor_cap(
    cat_name: str,
    cat_budgets: dict[str, float],
    total_budget: float,
) -> float:
    """Find matching allocated budget for vendor category or apply fallback ratio."""
    for b_name, b_amt in cat_budgets.items():
        if any(k in b_name for k in cat_name.lower().split()):
            return b_amt
    return round(total_budget * DEFAULT_VENDOR_BUDGET_RATIO, 2)


def _build_single_vendor_item(
    spec: VendorSpec,
    req: EventRequest,
    cat_budgets: dict[str, float],
    today: date,
) -> VendorChecklistItem:
    """Construct a single vendor checklist item with deadline and matched cap."""
    deadline = req.event_date - timedelta(days=spec.lead_time_days)
    actual_deadline = max(today, deadline)
    matched_cap = _match_vendor_cap(spec.category, cat_budgets, req.total_budget)
    return VendorChecklistItem(
        category=spec.category,
        budget_cap=matched_cap,
        booking_deadline=actual_deadline,
        lead_time_days=spec.lead_time_days,
        questions_to_ask=spec.interview_prompts,
        status="todo",
    )


def build_vendor_checklist(req: EventRequest, budget: BudgetResponse) -> list[VendorChecklistItem]:
    """Build vendor checklist with budget caps, booking deadlines, and questions.

    Args:
        req: Validated event request containing total budget and event date.
        budget: Calculated budget response containing itemized allocations.

    Returns:
        List of VendorChecklistItem with matched budget caps and interview prompts.
    """
    today = date.today()
    specs = _get_vendor_specs(req.event_type)
    cat_budgets: dict[str, float] = {item.category.lower(): item.allocated_amount for item in budget.items}
    return [_build_single_vendor_item(spec, req, cat_budgets, today) for spec in specs]
