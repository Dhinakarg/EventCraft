"""Pure deterministic backward-scheduled timeline engine with compression."""

from datetime import date, timedelta

from app.engine.data.task_templates import TASK_TEMPLATES_BY_EVENT_TYPE, TaskTemplate
from app.engine.profiles import get_standard_lead_time
from app.models import EventRequest, EventType, TimelineResponse, TimelineTask


def _get_task_templates(event_type: EventType) -> list[TaskTemplate]:
    """Dispatch task templates for event type."""
    templates = TASK_TEMPLATES_BY_EVENT_TYPE.get(event_type, TASK_TEMPLATES_BY_EVENT_TYPE[EventType.WEDDING])
    return list(templates)


def _build_timeline_task(
    template: TaskTemplate,
    event_date: date,
    scale: float,
    is_compressed: bool,
    available_days: int,
) -> TimelineTask:
    """Build single TimelineTask with computed due date and urgency labels."""
    today = date.today()
    target_days = (
        max(1, int(round(template.days_before_event * scale))) if is_compressed else template.days_before_event
    )
    target_days = min(target_days, available_days)
    computed_due = event_date - timedelta(days=target_days)
    actual_due = max(today, computed_due)

    if is_compressed:
        p_label = "Urgent Critical" if template.is_critical else "Deferred / Optional"
    else:
        p_label = "High Priority" if template.is_critical else "Standard"

    return TimelineTask(
        id=template.id,
        title=template.title,
        phase=template.phase,
        due_date=actual_due,
        days_before_event=target_days,
        priority=p_label,
        is_critical=template.is_critical,
        status="todo",
    )


def _schedule_tasks_backward(
    templates: list[TaskTemplate],
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
