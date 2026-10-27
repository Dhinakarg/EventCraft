"""FastAPI router for event plan generation endpoints."""

from fastapi import APIRouter

from app.models import EventRequest, PlanResponse
from app.services.plan_service import create_event_plan

router = APIRouter(tags=["plan"])


@router.post("/api/plan", response_model=PlanResponse)
def plan_endpoint(req: EventRequest) -> PlanResponse:
    """Generate comprehensive event plan with budget, timeline, vendors, and ideas."""
    return create_event_plan(req)
