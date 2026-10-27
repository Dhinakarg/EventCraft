"""Pure deterministic vendor breakdown and interview questions engine."""

from typing import List
from app.schemas import BudgetBreakdown, EventType, VendorCategory


def _wedding_venue_catering() -> List[dict]:
    """Return wedding templates for venue and catering."""
    return [
        {
            "category": "Venue & Facility",
            "pct": 0.40,
            "weeks": 40,
            "deliverables": ["Full day exclusive access", "Tables & chairs", "Onsite manager", "Bridal suite"],
            "questions": [
                "What is the noise curfew and cleanup deadline?",
                "Are we required to use preferred vendors?",
                "What is the bad weather backup space?",
            ],
        },
        {
            "category": "Catering & Bar",
            "pct": 0.25,
            "weeks": 24,
            "deliverables": ["Passed appetizers", "Entree courses", "Bar staff & glassware", "Tasting session"],
            "questions": [
                "How do you handle dietary restrictions and allergies?",
                "Is table service and cake cutting included?",
                "What is your server-to-guest ratio?",
            ],
        },
    ]


def _wedding_media_music() -> List[dict]:
    """Return wedding templates for photography and music."""
    return [
        {
            "category": "Photography & Video",
            "pct": 0.12,
            "weeks": 30,
            "deliverables": ["8-hour coverage", "2 shooters", "Edited digital gallery", "Highlight reel"],
            "questions": [
                "When will the full gallery and sneak peeks be delivered?",
                "Have you shot at our chosen venue before?",
                "Do we receive full personal printing rights?",
            ],
        },
        {
            "category": "Music & Entertainment",
            "pct": 0.07,
            "weeks": 20,
            "deliverables": ["Ceremony mic setup", "Cocktail hour sound", "Reception emcee & DJ"],
            "questions": [
                "Do you take do-not-play lists from the couple?",
                "What backup audio gear do you bring?",
                "Will the same person who signs the contract be our emcee?",
            ],
        },
    ]


def _get_wedding_vendor_templates() -> List[dict]:
    """Return raw vendor templates for wedding planning."""
    return _wedding_venue_catering() + _wedding_media_music()


def _get_birthday_vendor_templates() -> List[dict]:
    """Return raw vendor templates for birthday celebrations."""
    return [
        {
            "category": "Venue / Lounge",
            "pct": 0.30,
            "weeks": 8,
            "deliverables": ["Private space rental", "AV screen for slideshow", "Setup & teardown buffer"],
            "questions": [
                "Can we bring outside cake or snacks?",
                "Are wall decorations and balloon anchors permitted?",
                "Is parking included for guests?",
            ],
        },
        {
            "category": "Catering & Custom Cake",
            "pct": 0.35,
            "weeks": 4,
            "deliverables": ["Appetizer or buffet spread", "Custom themed birthday cake", "Beverage bar"],
            "questions": [
                "What custom cake flavor and fondant designs can you make?",
                "Do you provide biodegradable disposable plates and utensils?",
                "Can you deliver and assemble the cake onsite?",
            ],
        },
        {
            "category": "Entertainment & DJ",
            "pct": 0.15,
            "weeks": 6,
            "deliverables": ["Music playlist curation", "Lighting package", "Party games moderation"],
            "questions": [
                "What age group do you specialize in entertaining?",
                "Can guests make song requests during the party?",
                "Do you supply wireless microphones for speeches?",
            ],
        },
    ]


def _get_community_vendor_templates() -> List[dict]:
    """Return raw vendor templates for community gatherings."""
    return [
        {
            "category": "Staging, PA & AV Equipment",
            "pct": 0.25,
            "weeks": 12,
            "deliverables": ["Outdoor sound system", "Staging platform", "Microphones", "Technician on duty"],
            "questions": [
                "Is the gear rated for outdoor wind/rain protection?",
                "Do you supply generators or require grid power hookup?",
                "Will a sound technician remain onsite during the event?",
            ],
        },
        {
            "category": "Sanitation & Waste Management",
            "pct": 0.10,
            "weeks": 8,
            "deliverables": ["Portable restrooms", "Handwash stations", "Recycling & trash dumpsters"],
            "questions": [
                "How often are units serviced during a multi-hour festival?",
                "Do you include ADA-compliant accessible restrooms?",
                "What is the schedule for post-event collection?",
            ],
        },
        {
            "category": "Community Food Vendors / Trucks",
            "pct": 0.25,
            "weeks": 6,
            "deliverables": ["Diverse food offerings", "Quick service turnaround", "Health permits"],
            "questions": [
                "Do all participating trucks have active health inspection certificates?",
                "What electrical and water hookups do the trucks need?",
                "Is there a flat fee or revenue share arrangement?",
            ],
        },
    ]


def get_vendor_templates(event_type: EventType) -> List[dict]:
    """Dispatch vendor templates by event type."""
    if event_type == EventType.WEDDING:
        return _get_wedding_vendor_templates()
    if event_type == EventType.BIRTHDAY:
        return _get_birthday_vendor_templates()
    return _get_community_vendor_templates()


def build_vendor_recommendations(
    event_type: EventType, budget: BudgetBreakdown
) -> List[VendorCategory]:
    """Produce deterministic vendor categories, lead times, and checklists."""
    templates = get_vendor_templates(event_type)
    total_spendable = budget.total_budget - budget.contingency_fund

    results: List[VendorCategory] = []
    for item in templates:
        target_cost = round(total_spendable * item["pct"], 2)
        low_cost = round(target_cost * 0.85, 2)
        high_cost = round(target_cost * 1.15, 2)
        range_str = f"${low_cost:,.2f} - ${high_cost:,.2f}"

        results.append(
            VendorCategory(
                category=item["category"],
                allocated_budget=target_cost,
                estimated_cost_range=range_str,
                questions_to_ask=item["questions"],
                booking_lead_time_weeks=item["weeks"],
                key_deliverables=item["deliverables"],
            )
        )
    return results
