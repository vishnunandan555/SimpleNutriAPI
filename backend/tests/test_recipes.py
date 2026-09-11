from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_recipes():
    response = client.get("/api/v1/recipes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 5

def test_get_recipe_detail():
    response = client.get("/api/v1/recipes/ragi_dosa")
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["id"] == "ragi_dosa"
    assert len(recipe["ingredients"]) >= 2
    assert any("ragi" in ing["food_id"] for ing in recipe["ingredients"])

def test_recipe_ranking():
    # User has ragi, urad_dal, rice, and coconut_oil at home
    payload = {
        "available_food_ids": ["ragi", "urad_dal", "rice", "coconut_oil"],
        "target_tags": ["calcium", "iron"]
    }
    response = client.post("/api/v1/recommendations/recipes", json=payload)
    assert response.status_code == 200
    ranked = response.json()
    assert len(ranked) >= 1
    # ragi_dosa should have 100% kitchen match
    top_recipe = ranked[0]
    assert top_recipe["recipe"]["id"] == "ragi_dosa"
    assert top_recipe["match_percentage"] == 100.0

def test_shopping_list():
    # User selects ragi_dosa but only has ragi and rice
    payload = {
        "selected_recipe_ids": ["ragi_dosa"],
        "kitchen_inventory_food_ids": ["ragi", "rice"]
    }
    response = client.post("/api/v1/recommendations/shopping-list", json=payload)
    assert response.status_code == 200
    data = response.json()
    missing_ids = [item["food_id"] for item in data["items"]]
    assert any("black_gram" in fid or "b003" in fid for fid in missing_ids)
    assert any("coconut_oil" in fid or "t001" in fid for fid in missing_ids)
    assert not any("ragi" in fid or "a010" in fid for fid in missing_ids)

def test_filter_recipes_by_ingredient():
    response = client.get("/api/v1/recipes?ingredient=ragi")
    assert response.status_code == 200
    data = response.json()
    assert any(r["id"] == "ragi_dosa" for r in data["items"])

def test_filter_recipes_by_cuisine():
    response = client.get("/api/v1/recipes?cuisine=south_indian")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(r["cuisine"] == "south_indian" for r in data["items"])

def test_recipe_not_found():
    response = client.get("/api/v1/recipes/nonexistent_recipe_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_empty_pantry_recipe_ranking():
    payload = {
        "available_food_ids": [],
        "target_tags": ["iron"]
    }
    response = client.post("/api/v1/recommendations/recipes", json=payload)
    assert response.status_code == 200
    ranked = response.json()
    assert len(ranked) >= 1
    # With no pantry ingredients, match percentage is 0%
    assert all(r["match_percentage"] == 0.0 for r in ranked)
    assert all(len(r["missing_ingredients"]) > 0 for r in ranked)

def test_empty_shopping_list():
    payload = {
        "selected_recipe_ids": [],
        "kitchen_inventory_food_ids": ["ragi"]
    }
    response = client.post("/api/v1/recommendations/shopping-list", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_recipe_count"] == 0
    assert data["total_missing_items"] == 0
    assert data["items"] == []

def test_search_recipes_special_characters():
    response = client.get("/api/v1/recipes/search?q=%")
    assert response.status_code == 200
    response_underscore = client.get("/api/v1/recipes/search?q=_")
    assert response_underscore.status_code == 200
