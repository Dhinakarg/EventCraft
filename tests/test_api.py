"""API integration tests using FastAPI TestClient."""

from datetime import date, timedelta

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
    """Test deterministic full plan generation endpoint with EventRequest."""
    target_date = (date.today() + timedelta(days=250)).isoformat()
    payload = {
        "event_type": "wedding",
        "event_date": target_date,
        "guest_count": 80,
        "total_budget": 25000.0,
        "currency": "USD",
        "city": "San Francisco",
        "vibe": "rustic chic",
        "dietary": ["vegetarian"],
        "priorities": ["venue", "food"],
        "notes": "Outdoor garden reception",
    }
    response = client.post("/api/plan/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "wedding"
    assert data["total_budget"] == 25000.0
    assert len(data["budget"]["items"]) > 0
    assert len(data["timeline"]["tasks"]) > 0
    assert len(data["vendors"]) > 0


def test_budget_recalculation_api() -> None:
    """Test budget-only endpoint."""
    target_date = (date.today() + timedelta(days=60)).isoformat()
    payload = {
        "event_type": "birthday",
        "event_date": target_date,
        "guest_count": 40,
        "total_budget": 4000.0,
        "currency": "USD",
        "vibe": "glow in the dark",
    }
    response = client.post("/api/plan/budget", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_budget"] == 4000.0
    assert data["per_guest_cost"] == 100.0
    assert data["is_feasible"] is True


def test_ai_ideas_api() -> None:
    """Test creative ideas generation endpoint."""
    payload = {
        "event_type": "birthday",
        "vibe": "space galaxy",
        "dietary": ["nut-free"],
        "guest_count": 25,
        "city": "Seattle",
    }
    response = client.post("/api/ai/ideas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["themes"]) == 3
    assert len(data["menu_ideas"]) >= 1
    assert "source" in data


def test_ai_chat_api() -> None:
    """Test chat refinement endpoint."""
    payload = {
        "plan_context": "Wedding for 100 guests in modern style with $20k budget",
        "question": "How can I reduce catering costs for 100 people?",
    }
    response = client.post("/api/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
