"""Unit tests for backward-scheduled timeline engine and rush compression."""

from datetime import date, timedelta

from app.engine.timeline import create_backward_timeline
from app.models import EventRequest, EventType


def test_standard_timeline_scheduling() -> None:
    """Verify tasks are scheduled backward when ample lead time is available."""
    target_date = date.today() + timedelta(days=300)
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=target_date,
        guest_count=100,
        total_budget=25000.0,
    )
    res = create_backward_timeline(req)
    assert res.is_compressed is False
    assert res.rush_warning is None
    assert len(res.tasks) >= 5
    assert all(t.due_date <= target_date for t in res.tasks)
    assert all(t.due_date >= date.today() for t in res.tasks)


def test_compressed_timeline_and_rush_warning() -> None:
    """Verify rush plan warning and task prioritization when time is constrained."""
    # Wedding standard is 270 days, scheduling in 45 days
    target_date = date.today() + timedelta(days=45)
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=target_date,
        guest_count=80,
        total_budget=20000.0,
    )
    res = create_backward_timeline(req)
    assert res.is_compressed is True
    assert res.rush_warning is not None
    assert "rush plan" in res.rush_warning.lower()

    critical_tasks = [t for t in res.tasks if t.is_critical]
    deferred_tasks = [t for t in res.tasks if not t.is_critical]
    assert len(critical_tasks) > 0
    assert any("Urgent" in t.priority for t in critical_tasks)
    assert any("Deferred" in t.priority for t in deferred_tasks)


def test_edge_case_event_tomorrow() -> None:
    """Verify engine handles event scheduled for tomorrow gracefully."""
    target_date = date.today() + timedelta(days=1)
    req = EventRequest(
        event_type=EventType.BIRTHDAY,
        event_date=target_date,
        guest_count=20,
        total_budget=1500.0,
    )
    res = create_backward_timeline(req)
    assert res.is_compressed is True
    assert res.lead_time_days == 1
    # All task due dates should clamp safely to today or tomorrow
    assert all(t.due_date in (date.today(), target_date) for t in res.tasks)


def test_birthday_and_community_timelines() -> None:
    """Verify timeline generation across birthday and community event types."""
    req_bday = EventRequest(
        event_type=EventType.BIRTHDAY,
        event_date=date.today() + timedelta(days=65),
        guest_count=35,
        total_budget=3000.0,
    )
    res_bday = create_backward_timeline(req_bday)
    assert res_bday.is_compressed is False
    assert any("cake" in t.title.lower() for t in res_bday.tasks)

    req_comm = EventRequest(
        event_type=EventType.COMMUNITY,
        event_date=date.today() + timedelta(days=40),
        guest_count=300,
        total_budget=15000.0,
    )
    res_comm = create_backward_timeline(req_comm)
    assert res_comm.is_compressed is True
    assert any("permit" in t.title.lower() for t in res_comm.tasks)
