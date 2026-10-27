"""Pure deterministic checklist generation engine."""

from typing import List
from app.schemas import ChecklistTask, EventType


def _build_wedding_tasks() -> List[tuple]:
    """Return raw tasks for weddings (id, phase, task, priority, deadline)."""
    return [
        ("w1", "Initial Planning", "Determine target budget and maximum guest list", "High", "6-12 Months Out"),
        ("w2", "Initial Planning", "Research and book wedding ceremony & reception venue", "High", "8-10 Months Out"),
        ("w3", "Vendor Sourcing", "Interview and book photographer & videographer", "High", "7-9 Months Out"),
        ("w4", "Vendor Sourcing", "Book caterer and schedule menu tasting session", "High", "6-8 Months Out"),
        ("w5", "Vendor Sourcing", "Select florist and choose color palette", "Medium", "5-6 Months Out"),
        ("w6", "Final Countdown", "Mail official wedding invitations and open RSVP portal", "High", "2-3 Months Out"),
        ("w7", "Final Countdown", "Finalize seating chart and submit final headcounts", "High", "3-4 Weeks Out"),
        ("w8", "Event Week", "Pack emergency day kit and prepare vendor gratuities", "Medium", "3-5 Days Out"),
        ("w9", "Event Day", "Deliver marriage license and ring boxes to designated attendant", "High", "Day of Event"),
    ]


def _build_birthday_tasks() -> List[tuple]:
    """Return raw tasks for birthdays (id, phase, task, priority, deadline)."""
    return [
        ("b1", "Initial Planning", "Pick theme, color scheme, and guest headcount", "High", "6-8 Weeks Out"),
        ("b2", "Initial Planning", "Reserve party lounge, park pavilion, or private dining", "High", "5-6 Weeks Out"),
        ("b3", "Vendor Sourcing", "Order custom cake or cupcakes and confirm flavors", "High", "3-4 Weeks Out"),
        ("b4", "Vendor Sourcing", "Book entertainer (DJ, magician, photobooth, or clown)", "Medium", "3-4 Weeks Out"),
        ("b5", "Invitations", "Distribute digital invitations and gather dietary notes", "High", "3 Weeks Out"),
        ("b6", "Decor & Favors", "Purchase decorations, balloons, tableware, and favor bags", "Medium", "1-2 Weeks Out"),
        ("b7", "Event Day", "Pick up cake, setup balloon arch, and test sound/playlist", "High", "Morning of Event"),
    ]


def _build_community_tasks() -> List[tuple]:
    """Return raw tasks for community events (id, phase, task, priority, deadline)."""
    return [
        ("c1", "Permits & Safety", "File municipal park, sound, and road closure permits", "High", "12-16 Weeks Out"),
        ("c2", "Sponsors & Budget", "Recruit local community sponsors and confirm grants", "High", "10-12 Weeks Out"),
        ("c3", "Logistics", "Reserve portable restrooms, trash dumpsters, and tents", "High", "8-10 Weeks Out"),
        ("c4", "Volunteer Sourcing", "Recruit and assign volunteer team leads and safety staff", "High", "4-6 Weeks Out"),
        ("c5", "Outreach", "Distribute flyers, publicize on local media and community boards", "Medium", "4 Weeks Out"),
        ("c6", "Event Week", "Conduct site walkthrough and emergency plan briefing", "High", "1 Week Out"),
        ("c7", "Event Day", "Set up first-aid station, directional signs, and trash sweep", "High", "Day of Event"),
    ]


def build_event_checklist(event_type: EventType) -> List[ChecklistTask]:
    """Generate deterministic tasks tailored to the event type."""
    if event_type == EventType.WEDDING:
        raw_items = _build_wedding_tasks()
    elif event_type == EventType.BIRTHDAY:
        raw_items = _build_birthday_tasks()
    else:
        raw_items = _build_community_tasks()

    return [
        ChecklistTask(
            id=item[0],
            phase=item[1],
            task=item[2],
            priority=item[3],
            deadline_description=item[4],
            completed=False,
        )
        for item in raw_items
    ]
