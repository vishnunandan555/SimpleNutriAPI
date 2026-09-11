from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, select, func
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.schemas.common import HealthResponse, VersionResponse
from backend.app.models.food import Food, FoodNutrient
from backend.app.models.recipe import Recipe
from backend.app.models.taxonomy import Nutrient

router = APIRouter(tags=["Health & Versioning"])

@router.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse, summary="System Health Check")
def health_check(db: Session = Depends(get_db)):
    """
    Standard health check endpoint for Render monitoring and uptime checks.
    Validates database connectivity.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="ok" if "healthy" in db_status else "degraded",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        dataset_version="1.0.0",
        database=db_status,
        environment=settings.ENVIRONMENT
    )

@router.get("/api/v1/version", response_model=VersionResponse, summary="Dataset & Schema Version Metadata")
def get_version_info(db: Session = Depends(get_db)):
    """
    Returns canonical dataset version, schema version, source provenance releases,
    and entity counts as specified in SRS Section 19.
    """
    food_count = db.scalar(select(func.count(Food.id))) or 0
    recipe_count = db.scalar(select(func.count(Recipe.id))) or 0
    nutrient_count = db.scalar(select(func.count(Nutrient.id))) or 0
    fn_count = db.scalar(select(func.count(FoodNutrient.food_id))) or 0

    bundle_path = Path(__file__).resolve().parent.parent.parent.parent / "mobile_bundle" / "nutrition.db"

    return VersionResponse(
        service=settings.PROJECT_NAME,
        api_version=settings.VERSION,
        dataset_version="1.0.0",
        schema_version="1.0",
        created_at="2026-09-11T00:00:00Z",
        source_versions={
            "ifct": "2017 (ICMR-NIN Indian Food Composition Tables, 542 foods)",
            "usda": "FoodData Central Foundation Foods 2024",
            "dgi": "ICMR-NIN Dietary Guidelines for Indians 2024",
            "recipes": "1.0 (SimpleNutri Curated Indian & Global Dishes)"
        },
        counts={
            "foods": food_count,
            "recipes": recipe_count,
            "nutrients": nutrient_count,
            "food_nutrients": fn_count
        },
        offline_bundle_available=bundle_path.exists(),
        license_notice="Authoritative food composition data sourced from ICMR-NIN IFCT 2017 & USDA FoodData Central with full provenance."
    )
