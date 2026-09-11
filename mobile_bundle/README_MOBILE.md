# SimpleNutri — Offline Mobile Bundle

This bundle contains everything required to embed the **entire SimpleNutri knowledge base directly into an Android or Flutter mobile application** so it runs **100% offline with zero network latency**.

---

## 📦 What's in this folder?

1. **`nutrition.db`**: Pre-compiled, highly-optimized SQLite database containing:
   - Full food records (Indian millets, pulses, greens, vegetables, dairy, spices + global foods).
   - Authoritative nutrient breakdown per 100g (ICMR-NIN IFCT 2017 + USDA).
   - Curated recipes mapped strictly to canonical food IDs.
   - Categories, cuisines, diet types, and sources.
   - **SQLite FTS5 virtual table (`foods_fts`)** for instant substring and alias search.
2. **`flutter/nutrition_offline_service.dart`**: Complete, production-ready Flutter/Dart service that:
   - Copies `nutrition.db` to app storage on first run.
   - Executes offline food and recipe queries.
   - Performs cycle phase calculation completely on-device (protecting user privacy).
   - Ranks recipes based on kitchen inventory and missing ingredients.

---

## 🚀 How to use in Flutter (Quick Setup)

### Step 1: Add dependencies
In your Flutter app's `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  sqflite: ^2.3.0
  path: ^1.9.0
```

### Step 2: Add `nutrition.db` as an Asset
1. Copy `nutrition.db` from this folder into your Flutter app's `assets/` directory:
   ```bash
   cp mobile_bundle/nutrition.db your_flutter_app/assets/nutrition.db
   ```
2. Declare it in `pubspec.yaml`:
   ```yaml
   flutter:
     assets:
       - assets/nutrition.db
   ```

### Step 3: Copy Service File
Copy `mobile_bundle/flutter/nutrition_offline_service.dart` into your app's `lib/services/` directory.

### Step 4: Use it Anywhere (Offline)
```dart
import 'package:your_app/services/nutrition_offline_service.dart';

// 1. Calculate Cycle Phase (100% offline & private)
final phase = NutritionOfflineService.calculateCyclePhase(
  DateTime.now().subtract(const Duration(days: 8)),
  cycleLength: 28,
);
print("Phase: ${phase.phaseName}"); // Follicular Phase
print("Priorities: ${phase.priorityNutrientNames}"); // Protein, Folate, Zinc

// 2. Search Foods Offline
final foods = await NutritionOfflineService.searchFoods("ragi");
for (var f in foods) {
  print("${f.name}: Calcium=${f.calciumMg}mg, Iron=${f.ironMg}mg");
}

// 3. Match Kitchen Inventory & Rank Recipes
final recipes = await NutritionOfflineService.rankRecipes(
  availableFoodIds: ["ragi", "rice", "urad_dal", "coconut_oil"],
  targetTags: phase.targetTags,
);
print("Top Recipe: ${recipes.first['recipe_name']} (Match: ${recipes.first['match_percentage']}%)");
```

---

## 📱 How to use in Native Android (Kotlin / Java)
If writing native Kotlin instead of Flutter:
1. Place `nutrition.db` in `app/src/main/assets/databases/nutrition.db`.
2. Use Android's `SQLiteOpenHelper` or `Room` with `createFromAsset("databases/nutrition.db")`:
   ```kotlin
   val db = Room.databaseBuilder(context, AppDatabase::class.java, "nutrition.db")
       .createFromAsset("databases/nutrition.db")
       .build()
   ```
3. All tables, indexes, and relations are ready to query.
