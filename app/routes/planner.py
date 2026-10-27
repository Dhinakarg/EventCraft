"""Deterministic event planning routes."""

import uuid
from fastapi import APIRouter
from app.engine.budget import allocate_budget
from app.engine.checklist import build_event_checklist
from app.engine.timeline import create_event_timeline
from app.engine.vendors import build_vendor_recommendations
from app.schemas import (
    BudgetBreakdown,
    ChecklistTask,
    EventPlanRequest,
    EventTimeline,
    FullPlanResponse,
    VendorCategory,
)

router = APIRouter(prefix="/api/plan", tags=["Deterministic Planner"])


@router.post("/generate", response_model=FullPlanResponse)
def generate_full_plan(req: EventPlanRequest) -> FullPlanResponse:
    """Generate complete deterministic plan including budget, timeline, and vendors."""
    budget = allocate_budget(req.budget_total, req.guest_count, req.event_type)
    timeline = create_event_timeline(
        req.event_date, req.start_time, req.duration_hours, req.event_type
    )
    vendors = build_vendor_recommendations(req.event_type, budget)
    checklist = build_event_checklist(req.event_type)

    return FullPlanResponse(
        event_id=str(uuid.uuid4())[:8],
        event_name=req.event_name,
        event_type=req.event_type,
        guest_count=req.guest_count,
        total_budget=req.budget_total,
        event_date=req.event_date,
        budget=budget,
        timeline=timeline,
        vendors=vendors,
        checklist=checklist,
    )


@router.post("/budget", response_model=BudgetBreakdown)
def calculate_budget_only(req: EventPlanRequest) -> BudgetBreakdown:
    """Calculate deterministic budget breakdown without modifying other modules."""
    return allocate_budget(req.budget_total, req.guest_count, req.event_type)


@router.post("/timeline", response_model=EventTimeline)
def calculate_timeline_only(req: EventPlanRequest) -> EventTimeline:
    """Generate deterministic event timeline and countdown milestones."""
    return create_event_timeline(
        req.event_date, req.start_time, req.duration_hours, req.event_type
    )


@router.post("/vendors", response_model=list[VendorCategory])
def calculate_vendors_only(req: EventPlanRequest) -> list[VendorCategory]:
    """Calculate vendor categories and deliverables deterministically."""
    budget = allocate_budget(req.budget_total, req.guest_count, req.event_type)
    return build_vendor_recommendations(req.event_type, budget)


@router.post("/checklist", response_model=list[ChecklistTask])
def calculate_checklist_only(req: EventPlanRequest) -> list[ChecklistTask]:
    """Generate deterministic checklist tasks for event type."""
    return build_event_checklist(req.event_type)
