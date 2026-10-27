"""Pure deterministic RFC 5545 iCalendar (.ics) generation utility."""

from datetime import UTC, datetime

from app.models import TimelineTask


def _format_vevent(task: TimelineTask, now_str: str) -> list[str]:
    """Format single TimelineTask as RFC 5545 VEVENT block."""
    date_val = task.due_date.strftime("%Y%m%d")
    uid = f"{task.id}-{date_val}@eventcraft.ai"
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_str}Z",
        f"DTSTART;VALUE=DATE:{date_val}",
        f"SUMMARY:{task.title}",
        f"DESCRIPTION:Phase: {task.phase} | Priority: {task.priority}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
    ]


def generate_ics_calendar(tasks: list[TimelineTask], event_name: str = "Event Plan") -> str:
    """Generate valid iCalendar (.ics) string from a list of timeline tasks."""
    now_str = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EventCraft AI//Planner//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{event_name} Timeline",
    ]

    for task in tasks:
        lines.extend(_format_vevent(task, now_str))

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
