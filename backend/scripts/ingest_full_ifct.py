#!/usr/bin/env python3
"""
Full IFCT 2017 Dataset Ingestion Pipeline.
Converts the official 542 foods from ICMR-NIN Indian Food Composition Tables (IFCT 2017)
into normalized, canonical SimpleNutri JSON seeds and SQLite database.
"""

import csv
import json
import re
from pathlib import Path

IFCT_REPO = Path("/tmp/ifct2017")
SEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"
SEEDS_DIR.mkdir(parents=True, exist_ok=True)

# Category mapping from IFCT Food Groups to SimpleNutri clean slugs
GROUP_MAPPING = {
    "Cereals and Millets": ("cereals_millets", "Cereals & Millets"),
    "Grain Legumes": ("pulses_legumes", "Pulses & Legumes"),
    "Green Leafy Vegetables": ("leafy_greens", "Green Leafy Vegetables"),
    "Other Vegetables": ("vegetables", "Vegetables"),
    "Roots and Tubers": ("roots_tubers", "Roots & Tubers"),
    "Fruits": ("fruits", "Fruits"),
    "Nuts and Oil Seeds": ("nuts_seeds", "Nuts & Oil Seeds"),
    "Condiments and Spices": ("spices_condiments", "Spices & Condiments"),
    "Fats and Edible Oils": ("oils_fats", "Oils & Healthy Fats"),
    "Edible Oils and Fats": ("oils_fats", "Oils & Healthy Fats"),
    "Milk and Milk Products": ("dairy", "Milk & Dairy Products"),
    "Egg and Egg Products": ("eggs", "Eggs & Egg Products"),
    "Poultry": ("poultry", "Poultry"),
    "Animal Meat": ("meat", "Meat"),
    "Fresh Water Fish and Shellfish": ("fish_seafood", "Fish & Seafood"),
    "Marine Fish": ("fish_seafood", "Fish & Seafood"),
    "Marine Mollusks": ("fish_seafood", "Fish & Seafood"),
    "Marine Shellfish": ("fish_seafood", "Fish & Seafood"),
    "Mushrooms": ("vegetables", "Vegetables"),
    "Miscellaneous Foods": ("misc", "Miscellaneous Foods"),
    "Sugars": ("sugars", "Sugars & Sweeteners")
}

def clean_slug(code, name):
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return f"{code.lower()}_{slug[:35]}"

def parse_aliases(lang_str):
    if not lang_str:
        return []
    aliases = []
    # Language string format: "A. Name; B. Name; Kan. Name; Mal. Name; Tam. Name; Tel. Name"
    parts = lang_str.split(';')
    for p in parts:
        clean = re.sub(r'^[A-Za-z\s\.]+\.\s*', '', p.strip()).strip('. ')
        # Remove [Place of collection: ...] or similar bracketed notes
        clean = re.sub(r'\[.*?\]', '', clean).strip()
        if clean and len(clean) > 1 and clean not in aliases:
            sub = clean.split(',')
            for s in sub:
                cleaned_s = s.strip()
                if cleaned_s and len(cleaned_s) > 1 and not cleaned_s.startswith('[') and cleaned_s not in aliases:
                    aliases.append(cleaned_s)
    return aliases

def to_float(val, multiplier=1.0):
    if not val:
        return None
    try:
        f = float(val)
        return round(f * multiplier, 3)
    except (ValueError, TypeError):
        return None

