"""Main FastAPI application wiring routes, security middleware, and static assets."""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.ai.gemini_client import generate_event_ideas, refine_plan_chat
from app.ai.schemas import ChatRefineRequest, ChatRefineResponse, IdeasRequest
from app.config import get_settings
from app.engine.budget import allocate_event_budget
from app.engine.ics import generate_ics_calendar
from app.engine.timeline import create_backward_timeline
from app.engine.vendors import build_vendor_checklist
from app.models import EventRequest, EventType, PlanResponse
from app.security import SecurityHeadersMiddleware, generic_exception_handler

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def _build_warnings(budget_feasible: bool, b_notes: list[str], rush_warn: str | None) -> list[str]:
    """Compile budget and timeline warnings into a unified list."""
    warns: list[str] = []
    if not budget_feasible:
        warns.extend(b_notes)
    if rush_warn:
        warns.append(rush_warn)
    return warns


def health_endpoint() -> dict:
    """Return operational health status."""
    settings = get_settings()
    return {"status": "healthy", "service": "eventcraft-ai", "model": settings.gemini_model}


def create_event_plan(req: EventRequest) -> PlanResponse:
    """Generate master plan combining pure deterministic engines and GenAI ideas."""
    budget = allocate_event_budget(req)
    timeline = create_backward_timeline(req)
    vendors = build_vendor_checklist(req, budget)
    warnings = _build_warnings(budget.is_feasible, budget.feasibility_notes, timeline.rush_warning)

    ideas_req = IdeasRequest(
        event_type=req.event_type.value,
        vibe=req.vibe,
        dietary=req.dietary,
        guest_count=req.guest_count,
        city=req.city,
        notes=req.notes or "",
    )
    ideas = generate_event_ideas(ideas_req)

    return PlanResponse(
        event_type=req.event_type,
        event_date=req.event_date,
        guest_count=req.guest_count,
        total_budget=req.total_budget,
        currency=req.currency,
        city=req.city,
        vibe=req.vibe,
        budget=budget,
        timeline=timeline,
        vendors=vendors,
        warnings=warnings,
        ideas=ideas,
    )


def chat_endpoint(req: ChatRefineRequest) -> ChatRefineResponse:
    """Conversational plan refinement constrained to event planning."""
    return refine_plan_chat(req.plan_context, req.question)


def export_timeline_ics(
    event_date: date = Query(...),
    event_type: EventType = Query(default=EventType.WEDDING),
    guest_count: int = Query(default=100, ge=1, le=2000),
    total_budget: float = Query(default=10000.0, gt=0),
    vibe: str = Query(default="Modern"),
) -> Response:
    """Export backward-scheduled event timeline as an iCalendar (.ics) file."""
    req = EventRequest(
        event_type=event_type,
        event_date=event_date,
        guest_count=guest_count,
        total_budget=total_budget,
        vibe=vibe,
    )
    timeline = create_backward_timeline(req)
    ics_text = generate_ics_calendar(timeline.tasks, f"{vibe} {event_type.value}")
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="event_timeline.ics"'},
    )


def serve_index() -> FileResponse:
    """Serve primary single page application shell."""
    return FileResponse(str(STATIC_DIR / "index.html"))


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(Exception, generic_exception_handler)

    app.add_api_route("/health", health_endpoint, methods=["GET"])
    app.add_api_route("/api/plan", create_event_plan, methods=["POST"], response_model=PlanResponse)
    app.add_api_route("/api/chat", chat_endpoint, methods=["POST"], response_model=ChatRefineResponse)
    app.add_api_route("/api/export/ics", export_timeline_ics, methods=["GET"])
    app.add_api_route("/", serve_index, methods=["GET"])

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("app.main:app", host=cfg.host, port=cfg.port, reload=True)
