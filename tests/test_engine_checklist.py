"""Unit tests for deterministic checklist engine."""

from app.engine.checklist import build_event_checklist
from app.schemas import EventType


def test_wedding_checklist_generation() -> None:
    """Test generating full wedding checklist."""
    tasks = build_event_checklist(EventType.WEDDING)
    assert len(tasks) >= 8
    assert all(not t.completed for t in tasks)
    phases = {t.phase for t in tasks}
    assert "Initial Planning" in phases
    assert "Vendor Sourcing" in phases


def test_birthday_checklist_generation() -> None:
    """Test generating birthday checklist."""
    tasks = build_event_checklist(EventType.BIRTHDAY)
    assert len(tasks) >= 6
    task_names = [t.task for t in tasks]
    assert any("cake" in t.lower() for t in task_names)


def test_community_checklist_generation() -> None:
    """Test generating community checklist."""
    tasks = build_event_checklist(EventType.COMMUNITY)
    assert len(tasks) >= 6
    phases = {t.phase for t in tasks}
    assert "Permits & Safety" in phases
