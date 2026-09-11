from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.taxonomy import SourceSchema

class NutritionProfile(BaseModel):
    basis_g: float = 100.0
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
    folate_ug: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    vitamin_a_ug: Optional[float] = None
    vitamin_b6_mg: Optional[float] = None
    vitamin_b12_ug: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class FoodSummary(BaseModel):
    id: str
    name: str
    category: str
    aliases: List[str] = []
    regions: List[str] = []
    countries: List[str] = []
    cuisines: List[str] = []
    diet: List[str] = []
    tags: List[str] = []
    nutrition: NutritionProfile
    source_ids: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class FoodDetail(FoodSummary):
    sources: List[SourceSchema] = []

class FoodRecommendationRequest(BaseModel):
    target_tags: List[str] = []
    diet: Optional[str] = None
    region: Optional[str] = None
    cuisine: Optional[str] = None
    available_food_ids: List[str] = []
    limit: int = 25

class FoodRecommendationItem(BaseModel):
    food: FoodSummary
    score: float
    nutrient_match_score: float
    is_in_kitchen: bool
