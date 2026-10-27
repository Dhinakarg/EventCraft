"""Pure deterministic vendor checklist and booking deadline engine."""

from datetime import date, timedelta

from app.engine.profiles import DEFAULT_VENDOR_BUDGET_RATIO
from app.models import BudgetResponse, EventRequest, EventType, VendorChecklistItem


def _wedding_vendor_specs() -> list[tuple[str, int, list[str]]]:
    """Return wedding vendor lead times and essential interview questions."""
    return [
        (
            "Venue & Facility",
            210,
            [
                "What is the noise curfew and teardown deadline?",
                "Are we required to use exclusive in-house caterers?",
                "What bad-weather indoor backup room is guaranteed?",
            ],
        ),
        (
            "Catering & Bar",
            150,
            [
                "What is your server-to-guest staffing ratio?",
                "How do you accommodate dietary and allergy restrictions?",
                "Are menu tastings, table linens, and tableware included?",
            ],
        ),
        (
            "Photography & Video",
            120,
            [
                "How many hours of coverage and shooters are included?",
                "When will preview sneak-peeks and full high-res files be ready?",
                "Do you provide a full release for personal printing rights?",
            ],
        ),
        (
            "Entertainment & Music",
            90,
            [
                "Do you provide wireless microphones for speeches?",
                "Can we submit must-play and do-not-play track lists?",
                "What backup audio gear do you carry onsite?",
            ],
        ),
    ]


def _birthday_vendor_specs() -> list[tuple[str, int, list[str]]]:
    """Return birthday vendor lead times and questions."""
    return [
        (
            "Venue & Space",
            45,
            [
                "Can we bring outside cake, snacks, or special beverages?",
                "Are adhesive wall decorations and balloon anchors permitted?",
                "Is AV equipment available for photo slideshows?",
            ],
        ),
        (
            "Food & Beverages",
            30,
            [
                "Can you craft a custom-themed birthday cake design?",
                "Do you supply compostable tableware and napkins?",
                "What is the deadline for final guest count adjustments?",
            ],
        ),
        (
            "Entertainment & DJ",
            21,
            [
                "What age group and musical genres do you specialize in?",
                "Can you run interactive party games and announcements?",
                "Do you provide ambient party lighting packages?",
            ],
        ),
    ]


def _community_vendor_specs() -> list[tuple[str, int, list[str]]]:
    """Return community event vendor lead times and questions."""
    return [
        (
            "Permits & Staging",
            60,
            [
                "Is the staging platform certified for weather and load safety?",
                "Do you provide covered tent canopy structures?",
                "What is the delivery, installation, and inspection schedule?",
            ],
        ),
        (
            "Sound & Production",
            45,
            [
                "Is audio equipment wind-resistant for outdoor broadcast?",
                "Do you supply generator power or need dedicated line hookups?",
                "Will a licensed sound engineer remain stationed during the event?",
            ],
        ),
        (
            "Refreshments & Food",
            30,
            [
                "Do all participating food vendors hold active health permits?",
                "Are safe handwashing and cold storage stations required?",
                "Can you supply eco-friendly bulk water refill stations?",
            ],
        ),
    ]


def _get_vendor_specs(event_type: EventType) -> list[tuple[str, int, list[str]]]:
    """Dispatch vendor templates by event category."""
    if event_type == EventType.WEDDING:
        return _wedding_vendor_specs()
    if event_type == EventType.BIRTHDAY:
        return _birthday_vendor_specs()
    return _community_vendor_specs()


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

    checklist: list[VendorChecklistItem] = []
    for cat_name, lead_days, questions in specs:
        deadline = req.event_date - timedelta(days=lead_days)
        actual_deadline = max(today, deadline)

        matched_cap = 0.0
        for b_name, b_amt in cat_budgets.items():
            if any(k in b_name for k in cat_name.lower().split()):
                matched_cap = b_amt
                break
        if matched_cap == 0.0:
            matched_cap = round(req.total_budget * DEFAULT_VENDOR_BUDGET_RATIO, 2)

        checklist.append(
            VendorChecklistItem(
                category=cat_name,
                budget_cap=matched_cap,
                booking_deadline=actual_deadline,
                lead_time_days=lead_days,
                questions_to_ask=questions,
                status="todo",
            )
        )
    return checklist
