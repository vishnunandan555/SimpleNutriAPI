from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_foods():
    response = client.get("/api/v1/foods?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 10
    assert data["total"] >= 20

def test_filter_foods_category():
    response = client.get("/api/v1/foods?category=millets")
    assert response.status_code == 200
    data = response.json()
    assert all(item["category"] == "millets" for item in data["items"])

def test_get_food_detail():
    response = client.get("/api/v1/foods/ragi")
    assert response.status_code == 200
    food = response.json()
    assert "ragi" in food["id"]
    assert any("finger millet" in a.lower() for a in food["aliases"])
    assert food["nutrition"]["calcium_mg"] >= 300
    assert len(food["sources"]) >= 1

def test_search_foods():
    # Test search by name
    response = client.get("/api/v1/foods/search?q=spinach")
    assert response.status_code == 200
    results = response.json()
    assert any("spinach" in f["name"].lower() for f in results)

    # Test search by alias
    response_alias = client.get("/api/v1/foods/search?q=nachni")
    assert response_alias.status_code == 200
    results_alias = response_alias.json()
    assert any("ragi" in f["id"].lower() for f in results_alias)

def test_filter_foods_country():
    response = client.get("/api/v1/foods?country=IN&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert all("IN" in item["countries"] for item in data["items"])

def test_food_recommendations():
    payload = {
        "target_tags": ["calcium", "iron"],
        "diet": "vegetarian",
        "region": "india",
        "limit": 10
    }
    response = client.post("/api/v1/recommendations/foods", json=payload)
    assert response.status_code == 200
    ranked = response.json()
    assert len(ranked) >= 1
    assert "score" in ranked[0]
    assert "food" in ranked[0]
    assert ranked[0]["food"]["category"] is not None

def test_food_detail_not_found():
    response = client.get("/api/v1/foods/nonexistent_food_identifier_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_food_search_special_characters():
    # Wildcard search characters should be safely handled without SQL error
    response = client.get("/api/v1/foods/search?q=%")
    assert response.status_code == 200
    response_underscore = client.get("/api/v1/foods/search?q=_")
    assert response_underscore.status_code == 200

def test_food_pagination_out_of_bounds():
    response = client.get("/api/v1/foods?page=9999&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] > 0
    assert data["page"] == 9999
