import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'dart:convert';

/// Nutrition & Food Data Models for Flutter
class FoodItem {
  final String id;
  final String name;
  final String category;
  final List<String> aliases;
  final List<String> regions;
  final List<String> cuisines;
  final List<String> diet;
  final List<String> tags;
  final double basisG;
  final double? energyKcal;
  final double? proteinG;
  final double? carbG;
  final double? fatG;
  final double? fiberG;
  final double? ironMg;
  final double? calciumMg;
  final double? magnesiumMg;
  final double? zincMg;

  FoodItem({
    required this.id,
    required this.name,
    required this.category,
    required this.aliases,
    required this.regions,
    required this.cuisines,
    required this.diet,
    required this.tags,
    this.basisG = 100.0,
    this.energyKcal,
    this.proteinG,
    this.carbG,
    this.fatG,
    this.fiberG,
    this.ironMg,
    this.calciumMg,
    this.magnesiumMg,
    this.zincMg,
  });

  factory FoodItem.fromMap(Map<String, dynamic> map, List<String> aliasesList) {
    List<String> parseList(dynamic raw) {
      if (raw == null) return [];
      try {
        final decoded = jsonDecode(raw.toString());
        if (decoded is List) return decoded.map((e) => e.toString()).toList();
      } catch (_) {}
      return [];
    }

    return FoodItem(
      id: map['id'] as String,
      name: map['name'] as String,
      category: map['category'] as String,
      aliases: aliasesList,
      regions: parseList(map['regions_json']),
      cuisines: parseList(map['cuisines_json']),
      diet: parseList(map['diet_json']),
      tags: parseList(map['tags_json']),
      basisG: (map['basis_g'] as num?)?.toDouble() ?? 100.0,
      energyKcal: (map['energy_kcal'] as num?)?.toDouble(),
      proteinG: (map['protein_g'] as num?)?.toDouble(),
      carbG: (map['carbohydrate_g'] as num?)?.toDouble(),
      fatG: (map['fat_g'] as num?)?.toDouble(),
      fiberG: (map['fiber_g'] as num?)?.toDouble(),
      ironMg: (map['iron_mg'] as num?)?.toDouble(),
      calciumMg: (map['calcium_mg'] as num?)?.toDouble(),
      magnesiumMg: (map['magnesium_mg'] as num?)?.toDouble(),
      zincMg: (map['zinc_mg'] as num?)?.toDouble(),
    );
  }
}

class RecipeItem {
  final String id;
  final String name;
  final String? description;
  final String? cuisine;
  final List<String> tags;
  final List<String> mealType;
  final List<String> instructions;
  final int? prepTimeMin;
  final int? cookTimeMin;
  final int? servings;
  final List<RecipeIngredientItem> ingredients;
  final Map<String, double> nutritionPerServing;

  RecipeItem({
    required this.id,
    required this.name,
    this.description,
    this.cuisine,
    required this.tags,
    this.mealType = const [],
    this.instructions = const [],
    this.prepTimeMin,
    this.cookTimeMin,
    this.servings,
    required this.ingredients,
    this.nutritionPerServing = const {},
  });

  factory RecipeItem.fromMap(Map<String, dynamic> map, List<RecipeIngredientItem> ingredientsList) {
    List<String> parseList(dynamic raw) {
      if (raw == null) return [];
      try {
        final decoded = jsonDecode(raw.toString());
        if (decoded is List) return decoded.map((e) => e.toString()).toList();
      } catch (_) {}
      return [];
    }

    Map<String, double> parseNutrients(dynamic raw) {
      if (raw == null) return {};
      try {
        final decoded = jsonDecode(raw.toString());
        if (decoded is Map) {
          final Map<String, double> result = {};
          decoded.forEach((k, v) {
            if (v is num) result[k.toString()] = v.toDouble();
          });
          return result;
        }
      } catch (_) {}
      return {};
    }

    return RecipeItem(
      id: map['id'] as String,
      name: map['name'] as String,
      description: map['description'] as String?,
      cuisine: map['cuisine'] as String?,
      tags: parseList(map['tags_json']),
      mealType: parseList(map['meal_type_json']),
      instructions: parseList(map['instructions_json']),
      prepTimeMin: (map['prep_time_min'] as num?)?.toInt(),
      cookTimeMin: (map['cook_time_min'] as num?)?.toInt(),
      servings: (map['servings'] as num?)?.toInt(),
      ingredients: ingredientsList,
      nutritionPerServing: parseNutrients(map['nutrition_per_serving_json']),
    );
  }
}

