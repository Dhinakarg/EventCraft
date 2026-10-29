"""FastAPI router for interactive event planning chat assistant."""

from fastapi import APIRouter, Depends

from app.ai.gemini_client import LruCache, get_lru_cache, refine_plan_chat
from app.ai.schemas import ChatRefineRequest, ChatRefineResponse
from app.security import RateLimiter, get_rate_limiter

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatRefineResponse)
def chat_endpoint(
    req: ChatRefineRequest,
    cache: LruCache = Depends(get_lru_cache),
    _rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> ChatRefineResponse:
    """Conversational plan refinement constrained strictly to event planning topics."""
    return refine_plan_chat(req.plan_context, req.question, cache=cache)
