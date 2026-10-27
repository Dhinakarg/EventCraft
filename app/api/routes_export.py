"""FastAPI router for calendar and data export endpoints."""

from datetime import date

from fastapi import APIRouter, Query, Response

from app.constants import MAX_GUEST_COUNT, MIN_GUEST_COUNT
from app.engine.ics import generate_ics_calendar
from app.engine.timeline import create_backward_timeline
from app.models import EventRequest, EventType

router = APIRouter(tags=["export"])


@router.get("/api/export/ics")
def export_timeline_ics(
    event_date: date = Query(...),
    event_type: EventType = Query(default=EventType.WEDDING),
    guest_count: int = Query(default=100, ge=MIN_GUEST_COUNT, le=MAX_GUEST_COUNT),
    total_budget: float = Query(default=10000.0, gt=0),
    vibe: str = Query(default="Modern"),
) -> Response:
    """Export backward-scheduled event timeline as an iCalendar (.ics) file."""
    req = EventRequest(
        event_type=event_type,
        event_date=event_date,
        guest_count=guest_count,
        total_budget=total_budget,
        vibe=vibe,
    )
    timeline = create_backward_timeline(req)
    ics_text = generate_ics_calendar(timeline.tasks, f"{vibe} {event_type.value}")
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="event_timeline.ics"'},
    )
