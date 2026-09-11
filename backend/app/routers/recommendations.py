from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.cycle import CycleCalculationRequest, CyclePhaseResponse
from backend.app.schemas.recipe import (
    RecipeRankingRequest, RankedRecipe, ShoppingListRequest, ShoppingListResponse
)
from backend.app.schemas.food import FoodRecommendationRequest, FoodRecommendationItem
from backend.app.services.cycle_service import CycleService
from backend.app.services.recipe_service import RecipeService
from backend.app.services.food_service import FoodService

router = APIRouter(prefix="/api/v1", tags=["Cycle & Recommendations"])

@router.get("/cycle/phases", summary="Get Cycle Phase Nutritional Priorities")
def list_cycle_phases():
    """
    Retrieve supportive nutritional priorities, nutrient roles,
    and recommended food groups for all menstrual cycle phases.
    """
    return CycleService.get_all_phases()

@router.post("/cycle/estimate", response_model=CyclePhaseResponse, summary="Estimate Current Cycle Phase & Priorities")
def estimate_cycle_phase(payload: CycleCalculationRequest):
    """
    Calculates estimated cycle day and phase based on last period date and cycle length.
    Returns target nutrients, biological roles, and practical dietary tips.
    """
    try:
        return CycleService.calculate_cycle_phase(
            last_period_start_str=payload.last_period_start,
            cycle_length=payload.cycle_length_days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recommendations/recipes", response_model=List[RankedRecipe], summary="Rank Recipes by Kitchen Match & Nutrition")
def rank_recipes(
    payload: RecipeRankingRequest,
    db: Session = Depends(get_db)
):
    """
    Ranks recipes dynamically based on:
    1. Kitchen ingredient availability (% of required ingredients user already has)
    2. Nutritional target match (alignment with phase priorities)
    3. Missing ingredient penalty
    """
    return RecipeService.rank_recipes(
        db=db,
        available_food_ids=payload.available_food_ids,
        target_tags=payload.target_tags,
        diet=payload.diet,
        cuisine=payload.cuisine,
        region=payload.region,
        meal_type=payload.meal_type
    )

@router.post("/recommendations/foods", response_model=List[FoodRecommendationItem], summary="Rank Foods by Nutrient Relevance & Preferences")
def rank_foods(
    payload: FoodRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Ranks foods based on the 6-factor SRS formula (Section 9.4):
    nutrient_match * 0.40 + diet_match * 0.20 + region_match * 0.15 + cuisine_match * 0.10 + availability * 0.10 + preference * 0.05
    """
    return FoodService.rank_foods(
        db=db,
        target_tags=payload.target_tags,
        diet=payload.diet,
        region=payload.region,
        cuisine=payload.cuisine,
        available_food_ids=payload.available_food_ids,
        limit=payload.limit
    )

@router.post("/recommendations/shopping-list", response_model=ShoppingListResponse, summary="Generate Deduplicated Shopping List")
def generate_shopping_list(
    payload: ShoppingListRequest,
    db: Session = Depends(get_db)
):
    """
    Compares selected recipes against current kitchen inventory and produces
    a consolidated, deduplicated shopping list with aggregated quantities.
    """
    return RecipeService.generate_shopping_list(
        db=db,
        selected_recipe_ids=payload.selected_recipe_ids,
        kitchen_inventory_food_ids=payload.kitchen_inventory_food_ids
    )
