#!/usr/bin/env python3
"""
SimpleNutri Database Seeder.
Initializes tables via SQLAlchemy and populates canonical data seeds into SQLite or PostgreSQL.
Run on Render build or container startup.
"""

import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select, text, func

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))

from backend.app.core.config import settings
from backend.app.db.session import engine, SessionLocal
from backend.app.db.base import Base
from backend.app.models.source import Source
from backend.app.models.taxonomy import Category, Region, Country, Cuisine, DietType, Nutrient
from backend.app.models.food import Food, FoodAlias, FoodNutrient
from backend.app.models.recipe import Recipe, RecipeIngredient

SEEDS_DIR = BASE_DIR / "data" / "seeds"

def seed_database(force_reseed=False):
    print(f"🚀 Initializing SimpleNutri Database on: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}...")
    
    # 1. Create tables
    Base.metadata.create_all(bind=engine)
    print("  ✓ Schema tables verified/created")

    # 2. Check if already seeded with full dataset
    with SessionLocal() as db:
        food_count = db.scalar(select(func.count(Food.id))) or 0
        recipe_count = db.scalar(select(func.count(Recipe.id))) or 0
        if food_count >= 500 and recipe_count >= 50 and not force_reseed:
            print(f"  ℹ️ Database already contains full dataset ({food_count} foods, {recipe_count} recipes). Skipping seed population.")
            return

        print(f"  🌱 Seeding canonical knowledge base ({food_count} foods, {recipe_count} recipes -> updating to full dataset)...")

        # Clear existing data if partial or forced
        if food_count > 0:
            if "sqlite" in settings.DATABASE_URL:
                db.execute(text("PRAGMA foreign_keys = OFF;"))
            
            db.execute(text("DELETE FROM recipe_ingredients;"))
            db.execute(text("DELETE FROM recipes;"))
            db.execute(text("DELETE FROM food_nutrients;"))
            db.execute(text("DELETE FROM food_aliases;"))
            db.execute(text("DELETE FROM foods;"))
            db.execute(text("DELETE FROM cuisines;"))
            db.execute(text("DELETE FROM categories;"))
            db.execute(text("DELETE FROM regions;"))
            db.execute(text("DELETE FROM countries;"))
            db.execute(text("DELETE FROM diet_types;"))
            db.execute(text("DELETE FROM nutrients;"))
            db.execute(text("DELETE FROM sources;"))
            db.commit()

            if "sqlite" in settings.DATABASE_URL:
                db.execute(text("PRAGMA foreign_keys = ON;"))

        # Load JSON files
        with open(SEEDS_DIR / "sources.json") as f:
            sources_data = json.load(f)
        with open(SEEDS_DIR / "taxonomies.json") as f:
            taxonomies_data = json.load(f)
        with open(SEEDS_DIR / "foods.json") as f:
            foods_data = json.load(f)
        with open(SEEDS_DIR / "recipes.json") as f:
            recipes_data = json.load(f)

        # Insert Sources
        for s in sources_data:
            db.add(Source(
                id=s["id"],
                name=s["name"],
                version=s.get("version"),
                organization=s.get("organization"),
                country=s.get("country"),
                url=s.get("url"),
                basis=s.get("basis"),
                license_status=s.get("license_status"),
                notes=s.get("notes")
            ))
        db.flush()

        # Insert Categories (referenced by foods.category)
        for c in taxonomies_data.get("categories", []):
            db.add(Category(id=c["id"], name=c["name"], description=c.get("description")))
        db.flush()

        # Insert Regions (referenced by cuisines.region_id)
        for r in taxonomies_data.get("regions", []):
            db.add(Region(id=r["id"], name=r["name"], description=r.get("description")))
        db.flush()

        # Insert Countries
        for cnt in taxonomies_data.get("countries", []):
            db.add(Country(id=cnt["id"], name=cnt["name"]))
        db.flush()

        # Insert Cuisines (references regions.id)
        for cui in taxonomies_data.get("cuisines", []):
            db.add(Cuisine(id=cui["id"], name=cui["name"], region_id=cui.get("region_id")))
        db.flush()

        # Insert Diet Types
        for d in taxonomies_data.get("diet_types", []):
            db.add(DietType(id=d["id"], name=d["name"], description=d.get("description")))
        db.flush()
        
        nutrient_unit_map = {}
        for n in taxonomies_data.get("nutrients", []):
            db.add(Nutrient(id=n["id"], name=n["name"], unit=n["unit"], category=n["category"]))
            nutrient_unit_map[n["id"]] = n["unit"]
        db.flush()

        # Insert Foods (references categories.id)
        for f in foods_data:
            nutr = f.get("nutrition", {})
            food_obj = Food(
                id=f["id"],
                code=f.get("code"),
                name=f["name"],
                scientific_name=f.get("scientific_name"),
                category=f["category"],
                regions_json=json.dumps(f.get("regions", [])),
                countries_json=json.dumps(f.get("countries", [])),
                cuisines_json=json.dumps(f.get("cuisines", [])),
                diet_json=json.dumps(f.get("diet", [])),
                tags_json=json.dumps(f.get("tags", [])),
                source_ids_json=json.dumps(f.get("source_ids", [])),
                basis_g=nutr.get("basis_g", 100.0),
                energy_kcal=nutr.get("energy_kcal"),
                protein_g=nutr.get("protein_g"),
                carbohydrate_g=nutr.get("carbohydrate_g"),
                fat_g=nutr.get("fat_g"),
                fiber_g=nutr.get("fiber_g"),
                iron_mg=nutr.get("iron_mg"),
                calcium_mg=nutr.get("calcium_mg"),
                magnesium_mg=nutr.get("magnesium_mg"),
                zinc_mg=nutr.get("zinc_mg"),
                potassium_mg=nutr.get("potassium_mg"),
                sodium_mg=nutr.get("sodium_mg"),
                phosphorus_mg=nutr.get("phosphorus_mg"),
                folate_ug=nutr.get("folate_ug"),
                vitamin_c_mg=nutr.get("vitamin_c_mg"),
                vitamin_a_ug=nutr.get("vitamin_a_ug"),
                vitamin_b6_mg=nutr.get("vitamin_b6_mg"),
                thiamine_mg=nutr.get("thiamine_mg"),
                riboflavin_mg=nutr.get("riboflavin_mg"),
                niacin_mg=nutr.get("niacin_mg"),
                biotin_ug=nutr.get("biotin_ug"),
                vitamin_b12_ug=nutr.get("vitamin_b12_ug")
            )
            db.add(food_obj)
        db.flush()

        # Insert FoodAliases & FoodNutrients (references foods.id and nutrients.id)
        for f in foods_data:
            nutr = f.get("nutrition", {})
            for alias in f.get("aliases", []):
                db.add(FoodAlias(food_id=f["id"], alias=alias))

            for n_id, unit in nutrient_unit_map.items():
                val = nutr.get(n_id)
                if val is not None:
                    db.add(FoodNutrient(
                        food_id=f["id"],
                        nutrient_id=n_id,
                        amount=float(val),
                        unit=unit,
                        basis_g=100.0
                    ))
        db.flush()

        # Food nutrition lookup for pre-calculating recipe nutrition per serving
        food_nutr_lookup = {f["id"]: f.get("nutrition", {}) for f in foods_data}

        # Insert Recipes
        for r in recipes_data:
            servings = r.get("servings", 2) or 1
            if servings <= 0:
                servings = 1

            totals = {
                "energy_kcal": 0.0, "protein_g": 0.0, "carbohydrate_g": 0.0, "fat_g": 0.0,
                "fiber_g": 0.0, "iron_mg": 0.0, "calcium_mg": 0.0, "magnesium_mg": 0.0,
                "zinc_mg": 0.0, "potassium_mg": 0.0, "sodium_mg": 0.0, "vitamin_c_mg": 0.0,
                "folate_ug": 0.0, "vitamin_b6_mg": 0.0
            }
            for ing in r.get("ingredients", []):
                fid = ing.get("food_id")
                qty = float(ing.get("quantity", 0))
                f_nutr = food_nutr_lookup.get(fid, {})
                ratio = qty / 100.0
                for k in totals:
                    val = f_nutr.get(k)
                    if val is not None:
                        totals[k] += float(val) * ratio

            per_serving = {k: round(v / servings, 2) for k, v in totals.items()}

            recipe_obj = Recipe(
                id=r["id"],
                name=r["name"],
                description=r.get("description"),
                region=r.get("region"),
                country=r.get("country"),
                cuisine=r.get("cuisine"),
                diet_json=json.dumps(r.get("diet", [])),
                prep_time_min=r.get("prep_time_min"),
                cook_time_min=r.get("cook_time_min"),
                servings=r.get("servings", 2),
                tags_json=json.dumps(r.get("tags", [])),
                meal_type_json=json.dumps(r.get("meal_type", [])),
                instructions_json=json.dumps(r.get("instructions", [])),
                nutrition_per_serving_json=json.dumps(per_serving),
                source_ids_json=json.dumps(r.get("source_ids", []))
            )
            db.add(recipe_obj)
        db.flush()

        # Insert RecipeIngredients (references recipes.id and foods.id)
        for r in recipes_data:
            for ing in r.get("ingredients", []):
                db.add(RecipeIngredient(
                    recipe_id=r["id"],
                    food_id=ing["food_id"],
                    quantity=ing["quantity"],
                    unit=ing["unit"]
                ))
        db.flush()

        db.commit()

        # If using SQLite, rebuild FTS5 table
        if "sqlite" in settings.DATABASE_URL:
            try:
                db.execute(text("DROP TABLE IF EXISTS foods_fts;"))
                db.execute(text("""
                    CREATE VIRTUAL TABLE foods_fts USING fts5(
                        food_id UNINDEXED,
                        name,
                        aliases,
                        tags,
                        category,
                        cuisine
                    );
                """))
                # Populate FTS
                for f in foods_data:
                    aliases_str = " ".join(f.get("aliases", []))
                    tags_str = " ".join(f.get("tags", []))
                    cuisines_str = " ".join(f.get("cuisines", []))
                    db.execute(text("""
                        INSERT INTO foods_fts (food_id, name, aliases, tags, category, cuisine)
                        VALUES (:fid, :name, :aliases, :tags, :category, :cuisine)
                    """), {
                        "fid": f["id"],
                        "name": f["name"],
                        "aliases": aliases_str,
                        "tags": tags_str,
                        "category": f["category"],
                        "cuisine": cuisines_str
                    })
                db.commit()
            except Exception as e:
                print(f"  ℹ️ SQLite FTS5 setup note: {e}")

        final_food_count = db.scalar(select(func.count(Food.id)))
        final_recipe_count = db.scalar(select(func.count(Recipe.id)))
        final_nutrient_count = db.scalar(select(func.count(FoodNutrient.id)))
        print(f"  ✓ Successfully seeded {final_food_count} foods, {final_recipe_count} recipes, and {final_nutrient_count} normalized nutrient data points!")

if __name__ == "__main__":
    seed_database(force_reseed=False)
