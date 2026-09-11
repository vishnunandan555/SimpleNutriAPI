from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.food import FoodSummary, FoodDetail
from backend.app.services.food_service import FoodService

router = APIRouter(prefix="/api/v1/foods", tags=["Foods"])

@router.get("", response_model=PaginatedResponse[FoodSummary], summary="List and Filter Foods")
def list_foods(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Category filter (e.g. millets, pulses, leafy_greens)"),
    region: Optional[str] = Query(None, description="Region filter (e.g. india, global)"),
    country: Optional[str] = Query(None, description="Country filter (e.g. IN, US)"),
    cuisine: Optional[str] = Query(None, description="Cuisine filter (e.g. south_indian, kerala, north_indian)"),
    diet: Optional[str] = Query(None, description="Diet type (e.g. vegetarian, vegan, gluten_free)"),
    tag: Optional[str] = Query(None, description="Nutritional tag (e.g. iron, calcium, magnesium, protein, fiber)"),
    iron_min: Optional[float] = Query(None, description="Minimum iron (mg per 100g)"),
    calcium_min: Optional[float] = Query(None, description="Minimum calcium (mg per 100g)"),
    magnesium_min: Optional[float] = Query(None, description="Minimum magnesium (mg per 100g)"),
    protein_min: Optional[float] = Query(None, description="Minimum protein (g per 100g)"),
    fiber_min: Optional[float] = Query(None, description="Minimum fiber (g per 100g)")
):
    """
    Retrieve paginated food items with optional multi-criteria filters.
    All nutrition values are normalized per 100g edible portion.
    """
    items, total, total_pages = FoodService.get_foods(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        region=region,
        country=country,
        cuisine=cuisine,
        diet=diet,
        tag=tag,
        iron_min=iron_min,
        calcium_min=calcium_min,
        magnesium_min=magnesium_min,
        protein_min=protein_min,
        fiber_min=fiber_min
    )

    return PaginatedResponse[FoodSummary](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/search", response_model=List[FoodSummary], summary="Search Foods by Name or Alias")
def search_foods(
    q: str = Query(..., min_length=1, description="Search term (food name, regional alias, or tag)"),
    limit: int = Query(20, ge=1, le=50, description="Max results to return"),
    db: Session = Depends(get_db)
):
    """
    Search foods by English name, regional alias (e.g. 'palak', 'cheera', 'nachni'), or tags.
    """
    return FoodService.search_foods(db=db, query=q, limit=limit)

@router.get("/{food_id}", response_model=FoodDetail, summary="Get Food Details by ID")
def get_food_detail(food_id: str, db: Session = Depends(get_db)):
    """
    Retrieve complete food record with full macronutrient and micronutrient values
    and source citations (ICMR-NIN IFCT 2017 / USDA).
    """
    food = FoodService.get_food_by_id(db=db, food_id=food_id)
    if not food:
        raise HTTPException(status_code=404, detail=f"Food item with id '{food_id}' not found")
    return food
