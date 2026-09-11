#!/usr/bin/env python3
"""
Offline SQLite Database Exporter for SimpleNutri.
Compiles canonical seeds into a standalone, highly-optimized SQLite database (nutrition.db)
with full-text search (FTS5) for offline app usage.
"""

import json
import sqlite3
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
SEEDS_DIR = BASE_DIR / "data" / "seeds"
DB_PATH = BASE_DIR / "data" / "nutrition.db"
MOBILE_DIR = BASE_DIR.parent / "mobile_bundle"

def create_and_export_db():
    print("📦 Compiling Canonical Nutrition Knowledge Base (548+ foods) into SQLite...")

    # Load seeds
    with open(SEEDS_DIR / "sources.json") as f:
        sources = json.load(f)
    with open(SEEDS_DIR / "taxonomies.json") as f:
        taxonomies = json.load(f)
    with open(SEEDS_DIR / "foods.json") as f:
        foods = json.load(f)
    with open(SEEDS_DIR / "recipes.json") as f:
        recipes = json.load(f)

    # Remove existing db if present
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable WAL mode and foreign keys
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")

    # Schema definition
    cursor.executescript("""
        CREATE TABLE sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            organization TEXT,
            country TEXT,
            url TEXT,
            basis TEXT,
            license_status TEXT,
            notes TEXT
        );

        CREATE TABLE categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE regions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE countries (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE cuisines (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            region_id TEXT,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );

        CREATE TABLE diet_types (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE nutrients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            category TEXT NOT NULL
        );

        CREATE TABLE foods (
            id TEXT PRIMARY KEY,
            code TEXT,
            name TEXT NOT NULL,
            scientific_name TEXT,
            category TEXT NOT NULL,
            regions_json TEXT,
            countries_json TEXT,
            cuisines_json TEXT,
            diet_json TEXT,
            tags_json TEXT,
            source_ids_json TEXT,
            basis_g REAL DEFAULT 100,
            energy_kcal REAL,
            protein_g REAL,
            carbohydrate_g REAL,
            fat_g REAL,
            fiber_g REAL,
            iron_mg REAL,
            calcium_mg REAL,
            magnesium_mg REAL,
            zinc_mg REAL,
            potassium_mg REAL,
            sodium_mg REAL,
            phosphorus_mg REAL,
            folate_ug REAL,
            vitamin_c_mg REAL,
            vitamin_a_ug REAL,
            vitamin_b6_mg REAL,
            thiamine_mg REAL,
            riboflavin_mg REAL,
            niacin_mg REAL,
            biotin_ug REAL,
            vitamin_b12_ug REAL,
            FOREIGN KEY (category) REFERENCES categories(id)
        );

        CREATE TABLE food_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id TEXT NOT NULL,
            alias TEXT NOT NULL,
            FOREIGN KEY (food_id) REFERENCES foods(id)
        );

        CREATE TABLE food_nutrients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id TEXT NOT NULL,
            nutrient_id TEXT NOT NULL,
            amount REAL NOT NULL,
            unit TEXT NOT NULL,
            basis_g REAL DEFAULT 100,
            FOREIGN KEY (food_id) REFERENCES foods(id),
            FOREIGN KEY (nutrient_id) REFERENCES nutrients(id)
        );

        CREATE TABLE recipes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            region TEXT,
            country TEXT,
            cuisine TEXT,
            diet_json TEXT,
            prep_time_min INTEGER,
            cook_time_min INTEGER,
            servings INTEGER,
            tags_json TEXT,
            source_ids_json TEXT
        );

        CREATE TABLE recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            food_id TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        );

        -- Performance Indexes
        CREATE INDEX IF NOT EXISTS ix_foods_category ON foods(category);
        CREATE INDEX IF NOT EXISTS ix_foods_name ON foods(name);
        CREATE INDEX IF NOT EXISTS ix_foods_code ON foods(code);
        CREATE INDEX IF NOT EXISTS ix_foods_iron ON foods(iron_mg);
        CREATE INDEX IF NOT EXISTS ix_foods_calcium ON foods(calcium_mg);
        CREATE INDEX IF NOT EXISTS ix_foods_magnesium ON foods(magnesium_mg);
        CREATE INDEX IF NOT EXISTS ix_foods_protein ON foods(protein_g);
        CREATE INDEX IF NOT EXISTS ix_foods_fiber ON foods(fiber_g);
        CREATE INDEX IF NOT EXISTS ix_food_aliases_fid ON food_aliases(food_id);
        CREATE INDEX IF NOT EXISTS ix_food_aliases_alias ON food_aliases(alias);
        CREATE INDEX IF NOT EXISTS ix_food_nutrients_fn ON food_nutrients(food_id, nutrient_id);
        CREATE INDEX IF NOT EXISTS ix_food_nutrients_na ON food_nutrients(nutrient_id, amount);
        CREATE INDEX IF NOT EXISTS ix_recipes_cuisine ON recipes(cuisine);
        CREATE INDEX IF NOT EXISTS ix_recipes_region ON recipes(region);
        CREATE INDEX IF NOT EXISTS ix_recipes_country ON recipes(country);
        CREATE INDEX IF NOT EXISTS ix_recipe_ingredients_rf ON recipe_ingredients(recipe_id, food_id);

        -- Virtual Full Text Search Table (FTS5) for instant offline substring and alias lookups
        CREATE VIRTUAL TABLE foods_fts USING fts5(
            food_id UNINDEXED,
            name,
            aliases,
            tags,
            category,
            cuisine
        );
    """)

    # Populate Sources
    for s in sources:
        cursor.execute("""
            INSERT INTO sources (id, name, version, organization, country, url, basis, license_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (s["id"], s["name"], s.get("version"), s.get("organization"), s.get("country"), s.get("url"), s.get("basis"), s.get("license_status"), s.get("notes")))

    # Populate Taxonomies
    for c in taxonomies.get("categories", []):
        cursor.execute("INSERT INTO categories VALUES (?, ?, ?)", (c["id"], c["name"], c.get("description")))
    for r in taxonomies.get("regions", []):
        cursor.execute("INSERT INTO regions VALUES (?, ?, ?)", (r["id"], r["name"], r.get("description")))
    for cnt in taxonomies.get("countries", []):
        cursor.execute("INSERT INTO countries VALUES (?, ?)", (cnt["id"], cnt["name"]))
    for cui in taxonomies.get("cuisines", []):
        cursor.execute("INSERT INTO cuisines VALUES (?, ?, ?)", (cui["id"], cui["name"], cui.get("region_id")))
    for d in taxonomies.get("diet_types", []):
        cursor.execute("INSERT INTO diet_types VALUES (?, ?, ?)", (d["id"], d["name"], d.get("description")))
    
    nutrient_unit_map = {}
    for n in taxonomies.get("nutrients", []):
        cursor.execute("INSERT INTO nutrients VALUES (?, ?, ?, ?)", (n["id"], n["name"], n["unit"], n["category"]))
        nutrient_unit_map[n["id"]] = n["unit"]

    # Populate Foods
    for f in foods:
        nutr = f.get("nutrition", {})
        cursor.execute("""
            INSERT INTO foods (
                id, code, name, scientific_name, category, regions_json, countries_json, cuisines_json, diet_json, tags_json, source_ids_json,
                basis_g, energy_kcal, protein_g, carbohydrate_g, fat_g, fiber_g, iron_mg, calcium_mg, magnesium_mg,
                zinc_mg, potassium_mg, sodium_mg, phosphorus_mg, folate_ug, vitamin_c_mg, vitamin_a_ug, vitamin_b6_mg,
                thiamine_mg, riboflavin_mg, niacin_mg, biotin_ug, vitamin_b12_ug
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f["id"], f.get("code"), f["name"], f.get("scientific_name"), f["category"],
            json.dumps(f.get("regions", [])), json.dumps(f.get("countries", [])),
            json.dumps(f.get("cuisines", [])), json.dumps(f.get("diet", [])),
            json.dumps(f.get("tags", [])), json.dumps(f.get("source_ids", [])),
            nutr.get("basis_g", 100), nutr.get("energy_kcal"), nutr.get("protein_g"),
            nutr.get("carbohydrate_g"), nutr.get("fat_g"), nutr.get("fiber_g"),
            nutr.get("iron_mg"), nutr.get("calcium_mg"), nutr.get("magnesium_mg"),
            nutr.get("zinc_mg"), nutr.get("potassium_mg"), nutr.get("sodium_mg"),
            nutr.get("phosphorus_mg"), nutr.get("folate_ug"), nutr.get("vitamin_c_mg"),
            nutr.get("vitamin_a_ug"), nutr.get("vitamin_b6_mg"), nutr.get("thiamine_mg"),
            nutr.get("riboflavin_mg"), nutr.get("niacin_mg"), nutr.get("biotin_ug"),
            nutr.get("vitamin_b12_ug")
        ))

        # Insert aliases
        aliases_list = f.get("aliases", [])
        for a in aliases_list:
            cursor.execute("INSERT INTO food_aliases (food_id, alias) VALUES (?, ?)", (f["id"], a))

        # Insert FoodNutrient rows
        for n_id, unit in nutrient_unit_map.items():
            val = nutr.get(n_id)
            if val is not None:
                cursor.execute("""
                    INSERT INTO food_nutrients (food_id, nutrient_id, amount, unit, basis_g)
                    VALUES (?, ?, ?, ?, 100.0)
                """, (f["id"], n_id, float(val), unit))

        # Insert into FTS5 index
        aliases_str = " ".join(aliases_list)
        tags_str = " ".join(f.get("tags", []))
        cuisines_str = " ".join(f.get("cuisines", []))
        cursor.execute("""
            INSERT INTO foods_fts (food_id, name, aliases, tags, category, cuisine)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f["id"], f["name"], aliases_str, tags_str, f["category"], cuisines_str))

    # Populate Recipes
    for r in recipes:
        cursor.execute("""
            INSERT INTO recipes (
                id, name, description, region, country, cuisine, diet_json,
                prep_time_min, cook_time_min, servings, tags_json, source_ids_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], r["name"], r.get("description"), r.get("region"), r.get("country"),
            r.get("cuisine"), json.dumps(r.get("diet", [])), r.get("prep_time_min"),
            r.get("cook_time_min"), r.get("servings"), json.dumps(r.get("tags", [])),
            json.dumps(r.get("source_ids", []))
        ))

        for ing in r.get("ingredients", []):
            cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, food_id, quantity, unit)
                VALUES (?, ?, ?, ?)
            """, (r["id"], ing["food_id"], ing["quantity"], ing["unit"]))

    conn.commit()

    cursor.execute("SELECT count(*) FROM foods")
    food_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM recipes")
    recipe_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM food_nutrients")
    nutrient_data_count = cursor.fetchone()[0]

    conn.close()

    print(f"  ✓ Successfully created {DB_PATH}")
    print(f"  ✓ Database verified with {food_count} foods, {recipe_count} recipes, {nutrient_data_count} food nutrients, FTS5 indexed")

    # Copy to mobile_bundle directory
    MOBILE_DIR.mkdir(parents=True, exist_ok=True)
    mobile_db_dest = MOBILE_DIR / "nutrition.db"
    shutil.copyfile(DB_PATH, mobile_db_dest)
    print(f"  ✓ Mirrored to mobile bundle: {mobile_db_dest}\n")

if __name__ == "__main__":
    create_and_export_db()
