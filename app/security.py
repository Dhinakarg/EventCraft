"""Security middleware, per-IP rate limiting, and exception sanitizers."""

import time

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
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


MAX_REQUEST_BODY_SIZE: int = 1_048_576  # 1 MB


def check_request_body_size(request: Request, max_size: int = MAX_REQUEST_BODY_SIZE) -> JSONResponse | None:
    """Validate request Content-Length header against maximum allowed payload size."""
    raw_length = request.headers.get("content-length")
    if not raw_length:
        return None
    try:
        length = int(raw_length)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid Content-Length header."},
        )
    if length > max_size:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request payload exceeds maximum allowed size ({max_size} bytes)."},
        )
    return None


def _is_rate_limited(request: Request, limiter: RateLimiter, limit: int) -> bool:
    """Return True if an API request exceeds the rate limit for the client host."""
    if not request.url.path.startswith("/api/"):
        return False
    client_ip = request.client.host if request.client else "unknown"
    return not limiter.check(client_ip, limit)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Add essential security headers and enforce per-IP rate limits."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process incoming request, apply rate limiting, and inject security headers."""
        size_error = check_request_body_size(request)
        if size_error is not None:
            return size_error

        settings = get_settings()
        limiter: RateLimiter | None = getattr(request.app.state, "rate_limiter", None)
        active_limiter = limiter if limiter is not None else RateLimiter(settings.rate_limit_per_min)

        if _is_rate_limited(request, active_limiter, settings.rate_limit_per_min):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        csp = (
            "default-src 'self' https: data: 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com; "
            "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'"
        )
        response.headers["Content-Security-Policy"] = csp
        return response


_404_HTML_TEMPLATE: str = (
    "<!DOCTYPE html>"
    '<html lang="en">'
    "<head>"
    '  <meta charset="utf-8">'
    '  <meta name="viewport" content="width=device-width, initial-scale=1">'
    "  <title>404 - Page Not Found | EventCraft AI</title>"
    "  <style>"
    "    body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; "
    "      display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }"
    "    .error-card { text-align: center; max-width: 480px; padding: 2.5rem; background: #1e293b; "
    "      border-radius: 1rem; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }"
    "    h1 { font-size: 3rem; margin: 0 0 0.5rem; color: #f43f5e; }"
    "    h2 { font-size: 1.5rem; margin: 0 0 1rem; font-weight: 600; }"
    "    p { color: #94a3b8; margin: 0 0 1.5rem; line-height: 1.5; }"
    "    a { display: inline-block; background: #4f46e5; color: #fff; text-decoration: none; "
    "      padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 500; transition: background 0.2s; }"
    "    a:hover { background: #4338ca; }"
    "  </style>"
    "</head>"
    "<body>"
    '  <div class="error-card">'
    "    <h1>404</h1>"
    "    <h2>Page Not Found</h2>"
    "    <p>The requested page was not found on this server.</p>"
    '    <a href="/">Return to EventCraft AI</a>'
    "  </div>"
    "</body>"
    "</html>"
)


async def not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle 404 Not Found errors with structured JSON or accessible HTML error page."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept and not request.url.path.startswith("/api/"):
        return HTMLResponse(content=_404_HTML_TEMPLATE, status_code=404)

    detail = getattr(exc, "detail", "Not Found")
    detail_str = detail if isinstance(detail, str) else "Not Found"
    return JSONResponse(
        status_code=404,
        content={
            "detail": detail_str,
            "status_code": 404,
            "error": "Not Found",
            "message": f"Resource not found: {request.url.path}",
        },
    )


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle Starlette and FastAPI HTTP exceptions with appropriate status and error state."""
    status_code = getattr(exc, "status_code", 500)
    if status_code == 404:
        return await not_found_handler(request, exc)
    detail = getattr(exc, "detail", "An error occurred.")
    detail_str = detail if isinstance(detail, str) else str(detail)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "status_code": status_code,
            "error": detail_str,
            "message": f"HTTP {status_code}: {detail_str}",
        },
    )


async def validation_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle 422 RequestValidationError with structured error state."""
    raw_errors = getattr(exc, "errors", None)
    errors = raw_errors() if callable(raw_errors) else []
    safe_errors = jsonable_encoder(errors)
    return JSONResponse(
        status_code=422,
        content={
            "detail": safe_errors,
            "status_code": 422,
            "error": "Unprocessable Entity",
            "message": "Input validation failed. Please check the submitted fields.",
        },
    )


async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and mask internal traces in responses."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "status_code": 500,
            "error": "Internal Server Error",
            "message": "An internal server error occurred. Please try again later.",
        },
    )
