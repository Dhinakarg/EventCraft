"""Pure deterministic budget allocation and feasibility engine."""

from typing import NamedTuple

from app.constants import (
    DEFAULT_CONTINGENCY_RATE,
    MAX_CONTINGENCY_RATE,
    MIN_CONTINGENCY_RATE,
    PRIORITY_BOOST_MULTIPLIER,
)
from app.engine.profiles import (
    ProfileCategory,
    get_budget_profile,
    get_min_per_guest_threshold,
)
from app.models import BudgetItem, BudgetResponse, EventRequest, EventType


class FeasibilityResult(NamedTuple):
    """Feasibility outcome and recommendation notes."""

    is_feasible: bool
    notes: list[str]


class BudgetBuildResult(NamedTuple):
    """Constructed budget items and extracted contingency fund."""

    items: list[BudgetItem]
    contingency_fund: float


def _calculate_shifted_weights(
    profile: list[ProfileCategory],
    priorities: list[str],
    contingency_rate: float,
) -> dict[str, float]:
    """Shift category weights based on user priorities and renormalize to 100%."""
    non_contingency = [item for item in profile if item.priority_key != "contingency"]
    target_non_contingency_sum = 100.0 - contingency_rate

    raw_weights: dict[str, float] = {}
    for item in non_contingency:
        multiplier = PRIORITY_BOOST_MULTIPLIER if item.priority_key in priorities else 1.0
        raw_weights[item.category] = item.standard_percentage * multiplier

    raw_sum = sum(raw_weights.values())
    normalized: dict[str, float] = {}
    for cat, val in raw_weights.items():
        normalized[cat] = (val / raw_sum) * target_non_contingency_sum

    for item in profile:
        if item.priority_key == "contingency":
            normalized[item.category] = contingency_rate
    return normalized


def _balance_penny_discrepancy(amounts: list[float], total_budget: float) -> list[float]:
    """Adjust largest item by penny difference so sum equals total_budget exactly."""
    current_sum = round(sum(amounts), 2)
    diff = round(total_budget - current_sum, 2)
    if diff != 0.0 and amounts:
        max_idx = amounts.index(max(amounts))
        amounts[max_idx] = round(amounts[max_idx] + diff, 2)
    return amounts


def _check_feasibility(
    event_type: EventType, total_budget: float, guest_count: int, currency: str = "INR"
) -> FeasibilityResult:
    """Determine financial feasibility and offer concrete suggestions if underfunded."""
    per_guest = round(total_budget / max(guest_count, 1), 2)
    min_thresh = get_min_per_guest_threshold(event_type)
    if per_guest >= min_thresh:
        return FeasibilityResult(True, ["Budget is healthy and realistic for the projected guest count."])

    alert_msg = (
        f"Budget alert: Per-guest cost ({currency} {per_guest:,.2f}) is below "
        f"the recommended minimum ({currency} {min_thresh:,.2f})."
    )
    suggestions = [
        alert_msg,
        "Suggestion: Reduce guest count to comfortably preserve dining and venue standards.",
        "Suggestion: Shorten event duration or select off-peak weekday/Sunday time slots.",
        "Suggestion: Adopt DIY floral and table decor to maximize hospitality and catering funds.",
    ]
    return FeasibilityResult(False, suggestions)


def _build_budget_items(
    profile: list[ProfileCategory],
    balanced_amounts: list[float],
    req: EventRequest,
) -> BudgetBuildResult:
    """Construct BudgetItem list and extract contingency fund amount."""
    items: list[BudgetItem] = []
    contingency_fund = 0.0
    for idx, item in enumerate(profile):
        amt = balanced_amounts[idx]
        pct = round((amt / req.total_budget) * 100.0, 2)
        if item.priority_key == "contingency":
            contingency_fund = amt
        priority_label = "High" if item.priority_key in req.priorities else "Medium"
        tip = f"Target ~{req.currency} {amt:,.2f} ({pct}%)."
        items.append(
            BudgetItem(
                category=item.category,
                percentage=pct,
                allocated_amount=amt,
                description=item.description,
                priority=priority_label,
                tips=tip,
            )
        )
    return BudgetBuildResult(items, contingency_fund)


def allocate_event_budget(req: EventRequest, contingency_rate: float = DEFAULT_CONTINGENCY_RATE) -> BudgetResponse:
    """Allocate budget deterministically with priority weighting and exact balancing.

    Args:
        req: Validated event request containing total budget, guest count, and priorities.
        contingency_rate: Percentage of total budget reserved for emergency buffer.

    Returns:
        BudgetResponse with balanced line items, per-guest spending, and feasibility notes.
    """
    contingency_rate = max(MIN_CONTINGENCY_RATE, min(MAX_CONTINGENCY_RATE, contingency_rate))
    profile = get_budget_profile(req.event_type)
    weights = _calculate_shifted_weights(profile, req.priorities, contingency_rate)

    raw_amounts = [round(req.total_budget * (weights[item.category] / 100.0), 2) for item in profile]
    balanced_amounts = _balance_penny_discrepancy(raw_amounts, req.total_budget)

    build_res = _build_budget_items(profile, balanced_amounts, req)
    feasibility = _check_feasibility(req.event_type, req.total_budget, req.guest_count, req.currency)

    return BudgetResponse(
        total_budget=round(req.total_budget, 2),
        per_guest_cost=round(req.total_budget / req.guest_count, 2),
        currency=req.currency,
        contingency_fund=build_res.contingency_fund,
        contingency_percentage=contingency_rate,
        is_feasible=feasibility.is_feasible,
        feasibility_notes=feasibility.notes,
        items=build_res.items,
    )
