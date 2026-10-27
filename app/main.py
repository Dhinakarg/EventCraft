"""Main FastAPI application wiring routes, security middleware, and static assets."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.api.routes_chat import chat_endpoint
from app.api.routes_chat import router as chat_router
from app.api.routes_export import export_timeline_ics
from app.api.routes_export import router as export_router
from app.api.routes_plan import plan_endpoint as create_event_plan
from app.api.routes_plan import router as plan_router
from app.config import get_settings
from app.security import SecurityHeadersMiddleware, generic_exception_handler
from app.services.plan_service import _build_warnings

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

__all__ = [
    "HealthResponse",
    "_build_warnings",
    "app",
    "chat_endpoint",
    "create_app",
    "create_event_plan",
    "export_timeline_ics",
    "health_endpoint",
    "serve_index",
]


class HealthResponse(BaseModel):
    """Operational health status model."""

    status: str
    service: str
    model: str


def health_endpoint() -> HealthResponse:
    """Return operational health status."""
    settings = get_settings()
    return HealthResponse(status="healthy", service="eventcraft-ai", model=settings.gemini_model)


def serve_index() -> FileResponse:
    """Serve primary single page application shell."""
    return FileResponse(str(STATIC_DIR / "index.html"))


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="1.0.0")

    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(Exception, generic_exception_handler)

    # Core health & index endpoints
    application.add_api_route("/health", health_endpoint, methods=["GET"])
    application.add_api_route("/", serve_index, methods=["GET"])

    # Mount modular routers
    application.include_router(plan_router)
    application.include_router(chat_router)
    application.include_router(export_router)

    if STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return application


app = create_app()

if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("app.main:app", host=cfg.host, port=cfg.port, reload=True)
