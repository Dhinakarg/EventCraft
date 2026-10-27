"""Unit tests for deterministic budget engine."""

from app.engine.budget import allocate_budget, calculate_contingency
from app.schemas import EventType


def test_contingency_calculation() -> None:
    """Test 5 percent contingency fund buffer calculation."""
    res = calculate_contingency(10000.0, 0.05)
    assert res == 500.0


def test_wedding_budget_allocation_total() -> None:
    """Test wedding budget sums correctly with contingency."""
    total = 20000.0
    plan = allocate_budget(total, guest_count=100, event_type=EventType.WEDDING)

    assert plan.total_budget == 20000.0
    assert plan.per_guest_cost == 200.0
    assert plan.contingency_fund == 1000.0

    allocated_sum = sum(item.allocated_amount for item in plan.items)
    assert round(allocated_sum + plan.contingency_fund, 2) == total


def test_birthday_budget_allocation() -> None:
    """Test birthday budget items and per-guest metrics."""
    plan = allocate_budget(3000.0, guest_count=30, event_type=EventType.BIRTHDAY)
    assert plan.per_guest_cost == 100.0
    categories = [i.category for i in plan.items]
    assert "Theme Decor & Balloons" in categories


def test_community_budget_allocation() -> None:
    """Test community event allocation."""
    plan = allocate_budget(15000.0, guest_count=500, event_type=EventType.COMMUNITY)
    assert plan.per_guest_cost == 30.0
    categories = [i.category for i in plan.items]
    assert "Permits & Venue" in categories
    assert "Sound & Stage Production" in categories
