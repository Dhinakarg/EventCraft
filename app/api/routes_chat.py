"""FastAPI router for interactive event planning chat assistant."""

from fastapi import APIRouter

from app.ai.gemini_client import refine_plan_chat
from app.ai.schemas import ChatRefineRequest, ChatRefineResponse

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatRefineResponse)
def chat_endpoint(req: ChatRefineRequest) -> ChatRefineResponse:
    """Conversational plan refinement constrained strictly to event planning topics."""
    return refine_plan_chat(req.plan_context, req.question)
