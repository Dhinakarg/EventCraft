"""Main FastAPI application entrypoint for EventCraft AI."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes.ai_ideas import router as ai_ideas_router
from app.routes.chat import router as chat_router
from app.routes.planner import router as planner_router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Deterministic planning engine with GenAI creative assistance",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(planner_router)
    app.include_router(ai_ideas_router)
    app.include_router(chat_router)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/health")
    def health_check() -> dict:
        """Return operational health status."""
        return {
            "status": "healthy",
            "service": "eventcraft-ai",
            "model": settings.gemini_model,
        }

    @app.get("/")
    def serve_index() -> FileResponse:
        """Serve primary single page application shell."""
        index_file = STATIC_DIR / "index.html"
        return FileResponse(str(index_file))

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    cfg = get_settings()
    uvicorn.run("app.main:app", host=cfg.host, port=cfg.port, reload=True)
