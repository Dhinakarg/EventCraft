"""Security middleware, per-IP rate limiting, and exception sanitizers."""

import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import get_settings
from app.engine.profiles import RATE_LIMIT_WINDOW_SECONDS


class RateLimiter:
    """Per-IP sliding window rate limiter."""

    def __init__(
        self,
        limit_per_minute: int = 60,
        window_seconds: float = RATE_LIMIT_WINDOW_SECONDS,
    ) -> None:
        """Initialize RateLimiter with default limit and window duration."""
        self.limit_per_minute = limit_per_minute
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = {}

    def check(self, client_ip: str, limit_per_minute: int | None = None) -> bool:
        """Return True if request is within limit, False if exceeded."""
        limit = limit_per_minute if limit_per_minute is not None else self.limit_per_minute
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self._store.get(client_ip, [])
        active = [ts for ts in timestamps if ts > window_start]
        if len(active) >= limit:
            self._store[client_ip] = active
            return False

        active.append(now)
        self._store[client_ip] = active
        return True

    def reset(self) -> None:
        """Reset internal rate limit tracking."""
        self._store.clear()


def get_rate_limiter(request: Request) -> RateLimiter:
    """FastAPI dependency injecting the RateLimiter stored on app.state."""
    limiter: RateLimiter | None = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        limiter = RateLimiter()
        request.app.state.rate_limiter = limiter
    return limiter


class SecurityHeadersMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Add essential security headers and enforce per-IP rate limits."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process incoming request, apply rate limiting, and inject security headers."""
        settings = get_settings()
        rate_limiter: RateLimiter = getattr(request.app.state, "rate_limiter", None) or RateLimiter(
            settings.rate_limit_per_min
        )
        client_ip = request.client.host if request.client else "unknown"

        # Apply rate limiting to API routes
        if request.url.path.startswith("/api/") and not rate_limiter.check(client_ip, settings.rate_limit_per_min):
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
