from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.taxonomy import SourceSchema

class RecipeIngredientItem(BaseModel):
    food_id: str
    food_name: Optional[str] = None
    quantity: float
    unit: str

    model_config = ConfigDict(from_attributes=True)

class RecipeNutritionPerServing(BaseModel):
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrate_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    iron_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    magnesium_mg: Optional[float] = None
    zinc_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    folate_ug: Optional[float] = None
    vitamin_b6_mg: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class RecipeSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    cuisine: Optional[str] = None
    diet: List[str] = []
    prep_time_min: Optional[int] = None
    cook_time_min: Optional[int] = None
    servings: Optional[int] = 2
    tags: List[str] = []
    meal_type: List[str] = []
    instructions: List[str] = []
    nutrition_per_serving: Optional[RecipeNutritionPerServing] = None
    ingredients: List[RecipeIngredientItem] = []
    source_ids: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class RecipeDetail(RecipeSummary):
    sources: List[SourceSchema] = []

class RecipeRankingRequest(BaseModel):
    available_food_ids: List[str] = []
    target_tags: List[str] = []
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    region: Optional[str] = None
    meal_type: Optional[str] = None

class RankedRecipe(BaseModel):
    recipe: RecipeSummary
    match_percentage: float
    matching_ingredients: List[str]
    missing_ingredients: List[RecipeIngredientItem]
    score: float

class ShoppingListRequest(BaseModel):
    selected_recipe_ids: List[str]
    kitchen_inventory_food_ids: List[str] = []

class ShoppingListItem(BaseModel):
    food_id: str
    food_name: str
    quantity: float
    unit: str
    category: Optional[str] = None

class ShoppingListResponse(BaseModel):
    items: List[ShoppingListItem]
    selected_recipe_count: int
    total_missing_items: int