class RecipeIngredientItem {
  final String foodId;
  final double quantity;
  final String unit;

  RecipeIngredientItem({
    required this.foodId,
    required this.quantity,
    required this.unit,
  });
}

class CyclePhaseInfo {
  final int estimatedCycleDay;
  final String phaseId;
  final String phaseName;
  final String description;
  final List<String> priorityNutrientNames;
  final List<String> targetTags;
  final List<String> nutritionFocus;
  final List<String> nutritionContext;

  CyclePhaseInfo({
    required this.estimatedCycleDay,
    required this.phaseId,
    required this.phaseName,
    required this.description,
    required this.priorityNutrientNames,
    required this.targetTags,
    this.nutritionFocus = const [],
    this.nutritionContext = const [],
  });
}

/// Represents a food or recipe logged by the user for a meal (Home Screen Daily Ledger)
class DailyIntakeLogItem {
  final String id;
  final DateTime timestamp;
  final String? foodId;
  final String? recipeId;
  final String name;
  final double portionOrServings;
  final String meal; // 'breakfast', 'lunch', 'dinner', 'snack'
  final Map<String, double> nutrients;

  DailyIntakeLogItem({
    required this.id,
    required this.timestamp,
    this.foodId,
    this.recipeId,
    required this.name,
    this.portionOrServings = 1.0,
    this.meal = 'snack',
    required this.nutrients,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      'food_id': foodId,
      'recipe_id': recipeId,
      'name': name,
      'portion_or_servings': portionOrServings,
      'meal': meal,
      'nutrients': jsonEncode(nutrients),
    };
  }

  factory DailyIntakeLogItem.fromMap(Map<String, dynamic> map) {
    Map<String, double> parsedNutrients = {};
    try {
      final decoded = jsonDecode(map['nutrients'].toString());
      if (decoded is Map) {
        decoded.forEach((k, v) {
          if (v is num) parsedNutrients[k.toString()] = v.toDouble();
        });
      }
    } catch (_) {}

    return DailyIntakeLogItem(
      id: map['id'] as String,
      timestamp: DateTime.parse(map['timestamp'] as String),
      foodId: map['food_id'] as String?,
      recipeId: map['recipe_id'] as String?,
      name: map['name'] as String,
      portionOrServings: (map['portion_or_servings'] as num?)?.toDouble() ?? 1.0,
      meal: map['meal'] as String? ?? 'snack',
      nutrients: parsedNutrients,
    );
  }
}

/// Aggregated nutrient totals and RDA progress percentages for Home Screen progress bars
class DailyNutrientTotals {
  final double energyKcal;
  final double proteinG;
  final double carbG;
  final double fatG;
  final double fiberG;
  final double ironMg;
  final double calciumMg;
  final double magnesiumMg;
  final double zincMg;
  final double potassiumMg;
  final double sodiumMg;
  final double vitaminCMg;
  final double folateUg;
  final double vitaminB6Mg;

  /// Map of nutrient key to percentage of daily RDA achieved (0.0 to 100.0+)
  final Map<String, double> progressPercentages;

