#!/usr/bin/env python3
"""
Automated validation script for SimpleNutri canonical datasets.
Checks for:
1. Foreign key references (recipe ingredients -> foods.id, taxonomies, sources)
2. Duplicate IDs and aliases
3. Nutrient value ranges and positive quantity constraints
4. Completeness of mandatory metadata
"""

import json
import sys
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"

def load_json(filename):
    filepath = SEEDS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Missing required seed file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def validate():
    print("🔍 Starting SimpleNutri Canonical Data Validation...")
    errors = []
    warnings = []

    # 1. Load files
    sources = load_json("sources.json")
    taxonomies = load_json("taxonomies.json")
    foods = load_json("foods.json")
    recipes = load_json("recipes.json")

    source_ids = {s["id"] for s in sources}
    category_ids = {c["id"] for c in taxonomies.get("categories", [])}
    region_ids = {r["id"] for r in taxonomies.get("regions", [])}
    country_ids = {c["id"] for c in taxonomies.get("countries", [])}
    cuisine_ids = {c["id"] for c in taxonomies.get("cuisines", [])}
    diet_ids = {d["id"] for d in taxonomies.get("diet_types", [])}
    nutrient_ids = {n["id"] for n in taxonomies.get("nutrients", [])}

    # 2. Validate Sources
    if not source_ids:
        errors.append("No data sources found in sources.json")
    print(f"  ✓ {len(source_ids)} sources registered")

    # 3. Validate Foods
    food_ids = set()
    alias_map = {}

    for food in foods:
        fid = food.get("id")
        if not fid:
            errors.append("Food entry missing 'id'")
            continue
        if fid in food_ids:
            errors.append(f"Duplicate food id: '{fid}'")
        food_ids.add(fid)

        # Validate category
        if food.get("category") not in category_ids:
            errors.append(f"Food '{fid}' has invalid category: '{food.get('category')}'")

        # Validate regions
        for r in food.get("regions", []):
            if r not in region_ids:
                errors.append(f"Food '{fid}' has invalid region: '{r}'")

        # Validate countries
        for c in food.get("countries", []):
            if c not in country_ids:
                errors.append(f"Food '{fid}' has invalid country: '{c}'")

        # Validate diets
        for d in food.get("diet", []):
            if d not in diet_ids:
                errors.append(f"Food '{fid}' has invalid diet: '{d}'")

        # Validate sources
        for s in food.get("source_ids", []):
            if s not in source_ids:
                errors.append(f"Food '{fid}' references unregistered source: '{s}'")

        # Validate aliases
        for alias in food.get("aliases", []):
            alias_lower = alias.strip().lower()
            if alias_lower in alias_map and alias_map[alias_lower] != fid:
                warnings.append(f"Alias collision: '{alias}' shared by '{fid}' and '{alias_map[alias_lower]}'")
            alias_map[alias_lower] = fid

        # Validate nutrition values
        nutr = food.get("nutrition", {})
        if nutr.get("basis_g") != 100:
            errors.append(f"Food '{fid}' nutrition basis must be 100g, got {nutr.get('basis_g')}")
        
        for nkey, val in nutr.items():
            if nkey == "basis_g":
                continue
            if nkey not in nutrient_ids:
                warnings.append(f"Food '{fid}' has uncataloged nutrient: '{nkey}'")
            if val is not None and val < 0:
                errors.append(f"Food '{fid}' has negative nutrient value for '{nkey}': {val}")

    print(f"  ✓ {len(food_ids)} canonical foods validated across {len(category_ids)} categories")

    # 4. Validate Recipes
    recipe_ids = set()
    for recipe in recipes:
        rid = recipe.get("id")
        if not rid:
            errors.append("Recipe missing 'id'")
            continue
        if rid in recipe_ids:
            errors.append(f"Duplicate recipe id: '{rid}'")
        recipe_ids.add(rid)

        # Validate region/cuisine
        if recipe.get("region") and recipe.get("region") not in region_ids:
            errors.append(f"Recipe '{rid}' has invalid region: '{recipe.get('region')}'")
        if recipe.get("cuisine") and recipe.get("cuisine") not in cuisine_ids:
            errors.append(f"Recipe '{rid}' has invalid cuisine: '{recipe.get('cuisine')}'")

        # Validate ingredients
        ingredients = recipe.get("ingredients", [])
        if not ingredients:
            errors.append(f"Recipe '{rid}' has no ingredients")
        for ing in ingredients:
            ing_fid = ing.get("food_id")
            if not ing_fid:
                errors.append(f"Recipe '{rid}' ingredient missing 'food_id'")
            elif ing_fid not in food_ids:
                errors.append(f"Recipe '{rid}' references nonexistent food_id: '{ing_fid}'")
            qty = ing.get("quantity")
            if qty is None or qty <= 0:
                errors.append(f"Recipe '{rid}' ingredient '{ing_fid}' has invalid quantity: {qty}")
            if not ing.get("unit"):
                errors.append(f"Recipe '{rid}' ingredient '{ing_fid}' missing unit")

        for s in recipe.get("source_ids", []):
            if s not in source_ids:
                errors.append(f"Recipe '{rid}' references unregistered source: '{s}'")

    print(f"  ✓ {len(recipe_ids)} recipes validated with 100% canonical ingredient mapping")

    # 5. Summary
    if warnings:
        print(f"\n⚠️  {len(warnings)} Warnings:")
        for w in warnings:
            print(f"   - {w}")

    if errors:
        print(f"\n❌ {len(errors)} Validation Errors:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    print("\n🎉 ALL DATA VALIDATION CHECKS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    validate()
