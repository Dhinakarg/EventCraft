"""Unit tests for typed static data modules in app.engine.data and app.ai.data."""

from app.ai.data.fallback_content import (
    BIRTHDAY_FALLBACK_ACTIVITIES,
    CHAT_DISPATCH_RULES,
    COMMUNITY_FALLBACK_ACTIVITIES,
    WEDDING_FALLBACK_ACTIVITIES,
)
from app.engine.data.task_templates import TASK_TEMPLATES_BY_EVENT_TYPE
from app.engine.data.vendor_specs import VENDOR_SPECS_BY_EVENT_TYPE
from app.models import EventType


def test_task_templates_complete_for_all_event_types() -> None:
    """Every supported EventType must have a non-empty list of task templates."""
    for event_type in EventType:
        templates = TASK_TEMPLATES_BY_EVENT_TYPE.get(event_type)
        assert templates is not None, f"Missing task templates for {event_type}"
        assert len(templates) >= 3, f"Insufficient task templates for {event_type}"
        for t in templates:
            assert t.title != ""
            assert t.days_before_event >= 0
            assert t.phase != ""
            assert isinstance(t.is_critical, bool)


def test_vendor_specs_complete_for_all_event_types() -> None:
    """Every supported EventType must have vendor specifications with interview prompts."""
    for event_type in EventType:
        specs = VENDOR_SPECS_BY_EVENT_TYPE.get(event_type)
        assert specs is not None, f"Missing vendor specs for {event_type}"
        assert len(specs) >= 3, f"Insufficient vendor specs for {event_type}"
        for s in specs:
            assert s.category != ""
            assert s.lead_time_days > 0
            assert len(s.interview_prompts) > 0
            for prompt in s.interview_prompts:
                assert prompt != ""


def test_fallback_activities_data_integrity() -> None:
    """Fallback activity lists must contain descriptive strings."""
    assert len(WEDDING_FALLBACK_ACTIVITIES) > 0
    assert len(BIRTHDAY_FALLBACK_ACTIVITIES) > 0
    assert len(COMMUNITY_FALLBACK_ACTIVITIES) > 0


def test_chat_dispatch_rules_integrity() -> None:
    """Dispatch rules must define non-empty keywords and response text."""
    assert len(CHAT_DISPATCH_RULES) >= 3
    for keywords, reply_text in CHAT_DISPATCH_RULES:
        assert len(keywords) > 0
        assert len(reply_text) > 0
