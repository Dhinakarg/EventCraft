"""Typed task templates and milestones for deterministic backward scheduling."""

from typing import NamedTuple

from app.models import EventType


class TaskTemplate(NamedTuple):
    """Milestone task template for backward scheduling."""

    id: str
    title: str
    phase: str
    days_before_event: int
    is_critical: bool


WEDDING_TASK_TEMPLATES: tuple[TaskTemplate, ...] = (
    TaskTemplate("w1", "Tour and lock ceremony & reception venue", "Vision & Venue", 270, True),
    TaskTemplate("w2", "Interview and contract caterer and bar", "Vendor Sourcing", 210, True),
    TaskTemplate("w3", "Book lead photographer and videographer", "Vendor Sourcing", 180, True),
    TaskTemplate("w4", "Finalize floral designer and color palette", "Design & Decor", 120, False),
    TaskTemplate("w5", "Mail invitations and open digital RSVP portal", "Guest Logistics", 90, True),
    TaskTemplate("w6", "Order custom favors and personalized signage", "Design & Decor", 45, False),
    TaskTemplate("w7", "Submit final headcount to caterer and venue", "Final Countdown", 21, True),
    TaskTemplate("w8", "Conduct wedding rehearsal and distribute day run-of-show", "Event Week", 3, True),
)

BIRTHDAY_TASK_TEMPLATES: tuple[TaskTemplate, ...] = (
    TaskTemplate("b1", "Reserve private lounge, hall or dining venue", "Initial Setup", 60, True),
    TaskTemplate("b2", "Order custom birthday cake and select menu", "Food & Beverage", 40, True),
    TaskTemplate("b3", "Book DJ, performer or entertainment package", "Entertainment", 30, True),
    TaskTemplate("b4", "Distribute digital invitations and gather RSVPs", "Invitations", 25, True),
    TaskTemplate("b5", "Order customized balloon arches and backdrop decor", "Decor", 14, False),
    TaskTemplate("b6", "Assemble party favor bags and game props", "Preparation", 7, False),
    TaskTemplate("b7", "Confirm cake pickup and venue arrival time", "Event Day Prep", 2, True),
)

COMMUNITY_TASK_TEMPLATES: tuple[TaskTemplate, ...] = (
    TaskTemplate("c1", "File municipal sound, park, and road permits", "Permits & Safety", 90, True),
    TaskTemplate("c2", "Secure local sponsors and confirm event grants", "Budget & Sponsors", 75, True),
    TaskTemplate("c3", "Reserve sound staging, generators, and restrooms", "Logistics", 60, True),
    TaskTemplate("c4", "Recruit and assign volunteer zone leaders", "Staffing", 35, True),
    TaskTemplate("c5", "Distribute flyers and publicize on neighborhood boards", "Outreach", 21, False),
    TaskTemplate("c6", "Conduct safety walkthrough and emergency briefing", "Safety & Prep", 7, True),
    TaskTemplate("c7", "Set up first-aid tent and registration tables", "Site Staging", 1, True),
)

TASK_TEMPLATES_BY_EVENT_TYPE: dict[EventType, tuple[TaskTemplate, ...]] = {
    EventType.WEDDING: WEDDING_TASK_TEMPLATES,
    EventType.BIRTHDAY: BIRTHDAY_TASK_TEMPLATES,
    EventType.COMMUNITY: COMMUNITY_TASK_TEMPLATES,
}
