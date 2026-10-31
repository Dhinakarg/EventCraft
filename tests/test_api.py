"""API integration tests covering valid plan, 422 errors, rate limit 429, headers, and secret leakage."""

import asyncio
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from app.config import get_settings
from app.main import app, create_app
from app.security import (
    RateLimiter,
    generic_exception_handler,
    http_exception_handler,
    not_found_handler,
    validation_exception_handler,
)

client = TestClient(app)


def test_health_check() -> None:
    """Test health check status endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "eventcraft-ai"


def test_valid_plan_endpoint() -> None:
    """Verify POST /api/plan generates both deterministic plan and AI ideas."""
    target_date = (date.today() + timedelta(days=200)).isoformat()
    payload = {
        "event_type": "wedding",
        "event_date": target_date,
        "guest_count": 80,
        "total_budget": 25000.0,
        "vibe": "rustic chic",
        "city": "Napa",
        "priorities": ["venue", "food"],
    }
    with patch("app.ai.gemini_client._get_client", return_value=None):
        response = client.post("/api/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "wedding"
    assert data["total_budget"] == 25000.0
    assert len(data["budget"]["items"]) > 0
    assert len(data["timeline"]["tasks"]) > 0
    assert len(data["vendors"]) > 0
    assert data["ideas"] is not None
    assert len(data["ideas"]["themes"]) == 3


def test_plan_invalid_input_returns_422() -> None:
    """Verify POST /api/plan returns 422 for past date and invalid budget."""
    past_date = (date.today() - timedelta(days=5)).isoformat()
    bad_payload = {
        "event_type": "wedding",
        "event_date": past_date,  # past date fails validator
        "guest_count": 50,
        "total_budget": -500.0,  # negative budget fails gt=0
    }
    response = client.post("/api/plan", json=bad_payload)
    assert response.status_code == 422


def test_export_ics_calendar() -> None:
    """Verify GET /api/export/ics returns valid iCalendar payload."""
    target_date = (date.today() + timedelta(days=120)).isoformat()
    url = f"/api/export/ics?event_date={target_date}&event_type=wedding&guest_count=75&total_budget=18000&vibe=Modern"
    response = client.get(url)
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "")
    assert "BEGIN:VCALENDAR" in response.text
    assert "END:VCALENDAR" in response.text


def test_security_headers_present() -> None:
    """Verify mandatory security headers are present in responses."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("Permissions-Policy") == "geolocation=(), camera=(), microphone=()"
    assert response.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


def test_rate_limit_returns_429() -> None:
    """Verify exceeding per-IP rate limit triggers HTTP 429."""
    fresh_app = create_app()
    fresh_app.state.rate_limiter = RateLimiter(limit_per_minute=5)
    test_client = TestClient(fresh_app)

    with patch("app.security.get_settings") as mock_settings:
        mock_settings.return_value.rate_limit_per_min = 5
        # Fire requests up to the limit
        for _ in range(5):
            res = test_client.post("/api/chat", json={"plan_context": "test", "question": "budget tip"})
            assert res.status_code == 200

        # Next request must return 429
        res_exceeded = test_client.post("/api/chat", json={"plan_context": "test", "question": "budget tip"})
        assert res_exceeded.status_code == 429
        assert "rate limit" in res_exceeded.json()["detail"].lower()


def test_no_secrets_in_responses() -> None:
    """Verify responses never leak API keys, system tokens, or internal env vars."""
    target_date = (date.today() + timedelta(days=150)).isoformat()
    with patch("app.ai.gemini_client._get_client", return_value=None):
        response = client.post(
            "/api/plan",
            json={
                "event_type": "birthday",
                "event_date": target_date,
                "guest_count": 30,
                "total_budget": 3000.0,
            },
        )
    body_text = response.text
    header_text = str(response.headers)
    settings = get_settings()

    if settings.gemini_api_key:
        assert settings.gemini_api_key not in body_text
        assert settings.gemini_api_key not in header_text

    assert "api_key" not in body_text.lower() or "source" in body_text
    assert "password" not in body_text.lower()
    assert "traceback" not in body_text.lower()


def _mock_empty_settings() -> object:
    return type("Settings", (), {"gemini_api_key": ""})()


