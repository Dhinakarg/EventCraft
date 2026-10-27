"""Routes package init."""

from app.routes.ai_ideas import router as ai_ideas_router
from app.routes.chat import router as chat_router
from app.routes.planner import router as planner_router

__all__ = ["planner_router", "ai_ideas_router", "chat_router"]
