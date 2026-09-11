from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.recipe import RecipeSummary, RecipeDetail
from backend.app.services.recipe_service import RecipeService

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])

@router.get("", response_model=PaginatedResponse[RecipeSummary], summary="List and Filter Recipes")
def list_recipes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    region: Optional[str] = Query(None, description="Region filter (e.g. india, global)"),
    country: Optional[str] = Query(None, description="Country filter (e.g. IN, US)"),
    cuisine: Optional[str] = Query(None, description="Cuisine filter (e.g. south_indian, kerala, north_indian)"),
    diet: Optional[str] = Query(None, description="Diet filter (e.g. vegetarian, vegan, gluten_free)"),
    tag: Optional[str] = Query(None, description="Nutritional or phase tag (e.g. iron, calcium, luteal_phase)"),
    ingredient: Optional[str] = Query(None, description="Canonical food ID that must be present (e.g. palak, ragi)")
):
    """
    Retrieve recipes with canonical ingredient linkages and optional regional/dietary filters.
    """
    items, total, total_pages = RecipeService.get_recipes(
        db=db,
        page=page,
        page_size=page_size,
        region=region,
        country=country,
        cuisine=cuisine,
        diet=diet,
        tag=tag,
        ingredient_food_id=ingredient
    )

    return PaginatedResponse[RecipeSummary](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/search", response_model=List[RecipeSummary], summary="Search Recipes by Name or Description")
def search_recipes(
    q: str = Query(..., min_length=1, description="Search term for recipe name or ingredients"),
    limit: int = Query(20, ge=1, le=50, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search recipes by name, description, cuisine, or tags."""
    return RecipeService.search_recipes(db=db, query=q, limit=limit)

@router.get("/{recipe_id}", response_model=RecipeDetail, summary="Get Recipe Details by ID")
def get_recipe_detail(recipe_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full recipe details including all canonical ingredient mappings, quantities, and source attributions.
    """
    recipe = RecipeService.get_recipe_by_id(db=db, recipe_id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id '{recipe_id}' not found")
    return recipe
