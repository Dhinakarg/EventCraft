"""API integration tests covering valid plan, 422 errors, rate limit 429, headers, and secret leakage."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.security import clear_rate_limits

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
        "event_date": past_date, # past date fails validator
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
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


def test_rate_limit_returns_429() -> None:
    """Verify exceeding per-IP rate limit triggers HTTP 429."""
    clear_rate_limits()
    settings = get_settings()
    limit = settings.rate_limit_per_min

    # Fire requests up to the limit
    for _ in range(limit):
        res = client.post("/api/chat", json={"plan_context": "test", "question": "budget tip"})
        assert res.status_code == 200

    # Next request must return 429
    res_exceeded = client.post("/api/chat", json={"plan_context": "test", "question": "budget tip"})
    assert res_exceeded.status_code == 429
    assert "rate limit" in res_exceeded.json()["detail"].lower()
    clear_rate_limits()


def test_no_secrets_in_responses() -> None:
    """Verify responses never leak API keys, system tokens, or internal env vars."""
    clear_rate_limits()
    target_date = (date.today() + timedelta(days=150)).isoformat()
    response = client.post("/api/plan", json={
        "event_type": "birthday",
        "event_date": target_date,
        "guest_count": 30,
        "total_budget": 3000.0,
    })
    body_text = response.text
    header_text = str(response.headers)
    settings = get_settings()

    if settings.gemini_api_key:
        assert settings.gemini_api_key not in body_text
        assert settings.gemini_api_key not in header_text

    assert "api_key" not in body_text.lower() or "source" in body_text
    assert "password" not in body_text.lower()
    assert "traceback" not in body_text.lower()
