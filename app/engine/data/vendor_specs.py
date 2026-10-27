"""Typed vendor specifications and interview questions for event categories."""

from typing import NamedTuple

from app.models import EventType


class VendorSpec(NamedTuple):
    """Specification template for vendor checklist generation."""

    category: str
    lead_time_days: int
    interview_prompts: list[str]


WEDDING_VENDOR_SPECS: tuple[VendorSpec, ...] = (
    VendorSpec(
        "Venue & Facility",
        210,
        [
            "What is the noise curfew and teardown deadline?",
            "Are we required to use exclusive in-house caterers?",
            "What bad-weather indoor backup room is guaranteed?",
        ],
    ),
    VendorSpec(
        "Catering & Bar",
        150,
        [
            "What is your server-to-guest staffing ratio?",
            "How do you accommodate dietary and allergy restrictions?",
            "Are menu tastings, table linens, and tableware included?",
        ],
    ),
    VendorSpec(
        "Photography & Video",
        120,
        [
            "How many hours of coverage and shooters are included?",
            "When will preview sneak-peeks and full high-res files be ready?",
            "Do you provide a full release for personal printing rights?",
        ],
    ),
    VendorSpec(
        "Entertainment & Music",
        90,
        [
            "Do you provide wireless microphones for speeches?",
            "Can we submit must-play and do-not-play track lists?",
            "What backup audio gear do you carry onsite?",
        ],
    ),
)

BIRTHDAY_VENDOR_SPECS: tuple[VendorSpec, ...] = (
    VendorSpec(
        "Venue & Space",
        45,
        [
            "Can we bring outside cake, snacks, or special beverages?",
            "Are adhesive wall decorations and balloon anchors permitted?",
            "Is AV equipment available for photo slideshows?",
        ],
    ),
    VendorSpec(
        "Food & Beverages",
        30,
        [
            "Can you craft a custom-themed birthday cake design?",
            "Do you supply compostable tableware and napkins?",
            "What is the deadline for final guest count adjustments?",
        ],
    ),
    VendorSpec(
        "Entertainment & DJ",
        21,
        [
            "What age group and musical genres do you specialize in?",
            "Can you run interactive party games and announcements?",
            "Do you provide ambient party lighting packages?",
        ],
    ),
)

COMMUNITY_VENDOR_SPECS: tuple[VendorSpec, ...] = (
    VendorSpec(
        "Permits & Staging",
        60,
        [
            "Is the staging platform certified for weather and load safety?",
            "Do you provide covered tent canopy structures?",
            "What is the delivery, installation, and inspection schedule?",
        ],
    ),
    VendorSpec(
        "Sound & Production",
        45,
        [
            "Is audio equipment wind-resistant for outdoor broadcast?",
            "Do you supply generator power or need dedicated line hookups?",
            "Will a licensed sound engineer remain stationed during the event?",
        ],
    ),
    VendorSpec(
        "Refreshments & Food",
        30,
        [
            "Do all participating food vendors hold active health permits?",
            "Are safe handwashing and cold storage stations required?",
            "Can you supply eco-friendly bulk water refill stations?",
        ],
    ),
)

VENDOR_SPECS_BY_EVENT_TYPE: dict[EventType, tuple[VendorSpec, ...]] = {
    EventType.WEDDING: WEDDING_VENDOR_SPECS,
    EventType.BIRTHDAY: BIRTHDAY_VENDOR_SPECS,
    EventType.COMMUNITY: COMMUNITY_VENDOR_SPECS,
}
