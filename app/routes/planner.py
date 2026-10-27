"""Deterministic event planning routes integrating models and engine modules."""

from fastapi import APIRouter

from app.engine.budget import allocate_event_budget
from app.engine.timeline import create_backward_timeline
from app.engine.vendors import build_vendor_checklist
from app.models import (
    BudgetResponse,
    EventRequest,
    PlanResponse,
    TimelineResponse,
    VendorChecklistItem,
)

router = APIRouter(prefix="/api/plan", tags=["Deterministic Planner"])


@router.post("/generate", response_model=PlanResponse)
def generate_master_plan(req: EventRequest) -> PlanResponse:
    """Generate complete deterministic plan including budget, timeline, and vendors."""
    budget = allocate_event_budget(req)
    timeline = create_backward_timeline(req)
    vendors = build_vendor_checklist(req, budget)

    warnings: list[str] = []
    if not budget.is_feasible:
        warnings.extend(budget.feasibility_notes)
    if timeline.rush_warning:
        warnings.append(timeline.rush_warning)

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
    )


@router.post("/budget", response_model=BudgetResponse)
def calculate_budget_only(req: EventRequest) -> BudgetResponse:
    """Calculate deterministic budget breakdown without modifying other modules."""
    return allocate_event_budget(req)


@router.post("/timeline", response_model=TimelineResponse)
def calculate_timeline_only(req: EventRequest) -> TimelineResponse:
    """Generate deterministic event timeline and backward milestones."""
    return create_backward_timeline(req)


@router.post("/vendors", response_model=list[VendorChecklistItem])
def calculate_vendors_only(req: EventRequest) -> list[VendorChecklistItem]:
    """Calculate vendor categories and deliverables deterministically."""
    budget = allocate_event_budget(req)
    return build_vendor_checklist(req, budget)
