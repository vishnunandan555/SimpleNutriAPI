import json
from sqlalchemy import String, Float, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from backend.app.db.base import Base

class Food(Base):
    __tablename__ = "foods"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(64), ForeignKey("categories.id"), nullable=False, index=True)
    
    regions_json: Mapped[str] = mapped_column(Text, default="[]")
    countries_json: Mapped[str] = mapped_column(Text, default="[]")
    cuisines_json: Mapped[str] = mapped_column(Text, default="[]")
    diet_json: Mapped[str] = mapped_column(Text, default="[]")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    source_ids_json: Mapped[str] = mapped_column(Text, default="[]")

    basis_g: Mapped[float] = mapped_column(Float, default=100.0)
    energy_kcal: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    carbohydrate_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fat_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    iron_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    calcium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    magnesium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    zinc_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    potassium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sodium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phosphorus_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    folate_ug: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_c_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_a_ug: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_b6_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    thiamine_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    riboflavin_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    niacin_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    biotin_ug: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_b12_ug: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    aliases: Mapped[List["FoodAlias"]] = relationship("FoodAlias", back_populates="food", cascade="all, delete-orphan")
    nutrients_rel: Mapped[List["FoodNutrient"]] = relationship("FoodNutrient", back_populates="food", cascade="all, delete-orphan")

    @property
    def regions(self) -> list:
        try:
            return json.loads(self.regions_json or "[]")
        except Exception:
            return []

    @property
    def countries(self) -> list:
        try:
            return json.loads(self.countries_json or "[]")
        except Exception:
            return []

    @property
    def cuisines(self) -> list:
        try:
            return json.loads(self.cuisines_json or "[]")
        except Exception:
            return []

    @property
    def diet(self) -> list:
        try:
            return json.loads(self.diet_json or "[]")
        except Exception:
            return []

    @property
    def tags(self) -> list:
        try:
            return json.loads(self.tags_json or "[]")
        except Exception:
            return []

    @property
    def source_ids(self) -> list:
        try:
            return json.loads(self.source_ids_json or "[]")
        except Exception:
            return []


class FoodAlias(Base):
    __tablename__ = "food_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[str] = mapped_column(String(64), ForeignKey("foods.id"), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    food: Mapped["Food"] = relationship("Food", back_populates="aliases")


class FoodNutrient(Base):
    __tablename__ = "food_nutrients"
    __table_args__ = (
        Index("ix_food_nutrients_nutrient_amount", "nutrient_id", "amount"),
        Index("ix_food_nutrients_food_nutrient", "food_id", "nutrient_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[str] = mapped_column(String(64), ForeignKey("foods.id"), nullable=False, index=True)
    nutrient_id: Mapped[str] = mapped_column(String(64), ForeignKey("nutrients.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    basis_g: Mapped[float] = mapped_column(Float, default=100.0)

    food: Mapped["Food"] = relationship("Food", back_populates="nutrients_rel")
    nutrient: Mapped["backend.app.models.taxonomy.Nutrient"] = relationship("backend.app.models.taxonomy.Nutrient")
