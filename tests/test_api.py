"""API integration tests using FastAPI TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test health check status endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "eventcraft-ai"


def test_generate_plan_api() -> None:
    """Test deterministic full plan generation endpoint."""
    payload = {
        "event_type": "wedding",
        "event_name": "Sophia & Liam Wedding",
        "guest_count": 80,
        "budget_total": 25000.0,
        "event_date": "2027-08-15",
        "start_time": "15:30",
        "duration_hours": 6.0,
        "style_preference": "rustic chic",
    }
    response = client.post("/api/plan/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["event_name"] == "Sophia & Liam Wedding"
    assert data["budget"]["total_budget"] == 25000.0
    assert len(data["budget"]["items"]) > 0
    assert len(data["timeline"]["day_schedule"]) > 0
    assert len(data["vendors"]) > 0
    assert len(data["checklist"]) > 0


def test_budget_recalculation_api() -> None:
    """Test budget-only endpoint."""
    payload = {
        "event_type": "birthday",
        "event_name": "Marcus 30th Birthday",
        "guest_count": 40,
        "budget_total": 4000.0,
        "event_date": "2026-11-20",
    }
    response = client.post("/api/plan/budget", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_budget"] == 4000.0
    assert data["per_guest_cost"] == 100.0


def test_ai_ideas_api() -> None:
    """Test creative ideas generation endpoint."""
    payload = {
        "event_type": "birthday",
        "event_name": "Maya's 10th Birthday",
        "style_preference": "space galaxy",
        "topic": "themes",
        "guest_count": 25,
    }
    response = client.post("/api/ai/ideas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["ideas"]) >= 3
    assert len(data["decor_suggestions"]) >= 2
    assert "signature_touch" in data


def test_ai_chat_api() -> None:
    """Test chat refinement endpoint."""
    payload = {
        "messages": [
            {"role": "user", "content": "How can I reduce catering costs for 100 people?"}
        ],
        "current_plan": {"event_name": "Community Fair"},
    }
    response = client.post("/api/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
