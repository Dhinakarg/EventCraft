"""AI package initialization exporting ideas, chat refinement, and schemas."""

from app.ai.gemini_client import (
    LruCache,
    compute_request_hash,
    generate_event_ideas,
    get_lru_cache,
    refine_plan_chat,
)
from app.ai.schemas import (
    ChatRefineRequest,
    ChatRefineResponse,
    IdeasRequest,
    IdeasResponse,
)

__all__ = [
    "generate_event_ideas",
    "refine_plan_chat",
    "LruCache",
    "get_lru_cache",
    "compute_request_hash",
    "IdeasRequest",
    "IdeasResponse",
    "ChatRefineRequest",
    "ChatRefineResponse",
]
