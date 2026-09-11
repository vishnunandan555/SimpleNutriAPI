from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from pydantic import BaseModel, ConfigDict
from backend.app.db.session import get_db
from backend.app.models.taxonomy import Nutrient
from backend.app.models.food import Food, FoodNutrient
from backend.app.schemas.taxonomy import NutrientSchema
from backend.app.services.food_service import FoodService

router = APIRouter(prefix="/api/v1", tags=["Nutrients"])

class NutrientTopFoodItem(BaseModel):
    food_id: str
    food_name: str
    category: str
    amount: float
    unit: str
    basis: str = "per 100g"

class FoodNutrientEntry(BaseModel):
    nutrient_id: str
    nutrient_name: str
    amount: float
    unit: str
    category: str

# Column map for fast indexed lookups on foods table
NUTRIENT_COLUMN_MAP = {
    "iron_mg": Food.iron_mg,
    "calcium_mg": Food.calcium_mg,
    "magnesium_mg": Food.magnesium_mg,
    "zinc_mg": Food.zinc_mg,
    "protein_g": Food.protein_g,
    "fiber_g": Food.fiber_g,
    "carbohydrate_g": Food.carbohydrate_g,
    "fat_g": Food.fat_g,
    "energy_kcal": Food.energy_kcal,
    "potassium_mg": Food.potassium_mg,
    "sodium_mg": Food.sodium_mg,
    "phosphorus_mg": Food.phosphorus_mg,
    "folate_ug": Food.folate_ug,
    "vitamin_c_mg": Food.vitamin_c_mg,
    "vitamin_a_ug": Food.vitamin_a_ug,
    "vitamin_b6_mg": Food.vitamin_b6_mg,
    "thiamine_mg": Food.thiamine_mg,
    "riboflavin_mg": Food.riboflavin_mg,
    "niacin_mg": Food.niacin_mg,
    "biotin_ug": Food.biotin_ug,
    "vitamin_b12_ug": Food.vitamin_b12_ug
}

@router.get("/nutrients", response_model=List[NutrientSchema], summary="List All Cataloged Nutrients")
def list_nutrients(
    category: Optional[str] = Query(None, description="Filter by nutrient type: macro, mineral, vitamin"),
    db: Session = Depends(get_db)
):
    """
    Retrieve master definitions, units, and classifications for all tracked macro and micronutrients.
    """
    stmt = select(Nutrient).order_by(Nutrient.category.asc(), Nutrient.name.asc())
    if category:
        stmt = stmt.where(Nutrient.category == category)
    return db.scalars(stmt).all()

@router.get("/nutrients/{nutrient_id}", response_model=NutrientSchema, summary="Get Nutrient Definition")
def get_nutrient(nutrient_id: str, db: Session = Depends(get_db)):
    """Retrieve metadata for a specific nutrient."""
    nutrient = db.scalar(select(Nutrient).where(Nutrient.id == nutrient_id))
    if not nutrient:
        raise HTTPException(status_code=404, detail=f"Nutrient '{nutrient_id}' not found")
    return nutrient

@router.get("/nutrients/{nutrient_id}/top-foods", response_model=List[NutrientTopFoodItem], summary="Get Top Foods Richest in a Nutrient")
def get_top_foods_for_nutrient(
    nutrient_id: str,
    limit: int = Query(15, ge=1, le=50, description="Number of top foods to return"),
    category: Optional[str] = Query(None, description="Optional food category filter"),
    db: Session = Depends(get_db)
):
    """
    Ranks foods with the highest concentration of a specified nutrient per 100g edible portion.
    Crucial for nutritional goal planning (e.g. top iron, top calcium, or top magnesium foods).
    """
    nutrient = db.scalar(select(Nutrient).where(Nutrient.id == nutrient_id))
    if not nutrient:
        raise HTTPException(status_code=404, detail=f"Nutrient '{nutrient_id}' not found")

    col = NUTRIENT_COLUMN_MAP.get(nutrient_id)
    if col is None:
        # Fallback to FoodNutrient table
        stmt = (
            select(FoodNutrient, Food)
            .join(Food, FoodNutrient.food_id == Food.id)
            .where(FoodNutrient.nutrient_id == nutrient_id)
            .order_by(desc(FoodNutrient.amount))
            .limit(limit)
        )
        results = db.execute(stmt).all()
        return [
            NutrientTopFoodItem(
                food_id=f.id,
                food_name=f.name,
                category=f.category,
                amount=fn.amount,
                unit=fn.unit
            )
            for fn, f in results
        ]

    stmt = select(Food).where(col.isnot(None), col > 0)
    if category:
        stmt = stmt.where(Food.category == category)
    stmt = stmt.order_by(desc(col)).limit(limit)

    foods = db.scalars(stmt).all()
    return [
        NutrientTopFoodItem(
            food_id=f.id,
            food_name=f.name,
            category=f.category,
            amount=getattr(f, nutrient_id),
            unit=nutrient.unit
        )
        for f in foods
    ]

@router.get("/foods/{food_id}/nutrients", response_model=List[FoodNutrientEntry], summary="Get Complete Nutrient Breakdown for a Food")
def get_food_nutrients(food_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete, normalized list of all 21+ nutrients for a given food.
    """
    resolved_id = FoodService.resolve_food_id(db, food_id) or food_id
    food = db.scalar(select(Food).where(Food.id == resolved_id))
    if not food:
        raise HTTPException(status_code=404, detail=f"Food item '{food_id}' not found")

    nutrients = db.scalars(select(Nutrient).order_by(Nutrient.category.asc(), Nutrient.name.asc())).all()

    entries = []
    for n in nutrients:
        val = getattr(food, n.id, None)
        if val is not None:
            entries.append(
                FoodNutrientEntry(
                    nutrient_id=n.id,
                    nutrient_name=n.name,
                    amount=val,
                    unit=n.unit,
                    category=n.category
                )
            )

    return entries
