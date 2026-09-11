# SimpleNutri API & Nutrition Knowledge Base

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-blue.svg?style=flat&logo=python)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Data-ICMR--NIN%20IFCT%202017%20(542%20Foods)-orange.svg)](https://www.nin.res.in/)
[![License](https://img.shields.io/badge/License-CC--BY--4.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7.svg?logo=render)](https://render.com)

A production-grade, authoritative Nutrition Knowledge Base and REST API designed for deployment on **Render**, backed by official Indian food composition data (**ICMR-NIN IFCT 2017**) and global staples (**USDA FoodData Central**), evidence-based cycle personalization, and an intelligent kitchen-inventory recipe matcher.

Also includes an **offline mobile bundle (`mobile_bundle/`)** with a pre-compiled SQLite database and Flutter service so Android and iOS apps can operate 100% offline.

---

## 📑 Table of Contents

- [🌟 Key Features](#-key-features)
- [🏗️ System Workflow Architecture](#️-system-workflow-architecture)
- [🚀 Quickstart (Local Development)](#-quickstart-local-development)
- [📖 End-to-End Sample Guide & Tutorial](#-end-to-end-sample-guide--tutorial)
  - [Step 1: Check System Health & Dataset Metadata](#step-1-check-system-health--dataset-metadata)
  - [Step 2: Estimate Cycle Phase & Nutritional Priorities](#step-2-estimate-cycle-phase--nutritional-priorities)
  - [Step 3: Rank Foods for Nutritional Priorities](#step-3-rank-foods-for-nutritional-priorities)
  - [Step 4: Fast Autocomplete for Kitchen Pantry Items](#step-4-fast-autocomplete-for-kitchen-pantry-items)
  - [Step 5: Rank Recipes by Kitchen Inventory Match](#step-5-rank-recipes-by-kitchen-inventory-match)
  - [Step 6: Generate Deduplicated Shopping List for Missing Items](#step-6-generate-deduplicated-shopping-list-for-missing-items)
  - [Step 7: Deep Nutrition Breakdown & Leaderboards](#step-7-deep-nutrition-breakdown--leaderboards)
- [☁️ Deploying to Render](#️-deploying-to-render)
- [📱 Offline Mobile Integration (Flutter & Android)](#-offline-mobile-integration-flutter--android)
- [📡 Complete API Reference](#-complete-api-reference)
- [📜 Data Provenance & Attribution](#-data-provenance--attribution)

---

## 🌟 Key Features

1. **Authoritative Full-Scale Dataset (Zero Mock Data)**:
   - **548 Canonical Foods**: Complete dataset including all 542 foods from the official ICMR-NIN Indian Food Composition Tables (IFCT 2017) plus USDA foundation foods.
   - **11,265 Nutrient Data Points**: 21 normalized macro- and micronutrients per 100g edible portion.
   - **14 Indian Language Regional Aliases**: Hindi, Tamil, Telugu, Malayalam, Kannada, Marathi, Gujarati, Bengali, Odia, Punjabi, Assamese, etc. (e.g. *Ragi / Nachni / Kelvaragu*, *Spinach / Palak / Cheera*, *Urad Dal / Black Gram*).
   - **Distinct Entity Separation**: Clean architectural boundaries between **Foods**, **Ingredients**, and **Nutrients**.
2. **Cycle Context & Nutrition Goals**:
   - Estimates current cycle day and phase (Menstrual, Follicular, Ovulatory, Luteal) from last period start date and cycle length.
   - Maps phase to evidence-based nutritional priorities (Iron, Calcium, Magnesium, Folate, Vitamin C, Zinc, Protein).
   - Stateless and privacy-first: zero personal health tracking stored on the server.
3. **Multi-Factor Food Ranking Engine (SRS Section 9.4)**:
   - 6-factor formula: `nutrient_match * 0.40 + diet_match * 0.20 + region_match * 0.15 + cuisine_match * 0.10 + availability * 0.10 + preference * 0.05`.
4. **Kitchen Pantry & Recipe Matcher (SRS Section 10 & 11)**:
   - Resolves user inventory items (by ID, common slug, or regional alias) against canonical ingredient IDs.
   - Ranks recipes based on kitchen availability %, nutritional synergy, and missing ingredient penalties.
5. **Consolidated Deduplicated Shopping List (SRS Section 12)**:
   - Compares selected recipes against kitchen inventory, detects missing ingredients, aggregates quantities, and categorizes by grocery aisle.
6. **Turnkey Render Deployment**:
   - Pre-configured `render.yaml` Blueprint and multi-stage `Dockerfile`.
   - Auto-migrating and auto-seeding on startup. Supports both local SQLite and production Render PostgreSQL.
7. **Offline Mobile Ready (`mobile_bundle/`)**:
   - Standalone `nutrition.db` SQLite database with FTS5 search.
   - Ready-to-drop Flutter service (`nutrition_offline_service.dart`).

---

## 🏗️ System Workflow Architecture

```text
       Cycle Context (Last period date + Cycle length)
                              │
                              ▼
                     Cycle Engine (/estimate)
                              │
                              ▼
                Daily Nutritional Focus & Target Tags
             (e.g., Iron, Calcium, Magnesium, Folate)
                              │
                              ▼
           Food Knowledge Base & Ranking Engine (/foods)
          (Filter by Indian/Global, Millets, Greens, etc.)
                              │
                              ▼
              Available Kitchen Pantry (/ingredients)
         (User enters items: "ragi", "palak", "rice", etc.)
                              │
                              ▼
                Recipe Ranking Engine (/recipes)
          (Ranks by Kitchen Match % + Nutritional Synergy)
                              │
                              ▼
           Deduplicated Shopping List Engine (/shopping-list)
       (Aggregates missing ingredients and units across recipes)
```

---

## 🚀 Quickstart (Local Development)

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/SimpleNutriAPI.git
cd SimpleNutriAPI

# Create and activate Python 3.10+ virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install production and testing dependencies
pip install -r backend/requirements.txt
```

### 2. Seed Database & Export Offline Bundle
```bash
# Seed local database with full IFCT 2017 data (548 foods, 11,265 nutrients)
python backend/scripts/seed_db.py

# Export standalone offline SQLite database for mobile
python backend/scripts/export_offline_db.py
```

### 3. Run Automated Tests
```bash
# Run full pytest test suite (23 unit & integration tests)
pytest backend/tests/ -v
```

### 4. Launch Development Server
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive Web App & Explorer**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Dataset Metadata & Versioning**: [http://localhost:8000/api/v1/version](http://localhost:8000/api/v1/version)

---

## 📖 End-to-End Sample Guide & Tutorial

Here is a practical, step-by-step tutorial demonstrating the entire SimpleNutri workflow using `curl`.

---

### Step 1: Check System Health & Dataset Metadata

Verify that the API and database are running, and inspect the authoritative data provenance.

```bash
curl -s http://localhost:8000/api/v1/version | jq .
```

**Sample Response:**
```json
{
  "service": "SimpleNutri API",
  "api_version": "1.0.0",
  "dataset_version": "1.0.0",
  "schema_version": "1.0",
  "created_at": "2026-09-11T00:00:00Z",
  "source_versions": {
    "ifct": "2017 (ICMR-NIN Indian Food Composition Tables, 542 foods)",
    "usda": "FoodData Central Foundation Foods 2024",
    "dgi": "ICMR-NIN Dietary Guidelines for Indians 2024",
    "recipes": "1.0 (SimpleNutri Curated Indian & Global Dishes)"
  },
  "counts": {
    "foods": 548,
    "recipes": 10,
    "nutrients": 21,
    "food_nutrients": 11265
  },
  "offline_bundle_available": true,
  "license_notice": "Authoritative food composition data sourced from ICMR-NIN IFCT 2017 & USDA FoodData Central with full provenance."
}
```

---

### Step 2: Estimate Cycle Phase & Nutritional Priorities

A user provides the first day of their last menstrual period and their typical cycle length. The engine calculates the current cycle day, estimated phase, biological explanation, and recommended target nutrients.

```bash
curl -s -X POST http://localhost:8000/api/v1/cycle/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "last_period_start": "2026-09-08",
    "cycle_length_days": 28
  }' | jq .
```

**Sample Response:**
```json
{
  "cycle_day": 4,
  "phase": "menstrual",
  "phase_name": "Menstrual Phase",
  "day_range": "Days 1–5",
  "description": "Estrogen and progesterone are at baseline. Focus on replenishing micronutrients lost through menstrual blood and combating fatigue.",
  "recommended_tags": [
    "iron",
    "calcium",
    "magnesium",
    "vitamin_c",
    "anti_inflammatory"
  ],
  "biological_rationale": "Iron losses during menses require dietary repletion accompanied by Vitamin C for non-heme absorption. Magnesium eases uterine cramping.",
  "dietary_tips": [
    "Pair plant-based iron sources (ragi, spinach, lentils) with Vitamin C (lemon, amla) for enhanced bio-availability.",
    "Stay hydrated and prioritize warm, easily digestible lentil broths and porridges."
  ]
}
```

---

### Step 3: Rank Foods for Nutritional Priorities

Using the `recommended_tags` from the estimated phase (`["iron", "calcium"]`), query the multi-factor food ranking engine.

```bash
curl -s -X POST http://localhost:8000/api/v1/recommendations/foods \
  -H "Content-Type: application/json" \
  -d '{
    "target_tags": ["iron", "calcium"],
    "diet": "vegetarian",
    "region": "india",
    "limit": 3
  }' | jq .
```

**Sample Response:**
```json
[
  {
    "food": {
      "id": "a001_amaranth_seed_black",
      "name": "Amaranth seed, black",
      "category": "cereals_millets",
      "aliases": ["Rajgira", "Ramdana", "Cheera vithu", "Keerai vidai"],
      "tags": ["iron", "calcium", "magnesium", "protein", "fiber"],
      "nutrition": {
        "energy_kcal": 356.1,
        "protein_g": 14.59,
        "iron_mg": 9.33,
        "calcium_mg": 181.0,
        "fiber_g": 7.02
      }
    },
    "score": 87.5,
    "nutrient_match_score": 100.0,
    "is_in_kitchen": false
  },
  {
    "food": {
      "id": "a010_ragi",
      "name": "Ragi",
      "category": "cereals_millets",
      "aliases": ["Finger millet", "Nachni", "Kelvaragu", "Bavato"],
      "tags": ["calcium", "iron", "fiber", "magnesium"],
      "nutrition": {
        "energy_kcal": 320.7,
        "protein_g": 7.16,
        "iron_mg": 4.62,
        "calcium_mg": 364.0,
        "fiber_g": 11.18
      }
    },
    "score": 87.5,
    "nutrient_match_score": 100.0,
    "is_in_kitchen": false
  }
]
```

---

### Step 4: Fast Autocomplete for Kitchen Pantry Items

When the user types items into their kitchen pantry, the autocomplete endpoint matches prefixes across English, scientific names, and **14 Indian languages** in under 50 milliseconds.

```bash
curl -s "http://localhost:8000/api/v1/ingredients/autocomplete?q=palak" | jq .
```

**Sample Response:**
```json
[
  {
    "id": "c033_spinach",
    "name": "Spinach",
    "matched_alias": "Palak",
    "category": "leafy_greens"
  },
  {
    "id": "c007_basella_leaves",
    "name": "Basella leaves",
    "matched_alias": "Palak",
    "category": "leafy_greens"
  }
]
```

---

### Step 5: Rank Recipes by Kitchen Inventory Match

The user enters ingredients they currently have in their kitchen: `["ragi", "urad_dal", "rice", "coconut_oil"]`. The engine ranks recipes by kitchen match percentage, nutritional synergy bonus, and missing ingredient penalty.

```bash
curl -s -X POST http://localhost:8000/api/v1/recommendations/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "available_food_ids": ["ragi", "urad_dal", "rice", "coconut_oil"],
    "target_tags": ["calcium", "iron"]
  }' | jq '.[0]'
```

**Sample Response:**
```json
{
  "recipe": {
    "id": "ragi_dosa",
    "name": "Crispy Ragi Dosa",
    "description": "Nutrient-dense fermented crepes made with finger millet and black gram, naturally packed with calcium and iron.",
    "region": "india",
    "cuisine": "south_indian",
    "diet": ["vegetarian", "vegan", "gluten_free"],
    "prep_time_min": 20,
    "cook_time_min": 15,
    "servings": 4,
    "ingredients": [
      { "food_id": "a010_ragi", "food_name": "Ragi", "quantity": 150.0, "unit": "g" },
      { "food_id": "b003_black_gram_dal", "food_name": "Black gram, dal", "quantity": 50.0, "unit": "g" },
      { "food_id": "a015_rice_raw_milled", "food_name": "Rice, raw, milled", "quantity": 50.0, "unit": "g" },
      { "food_id": "t001_coconut_oil", "food_name": "Coconut oil", "quantity": 10.0, "unit": "g" }
    ]
  },
  "match_percentage": 100.0,
  "matching_ingredients": [
    "a010_ragi",
    "b003_black_gram_dal",
    "a015_rice_raw_milled",
    "t001_coconut_oil"
  ],
  "missing_ingredients": [],
  "score": 76.0
}
```

---

### Step 6: Generate Deduplicated Shopping List for Missing Items

What if the user only has `ragi` and `rice` at home and selects the `ragi_dosa` recipe? The shopping list engine identifies precisely what is missing and consolidates quantities.

```bash
curl -s -X POST http://localhost:8000/api/v1/recommendations/shopping-list \
  -H "Content-Type: application/json" \
  -d '{
    "selected_recipe_ids": ["ragi_dosa"],
    "kitchen_inventory_food_ids": ["ragi", "rice"]
  }' | jq .
```

**Sample Response:**
```json
{
  "items": [
    {
      "food_id": "b003_black_gram_dal",
      "food_name": "Black gram, dal",
      "quantity": 50.0,
      "unit": "g",
      "category": "pulses_legumes"
    },
    {
      "food_id": "t001_coconut_oil",
      "food_name": "Coconut oil",
      "quantity": 10.0,
      "unit": "g",
      "category": "oils_fats"
    }
  ],
  "selected_recipe_count": 1,
  "total_missing_items": 2
}
```

---

### Step 7: Deep Nutrition Breakdown & Leaderboards

Query the complete composition of any food item across all 21 nutrients:

```bash
curl -s "http://localhost:8000/api/v1/foods/ragi/nutrients" | jq '.[0:4]'
```

**Sample Response:**
```json
[
  { "nutrient_id": "energy_kcal", "nutrient_name": "Energy", "amount": 320.7, "unit": "kcal", "category": "macro" },
  { "nutrient_id": "protein_g", "nutrient_name": "Protein", "amount": 7.16, "unit": "g", "category": "macro" },
  { "nutrient_id": "calcium_mg", "nutrient_name": "Calcium", "amount": 364.0, "unit": "mg", "category": "mineral" },
  { "nutrient_id": "fiber_g", "nutrient_name": "Dietary Fiber", "amount": 11.18, "unit": "g", "category": "macro" }
]
```

Find the top calcium-rich foods in India:
```bash
curl -s "http://localhost:8000/api/v1/nutrients/calcium_mg/top-foods?limit=3" | jq .
```

**Sample Response:**
```json
[
  { "food_id": "h009_gingelly_seeds_black", "food_name": "Gingelly seeds, black", "category": "nuts_seeds", "amount": 1664.0, "unit": "mg" },
  { "food_id": "g032_poppy_seeds", "food_name": "Poppy seeds", "category": "spices_condiments", "amount": 1372.0, "unit": "mg" },
  { "food_id": "h011_gingelly_seeds_white", "food_name": "Gingelly seeds, white", "category": "nuts_seeds", "amount": 1283.0, "unit": "mg" }
]
```

---

## ☁️ Deploying to Render (Step-by-Step Guide)

SimpleNutri API is optimized specifically for Render. It runs as a continuous, high-performance web service with zero cold starts, persistent memory cache, and automatic deployments.

### Method 1: Automated Blueprint Deployment (Recommended — 1-Click)

1. **Sign Up / Log In**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and log in with your GitHub account.
2. **Create New Blueprint**:
   - Click the **"New +"** button in the top navigation bar.
   - Select **"Blueprint"**.
3. **Connect Your Repository**:
   - Under **Connect a repository**, choose `vishnunandan555/SimpleNutriAPI`.
4. **Deploy**:
   - Render automatically parses [`render.yaml`](render.yaml) from your repository.
   - It will show the pre-configured service:
     - **Name**: `simplenutri-api`
     - **Runtime**: `Python 3.12`
     - **Plan**: `Free`
     - **Build Command**: `pip install -r backend/requirements.txt && python backend/scripts/seed_db.py`
     - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
     - **Health Check Path**: `/health`
   - Click **"Apply"**.
5. **Done!**:
   - Render will build the project, run database verification, and issue a free SSL certificate.
   - Your live service will be accessible at: `https://simplenutri-api.onrender.com`.

---

### Method 2: Manual Web Service Setup

If you prefer to configure manually instead of using Blueprints:

1. In the Render Dashboard, click **New +** → **Web Service**.
2. Select your `vishnunandan555/SimpleNutriAPI` repository.
3. Configure the settings:
   - **Name**: `simplenutri-api`
   - **Region**: Choose the closest region (e.g. `Oregon (US West)` or `Frankfurt (EU)`).
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && python backend/scripts/seed_db.py
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
4. Expand **Advanced Settings**:
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes` (automatically redeploys every time you push to `main`).
5. Click **Create Web Service**.

---

### Method 3: Native Docker Container Deployment

You can also deploy via the included multi-stage [`Dockerfile`](Dockerfile):

1. Click **New +** → **Web Service**.
2. Select `vishnunandan555/SimpleNutriAPI`.
3. Set **Runtime** to `Docker`.
4. Render will automatically detect and build the `Dockerfile`, seed the database, and bind to `$PORT`.

---

### 🗄️ Optional: Connecting Render Managed PostgreSQL

SimpleNutri works out of the box with the embedded SQLite database (`nutrition.db`). If you want to scale to a dedicated PostgreSQL database on Render:

1. In the Render Dashboard, click **New +** → **PostgreSQL**.
2. Set a name (e.g., `simplenutri-db`) and click **Create Database**.
3. Copy the **Internal Database URL** (e.g., `postgres://user:pass@dpg-xxx:5432/simplenutri_db`).
4. In your `simplenutri-api` Web Service, go to **Environment** → **Add Environment Variable**:
   - Key: `DATABASE_URL`
   - Value: `[Your Copied PostgreSQL Connection String]`
5. Click **Save Changes**. SimpleNutri will automatically connect to PostgreSQL, create all relational schemas, and seed all 548 canonical foods and 11,265 nutrient entries on first boot!

---

## 📱 Offline Mobile Integration (Flutter & Android)

The `mobile_bundle/` directory is isolated from the backend and contains everything required for offline native/mobile apps:
- `mobile_bundle/nutrition.db`: Clean SQLite database with 548 canonical foods, 10 recipes, 11,265 food-nutrient pairs, and SQLite FTS5 search.
- `mobile_bundle/flutter/nutrition_offline_service.dart`: Ready-to-drop pure Dart service.

### Quick Flutter Setup:
1. Copy `mobile_bundle/nutrition.db` into your Flutter app's `assets/` directory.
2. Add `sqflite` and `path_provider` to your `pubspec.yaml`:
   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     sqflite: ^2.3.0
     path: ^1.8.3
   ```
3. Initialize and query completely offline:
   ```dart
   import 'package:nutrition_app/nutrition_offline_service.dart';

   void main() async {
     WidgetsFlutterBinding.ensureInitialized();
     final service = NutritionOfflineService();
     await service.init();

     // Fast full-text food search across 14 languages
     final foods = await service.searchFoods('spinach');
     print('Found: ${foods.first['name']}');

     // Estimate cycle phase & nutrition priorities offline
     final phase = service.estimateCyclePhase(
       lastPeriodStart: DateTime.now().subtract(const Duration(days: 4)),
       cycleLengthDays: 28,
     );
     print('Phase: ${phase['phase_name']}');
   }
   ```

---

## 📡 Complete API Reference

| Tag | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health` | Service uptime and database probe |
| **Metadata** | `GET` | `/api/v1/version` | Canonical dataset release, schema version, and entity counts |
| **Foods** | `GET` | `/api/v1/foods` | Paginated foods with multi-criteria filters (`region`, `country`, `cuisine`, `diet`, `tag`, `iron_min`, `calcium_min`, `protein_min`, `fiber_min`) |
| | `GET` | `/api/v1/foods/search` | Search foods by English name, regional alias, or tag |
| | `GET` | `/api/v1/foods/{food_id}` | Complete food detail with nutrient profile & sources |
| | `GET` | `/api/v1/foods/{food_id}/nutrients` | Normalized breakdown of all 21 nutrients for a food |
| **Ingredients** | `GET` | `/api/v1/ingredients` | Standardized kitchen ingredients linked to canonical food IDs |
| | `GET` | `/api/v1/ingredients/autocomplete` | Fast autocomplete matching English and 14 Indian languages |
| | `GET` | `/api/v1/ingredients/{ingredient_id}` | Ingredient details with regional aliases and dietary flags |
| **Nutrients** | `GET` | `/api/v1/nutrients` | Master list of 21 tracked nutrients and standard units |
| | `GET` | `/api/v1/nutrients/{nutrient_id}` | Nutrient metadata and unit definition |
| | `GET` | `/api/v1/nutrients/{nutrient_id}/top-foods` | Ranked foods richest in a nutrient per 100g edible portion |
| **Recipes** | `GET` | `/api/v1/recipes` | Filter recipes by `region`, `country`, `cuisine`, `diet`, `tag`, or `ingredient` |
| | `GET` | `/api/v1/recipes/search` | Search recipes by title, description, or ingredients |
| | `GET` | `/api/v1/recipes/{recipe_id}` | Recipe detail with quantities, units, and instructions |
| **Recommendations** | `GET` | `/api/v1/cycle/phases` | Evidence-based cycle phases and target nutrients |
| | `POST` | `/api/v1/cycle/estimate` | Stateless cycle day and phase calculation |
| | `POST` | `/api/v1/recommendations/foods` | 6-factor weighted food ranking engine (SRS Section 9.4) |
| | `POST` | `/api/v1/recommendations/recipes` | Kitchen match % + nutrition synergy ranking (SRS Section 10) |
| | `POST` | `/api/v1/recommendations/shopping-list` | Consolidated deduplicated shopping list (SRS Section 12) |
| **Taxonomy** | `GET` | `/api/v1/categories` | Food categories |
| | `GET` | `/api/v1/regions` | Geographical regions |
| | `GET` | `/api/v1/countries` | Supported countries |
| | `GET` | `/api/v1/cuisines` | Regional cuisines |
| | `GET` | `/api/v1/diet-types` | Dietary compatibility |
| | `GET` | `/api/v1/sources` | Data provenance citations |

---

## 📜 Data Provenance & Attribution

- **ICMR-NIN Indian Food Composition Tables (IFCT 2017)**:
  - *Citation*: Longvah, T., Ananthan, R., Bhaskarachary, K., & Venkaiah, K. (2017). *Indian Food Composition Tables*. National Institute of Nutrition, Indian Council of Medical Research, Hyderabad, India.
  - Sourced under fair-use academic attribution for nutritional research and public guidance.
- **USDA FoodData Central**:
  - Foundation Foods Database, Agricultural Research Service, U.S. Department of Agriculture. Public Domain.
- **ICMR-NIN Dietary Guidelines for Indians (2024)**:
  - Evidence base for menstrual and lifestyle micronutrient priorities.
- **Recipes**:
  - Curated canonical recipes released under [Creative Commons Attribution 4.0 (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/).
