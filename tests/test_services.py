"""Unit tests for app.services.plan_service."""

from datetime import date, timedelta
from unittest.mock import patch

from app.models import EventRequest, EventType, PriorityEnum
from app.services.plan_service import _build_warnings, create_event_plan


def test_build_warnings_all_clear() -> None:
    """Warnings list should be empty when budget is feasible and lead time is normal."""
    warnings = _build_warnings(budget_feasible=True, b_notes=[], rush_warn=None)
    assert warnings == []


def test_build_warnings_budget_notes_only() -> None:
    """Warnings list should include budget notes when budget is not feasible."""
    notes = ["Budget ₹100/guest is below minimum recommended ₹500/guest"]
    warnings = _build_warnings(budget_feasible=False, b_notes=notes, rush_warn=None)
    assert warnings == notes


def test_build_warnings_rush_warning_only() -> None:
    """Warnings list should include rush warning when rush condition is flagged."""
    rush = "Event date is only 5 days away. Urgent vendor confirmations needed."
    warnings = _build_warnings(budget_feasible=True, b_notes=[], rush_warn=rush)
    assert warnings == [rush]


def test_build_warnings_combined() -> None:
    """Warnings should merge budget notes and rush warning when both trigger."""
    notes = ["Low budget per attendee"]
    rush = "Short planning window"
    warnings = _build_warnings(budget_feasible=False, b_notes=notes, rush_warn=rush)
    assert len(warnings) == 2
    assert notes[0] in warnings
    assert rush in warnings


def test_create_event_plan_generates_complete_response() -> None:
    """create_event_plan should coordinate budget, timeline, vendors, and fallback/mock ideas."""
    target_date = date.today() + timedelta(days=90)
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=target_date,
        guest_count=120,
        total_budget=500_000,
        currency="INR",
        city="Bengaluru",
        vibe="Royal Classic",
        priorities=[PriorityEnum.FOOD, PriorityEnum.VENUE],
    )

    with patch("app.ai.gemini_client._get_client", return_value=None):
        plan = create_event_plan(req)

    assert plan.event_type == EventType.WEDDING
    assert plan.guest_count == 120
    assert plan.total_budget == 500_000
    assert plan.budget.total_budget == 500_000
    assert len(plan.timeline.tasks) > 0
    assert len(plan.vendors) > 0
    assert plan.ideas is not None
    assert len(plan.ideas.themes) > 0


def test_create_event_plan_propagates_rush_warning() -> None:
    """create_event_plan should include rush warning in PlanResponse for short lead times."""
    target_date = date.today() + timedelta(days=7)
    req = EventRequest(
        event_type=EventType.BIRTHDAY,
        event_date=target_date,
        guest_count=30,
        total_budget=50_000,
        currency="INR",
        city="Mumbai",
    )

    with patch("app.ai.gemini_client._get_client", return_value=None):
        plan = create_event_plan(req)

    assert plan.timeline.rush_warning is not None
    assert any("rush" in w.lower() or "days away" in w.lower() for w in plan.warnings)


def test_create_event_plan_community_festival() -> None:
    """create_event_plan should correctly orchestrate a community festival event type."""
    target_date = date.today() + timedelta(days=60)
    req = EventRequest(
        event_type=EventType.COMMUNITY,
        event_date=target_date,
        guest_count=200,
        total_budget=1_000_000,
        currency="INR",
        city="Hyderabad",
        vibe="Green Horizons",
    )

    with patch("app.ai.gemini_client._get_client", return_value=None):
        plan = create_event_plan(req)

    assert plan.event_type == EventType.COMMUNITY
    assert plan.budget.contingency_fund > 0
    assert any("Staging" in v.category or "Sound" in v.category or "Venue" in v.category for v in plan.vendors)
