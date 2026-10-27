"""Creative AI idea generation routes using app.ai module."""

from fastapi import APIRouter

from app.ai.gemini_client import generate_event_ideas
from app.ai.schemas import IdeasRequest, IdeasResponse

router = APIRouter(prefix="/api/ai", tags=["Creative Ideas"])


@router.post("/ideas", response_model=IdeasResponse)
def get_creative_ideas(req: IdeasRequest) -> IdeasResponse:
    """Generate structured themes, decor, and personal touches using Gemini or fallback."""
    return generate_event_ideas(req)
