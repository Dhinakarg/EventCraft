"""Creative AI idea generation routes."""

from fastapi import APIRouter

from app.schemas import CreativeIdeaResponse, CreativePromptRequest
from app.services.ai_service import generate_creative_ideas

router = APIRouter(prefix="/api/ai", tags=["Creative Ideas"])


@router.post("/ideas", response_model=CreativeIdeaResponse)
def get_creative_ideas(req: CreativePromptRequest) -> CreativeIdeaResponse:
    """Generate theme, decor, and signature touch ideas using LLM or fallback."""
    return generate_creative_ideas(req)
