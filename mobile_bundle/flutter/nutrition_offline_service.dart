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
  final List<RecipeIngredientItem> ingredients;

  RecipeItem({
    required this.id,
    required this.name,
    this.description,
    this.cuisine,
    required this.tags,
    required this.ingredients,
  });
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

  CyclePhaseInfo({
    required this.estimatedCycleDay,
    required this.phaseId,
    required this.phaseName,
    required this.description,
    required this.priorityNutrientNames,
    required this.targetTags,
  });
}

/// Offline Nutrition Database & Logic Engine for Flutter
class NutritionOfflineService {
  static Database? _db;

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
        description: "Replenish iron losses and ease muscle cramping with magnesium and vitamin C.",
        priorityNutrientNames: ["Iron", "Vitamin C", "Magnesium"],
        targetTags: ["iron", "vitamin_c", "magnesium", "anti_inflammatory"],
      );
    } else if (cycleDay <= 13) {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "follicular",
        phaseName: "Follicular Phase",
        description: "Support rising estrogen, follicle growth, and stamina with clean protein and B-vitamins.",
        priorityNutrientNames: ["Protein", "Folate (B9)", "Zinc"],
        targetTags: ["protein", "folate", "zinc"],
      );
    } else if (cycleDay <= 16) {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "ovulatory",
        phaseName: "Ovulatory Phase",
        description: "Promote healthy estrogen clearance and cellular health with soluble fiber and antioxidants.",
        priorityNutrientNames: ["Dietary Fiber", "Zinc", "Potassium"],
        targetTags: ["fiber", "zinc", "antioxidant"],
      );
    } else {
      return CyclePhaseInfo(
        estimatedCycleDay: cycleDay,
        phaseId: "luteal",
        phaseName: "Luteal Phase",
        description: "Support progesterone synthesis and mood balance with magnesium, calcium, and complex carbs.",
        priorityNutrientNames: ["Magnesium", "Calcium", "Vitamin B6", "Complex Carbs"],
        targetTags: ["magnesium", "calcium", "vitamin_b6", "complex_carbs", "pms_support"],
      );
    }
  }

  /// Offline Kitchen Matching & Recipe Ranking
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

      // Tag bonus
      List<String> tags = [];
      try {
        final decoded = jsonDecode(r['tags_json'].toString());
        if (decoded is List) tags = decoded.map((e) => e.toString().toLowerCase()).toList();
      } catch (_) {}

      final overlap = tags.where((t) => targetTagSet.contains(t)).length;
      final score = (matchPct * 0.6) + (overlap * 20.0 * 0.4) - (missing.length * 5.0);

      ranked.add({
        'recipe_id': rid,
        'recipe_name': r['name'],
        'cuisine': r['cuisine'],
        'match_percentage': matchPct.roundToDouble(),
        'matched_count': matched.length,
        'missing_ingredients': missing.map((m) => {'food_id': m.foodId, 'quantity': m.quantity, 'unit': m.unit}).toList(),
        'score': score.roundToDouble(),
      });
    }

    ranked.sort((a, b) => (b['score'] as double).compareTo(a['score'] as double));
    return ranked;
  }
}