  DailyNutrientTotals({
    required this.energyKcal,
    required this.proteinG,
    required this.carbG,
    required this.fatG,
    required this.fiberG,
    required this.ironMg,
    required this.calciumMg,
    required this.magnesiumMg,
    required this.zincMg,
    required this.potassiumMg,
    required this.sodiumMg,
    required this.vitaminCMg,
    required this.folateUg,
    required this.vitaminB6Mg,
    required this.progressPercentages,
  });
}

/// Offline Nutrition Database & Logic Engine for Flutter
class NutritionOfflineService {
  static Database? _db;

  /// Default Daily Reference Values based on ICMR-NIN RDA (2024) for adult Indian women
  static const Map<String, double> defaultRdaTargets = {
    'energy_kcal': 2000.0,
    'protein_g': 46.0,
    'carbohydrate_g': 250.0,
    'fat_g': 25.0,
    'fiber_g': 30.0,
    'iron_mg': 29.0,
    'calcium_mg': 1000.0,
    'magnesium_mg': 370.0,
    'zinc_mg': 13.2,
    'potassium_mg': 3500.0,
    'sodium_mg': 2000.0,
    'vitamin_c_mg': 65.0,
    'folate_ug': 220.0,
    'vitamin_b6_mg': 1.9,
  };

  /// Initialize and open bundled nutrition.db from assets
  static Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDatabase();
    return _db!;
  }

  static Future<Database> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, "nutrition.db");

    // Check if database exists in device storage, if not copy from assets
    final exists = await databaseExists(path);
    if (!exists) {
      try {
        await Directory(dirname(path)).create(recursive: true);
        ByteData data = await rootBundle.load("assets/nutrition.db");
        List<int> bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
        await File(path).writeAsBytes(bytes, flush: true);
      } catch (e) {
        throw Exception("Failed to copy bundled nutrition.db asset: $e");
      }
    }

    return await openDatabase(path, readOnly: true);
  }

  /// Search foods completely offline by name or alias
  static Future<List<FoodItem>> searchFoods(String query, {int limit = 20}) async {
    final db = await database;
    final cleanQ = "%${query.trim().toLowerCase()}%";

    final results = await db.rawQuery('''
      SELECT DISTINCT f.* FROM foods f
      LEFT JOIN food_aliases a ON f.id = a.food_id
      WHERE LOWER(f.name) LIKE ? OR LOWER(a.alias) LIKE ? OR LOWER(f.tags_json) LIKE ?
      LIMIT ?
    ''', [cleanQ, cleanQ, cleanQ, limit]);

    List<FoodItem> items = [];
    for (var row in results) {
      final fid = row['id'] as String;
      final aliasRows = await db.query('food_aliases', where: 'food_id = ?', whereArgs: [fid]);
      final aliases = aliasRows.map((a) => a['alias'].toString()).toList();
      items.add(FoodItem.fromMap(row, aliases));
    }
    return items;
  }

  /// Calculate estimated cycle phase locally (100% private, zero network calls)
  static CyclePhaseInfo calculateCyclePhase(DateTime lastPeriodStart, {int cycleLength = 28}) {
    final now = DateTime.now();
    final difference = now.difference(lastPeriodStart).inDays;
    final cycleDay = (difference < 0) ? 1 : ((difference % cycleLength) + 1);

    if (cycleDay <= 5) {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "menstrual",
        phaseName: "Menstrual Phase",
        description: "Support overall nutritional adequacy with dietary iron, vitamin C, and magnesium for muscle comfort.",
        priorityNutrientNames: ["Iron", "Vitamin C", "Magnesium"],
        targetTags: ["iron", "vitamin_c", "magnesium", "anti_inflammatory"],
        nutritionFocus: ["iron", "vitamin_c", "protein", "folate"],
        nutritionContext: [
          "Menstrual blood loss increases iron requirements over time.",
          "Vitamin C can improve absorption of non-heme iron from plant foods.",
          "Adequate protein supports tissue repair and cellular recovery.",
          "Hydration and light mineral balance support overall comfort.",
        ],
      );
    } else if (cycleDay <= 13) {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "follicular",
        phaseName: "Follicular Phase",
        description: "Support general vitality and cellular energy with clean protein, B-vitamins, and zinc.",
        priorityNutrientNames: ["Protein", "Folate (B9)", "Zinc"],
        targetTags: ["protein", "folate", "zinc"],
        nutritionFocus: ["protein", "folate", "zinc", "vitamin_b6"],
        nutritionContext: [
          "Rising follicular activity benefits from steady protein intake.",
          "Folate and zinc support cellular energy and normal cell division.",
          "Complex carbohydrates and whole grains maintain steady stamina.",
        ],
      );
    } else if (cycleDay <= 16) {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "ovulatory",
        phaseName: "Ovulatory Phase",
        description: "Prioritize nutrient-dense whole foods, dietary fiber, and adequate hydration.",
        priorityNutrientNames: ["Dietary Fiber", "Zinc", "Potassium"],
        targetTags: ["fiber", "zinc", "antioxidant"],
        nutritionFocus: ["fiber", "zinc", "antioxidant", "potassium"],
        nutritionContext: [
          "Higher estrogen peaks benefit from dietary fiber to assist normal hepatic hormone clearance.",
          "Zinc and antioxidant-rich foods support cellular health during ovulation.",
          "Adequate hydration and leafy greens support electrolyte balance.",
        ],
      );
    } else {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "luteal",
        phaseName: "Luteal Phase",
        description: "Support steady energy and mood balance with magnesium, calcium, and complex carbs.",
        priorityNutrientNames: ["Magnesium", "Calcium", "Vitamin B6", "Complex Carbs"],
        targetTags: ["magnesium", "calcium", "vitamin_b6", "complex_carbs", "pms_support"],
        nutritionFocus: ["magnesium", "calcium", "vitamin_b6", "complex_carbs"],
        nutritionContext: [
          "Progesterone elevation increases basal metabolic rate slightly, favoring complex carbohydrates.",
          "Magnesium and calcium dietary intake support smooth muscle relaxation and comfort.",
          "Vitamin B6 assists normal neurotransmitter synthesis, supporting mood stability.",
        ],
      );
    }
  }

  /// Offline Kitchen Matching & Recipe Ranking with Nutrition Per Serving
  static Future<List<Map<String, dynamic>>> rankRecipes({
    required List<String> availableFoodIds,
    List<String> targetTags = const [],
  }) async {
    final db = await database;
    final recipeRows = await db.query('recipes');
    final availableSet = availableFoodIds.map((e) => e.toLowerCase()).toSet();
    final targetTagSet = targetTags.map((e) => e.toLowerCase()).toSet();

    List<Map<String, dynamic>> ranked = [];

    for (var r in recipeRows) {
      final rid = r['id'] as String;
      final ingRows = await db.query('recipe_ingredients', where: 'recipe_id = ?', whereArgs: [rid]);
      
      final ings = ingRows.map((i) => RecipeIngredientItem(
        foodId: i['food_id'] as String,
        quantity: (i['quantity'] as num).toDouble(),
        unit: i['unit'] as String,
      )).toList();

      final matched = ings.where((i) => availableSet.contains(i.foodId.toLowerCase())).toList();
      final missing = ings.where((i) => !availableSet.contains(i.foodId.toLowerCase())).toList();
      final matchPct = (matched.length / (ings.isEmpty ? 1 : ings.length)) * 100;

      // Parse tags, meal_type, instructions
      List<String> tags = [];
      List<String> mealType = [];
      List<String> instructions = [];
      Map<String, double> nutritionPerServing = {};

      try {
        final decoded = jsonDecode(r['tags_json'].toString());
        if (decoded is List) tags = decoded.map((e) => e.toString().toLowerCase()).toList();
      } catch (_) {}
      try {
        final decoded = jsonDecode(r['meal_type_json'].toString());
        if (decoded is List) mealType = decoded.map((e) => e.toString().toLowerCase()).toList();
      } catch (_) {}
      try {
        final decoded = jsonDecode(r['instructions_json'].toString());
        if (decoded is List) instructions = decoded.map((e) => e.toString()).toList();
      } catch (_) {}
      try {
        final decoded = jsonDecode(r['nutrition_per_serving_json'].toString());
        if (decoded is Map) {
          decoded.forEach((k, v) {
            if (v is num) nutritionPerServing[k.toString()] = v.toDouble();
          });
        }
      } catch (_) {}

      final overlap = tags.where((t) => targetTagSet.contains(t)).length;
      final score = (matchPct * 0.6) + (overlap * 20.0 * 0.4) - (missing.length * 5.0);

      ranked.add({
        'recipe_id': rid,
        'recipe_name': r['name'],
        'cuisine': r['cuisine'],
        'servings': r['servings'],
        'prep_time_min': r['prep_time_min'],
        'cook_time_min': r['cook_time_min'],
        'meal_type': mealType,
        'instructions': instructions,
        'nutrition_per_serving': nutritionPerServing,
        'match_percentage': matchPct.roundToDouble(),
        'matched_count': matched.length,
        'missing_ingredients': missing.map((m) => {'food_id': m.foodId, 'quantity': m.quantity, 'unit': m.unit}).toList(),
        'score': score.roundToDouble(),
      });
    }

    ranked.sort((a, b) => (b['score'] as double).compareTo(a['score'] as double));
    return ranked;
  }

  /// Calculate daily nutrient intake totals and progress against RDA targets for Home Screen progress bars
  static DailyNutrientTotals calculateDailyNutrientProgress(
    List<DailyIntakeLogItem> logs, {
    Map<String, double>? customRda,
  }) {
    final targets = customRda ?? defaultRdaTargets;
    final Map<String, double> totals = {
      'energy_kcal': 0.0,
      'protein_g': 0.0,
      'carbohydrate_g': 0.0,
      'fat_g': 0.0,
      'fiber_g': 0.0,
      'iron_mg': 0.0,
      'calcium_mg': 0.0,
      'magnesium_mg': 0.0,
      'zinc_mg': 0.0,
      'potassium_mg': 0.0,
      'sodium_mg': 0.0,
      'vitamin_c_mg': 0.0,
      'folate_ug': 0.0,
      'vitamin_b6_mg': 0.0,
    };

    for (final log in logs) {
      final portion = log.portionOrServings;
      log.nutrients.forEach((k, v) {
        if (totals.containsKey(k)) {
          totals[k] = (totals[k] ?? 0.0) + (v * portion);
        }
      });
    }

    final Map<String, double> progress = {};
    totals.forEach((k, v) {
      final target = targets[k] ?? 1.0;
      progress[k] = target > 0 ? ((v / target) * 100.0) : 0.0;
    });

    return DailyNutrientTotals(
      energyKcal: totals['energy_kcal'] ?? 0.0,
      proteinG: totals['protein_g'] ?? 0.0,
      carbG: totals['carbohydrate_g'] ?? 0.0,
      fatG: totals['fat_g'] ?? 0.0,
      fiberG: totals['fiber_g'] ?? 0.0,
      ironMg: totals['iron_mg'] ?? 0.0,
      calciumMg: totals['calcium_mg'] ?? 0.0,
      magnesiumMg: totals['magnesium_mg'] ?? 0.0,
      zincMg: totals['zinc_mg'] ?? 0.0,
      potassiumMg: totals['potassium_mg'] ?? 0.0,
      sodiumMg: totals['sodium_mg'] ?? 0.0,
      vitaminCMg: totals['vitamin_c_mg'] ?? 0.0,
      folateUg: totals['folate_ug'] ?? 0.0,
      vitaminB6Mg: totals['vitamin_b6_mg'] ?? 0.0,
      progressPercentages: progress,
    );
  }
}
