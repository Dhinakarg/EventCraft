"""Pydantic v2 schemas for Gemini AI structured responses and requests."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.sanitizer import sanitize_raw_text


class IdeasResponse(BaseModel):
    """Structured creative ideas schema returned by Gemini AI or fallback."""

    model_config = ConfigDict(extra="ignore")

    themes: list[str] = Field(..., min_length=3, description="Exactly 3 creative theme concepts")
    menu_ideas: list[str] = Field(..., min_length=1, description="Catering and beverage ideas")
    activities: list[str] = Field(..., min_length=1, description="Interactive games and activities")
    decor_tips: list[str] = Field(..., min_length=1, description="Decor and lighting suggestions")
    personal_touches: list[str] = Field(..., min_length=1, description="Unique memorable touches")
    source: Literal["ai", "fallback"] = Field(default="ai")


class IdeasRequest(BaseModel):
    """Input parameters for generating structured ideas."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: str = Field(default="wedding", max_length=50)
    vibe: str = Field(default="modern", max_length=100)
    dietary: list[str] = Field(default_factory=list)
    guest_count: int = Field(default=50, ge=1, le=2000)
    city: str | None = Field(default="", max_length=100)
    notes: str | None = Field(default="", max_length=500)

    @field_validator("event_type", "vibe", "city", "notes")
    @classmethod
    def clean_text(cls, v: str | None) -> str:
        """Sanitize control chars and truncate untrusted input."""
        return sanitize_raw_text(v or "", max_length=500)


class ChatRefineRequest(BaseModel):
    """Conversational plan refinement query."""

    model_config = ConfigDict(str_strip_whitespace=True)

    plan_context: str = Field(default="", max_length=1000)
    question: str = Field(..., min_length=2, max_length=300)

    @field_validator("plan_context", "question")
    @classmethod
    def clean_chat_text(cls, v: str) -> str:
        """Sanitize untrusted chat questions."""
        return sanitize_raw_text(v, max_length=300)


class ChatRefineResponse(BaseModel):
    """Assistant conversational reply."""

    reply: str
    source: Literal["ai", "fallback"] = Field(default="ai")
