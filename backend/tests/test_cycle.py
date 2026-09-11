from datetime import date, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_cycle_phases():
    response = client.get("/api/v1/cycle/phases")
    assert response.status_code == 200
    phases = response.json()
    assert len(phases) == 4
    phase_ids = [p["id"] for p in phases]
    assert "menstrual" in phase_ids
    assert "follicular" in phase_ids
    assert "ovulatory" in phase_ids
    assert "luteal" in phase_ids

def test_estimate_cycle_phase():
    two_days_ago = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "last_period_start": two_days_ago,
        "cycle_length_days": 28
    }
    response = client.post("/api/v1/cycle/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["phase_id"] == "menstrual"
    assert data["estimated_cycle_day"] == 2
    assert any(n["nutrient_id"] == "iron_mg" for n in data["priority_nutrients"])

def test_estimate_cycle_invalid_date():
    payload = {
        "last_period_start": "not-a-date",
        "cycle_length_days": 28
    }
    response = client.post("/api/v1/cycle/estimate", json=payload)
    assert response.status_code == 400
    assert "Date format must be YYYY-MM-DD" in response.json()["detail"]

def test_estimate_cycle_invalid_length():
    two_days_ago = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "last_period_start": two_days_ago,
        "cycle_length_days": 10  # Out of range (20-45 days), caught by Pydantic
    }
    response = client.post("/api/v1/cycle/estimate", json=payload)
    assert response.status_code == 422
