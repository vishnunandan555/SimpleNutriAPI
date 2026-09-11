from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_nutrients():
    response = client.get("/api/v1/nutrients")
    assert response.status_code == 200
    nutrients = response.json()
    assert len(nutrients) >= 15
    nutrient_ids = [n["id"] for n in nutrients]
    assert "iron_mg" in nutrient_ids
    assert "calcium_mg" in nutrient_ids
    assert "protein_g" in nutrient_ids

def test_get_top_foods_for_iron():
    response = client.get("/api/v1/nutrients/iron_mg/top-foods?limit=5")
    assert response.status_code == 200
    top_foods = response.json()
    assert len(top_foods) == 5
    # First item should have high iron
    assert top_foods[0]["amount"] > 5.0
    assert top_foods[0]["unit"] == "mg"

def test_get_top_foods_for_calcium():
    response = client.get("/api/v1/nutrients/calcium_mg/top-foods?limit=5")
    assert response.status_code == 200
    top_foods = response.json()
    assert len(top_foods) == 5
    assert top_foods[0]["amount"] > 100.0

def test_get_food_nutrients():
    response = client.get("/api/v1/foods/a010_ragi/nutrients")
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) >= 10
    n_map = {e["nutrient_id"]: e["amount"] for e in entries}
    assert n_map["calcium_mg"] >= 300.0

def test_nutrient_not_found():
    response = client.get("/api/v1/nutrients/nonexistent_nutrient_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_food_nutrients_food_not_found():
    response = client.get("/api/v1/foods/nonexistent_food_xyz/nutrients")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
