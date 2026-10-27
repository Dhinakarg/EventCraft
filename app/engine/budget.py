"""Pure deterministic budget allocation engine."""

from typing import Dict, List
from app.schemas import BudgetBreakdown, BudgetItem, EventType

# Base percentage allocations by event type
_WEDDING_WEIGHTS = [
    ("Venue & Rentals", 0.40, "High", "Primary venue space, tables, chairs, lighting"),
    ("Catering & Bar", 0.25, "High", "Full dinner, cocktail hour, beverages, service staff"),
    ("Photography & Video", 0.12, "Medium", "Ceremony & reception photo/videography coverage"),
    ("Decor & Florals", 0.08, "Medium", "Centerpieces, bouquet, ceremony arch, ambient styling"),
    ("Music & Entertainment", 0.07, "Medium", "DJ or live band, sound equipment, emcee"),
    ("Attire & Beauty", 0.04, "Medium", "Hair, makeup, wardrobe accessories"),
    ("Stationery & Favors", 0.04, "Low", "Invitations, signage, personalized guest favors"),
]

_BIRTHDAY_WEIGHTS = [
    ("Venue & Space", 0.30, "High", "Party room, outdoor pavilion, or private dining lounge"),
    ("Food & Beverages", 0.35, "High", "Buffet or plated dining, specialty cake, drinks"),
    ("Entertainment & Games", 0.15, "High", "DJ, magician, photobooth, arcade or live host"),
    ("Theme Decor & Balloons", 0.10, "Medium", "Backdrops, balloon garlands, tableware"),
    ("Photography", 0.05, "Low", "Event photos and candids"),
    ("Favors & Goodie Bags", 0.05, "Low", "Party favor boxes, guest memorabilia"),
]

_COMMUNITY_WEIGHTS = [
    ("Permits & Venue", 0.25, "High", "Park permits, hall rental, sanitation facilities"),
    ("Sound & Stage Production", 0.25, "High", "PA systems, staging, microphones, generators"),
    ("Refreshments & Hydration", 0.25, "High", "Water stations, community snacks, meal boxes"),
    ("Signage & Accessibility", 0.10, "Medium", "Directional banners, ramps, safety signage"),
    ("Activities & Materials", 0.10, "Medium", "Workshop supplies, volunteer kits, games"),
    ("Emergency & Clean-up", 0.05, "Low", "First aid, trash receptacles, volunteer cleanup"),
]


def get_weights_for_event(event_type: EventType) -> List[tuple]:
    """Return category allocation tuples for the given event type."""
    if event_type == EventType.WEDDING:
        return _WEDDING_WEIGHTS
    if event_type == EventType.BIRTHDAY:
        return _BIRTHDAY_WEIGHTS
    return _COMMUNITY_WEIGHTS


def calculate_contingency(total_budget: float, rate: float = 0.05) -> float:
    """Calculate contingency buffer from total budget."""
    return round(total_budget * rate, 2)


def allocate_budget(
    total_budget: float, guest_count: int, event_type: EventType
) -> BudgetBreakdown:
    """Deterministically allocate budget across standard categories."""
    contingency = calculate_contingency(total_budget, 0.05)
    spendable = total_budget - contingency
    weights = get_weights_for_event(event_type)

    items: List[BudgetItem] = []
    for cat, pct, priority, desc in weights:
        amount = round(spendable * pct, 2)
        tip = f"Target ~${amount:,.2f} to stay on track."
        items.append(
            BudgetItem(
                category=cat,
                percentage=round(pct * 100, 1),
                allocated_amount=amount,
                description=desc,
                priority=priority,
                tips=tip,
            )
        )

    per_guest = round(total_budget / max(guest_count, 1), 2)
    return BudgetBreakdown(
        total_budget=round(total_budget, 2),
        per_guest_cost=per_guest,
        items=items,
        contingency_fund=contingency,
    )
