from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.db.session import get_db
from backend.app.models.taxonomy import Category, Region, Country, Cuisine, DietType, Nutrient
from backend.app.models.source import Source
from backend.app.schemas.taxonomy import (
    CategorySchema, RegionSchema, CountrySchema, CuisineSchema, DietTypeSchema, NutrientSchema, SourceSchema
)

router = APIRouter(prefix="/api/v1", tags=["Taxonomy"])

@router.get("/categories", response_model=List[CategorySchema], summary="Get Food Categories")
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all food categories (e.g. millets, pulses, leafy greens, etc.)."""
    return db.scalars(select(Category).order_by(Category.name.asc())).all()

@router.get("/regions", response_model=List[RegionSchema], summary="Get Food Regions")
def get_regions(db: Session = Depends(get_db)):
    """Retrieve geographical regions (e.g. India, Global)."""
    return db.scalars(select(Region).order_by(Region.name.asc())).all()

@router.get("/countries", response_model=List[CountrySchema], summary="Get Countries")
def get_countries(db: Session = Depends(get_db)):
    """Retrieve supported country codes and names."""
    return db.scalars(select(Country).order_by(Country.name.asc())).all()

@router.get("/cuisines", response_model=List[CuisineSchema], summary="Get Cuisines")
def get_cuisines(db: Session = Depends(get_db)):
    """Retrieve regional cuisines (e.g. South Indian, Kerala, North Indian, Mediterranean)."""
    return db.scalars(select(Cuisine).order_by(Cuisine.name.asc())).all()

@router.get("/diet-types", response_model=List[DietTypeSchema], summary="Get Diet Types")
def get_diet_types(db: Session = Depends(get_db)):
    """Retrieve dietary compatibility tags (e.g. vegetarian, vegan, gluten_free)."""
    return db.scalars(select(DietType).order_by(DietType.name.asc())).all()

@router.get("/nutrients", response_model=List[NutrientSchema], summary="Get Nutrient Definitions")
def get_nutrients(db: Session = Depends(get_db)):
    """Retrieve standardized nutrient definitions and standard measurement units."""
    return db.scalars(select(Nutrient).order_by(Nutrient.category.asc(), Nutrient.name.asc())).all()

@router.get("/sources", response_model=List[SourceSchema], summary="Get Data Provenance Sources")
def get_sources(db: Session = Depends(get_db)):
    """Retrieve citations and provenance references (ICMR-NIN IFCT 2017, USDA FoodData Central)."""
    return db.scalars(select(Source).order_by(Source.name.asc())).all()
