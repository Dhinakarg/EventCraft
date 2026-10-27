"""Unit tests for deterministic vendor engine."""

from app.engine.budget import allocate_budget
from app.engine.vendors import build_vendor_recommendations, get_vendor_templates
from app.schemas import EventType


def test_vendor_templates_wedding() -> None:
    """Test retrieving wedding vendor templates."""
    templates = get_vendor_templates(EventType.WEDDING)
    assert len(templates) >= 4
    categories = [t["category"] for t in templates]
    assert "Venue & Facility" in categories


def test_build_vendor_recommendations() -> None:
    """Test vendor budget calculation and questions generation."""
    budget = allocate_budget(10000.0, 50, EventType.WEDDING)
    vendors = build_vendor_recommendations(EventType.WEDDING, budget)
    assert len(vendors) >= 4
    for v in vendors:
        assert v.allocated_budget > 0
        assert len(v.questions_to_ask) >= 2
        assert len(v.key_deliverables) >= 2
        assert v.booking_lead_time_weeks > 0


def test_vendor_recommendations_community() -> None:
    """Test community event vendor generation."""
    budget = allocate_budget(8000.0, 200, EventType.COMMUNITY)
    vendors = build_vendor_recommendations(EventType.COMMUNITY, budget)
    categories = [v.category for v in vendors]
    assert any("Staging" in c for c in categories)
