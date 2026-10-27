"""Unit tests for deterministic timeline engine."""

from datetime import date
from app.engine.timeline import build_day_schedule, build_milestones, create_event_timeline
from app.schemas import EventType


def test_build_milestones() -> None:
    """Test milestone countdown generation."""
    target_date = date(2027, 6, 20)
    milestones = build_milestones(target_date)
    assert len(milestones) == 4
    assert milestones[0].days_before == 180
    assert len(milestones[0].action_items) >= 2


def test_build_wedding_schedule() -> None:
    """Test day-of schedule blocks for wedding."""
    schedule = build_day_schedule("16:00", 5.0, EventType.WEDDING)
    assert len(schedule) >= 5
    titles = [s.title for s in schedule]
    assert any("Ceremony" in t for t in titles)
    assert any("Dinner" in t for t in titles)


def test_build_birthday_schedule() -> None:
    """Test day-of schedule blocks for birthday party."""
    schedule = build_day_schedule("14:00", 4.0, EventType.BIRTHDAY)
    assert len(schedule) >= 4
    titles = [s.title for s in schedule]
    assert any("Cake" in t for t in titles)


def test_create_full_timeline() -> None:
    """Test combined timeline creation."""
    timeline = create_event_timeline(date(2027, 9, 1), "15:00", 6.0, EventType.COMMUNITY)
    assert len(timeline.day_schedule) > 0
    assert len(timeline.milestones) > 0
