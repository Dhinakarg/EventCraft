"""Pydantic v2 data models and validation schemas for EventCraft AI."""

from datetime import date
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.sanitizer import sanitize_raw_text


class EventType(str, Enum):
    """Supported event categories."""

    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"


class EventPlanRequest(BaseModel):
    """Request model for generating a comprehensive event plan."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: EventType = Field(default=EventType.WEDDING)
    event_name: str = Field(..., min_length=2, max_length=120)
    guest_count: int = Field(default=50, ge=1, le=10000)
    budget_total: float = Field(default=5000.0, ge=100.0, le=10000000.0)
    event_date: date = Field(...)
    start_time: str = Field(default="16:00", max_length=8)
    duration_hours: float = Field(default=5.0, ge=1.0, le=24.0)
    style_preference: str = Field(default="modern", max_length=50)
    location_type: str = Field(default="indoor", max_length=30)
    custom_notes: Optional[str] = Field(default="", max_length=500)

    @field_validator("event_name", "custom_notes", "style_preference", "location_type")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> str:
        """Sanitize control characters and strip whitespace."""
        return sanitize_raw_text(v or "", max_length=500)


class BudgetItem(BaseModel):
    """Single item allocation in the budget."""

    category: str
    percentage: float
    allocated_amount: float
    description: str
    priority: str
    tips: str


class BudgetBreakdown(BaseModel):
    """Complete deterministic budget allocation."""

    total_budget: float
    per_guest_cost: float
    currency: str = "USD"
    items: List[BudgetItem]
    contingency_fund: float


class TimelineScheduleItem(BaseModel):
    """Specific event-day scheduled activity."""

    time: str
    title: str
    description: str
    responsible: str


class MilestoneItem(BaseModel):
    """Pre-event countdown milestone."""

    timeframe: str
    days_before: int
    title: str
    action_items: List[str]


class EventTimeline(BaseModel):
    """Event day schedule and advance milestones."""

    day_schedule: List[TimelineScheduleItem]
    milestones: List[MilestoneItem]


class VendorCategory(BaseModel):
    """Recommended vendor category and search criteria."""

    category: str
    allocated_budget: float
    estimated_cost_range: str
    questions_to_ask: List[str]
    booking_lead_time_weeks: int
    key_deliverables: List[str]


class ChecklistTask(BaseModel):
    """Individual checklist item."""

    id: str
    phase: str
    task: str
    priority: str
    deadline_description: str
    completed: bool = False


class FullPlanResponse(BaseModel):
    """Aggregated deterministic plan output."""

    event_id: str
    event_name: str
    event_type: EventType
    guest_count: int
    total_budget: float
    event_date: date
    budget: BudgetBreakdown
    timeline: EventTimeline
    vendors: List[VendorCategory]
    checklist: List[ChecklistTask]


class CreativePromptRequest(BaseModel):
    """Request for AI-assisted creative suggestions."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: EventType
    event_name: str = Field(..., max_length=120)
    style_preference: str = Field(default="modern", max_length=50)
    topic: str = Field(default="themes", max_length=50)
    guest_count: int = Field(default=50, ge=1, le=10000)
    additional_context: Optional[str] = Field(default="", max_length=300)

    @field_validator("event_name", "topic", "additional_context")
    @classmethod
    def clean_text(cls, v: Optional[str]) -> str:
        """Sanitize text input safely."""
        return sanitize_raw_text(v or "", max_length=300)


class CreativeIdeaResponse(BaseModel):
    """Structured creative ideas from AI or deterministic fallback."""

    topic: str
    title: str
    ideas: List[str]
    decor_suggestions: List[str]
    signature_touch: str
    source: str = "ai"


class ChatMessage(BaseModel):
    """Single chat turn in conversation."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., max_length=1000)

    @field_validator("content")
    @classmethod
    def clean_content(cls, v: str) -> str:
        """Sanitize chat message text."""
        return sanitize_raw_text(v, max_length=1000)


class ChatRequest(BaseModel):
    """Chat refinement request payload."""

    messages: List[ChatMessage] = Field(..., max_length=20)
    current_plan: Optional[Dict] = None


class ChatResponse(BaseModel):
    """Assistant response with optional updated parameters."""

    reply: str
    plan_adjustments: Optional[Dict] = None
