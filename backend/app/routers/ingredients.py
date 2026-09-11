from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from pydantic import BaseModel, ConfigDict
from backend.app.db.session import get_db
from backend.app.models.food import Food, FoodAlias
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.food_service import FoodService

router = APIRouter(prefix="/api/v1/ingredients", tags=["Ingredients"])

class IngredientItem(BaseModel):
    id: str
    code: Optional[str] = None
    name: str
    category: str
    aliases: List[str] = []
    diet: List[str] = []
    model_config = ConfigDict(from_attributes=True)

class IngredientAutocomplete(BaseModel):
    id: str
    name: str
    matched_alias: Optional[str] = None
    category: str

@router.get("", response_model=PaginatedResponse[IngredientItem], summary="Browse Kitchen Ingredients")
def list_ingredients(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(30, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by ingredient category"),
    q: Optional[str] = Query(None, description="Search ingredient by name or alias")
):
    """
    Retrieve standardized kitchen and recipe ingredients linked to canonical food IDs.
    """
    stmt = select(Food).options(selectinload(Food.aliases))
    count_stmt = select(func.count(func.distinct(Food.id)))

    if category:
        stmt = stmt.where(Food.category == category)
        count_stmt = count_stmt.where(Food.category == category)

    if q:
        clean_q = f"%{q.strip().lower()}%"
        filter_expr = or_(
            func.lower(Food.name).like(clean_q),
            Food.aliases.any(func.lower(FoodAlias.alias).like(clean_q))
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.outerjoin(FoodAlias, Food.id == FoodAlias.food_id).where(
            or_(
                func.lower(Food.name).like(clean_q),
                func.lower(FoodAlias.alias).like(clean_q)
            )
        )

    total = db.scalar(count_stmt) or 0
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    offset = (page - 1) * page_size
    foods = db.scalars(stmt.order_by(Food.name.asc()).offset(offset).limit(page_size)).unique().all()

    items = [
        IngredientItem(
            id=f.id,
            code=f.code,
            name=f.name,
            category=f.category,
            aliases=[a.alias for a in f.aliases] if f.aliases else [],
            diet=f.diet
        )
        for f in foods
    ]

    return PaginatedResponse[IngredientItem](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/autocomplete", response_model=List[IngredientAutocomplete], summary="Fast Ingredient Autocomplete")
def autocomplete_ingredients(
    q: str = Query(..., min_length=1, description="Prefix or partial name/alias"),
    limit: int = Query(15, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Fast autocomplete query designed for kitchen pantry input and search bars.
    Matches English names, regional Indian languages (Hindi, Tamil, Malayalam, etc.), and tags.
    """
    clean_q = f"%{q.strip().lower()}%"

    results = (
        db.query(Food, FoodAlias.alias)
        .outerjoin(FoodAlias, Food.id == FoodAlias.food_id)
        .filter(
            or_(
                func.lower(Food.name).like(clean_q),
                func.lower(FoodAlias.alias).like(clean_q)
            )
        )
        .limit(limit * 2)
        .all()
    )

    seen = set()
    output = []
    for food, alias in results:
        if food.id in seen:
            continue
        seen.add(food.id)
        matched = alias if alias and q.lower() in alias.lower() else None
        output.append(
            IngredientAutocomplete(
                id=food.id,
                name=food.name,
                matched_alias=matched,
                category=food.category
            )
        )
        if len(output) >= limit:
            break

    return output

@router.get("/{ingredient_id}", response_model=IngredientItem, summary="Get Ingredient Details")
def get_ingredient(ingredient_id: str, db: Session = Depends(get_db)):
    """Retrieve ingredient metadata by ID, code, or common alias."""
    resolved_id = FoodService.resolve_food_id(db, ingredient_id) or ingredient_id
    food = db.scalar(
        select(Food).where(Food.id == resolved_id).options(selectinload(Food.aliases))
    )
    if not food:
        raise HTTPException(status_code=404, detail=f"Ingredient '{ingredient_id}' not found")

    return IngredientItem(
        id=food.id,
        code=food.code,
        name=food.name,
        category=food.category,
        aliases=[a.alias for a in food.aliases] if food.aliases else [],
        diet=food.diet
    )
