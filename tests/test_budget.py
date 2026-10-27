"""Unit tests for deterministic budget engine and feasibility checks."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.engine.budget import allocate_event_budget
from app.models import EventRequest, EventType


def test_budget_exact_sum_matching_total() -> None:
    """Verify sum of allocated items matches total_budget exactly to the cent."""
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=200),
        guest_count=120,
        total_budget=34567.89,
        currency="USD",
        priorities=["venue", "food"],
    )
    res = allocate_event_budget(req, contingency_rate=8.0)
    allocated_sum = round(sum(i.allocated_amount for i in res.items), 2)
    assert allocated_sum == 34567.89
    assert res.contingency_fund > 0


def test_budget_priority_weight_shifting() -> None:
    """Verify prioritized categories receive shifted higher percentages."""
    base_req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=150),
        guest_count=100,
        total_budget=20000.0,
        priorities=[],
    )
    base_res = allocate_event_budget(base_req)
    base_venue_pct = next(i.percentage for i in base_res.items if "Venue" in i.category)

    boost_req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=150),
        guest_count=100,
        total_budget=20000.0,
        priorities=["venue"],
    )
    boost_res = allocate_event_budget(boost_req)
    boost_venue_pct = next(i.percentage for i in boost_res.items if "Venue" in i.category)

    assert boost_venue_pct > base_venue_pct
    assert round(sum(i.percentage for i in boost_res.items), 1) == 100.0


def test_feasibility_check_underfunded_warning() -> None:
    """Verify low budget per guest triggers feasibility alert and suggestions."""
    req = EventRequest(
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=100),
        guest_count=500,
        total_budget=5000.0, # $10/guest is below $90 wedding threshold
    )
    res = allocate_event_budget(req)
    assert res.is_feasible is False
    assert any("reduce guest" in s.lower() for s in res.feasibility_notes)
    assert any("diy" in s.lower() for s in res.feasibility_notes)


def test_budget_edge_case_single_guest_and_max_guests() -> None:
    """Verify engine handles 1 guest and 2000 guests properly."""
    req_one = EventRequest(
        event_type=EventType.BIRTHDAY,
        event_date=date.today() + timedelta(days=30),
        guest_count=1,
        total_budget=500.0,
    )
    res_one = allocate_event_budget(req_one)
    assert res_one.per_guest_cost == 500.0

    req_max = EventRequest(
        event_type=EventType.COMMUNITY,
        event_date=date.today() + timedelta(days=120),
        guest_count=2000,
        total_budget=100000.0,
    )
    res_max = allocate_event_budget(req_max)
    assert res_max.per_guest_cost == 50.0
    assert res_max.is_feasible is True


def test_invalid_event_request_inputs() -> None:
    """Verify validation errors for past date, zero budget, and invalid priorities."""
    with pytest.raises(ValidationError):
        EventRequest(
            event_type=EventType.WEDDING,
            event_date=date.today() - timedelta(days=1), # past date
            guest_count=50,
            total_budget=1000.0,
        )

    with pytest.raises(ValidationError):
        EventRequest(
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=30),
            guest_count=50,
            total_budget=0.0, # zero budget
        )

    with pytest.raises(ValidationError):
        EventRequest(
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=30),
            guest_count=50,
            total_budget=1000.0,
            priorities=["venue", "food", "decor", "photography"], # > 3 priorities
        )
