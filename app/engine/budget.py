"""Pure deterministic budget allocation and feasibility engine."""


from app.engine.profiles import (
    get_budget_profile,
    get_min_per_guest_threshold,
)
from app.models import BudgetItem, BudgetResponse, EventRequest, EventType


def _calculate_shifted_weights(
    profile: list[tuple[str, float, str, str]],
    priorities: list[str],
    contingency_rate: float,
) -> dict[str, float]:
    """Shift category weights based on user priorities and renormalize to 100%."""
    non_contingency = [item for item in profile if item[2] != "contingency"]
    target_non_contingency_sum = 100.0 - contingency_rate

    raw_weights: dict[str, float] = {}
    for cat, base_pct, p_key, _ in non_contingency:
        multiplier = 1.35 if p_key in priorities else 1.0
        raw_weights[cat] = base_pct * multiplier

    raw_sum = sum(raw_weights.values())
    normalized: dict[str, float] = {}
    for cat, val in raw_weights.items():
        normalized[cat] = (val / raw_sum) * target_non_contingency_sum

    for item in profile:
        if item[2] == "contingency":
            normalized[item[0]] = contingency_rate
    return normalized


def _balance_penny_discrepancy(
    amounts: list[float], total_budget: float
) -> list[float]:
    """Adjust largest item by penny difference so sum equals total_budget exactly."""
    current_sum = round(sum(amounts), 2)
    diff = round(total_budget - current_sum, 2)
    if diff != 0.0 and amounts:
        max_idx = amounts.index(max(amounts))
        amounts[max_idx] = round(amounts[max_idx] + diff, 2)
    return amounts


def _check_feasibility(
    event_type: EventType, total_budget: float, guest_count: int
) -> tuple[bool, list[str]]:
    """Determine financial feasibility and offer concrete suggestions if underfunded."""
    per_guest = round(total_budget / max(guest_count, 1), 2)
    min_thresh = get_min_per_guest_threshold(event_type)
    if per_guest >= min_thresh:
        return True, ["Budget is healthy and realistic for the projected guest count."]

    suggestions = [
        f"Budget alert: Per-guest cost (${per_guest:,.2f}) is below the recommended minimum (${min_thresh:,.2f}).",
        "Suggestion: Reduce guest count to comfortably preserve dining and venue standards.",
        "Suggestion: Shorten event duration or select off-peak weekday/Sunday time slots.",
        "Suggestion: Adopt DIY floral and table decor to maximize hospitality and catering funds.",
    ]
    return False, suggestions


def allocate_event_budget(req: EventRequest, contingency_rate: float = 8.0) -> BudgetResponse:
    """Allocate budget deterministically with priority weighting and exact balancing."""
    contingency_rate = max(5.0, min(10.0, contingency_rate))
    profile = get_budget_profile(req.event_type)
    weights = _calculate_shifted_weights(profile, req.priorities, contingency_rate)

    raw_amounts = [round(req.total_budget * (weights[item[0]] / 100.0), 2) for item in profile]
    balanced_amounts = _balance_penny_discrepancy(raw_amounts, req.total_budget)

    items: list[BudgetItem] = []
    contingency_fund = 0.0
    for idx, (cat, _, p_key, desc) in enumerate(profile):
        amt = balanced_amounts[idx]
        pct = round((amt / req.total_budget) * 100.0, 2)
        if p_key == "contingency":
            contingency_fund = amt
        priority_label = "High" if p_key in req.priorities else "Medium"
        tip = f"Target ~{req.currency} {amt:,.2f} ({pct}%)."
        items.append(BudgetItem(
            category=cat, percentage=pct, allocated_amount=amt,
            description=desc, priority=priority_label, tips=tip
        ))

    is_feasible, notes = _check_feasibility(req.event_type, req.total_budget, req.guest_count)
    return BudgetResponse(
        total_budget=round(req.total_budget, 2),
        per_guest_cost=round(req.total_budget / req.guest_count, 2),
        currency=req.currency,
        contingency_fund=contingency_fund,
        contingency_percentage=contingency_rate,
        is_feasible=is_feasible,
        feasibility_notes=notes,
        items=items,
    )