def test_full_plan_request_to_plan_flow_with_fallback_ideas(monkeypatch: pytest.MonkeyPatch) -> None:
    """Integration test of end-to-end request->plan flow with fallback ideas."""
    monkeypatch.setattr(
        "app.ai.gemini_client.get_settings",
        _mock_empty_settings,
    )
    target_date = (date.today() + timedelta(days=180)).isoformat()
    payload = {
        "event_type": "community",
        "event_date": target_date,
        "guest_count": 250,
        "total_budget": 12000.0,
        "currency": "USD",
        "city": "Austin",
        "vibe": "Eco-friendly Festival",
        "dietary": ["Vegan", "Nut-Free"],
        "priorities": ["venue", "entertainment"],
        "notes": "Include local musicians and compostable tableware.",
    }
    response = client.post("/api/plan", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["ideas"]["source"] == "fallback"
    assert len(data["ideas"]["themes"]) == 3
    assert len(data["ideas"]["menu_ideas"]) > 0
    assert len(data["ideas"]["activities"]) > 0
    assert data["budget"]["total_budget"] == 12000.0
    allocated_sum = sum(item["allocated_amount"] for item in data["budget"]["items"])
    assert round(allocated_sum, 2) == 12000.0
    assert len(data["timeline"]["tasks"]) > 0
    assert len(data["vendors"]) > 0
    assert all(v["status"] == "todo" for v in data["vendors"])


def test_generic_exception_handler_masking() -> None:
    """Verify generic exception handler masks internal details and returns 500 JSON."""
    scope = {"type": "http", "method": "GET", "path": "/"}
    req = Request(scope)
    res = asyncio.run(generic_exception_handler(req, RuntimeError("Sensitive internal database error")))
    assert res.status_code == 500
    assert b"Sensitive" not in res.body
    assert b"internal server error" in res.body


def test_request_body_size_limit_exceeded() -> None:
    """Verify requests with Content-Length exceeding 1MB are rejected with HTTP 413."""
    headers = {"Content-Length": "2000000", "Content-Type": "application/json"}
    response = client.post("/api/chat", content=b"{}", headers=headers)
    assert response.status_code == 413
    assert "maximum allowed size" in response.json()["detail"].lower()


def test_invalid_content_length_returns_400() -> None:
    """Verify malformed Content-Length header is rejected with HTTP 400."""
    headers = {"Content-Length": "not-a-number", "Content-Type": "application/json"}
    response = client.post("/api/chat", content=b"{}", headers=headers)
    assert response.status_code == 400
    assert "invalid content-length" in response.json()["detail"].lower()


def test_rate_limiter_uses_non_spoofable_client_host() -> None:
    """Verify rate limiter relies on request.client.host and ignores spoofed X-Forwarded-For."""
    fresh_app = create_app()
    fresh_app.state.rate_limiter = RateLimiter(limit_per_minute=2)
    test_client = TestClient(fresh_app)

    with patch("app.security.get_settings") as mock_settings:
        mock_settings.return_value.rate_limit_per_min = 2
        # Send 2 requests with spoofed X-Forwarded-For headers
        res1 = test_client.post(
            "/api/chat",
            json={"plan_context": "test", "question": "q1"},
            headers={"X-Forwarded-For": "1.2.3.4"},
        )
        assert res1.status_code == 200

        res2 = test_client.post(
            "/api/chat",
            json={"plan_context": "test", "question": "q2"},
            headers={"X-Forwarded-For": "5.6.7.8"},
        )
        assert res2.status_code == 200

        # Third request from same test_client (same client.host = testclient) must be blocked
        res3 = test_client.post(
            "/api/chat",
            json={"plan_context": "test", "question": "q3"},
            headers={"X-Forwarded-For": "9.10.11.12"},
        )
        assert res3.status_code == 429


def test_openapi_schema_metadata_complete() -> None:
    """Verify all routes have summary, description, and response_description in OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})

    for endpoint in ["/api/plan", "/api/chat"]:
        op = paths[endpoint]["post"]
        assert op.get("summary")
        assert op.get("description")
        assert op["responses"]["200"].get("description")

    ics_op = paths["/api/export/ics"]["get"]
    assert ics_op.get("summary")
    assert ics_op.get("description")
    assert ics_op["responses"]["200"].get("description")

    health_op = paths["/health"]["get"]
    assert health_op.get("summary")
    assert health_op.get("description")
    assert health_op["responses"]["200"].get("description")


def test_direct_not_found_handler_json_and_html() -> None:
    """Verify not_found_handler generates appropriate JSON and HTML payloads."""
    json_scope = {"type": "http", "method": "GET", "path": "/cart", "headers": []}
    req_json = Request(json_scope)
    res_json = asyncio.run(not_found_handler(req_json, RuntimeError("Not found")))
    assert res_json.status_code == 404
    assert b"Resource not found: /cart" in res_json.body

    html_scope = {
        "type": "http",
        "method": "GET",
        "path": "/cart",
        "headers": [(b"accept", b"text/html,application/xhtml+xml")],
    }
    req_html = Request(html_scope)
    res_html = asyncio.run(not_found_handler(req_html, RuntimeError("Not found")))
    assert res_html.status_code == 404
    assert b"404" in res_html.body
    assert b"Page Not Found" in res_html.body


def test_direct_http_exception_handler_codes() -> None:
    """Verify http_exception_handler delegates 404 and formats generic HTTP codes."""
    scope = {"type": "http", "method": "GET", "path": "/test", "headers": []}
    req = Request(scope)

    res_404 = asyncio.run(http_exception_handler(req, StarletteHTTPException(status_code=404, detail="Missing")))
    assert res_404.status_code == 404

    res_403 = asyncio.run(http_exception_handler(req, StarletteHTTPException(status_code=403, detail="Forbidden")))
    assert res_403.status_code == 403
    assert b"Forbidden" in res_403.body


def test_direct_validation_exception_handler() -> None:
    """Verify validation_exception_handler returns 422 JSON with structured details."""
    scope = {"type": "http", "method": "POST", "path": "/api/plan", "headers": []}
    req = Request(scope)

    class MockValidationError:
        """Mock RequestValidationError for handler testing."""

        def errors(self) -> list[dict[str, str]]:
            """Return mock validation error list."""
            return [{"loc": "guest_count", "msg": "Input should be greater than 0"}]

    res_422 = asyncio.run(validation_exception_handler(req, MockValidationError()))  # type: ignore[arg-type]
    assert res_422.status_code == 422
    assert b"Unprocessable Entity" in res_422.body
    assert b"guest_count" in res_422.body
