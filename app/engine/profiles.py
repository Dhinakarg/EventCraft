"""Event profiles defining standard budget weights, vendor categories, and lead times."""


from app.models import EventType

# Standard budget allocation profiles (sum to 100%)
# (Category, standard_percentage, priority_key, description)
WEDDING_PROFILE: list[tuple[str, float, str, str]] = [
    ("Venue & Facility", 30.0, "venue", "Primary venue space, rentals, and setup"),
    ("Catering & Bar", 30.0, "food", "Full dinner, appetizers, beverages, and service staff"),
    ("Decor & Florals", 10.0, "decor", "Centerpieces, bouquet, ceremony arch, and styling"),
    ("Photography & Video", 8.0, "photography", "Full day ceremony & reception photo/video coverage"),
    ("Attire & Beauty", 8.0, "other", "Wardrobe, accessories, hair, and makeup"),
    ("Entertainment & Music", 6.0, "entertainment", "DJ, live band, sound equipment, and emcee"),
    ("Contingency & Misc", 8.0, "contingency", "Reserved emergency buffer and miscellaneous fees"),
]

BIRTHDAY_PROFILE: list[tuple[str, float, str, str]] = [
    ("Venue & Space", 28.0, "venue", "Private room, lounge, or party venue rental"),
    ("Food & Beverages", 32.0, "food", "Buffet or plated dining, specialty cake, and drinks"),
    ("Theme Decor & Balloons", 12.0, "decor", "Custom backdrops, balloon installations, tableware"),
    ("Entertainment & DJ", 12.0, "entertainment", "Music, host, performer, games, or photobooth"),
    ("Photography", 8.0, "photography", "Event candids, portraits, and digital album"),
    ("Contingency & Favors", 8.0, "contingency", "Reserve contingency buffer and party favors"),
]

COMMUNITY_PROFILE: list[tuple[str, float, str, str]] = [
    ("Permits & Staging", 26.0, "venue", "Municipal permits, park fees, stages, and tents"),
    ("Refreshments & Food", 28.0, "food", "Water stations, community snacks, meal boxes"),
    ("Sound & Production", 16.0, "entertainment", "PA systems, microphones, generators, and audio lead"),
    ("Signage & Decor", 12.0, "decor", "Directional banners, accessible ramps, and flags"),
    ("Activities & Supplies", 10.0, "other", "Workshops, volunteer kits, badges, and games"),
    ("Contingency & Safety", 8.0, "contingency", "First-aid, emergency sanitation, and reserve fund"),
]

# Standard lead-time requirements in days
STANDARD_LEAD_TIMES: dict[EventType, int] = {
    EventType.WEDDING: 270,
    EventType.BIRTHDAY: 60,
    EventType.COMMUNITY: 90,
}

# Minimum feasible cost per guest thresholds
MIN_PER_GUEST_COST: dict[EventType, float] = {
    EventType.WEDDING: 90.0,
    EventType.BIRTHDAY: 30.0,
    EventType.COMMUNITY: 15.0,
}


def get_budget_profile(event_type: EventType) -> list[tuple[str, float, str, str]]:
    """Return standard budget percentage tuples for the event type."""
    if event_type == EventType.WEDDING:
        return WEDDING_PROFILE
    if event_type == EventType.BIRTHDAY:
        return BIRTHDAY_PROFILE
    return COMMUNITY_PROFILE


def get_standard_lead_time(event_type: EventType) -> int:
    """Return standard advance planning days needed for event type."""
    return STANDARD_LEAD_TIMES.get(event_type, 90)


def get_min_per_guest_threshold(event_type: EventType) -> float:
    """Return minimum realistic spending per guest for feasibility checking."""
    return MIN_PER_GUEST_COST.get(event_type, 20.0)
