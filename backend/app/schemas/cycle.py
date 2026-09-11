from typing import List
from pydantic import BaseModel, Field

class CycleCalculationRequest(BaseModel):
    last_period_start: str = Field(..., description="Date of last menstrual period start (YYYY-MM-DD)")
    cycle_length_days: int = Field(28, ge=21, le=45, description="Usual cycle length in days (typically 21-35)")

class PhaseNutrientInfo(BaseModel):
    nutrient_id: str
    nutrient_name: str
    biological_role: str
    top_food_sources: List[str]

class CyclePhaseResponse(BaseModel):
    estimated_cycle_day: int
    cycle_length_days: int
    phase_id: str
    phase_name: str
    phase_day_range: str
    description: str
    priority_nutrients: List[PhaseNutrientInfo]
    recommended_tags: List[str]
    dietary_tips: List[str]
    disclaimer: str = (
        "Personalization is an estimate based on cycle day and general evidence-based nutritional guidelines. "
        "It is not a diagnostic tool or medical prescription."
    )
