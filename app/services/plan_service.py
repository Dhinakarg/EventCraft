"""Domain planning service orchestrating deterministic engines and AI ideation."""

from app.ai.gemini_client import LruCache, generate_event_ideas
from app.ai.schemas import IdeasRequest
from app.engine.budget import allocate_event_budget
from app.engine.timeline import create_backward_timeline
from app.engine.vendors import build_vendor_checklist
from app.models import EventRequest, PlanResponse


def _build_warnings(budget_feasible: bool, b_notes: list[str], rush_warn: str | None) -> list[str]:
    """Compile budget and timeline warnings into a unified list."""
    warns: list[str] = []
    if not budget_feasible:
        warns.extend(b_notes)
    if rush_warn:
        warns.append(rush_warn)
    return warns


def create_event_plan(req: EventRequest, cache: LruCache | None = None) -> PlanResponse:
    """Generate master plan combining pure deterministic engines and GenAI ideas.

    Args:
        req: Validated user event request.
        cache: Optional LruCache instance for caching ideas.

    Returns:
        PlanResponse with budget, timeline, vendors, warnings, and creative ideas.
    """
    budget = allocate_event_budget(req)
    timeline = create_backward_timeline(req)
    vendors = build_vendor_checklist(req, budget)
    warnings = _build_warnings(budget.is_feasible, budget.feasibility_notes, timeline.rush_warning)

    ideas_req = IdeasRequest(
        event_type=req.event_type.value,
        vibe=req.vibe,
        dietary=req.dietary,
        guest_count=req.guest_count,
        city=req.city,
        notes=req.notes or "",
    )
    ideas = generate_event_ideas(ideas_req, cache=cache)

    return PlanResponse(
        event_type=req.event_type,
        event_date=req.event_date,
        guest_count=req.guest_count,
        total_budget=req.total_budget,
        currency=req.currency,
        city=req.city,
        vibe=req.vibe,
        budget=budget,
        timeline=timeline,
        vendors=vendors,
        warnings=warnings,
        ideas=ideas,
    )
