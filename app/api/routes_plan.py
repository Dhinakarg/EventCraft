"""FastAPI router for event plan generation endpoints."""

from fastapi import APIRouter, Depends

from app.ai.gemini_client import LruCache, get_lru_cache
from app.models import EventRequest, PlanResponse
from app.security import RateLimiter, get_rate_limiter
from app.services.plan_service import create_event_plan

router = APIRouter(tags=["plan"])


@router.post("/api/plan", response_model=PlanResponse)
def plan_endpoint(
    req: EventRequest,
    cache: LruCache = Depends(get_lru_cache),
    _rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> PlanResponse:
    """Generate comprehensive event plan with budget, timeline, vendors, and ideas."""
    return create_event_plan(req, cache=cache)
