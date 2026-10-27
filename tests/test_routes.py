"""Integration and unit tests for FastAPI routers in app.api."""

from datetime import date, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_route_health() -> None:
    """GET /health must return status healthy."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_route_security_headers_present() -> None:
    """Security headers must be attached to API responses."""
    resp = client.get("/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert "strict-origin" in resp.headers.get("referrer-policy", "")


def test_route_plan_success() -> None:
    """POST /api/plan with valid payload should return complete plan."""
    target_date = (date.today() + timedelta(days=45)).isoformat()
    payload = {
        "event_type": "birthday",
        "event_date": target_date,
        "guest_count": 25,
        "total_budget": 40000,
        "currency": "INR",
        "city": "Chennai",
        "vibe": "Tropical Glow",
    }
    with patch("app.ai.gemini_client._get_client", return_value=None):
        resp = client.post("/api/plan", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["event_type"] == "birthday"
    assert data["budget"]["total_budget"] == 40000
    assert len(data["timeline"]["tasks"]) > 0


def test_route_plan_validation_error() -> None:
    """POST /api/plan with invalid payload should return HTTP 422 Unprocessable Entity."""
    payload = {
        "event_type": "wedding",
        "event_date": "not-a-date",
        "guest_count": -5,
        "total_budget": -100,
    }
    resp = client.post("/api/plan", json=payload)
    assert resp.status_code == 422


def test_route_chat_response() -> None:
    """POST /api/chat with question should return assistant reply."""
    payload = {
        "question": "How should I allocate budget for food?",
        "plan_context": "Wedding with 100 guests and 500000 budget in Bengaluru",
    }
    with patch("app.ai.gemini_client._get_client", return_value=None):
        resp = client.post("/api/chat", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["source"] in ("ai", "fallback")


def test_route_chat_sanitizes_html_tags() -> None:
    """POST /api/chat should sanitize any script or HTML injection in the prompt."""
    payload = {
        "question": "<script>alert('xss')</script>Where can I save on venue costs?",
        "plan_context": "Corporate event",
    }
    with patch("app.ai.gemini_client._get_client", return_value=None):
        resp = client.post("/api/chat", json=payload)

    assert resp.status_code == 200
    assert "<script>" not in resp.json()["reply"]


def test_route_export_ics_success() -> None:
    """GET /api/export/ics should return calendar file attachment."""
    event_date = (date.today() + timedelta(days=30)).isoformat()
    resp = client.get(
        "/api/export/ics",
        params={
            "event_type": "wedding",
            "event_date": event_date,
            "guest_count": 50,
            "total_budget": 200000,
            "vibe": "Rustic",
        },
    )
    assert resp.status_code == 200
    assert "text/calendar" in resp.headers.get("content-type", "")
    assert "BEGIN:VCALENDAR" in resp.text
    assert "BEGIN:VEVENT" in resp.text
    assert "END:VCALENDAR" in resp.text


def test_route_export_ics_invalid_date() -> None:
    """GET /api/export/ics with malformed date should return 422 Unprocessable Entity."""
    resp = client.get(
        "/api/export/ics",
        params={
            "event_type": "wedding",
            "event_date": "invalid-date-format",
        },
    )
    assert resp.status_code == 422
