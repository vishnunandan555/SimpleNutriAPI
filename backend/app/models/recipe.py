import json
from sqlalchemy import String, Float, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from backend.app.db.base import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    cuisine: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    diet_json: Mapped[str] = mapped_column(Text, default="[]")
    prep_time_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cook_time_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[Optional[int]] = mapped_column(Integer, default=2)
    
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    meal_type_json: Mapped[str] = mapped_column(Text, default="[]")
    instructions_json: Mapped[str] = mapped_column(Text, default="[]")
    nutrition_per_serving_json: Mapped[str] = mapped_column(Text, default="{}")
    source_ids_json: Mapped[str] = mapped_column(Text, default="[]")

    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )

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
    def meal_type(self) -> list:
        try:
            return json.loads(self.meal_type_json or "[]")
        except Exception:
            return []

    @property
    def instructions(self) -> list:
        try:
            return json.loads(self.instructions_json or "[]")
        except Exception:
            return []

    @property
    def nutrition_per_serving(self) -> dict:
        try:
            return json.loads(self.nutrition_per_serving_json or "{}")
        except Exception:
            return {}

    @property
    def source_ids(self) -> list:
        try:
            return json.loads(self.source_ids_json or "[]")
        except Exception:
            return []


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        Index("ix_recipe_ingredients_recipe_food", "recipe_id", "food_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[str] = mapped_column(String(64), ForeignKey("recipes.id"), nullable=False, index=True)
    food_id: Mapped[str] = mapped_column(String(64), ForeignKey("foods.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    food: Mapped["Food"] = relationship("backend.app.models.food.Food")