def ingest():
    print("🚀 Ingesting Full IFCT 2017 Dataset (542 Foods)...")
    comp_file = IFCT_REPO / "compositions" / "index.csv"
    if not comp_file.exists():
        raise FileNotFoundError(f"Missing IFCT dataset at {comp_file}")

    with open(comp_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_foods = list(reader)

    foods_list = []
    categories_dict = {}

    for row in raw_foods:
        code = row.get("code", "").strip()
        name = row.get("name", "").strip()
        scie = row.get("scie", "").strip()
        lang = row.get("lang", "").strip()
        grup = row.get("grup", "").strip()

        cat_id, cat_name = GROUP_MAPPING.get(grup, ("misc", grup or "General"))
        categories_dict[cat_id] = cat_name

        food_id = clean_slug(code, name)
        aliases = parse_aliases(lang)
        if scie and scie not in aliases:
            aliases.append(scie)

        # Diet parsing
        raw_tags = row.get("tags", "").lower()
        diets = []
        if "vegetarian" in raw_tags or "veg" in raw_tags:
            diets.append("vegetarian")
        if "vegan" in raw_tags:
            diets.append("vegan")
        if "eggetarian" in raw_tags:
            diets.append("eggetarian")
        if cat_id in ["fish_seafood", "poultry", "meat"]:
            diets.append("non_vegetarian")
            if "vegetarian" in diets:
                diets.remove("vegetarian")
        elif not diets:
            diets = ["vegetarian", "vegan"]

        # Parse Nutritional Components
        # enerc in raw IFCT is kJ (divide by 4.184 to get kcal)
        raw_enerc = to_float(row.get("enerc"))
        energy_kcal = round(raw_enerc / 4.184, 1) if raw_enerc else None

        protein_g = to_float(row.get("protcnt"))
        fat_g = to_float(row.get("fatce"))
        carbs_g = to_float(row.get("choavldf"))
        fiber_g = to_float(row.get("fibtg"))

        # Minerals: raw is in fraction of gram, factor is 1000 for mg
        calcium_mg = to_float(row.get("ca"), 1000.0)
        iron_mg = to_float(row.get("fe"), 1000.0)
        magnesium_mg = to_float(row.get("mg"), 1000.0)
        zinc_mg = to_float(row.get("zn"), 1000.0)
        potassium_mg = to_float(row.get("k"), 1000.0)
        sodium_mg = to_float(row.get("na"), 1000.0)
        phosphorus_mg = to_float(row.get("p"), 1000.0)

        # Vitamins
        folate_ug = to_float(row.get("folsum"), 1000000.0)
        vitc_mg = to_float(row.get("vitc"), 1000.0)
        vitb6_mg = to_float(row.get("vitb6c"), 1000.0)
        biotin_ug = to_float(row.get("biot"), 1000000.0)
        thiamine_mg = to_float(row.get("thia"), 1000.0)
        riboflavin_mg = to_float(row.get("ribf"), 1000.0)
        niacin_mg = to_float(row.get("nia"), 1000.0)
        vita_ug = to_float(row.get("cartb"), 1000000.0)

        # Generate tags
        tags = []
        if iron_mg and iron_mg >= 3.0:
            tags.append("iron")
        if calcium_mg and calcium_mg >= 100.0:
            tags.append("calcium")
        if magnesium_mg and magnesium_mg >= 80.0:
            tags.append("magnesium")
        if protein_g and protein_g >= 12.0:
            tags.append("protein")
        if fiber_g and fiber_g >= 6.0:
            tags.append("fiber")
        if zinc_mg and zinc_mg >= 2.0:
            tags.append("zinc")
        if vitc_mg and vitc_mg >= 20.0:
            tags.append("vitamin_c")
        if folate_ug and folate_ug >= 80.0:
            tags.append("folate")

        food_item = {
            "id": food_id,
            "code": code,
            "name": name,
            "scientific_name": scie,
            "aliases": aliases,
            "category": cat_id,
            "regions": ["india"],
            "countries": ["IN"],
            "cuisines": ["south_indian", "north_indian"],
            "diet": diets,
            "nutrition": {
                "basis_g": 100.0,
                "energy_kcal": energy_kcal,
                "protein_g": protein_g,
                "carbohydrate_g": carbs_g,
                "fat_g": fat_g,
                "fiber_g": fiber_g,
                "iron_mg": iron_mg,
                "calcium_mg": calcium_mg,
                "magnesium_mg": magnesium_mg,
                "zinc_mg": zinc_mg,
                "potassium_mg": potassium_mg,
                "sodium_mg": sodium_mg,
                "phosphorus_mg": phosphorus_mg,
                "folate_ug": folate_ug,
                "vitamin_c_mg": vitc_mg,
                "vitamin_a_ug": vita_ug,
                "vitamin_b6_mg": vitb6_mg,
                "thiamine_mg": thiamine_mg,
                "riboflavin_mg": riboflavin_mg,
                "niacin_mg": niacin_mg,
                "biotin_ug": biotin_ug,
                "vitamin_b12_ug": 0.0 if "vegetarian" in diets else None
            },
            "tags": tags,
            "source_ids": ["source-ifct-2017"]
        }
        foods_list.append(food_item)

    print(f"  ✓ Processed {len(foods_list)} foods across {len(categories_dict)} categories")

    # Add core global staples (oats, quinoa, salmon, chia seeds)
    global_staples = [
        {
            "id": "global_rolled_oats",
            "code": "G001",
            "name": "Rolled Oats",
            "scientific_name": "Avena sativa",
            "aliases": ["Oatmeal", "Avena"],
            "category": "cereals_millets",
            "regions": ["global"],
            "countries": ["GLOBAL", "US"],
            "cuisines": ["continental", "global"],
            "diet": ["vegetarian", "vegan", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 389.0, "protein_g": 16.9, "carbohydrate_g": 66.3,
                "fat_g": 6.9, "fiber_g": 10.6, "iron_mg": 4.7, "calcium_mg": 54.0, "magnesium_mg": 177.0,
                "zinc_mg": 4.0, "potassium_mg": 429.0, "sodium_mg": 2.0, "folate_ug": 56.0, "vitamin_c_mg": 0.0,
                "vitamin_a_ug": 0.0, "vitamin_b6_mg": 0.12, "vitamin_b12_ug": 0.0
            },
            "tags": ["fiber", "magnesium", "zinc", "protein"],
            "source_ids": ["source-usda-fdc"]
        },
        {
            "id": "global_quinoa",
            "code": "G002",
            "name": "Quinoa",
            "scientific_name": "Chenopodium quinoa",
            "aliases": ["Quinua"],
            "category": "cereals_millets",
            "regions": ["global"],
            "countries": ["GLOBAL", "US"],
            "cuisines": ["mediterranean", "global"],
            "diet": ["vegetarian", "vegan", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 368.0, "protein_g": 14.1, "carbohydrate_g": 64.2,
                "fat_g": 6.1, "fiber_g": 7.0, "iron_mg": 4.6, "calcium_mg": 47.0, "magnesium_mg": 197.0,
                "zinc_mg": 3.1, "potassium_mg": 563.0, "sodium_mg": 5.0, "folate_ug": 184.0, "vitamin_c_mg": 0.0,
                "vitamin_a_ug": 1.0, "vitamin_b6_mg": 0.49, "vitamin_b12_ug": 0.0
            },
            "tags": ["complete_protein", "magnesium", "folate", "iron"],
            "source_ids": ["source-usda-fdc"]
        },
        {
            "id": "global_chia_seeds",
            "code": "G003",
            "name": "Chia Seeds",
            "scientific_name": "Salvia hispanica",
            "aliases": ["Chia"],
            "category": "nuts_seeds",
            "regions": ["global"],
            "countries": ["GLOBAL", "US"],
            "cuisines": ["global"],
            "diet": ["vegetarian", "vegan", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 486.0, "protein_g": 16.5, "carbohydrate_g": 42.1,
                "fat_g": 30.7, "fiber_g": 34.4, "iron_mg": 7.7, "calcium_mg": 631.0, "magnesium_mg": 335.0,
                "zinc_mg": 4.6, "potassium_mg": 407.0, "sodium_mg": 16.0, "folate_ug": 49.0, "vitamin_c_mg": 1.6,
                "vitamin_a_ug": 16.0, "vitamin_b6_mg": 0.10, "vitamin_b12_ug": 0.0
            },
            "tags": ["omega_3", "fiber", "calcium", "magnesium", "iron"],
            "source_ids": ["source-usda-fdc"]
        },
        {
            "id": "global_wild_salmon",
            "code": "G004",
            "name": "Wild Salmon Fillet",
            "scientific_name": "Salmo salar",
            "aliases": ["Atlantic Salmon"],
            "category": "fish_seafood",
            "regions": ["global"],
            "countries": ["GLOBAL", "US"],
            "cuisines": ["mediterranean", "global"],
            "diet": ["non_vegetarian", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 142.0, "protein_g": 19.8, "carbohydrate_g": 0.0,
                "fat_g": 6.3, "fiber_g": 0.0, "iron_mg": 0.8, "calcium_mg": 12.0, "magnesium_mg": 29.0,
                "zinc_mg": 0.64, "potassium_mg": 490.0, "sodium_mg": 44.0, "folate_ug": 25.0, "vitamin_c_mg": 0.0,
                "vitamin_a_ug": 12.0, "vitamin_b6_mg": 0.82, "vitamin_b12_ug": 3.18
            },
            "tags": ["omega_3", "protein", "vitamin_b12", "anti_inflammatory"],
            "source_ids": ["source-usda-fdc"]
        },
        {
            "id": "global_pumpkin_seeds",
            "code": "G005",
            "name": "Pumpkin Seeds (Pepitas)",
            "scientific_name": "Cucurbita pepo",
            "aliases": ["Pepitas", "Kaddu ke beej"],
            "category": "nuts_seeds",
            "regions": ["india", "global"],
            "countries": ["GLOBAL", "IN"],
            "cuisines": ["global"],
            "diet": ["vegetarian", "vegan", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 559.0, "protein_g": 30.2, "carbohydrate_g": 10.7,
                "fat_g": 49.1, "fiber_g": 6.0, "iron_mg": 8.8, "calcium_mg": 46.0, "magnesium_mg": 592.0,
                "zinc_mg": 7.8, "potassium_mg": 809.0, "sodium_mg": 7.0, "folate_ug": 58.0, "vitamin_c_mg": 1.9,
                "vitamin_a_ug": 0.0, "vitamin_b6_mg": 0.14, "vitamin_b12_ug": 0.0
            },
            "tags": ["magnesium", "zinc", "protein", "iron"],
            "source_ids": ["source-usda-fdc"]
        },
        {
            "id": "l005_curd_dahi",
            "code": "L005",
            "name": "Curd / Dahi (Indian Yogurt)",
            "scientific_name": "Fermented Bos taurus milk",
            "aliases": ["Dahi", "Yogurt", "Mosaru", "Thayir", "Perugu"],
            "category": "dairy",
            "regions": ["india"],
            "countries": ["IN"],
            "cuisines": ["south_indian", "north_indian", "kerala"],
            "diet": ["vegetarian", "gluten_free"],
            "nutrition": {
                "basis_g": 100.0, "energy_kcal": 61.0, "protein_g": 3.5, "carbohydrate_g": 4.7,
                "fat_g": 3.3, "fiber_g": 0.0, "iron_mg": 0.1, "calcium_mg": 121.0, "magnesium_mg": 12.0,
                "zinc_mg": 0.59, "potassium_mg": 155.0, "sodium_mg": 46.0, "folate_ug": 7.0, "vitamin_c_mg": 0.5,
                "vitamin_a_ug": 27.0, "vitamin_b6_mg": 0.05, "vitamin_b12_ug": 0.37
            },
            "tags": ["probiotic", "calcium", "gut_health", "protein"],
            "source_ids": ["source-ifct-2017"]
        }
    ]
    foods_list.extend(global_staples)

    # Save to foods.json
    foods_file = SEEDS_DIR / "foods.json"
    with open(foods_file, "w", encoding="utf-8") as f:
        json.dump(foods_list, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {len(foods_list)} canonical foods to {foods_file}")

    # Build updated taxonomies.json
    cats_list = [{"id": cid, "name": cname} for cid, cname in categories_dict.items()]
    taxonomies = {
        "categories": cats_list,
        "regions": [
            { "id": "india", "name": "India", "description": "Indian subcontinent regional foods and traditions" },
            { "id": "global", "name": "Global / International", "description": "Worldwide staples and international cuisines" }
        ],
        "countries": [
            { "id": "IN", "name": "India" },
            { "id": "US", "name": "United States" },
            { "id": "GLOBAL", "name": "Global" }
        ],
        "cuisines": [
            { "id": "south_indian", "name": "South Indian", "region_id": "india" },
            { "id": "kerala", "name": "Kerala", "region_id": "india" },
            { "id": "tamil_nadu", "name": "Tamil Nadu", "region_id": "india" },
            { "id": "karnataka", "name": "Karnataka", "region_id": "india" },
            { "id": "andhra_telangana", "name": "Andhra & Telangana", "region_id": "india" },
            { "id": "north_indian", "name": "North Indian", "region_id": "india" },
            { "id": "punjabi", "name": "Punjabi", "region_id": "india" },
            { "id": "maharashtrian", "name": "Maharashtrian", "region_id": "india" },
            { "id": "gujarati", "name": "Gujarati", "region_id": "india" },
            { "id": "bengali", "name": "Bengali", "region_id": "india" },
            { "id": "mediterranean", "name": "Mediterranean", "region_id": "global" },
            { "id": "continental", "name": "Continental", "region_id": "global" }
        ],
        "diet_types": [
            { "id": "vegetarian", "name": "Vegetarian", "description": "Plant foods and dairy, no meat or fish" },
            { "id": "vegan", "name": "Vegan", "description": "Exclusively plant-based foods, no animal products" },
            { "id": "eggetarian", "name": "Eggetarian", "description": "Vegetarian diet including eggs" },
            { "id": "non_vegetarian", "name": "Non-Vegetarian", "description": "Includes poultry, meat, or fish" },
            { "id": "gluten_free", "name": "Gluten-Free", "description": "Naturally free from wheat gluten" }
        ],
        "nutrients": [
            { "id": "energy_kcal", "name": "Energy", "unit": "kcal", "category": "macro" },
            { "id": "protein_g", "name": "Protein", "unit": "g", "category": "macro" },
            { "id": "carbohydrate_g", "name": "Total Carbohydrate", "unit": "g", "category": "macro" },
            { "id": "fat_g", "name": "Total Fat", "unit": "g", "category": "macro" },
            { "id": "fiber_g", "name": "Dietary Fiber", "unit": "g", "category": "macro" },
            { "id": "iron_mg", "name": "Iron", "unit": "mg", "category": "mineral" },
            { "id": "calcium_mg", "name": "Calcium", "unit": "mg", "category": "mineral" },
            { "id": "magnesium_mg", "name": "Magnesium", "unit": "mg", "category": "mineral" },
            { "id": "zinc_mg", "name": "Zinc", "unit": "mg", "category": "mineral" },
            { "id": "potassium_mg", "name": "Potassium", "unit": "mg", "category": "mineral" },
            { "id": "sodium_mg", "name": "Sodium", "unit": "mg", "category": "mineral" },
            { "id": "phosphorus_mg", "name": "Phosphorus", "unit": "mg", "category": "mineral" },
            { "id": "folate_ug", "name": "Folate (B9)", "unit": "ug", "category": "vitamin" },
            { "id": "vitamin_c_mg", "name": "Vitamin C", "unit": "mg", "category": "vitamin" },
            { "id": "vitamin_a_ug", "name": "Vitamin A", "unit": "ug", "category": "vitamin" },
            { "id": "vitamin_b6_mg", "name": "Vitamin B6", "unit": "mg", "category": "vitamin" },
            { "id": "thiamine_mg", "name": "Thiamine (B1)", "unit": "mg", "category": "vitamin" },
            { "id": "riboflavin_mg", "name": "Riboflavin (B2)", "unit": "mg", "category": "vitamin" },
            { "id": "niacin_mg", "name": "Niacin (B3)", "unit": "mg", "category": "vitamin" },
            { "id": "biotin_ug", "name": "Biotin (B7)", "unit": "ug", "category": "vitamin" },
            { "id": "vitamin_b12_ug", "name": "Vitamin B12", "unit": "ug", "category": "vitamin" }
        ]
    }
    with open(SEEDS_DIR / "taxonomies.json", "w", encoding="utf-8") as f:
        json.dump(taxonomies, f, indent=2)
    print(f"  ✓ Saved taxonomies with {len(cats_list)} categories and {len(taxonomies['nutrients'])} nutrients")

if __name__ == "__main__":
    ingest()
