"""Unit tests for vendor checklist and booking deadline engine."""

from datetime import date, timedelta

from app.engine.budget import allocate_event_budget
from app.engine.vendors import build_vendor_checklist
from app.models import EventRequest, EventType


def test_vendor_checklist_generation() -> None:
    """Verify vendor items contain budget cap, deadline, questions, and todo status."""
    target_date = date.today() + timedelta(days=200)
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=target_date,
        guest_count=100,
        total_budget=30000.0,
    )
    budget = allocate_event_budget(req)
    checklist = build_vendor_checklist(req, budget)

    assert len(checklist) >= 4
    for item in checklist:
        assert item.budget_cap > 0
        assert item.status == "todo"
        assert item.booking_deadline <= target_date
        assert item.booking_deadline >= date.today()
        assert len(item.questions_to_ask) >= 3


def test_vendor_deadline_compression_edge_case() -> None:
    """Verify vendor deadlines clamp to today when time is severely constrained."""
    target_date = date.today() + timedelta(days=10)
    req = EventRequest(
        event_type=EventType.BIRTHDAY,
        event_date=target_date,
        guest_count=30,
        total_budget=2500.0,
    )
    budget = allocate_event_budget(req)
    checklist = build_vendor_checklist(req, budget)

    assert len(checklist) >= 3
    # With only 10 days, long lead-time items must clamp safely to date.today()
    assert all(item.booking_deadline >= date.today() for item in checklist)
    assert all(item.booking_deadline <= target_date for item in checklist)


def test_community_vendor_categories() -> None:
    """Verify community vendor categories include staging, sound, and food."""
    target_date = date.today() + timedelta(days=90)
    req = EventRequest(
        event_type=EventType.COMMUNITY,
        event_date=target_date,
        guest_count=400,
        total_budget=16000.0,
    )
    budget = allocate_event_budget(req)
    checklist = build_vendor_checklist(req, budget)

    categories = [c.category for c in checklist]
    assert any("Staging" in cat for cat in categories)
    assert any("Sound" in cat for cat in categories)
