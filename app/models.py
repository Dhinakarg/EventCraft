"""Pydantic v2 domain models for EventCraft AI planning requests and responses."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.sanitizer import sanitize_raw_text

VALID_PRIORITIES = {"venue", "food", "decor", "photography", "entertainment", "other"}


class EventType(str, Enum):
    """Supported event categories."""

    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"


class PriorityEnum(str, Enum):
    """Allowed planning priority categories."""

    VENUE = "venue"
    FOOD = "food"
    DECOR = "decor"
    PHOTOGRAPHY = "photography"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class EventRequest(BaseModel):
    """Validated user request payload for generating an event plan."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: EventType
    event_date: date
    guest_count: int = Field(..., ge=1, le=2000)
    total_budget: float = Field(..., gt=0.0)
    currency: str = Field(default="INR", max_length=10)
    city: str = Field(default="", max_length=100)
    vibe: str = Field(default="modern", max_length=80)
    dietary: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    notes: str | None = Field(default="", max_length=500)

    @field_validator("event_date")
    @classmethod
    def validate_future_date(cls, v: date) -> date:
        """Ensure the event date is set strictly in the future."""
        if v <= date.today():
            raise ValueError("event_date must be in the future")
        return v

    @field_validator("priorities")
    @classmethod
    def validate_priorities(cls, v: list[str]) -> list[str]:
        """Validate maximum 3 priorities from the allowed set."""
        if len(v) > 3:
            raise ValueError("priorities cannot exceed 3 items")
        cleaned = []
        for p in v:
            norm = p.strip().lower()
            if norm not in VALID_PRIORITIES:
                msg = f"Invalid priority '{p}'. Must be one of {sorted(VALID_PRIORITIES)}"
                raise ValueError(msg)
            if norm not in cleaned:
                cleaned.append(norm)
        return cleaned

    @field_validator("city", "vibe", "notes")
    @classmethod
    def sanitize_strings(cls, v: str | None) -> str:
        """Sanitize control chars and clamp length."""
        return sanitize_raw_text(v or "", max_length=500)


class BudgetItem(BaseModel):
    """Single item allocation in the deterministic budget."""

    category: str
    percentage: float
    allocated_amount: float
    description: str
    priority: str
    tips: str


class BudgetResponse(BaseModel):
    """Complete deterministic budget breakdown."""

    total_budget: float
    per_guest_cost: float
    currency: str
    contingency_fund: float
    contingency_percentage: float
    is_feasible: bool
    feasibility_notes: list[str]
    items: list[BudgetItem]


class TimelineTask(BaseModel):
    """Single scheduled task with backward-calculated due date."""

    id: str
    title: str
    phase: str
    due_date: date
    days_before_event: int
    priority: str
    is_critical: bool
    status: str = "todo"


class TimelineResponse(BaseModel):
    """Structured timeline response with tasks and rush warnings."""

    lead_time_days: int
    standard_lead_time_days: int
    is_compressed: bool
    tasks: list[TimelineTask]
    rush_warning: str | None = None


class VendorChecklistItem(BaseModel):
    """Vendor checklist per category with budget cap and booking deadline."""

    category: str
    budget_cap: float
    booking_deadline: date
    lead_time_days: int
    questions_to_ask: list[str]
    status: str = "todo"


class PlanResponse(BaseModel):
    """Unified master response containing budget, timeline, vendors, and warnings."""

    event_type: EventType
    event_date: date
    guest_count: int
    total_budget: float
    currency: str
    city: str
    vibe: str
    budget: BudgetResponse
    timeline: TimelineResponse
    vendors: list[VendorChecklistItem]
    warnings: list[str]
    ideas: object | None = None
