"""Pure deterministic backward-scheduled timeline engine with compression."""

from datetime import date, timedelta

from app.engine.profiles import get_standard_lead_time
from app.models import EventRequest, EventType, TimelineResponse, TimelineTask


def _get_wedding_task_templates() -> list[tuple[str, str, str, int, bool]]:
    """Return wedding tasks (id, title, phase, std_days_before, is_critical)."""
    return [
        ("w1", "Tour and lock ceremony & reception venue", "Vision & Venue", 270, True),
        ("w2", "Interview and contract caterer and bar", "Vendor Sourcing", 210, True),
        ("w3", "Book lead photographer and videographer", "Vendor Sourcing", 180, True),
        ("w4", "Finalize floral designer and color palette", "Design & Decor", 120, False),
        ("w5", "Mail invitations and open digital RSVP portal", "Guest Logistics", 90, True),
        ("w6", "Order custom favors and personalized signage", "Design & Decor", 45, False),
        ("w7", "Submit final headcount to caterer and venue", "Final Countdown", 21, True),
        ("w8", "Conduct wedding rehearsal and distribute day run-of-show", "Event Week", 3, True),
    ]


def _get_birthday_task_templates() -> list[tuple[str, str, str, int, bool]]:
    """Return birthday tasks (id, title, phase, std_days_before, is_critical)."""
    return [
        ("b1", "Reserve private lounge, hall or dining venue", "Initial Setup", 60, True),
        ("b2", "Order custom birthday cake and select menu", "Food & Beverage", 40, True),
        ("b3", "Book DJ, performer or entertainment package", "Entertainment", 30, True),
        ("b4", "Distribute digital invitations and gather RSVPs", "Invitations", 25, True),
        ("b5", "Order customized balloon arches and backdrop decor", "Decor", 14, False),
        ("b6", "Assemble party favor bags and game props", "Preparation", 7, False),
        ("b7", "Confirm cake pickup and venue arrival time", "Event Day Prep", 2, True),
    ]


def _get_community_task_templates() -> list[tuple[str, str, str, int, bool]]:
    """Return community tasks (id, title, phase, std_days_before, is_critical)."""
    return [
        ("c1", "File municipal sound, park, and road permits", "Permits & Safety", 90, True),
        ("c2", "Secure local sponsors and confirm event grants", "Budget & Sponsors", 75, True),
        ("c3", "Reserve sound staging, generators, and restrooms", "Logistics", 60, True),
        ("c4", "Recruit and assign volunteer zone leaders", "Staffing", 35, True),
        ("c5", "Distribute flyers and publicize on neighborhood boards", "Outreach", 21, False),
        ("c6", "Conduct safety walkthrough and emergency briefing", "Safety & Prep", 7, True),
        ("c7", "Set up first-aid tent and registration tables", "Site Staging", 1, True),
    ]


def _get_task_templates(event_type: EventType) -> list[tuple[str, str, str, int, bool]]:
    """Dispatch task templates for event type."""
    if event_type == EventType.WEDDING:
        return _get_wedding_task_templates()
    if event_type == EventType.BIRTHDAY:
        return _get_birthday_task_templates()
    return _get_community_task_templates()


def _build_timeline_task(
    template: tuple[str, str, str, int, bool],
    event_date: date,
    scale: float,
    is_compressed: bool,
    available_days: int,
) -> TimelineTask:
    """Build single TimelineTask with computed due date and urgency labels."""
    today = date.today()
    t_id, title, phase, std_days, is_crit = template
    target_days = max(1, int(round(std_days * scale))) if is_compressed else std_days
    target_days = min(target_days, available_days)
    computed_due = event_date - timedelta(days=target_days)
    actual_due = max(today, computed_due)

    if is_compressed:
        p_label = "Urgent Critical" if is_crit else "Deferred / Optional"
    else:
        p_label = "High Priority" if is_crit else "Standard"

    return TimelineTask(
        id=t_id,
        title=title,
        phase=phase,
        due_date=actual_due,
        days_before_event=target_days,
        priority=p_label,
        is_critical=is_crit,
        status="todo",
    )


def _schedule_tasks_backward(
    templates: list[tuple[str, str, str, int, bool]],
    event_date: date,
    available_days: int,
    std_lead: int,
    is_compressed: bool,
) -> list[TimelineTask]:
    """Calculate task due dates backward from event_date with proportional compression."""
    scale = (available_days / std_lead) if (is_compressed and std_lead > 0) else 1.0

    tasks = [_build_timeline_task(tmpl, event_date, scale, is_compressed, available_days) for tmpl in templates]
    return sorted(tasks, key=lambda t: t.due_date)


def create_backward_timeline(req: EventRequest) -> TimelineResponse:
    """Schedule tasks backward from event_date, compressing if timeframe is constrained.

    Args:
        req: Validated event request containing target event date and type.

    Returns:
        TimelineResponse containing scheduled milestone tasks and rush warnings.
    """
    today = date.today()
    available_days = max(1, (req.event_date - today).days)
    std_lead = get_standard_lead_time(req.event_type)
    is_compressed = available_days < std_lead

    rush_warning = None
    if is_compressed:
        rush_warning = (
            f"Rush plan: Available lead time ({available_days} days) is less than standard "
            f"({std_lead} days). Non-critical tasks are deferred; lock critical vendors now."
        )

    templates = _get_task_templates(req.event_type)
    scheduled_tasks = _schedule_tasks_backward(templates, req.event_date, available_days, std_lead, is_compressed)
    return TimelineResponse(
        lead_time_days=available_days,
        standard_lead_time_days=std_lead,
        is_compressed=is_compressed,
        tasks=scheduled_tasks,
        rush_warning=rush_warning,
    )
