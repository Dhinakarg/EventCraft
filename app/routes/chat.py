"""Chat conversation routes for event plan refinement using app.ai module."""

from fastapi import APIRouter

from app.ai.gemini_client import refine_plan_chat
from app.ai.schemas import ChatRefineRequest, ChatRefineResponse

router = APIRouter(prefix="/api/ai", tags=["Chat Assistant"])


@router.post("/chat", response_model=ChatRefineResponse)
def chat_refinement(req: ChatRefineRequest) -> ChatRefineResponse:
    """Conversational assistant to answer questions and refine event specifics."""
    return refine_plan_chat(req.plan_context, req.question)
