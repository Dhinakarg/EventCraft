"""Chat conversation routes for event plan refinement."""

from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import refine_plan_with_chat

router = APIRouter(prefix="/api/ai", tags=["Chat Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat_refinement(req: ChatRequest) -> ChatResponse:
    """Conversational assistant to answer questions and refine event specifics."""
    return refine_plan_with_chat(req.messages, req.current_plan)
