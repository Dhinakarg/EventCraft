"""Security middleware, per-IP rate limiting, and exception sanitizers."""

import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import get_settings
from app.engine.profiles import RATE_LIMIT_WINDOW_SECONDS

# In-memory IP tracking: ip -> list of timestamps
_RATE_LIMIT_STORE: dict[str, list[float]] = {}


def check_rate_limit(client_ip: str, limit_per_minute: int) -> bool:
    """Return True if request is within limit, False if exceeded."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = _RATE_LIMIT_STORE.get(client_ip, [])
    active = [ts for ts in timestamps if ts > window_start]
    if len(active) >= limit_per_minute:
        _RATE_LIMIT_STORE[client_ip] = active
        return False

    active.append(now)
    _RATE_LIMIT_STORE[client_ip] = active
    return True


def clear_rate_limits() -> None:
    """Clear in-memory rate limit tracking for testing."""
    _RATE_LIMIT_STORE.clear()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Add essential security headers and enforce per-IP rate limits."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process incoming request, apply rate limiting, and inject security headers."""
        settings = get_settings()
        client_ip = request.client.host if request.client else "unknown"

        # Apply rate limiting to API routes
        if request.url.path.startswith("/api/") and not check_rate_limit(client_ip, settings.rate_limit_per_min):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        csp = (
            "default-src 'self' https: data: 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com; "
            "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'"
        )
        response.headers["Content-Security-Policy"] = csp
        return response


async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and mask internal traces in responses."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )
