from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_ingredients():
    response = client.get("/api/v1/ingredients?page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 500

def test_autocomplete_ingredients():
    # Search for ragi
    response = client.get("/api/v1/ingredients/autocomplete?q=ragi")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("ragi" in item["id"] or "ragi" in item["name"].lower() for item in results)

    # Search for spinach / palak
    response_spinach = client.get("/api/v1/ingredients/autocomplete?q=spinach")
    assert response_spinach.status_code == 200
    results_spinach = response_spinach.json()
    assert any("spinach" in item["name"].lower() for item in results_spinach)

def test_get_ingredient_detail():
    response = client.get("/api/v1/ingredients/ragi")
    assert response.status_code == 200
    item = response.json()
    assert "ragi" in item["id"]
    assert "millets" in item["category"]

def test_ingredient_not_found():
    response = client.get("/api/v1/ingredients/nonexistent_ingredient_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
