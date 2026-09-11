from datetime import date, datetime
from backend.app.schemas.cycle import CyclePhaseResponse, PhaseNutrientInfo

PHASE_CONFIGS = {
    "menstrual": {
        "id": "menstrual",
        "name": "Menstrual Phase",
        "day_range": "Days 1 – 5",
        "description": "Support overall nutritional adequacy during menses. Focus on dietary sources of iron, vitamin C to assist plant-iron absorption, and magnesium to promote general muscle relaxation and comfort.",
        "nutrition_focus": ["iron", "vitamin_c", "magnesium", "protein", "anti_inflammatory"],
        "nutrition_context": [
            "Menstrual blood loss increases iron requirements over time.",
            "Vitamin C improves absorption of non-heme iron from plant foods.",
            "Magnesium helps support normal muscle relaxation and physical comfort."
        ],
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="iron_mg",
                nutrient_name="Iron",
                biological_role="Important for supporting normal red blood cell formation and dietary iron replenishment during menstruation.",
                nutrition_context="Important for supporting normal red blood cell formation and dietary iron replenishment during menstruation.",
                top_food_sources=["Cheera (Amaranth)", "Palak (Spinach)", "Bajra", "Ragi", "Moringa", "Chickpeas"]
            ),
            PhaseNutrientInfo(
                nutrient_id="vitamin_c_mg",
                nutrient_name="Vitamin C",
                biological_role="Helps enhance dietary absorption of non-heme plant iron when consumed together in meals.",
                nutrition_context="Helps enhance dietary absorption of non-heme plant iron when consumed together in meals.",
                top_food_sources=["Amla", "Papaya", "Moringa Leaves", "Tomatoes", "Citrus"]
            ),
            PhaseNutrientInfo(
                nutrient_id="magnesium_mg",
                nutrient_name="Magnesium",
                biological_role="Helps support normal neuromuscular function, muscle relaxation, and physical comfort.",
                nutrition_context="Helps support normal neuromuscular function, muscle relaxation, and physical comfort.",
                top_food_sources=["Pumpkin Seeds", "Almonds", "Ragi", "Spinach", "Moong Dal"]
            )
        ],
        "tags": ["iron", "vitamin_c", "magnesium", "anti_inflammatory", "menstrual_phase"],
        "dietary_tips": [
            "Pair iron-rich lentils or greens with vitamin C sources (e.g. fresh lemon juice or amla) to support optimal absorption.",
            "Incorporate gentle warming spices like ginger and turmeric into warm dishes and teas.",
            "Stay well hydrated with warm soups, broths, and water throughout the day."
        ]
    },
    "follicular": {
        "id": "follicular",
        "name": "Follicular Phase",
        "day_range": "Days 6 – 13",
        "description": "Support general vitality and cellular energy as activity levels rise. Focus on quality protein, B-vitamins, and zinc for overall daily stamina and metabolic support.",
        "nutrition_focus": ["protein", "folate", "zinc", "b_vitamins"],
        "nutrition_context": [
            "Active follicle growth and daily energy benefit from quality dietary protein.",
            "B-vitamins and folate support cellular energy pathways and vitality.",
            "Zinc supports normal enzymatic defenses and immune health."
        ],
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="protein_g",
                nutrient_name="Quality Protein",
                biological_role="Provides essential dietary amino acids to support everyday muscle recovery, tissue maintenance, and steady stamina.",
                nutrition_context="Provides essential dietary amino acids to support everyday muscle recovery, tissue maintenance, and steady stamina.",
                top_food_sources=["Moong Dal", "Eggs", "Chickpeas", "Paneer", "Quinoa", "Salmon"]
            ),
            PhaseNutrientInfo(
                nutrient_id="folate_ug",
                nutrient_name="Folate & B-Vitamins",
                biological_role="Supports normal cellular division, metabolic energy pathways, and general wellbeing.",
                nutrition_context="Supports normal cellular division, metabolic energy pathways, and general wellbeing.",
                top_food_sources=["Whole Green Moong", "Chickpeas", "Spinach", "Oats", "Beetroot"]
            ),
            PhaseNutrientInfo(
                nutrient_id="zinc_mg",
                nutrient_name="Zinc",
                biological_role="Supports normal immune function, enzymatic processes, and cellular protection.",
                nutrition_context="Supports normal immune function, enzymatic processes, and cellular protection.",
                top_food_sources=["Pumpkin Seeds", "Sesame Seeds", "Bajra", "Eggs"]
            )
        ],
        "tags": ["protein", "folate", "zinc", "b_vitamins", "follicular_phase"],
        "dietary_tips": [
            "Include freshly prepared legumes, sprouts, and whole grains for bioavailable B-vitamins and steady energy.",
            "Add colorful salads, lightly cooked vegetables, and grains like oats, quinoa, or millets to meals.",
            "Incorporate probiotic foods like curd or yogurt to support everyday gut health and digestion."
        ]
    },
    "ovulatory": {
        "id": "ovulatory",
        "name": "Ovulatory Phase",
        "day_range": "Days 14 – 16",
        "description": "Prioritize nutrient-rich whole foods, dietary fiber, and adequate hydration to support everyday digestive balance and vitality.",
        "nutrition_focus": ["fiber", "zinc", "potassium", "antioxidants"],
        "nutrition_context": [
            "Dietary fiber binds metabolized compounds to support digestive regularity.",
            "Zinc contributes to normal macronutrient metabolism and cellular maintenance.",
            "Potassium and electrolytes support cellular hydration and vascular tone."
        ],
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="fiber_g",
                nutrient_name="Dietary Fiber",
                biological_role="Promotes healthy gastrointestinal motility, digestive regularity, and overall nutrient balance.",
                nutrition_context="Promotes healthy gastrointestinal motility, digestive regularity, and overall nutrient balance.",
                top_food_sources=["Chia Seeds", "Rolled Oats", "Ragi", "Chickpeas", "Kidney Beans"]
            ),
            PhaseNutrientInfo(
                nutrient_id="zinc_mg",
                nutrient_name="Zinc",
                biological_role="Contributes to normal macronutrient metabolism, immune health, and cellular maintenance.",
                nutrition_context="Contributes to normal macronutrient metabolism, immune health, and cellular maintenance.",
                top_food_sources=["Sesame Seeds", "Pumpkin Seeds", "Bajra", "Whole Wheat"]
            ),
            PhaseNutrientInfo(
                nutrient_id="potassium_mg",
                nutrient_name="Potassium & Electrolytes",
                biological_role="Supports normal electrolyte balance, hydration, and vascular tone.",
                nutrition_context="Supports normal electrolyte balance, hydration, and vascular tone.",
                top_food_sources=["Beetroot", "Sweet Potato", "Spinach", "Coconut", "Lentils"]
            )
        ],
        "tags": ["fiber", "zinc", "antioxidant", "potassium", "ovulatory_phase"],
        "dietary_tips": [
            "Incorporate fiber-rich foods like chia seeds, oats, leafy greens, and whole legumes to support smooth digestion.",
            "Include colorful cruciferous vegetables and onions/garlic as part of balanced, diverse meals.",
            "Maintain consistent daily fluid intake with water, herbal infusions, and fresh fruits."
        ]
    },
    "luteal": {
        "id": "luteal",
        "name": "Luteal Phase",
        "day_range": "Days 17 – Cycle End",
        "description": "Support steady physical comfort, balanced energy, and mood during the premenstrual phase. Emphasize magnesium, vitamin B6, calcium, and unrefined complex carbohydrates.",
        "nutrition_focus": ["magnesium", "vitamin_b6", "calcium", "complex_carbs"],
        "nutrition_context": [
            "Magnesium and vitamin B6 work synergistically to support neurotransmitter balance and mood stability.",
            "Complex carbohydrates provide steady glucose release to support consistent daily energy.",
            "Calcium contributes to normal muscle function and general premenstrual physical comfort."
        ],
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="magnesium_mg",
                nutrient_name="Magnesium",
                biological_role="Contributes to normal nervous system functioning, psychological wellbeing, and reduction of fatigue.",
                nutrition_context="Contributes to normal nervous system functioning, psychological wellbeing, and reduction of fatigue.",
                top_food_sources=["Pumpkin Seeds", "Almonds", "Ragi", "Jowar", "Spinach"]
            ),
            PhaseNutrientInfo(
                nutrient_id="vitamin_b6_mg",
                nutrient_name="Vitamin B6 (Pyridoxine)",
                biological_role="Contributes to normal energy-yielding metabolism and regulation of hormonal activity.",
                nutrition_context="Contributes to normal energy-yielding metabolism and regulation of hormonal activity.",
                top_food_sources=["Garlic", "Salmon", "Chickpeas", "Sweet Potato", "Turmeric"]
            ),
            PhaseNutrientInfo(
                nutrient_id="calcium_mg",
                nutrient_name="Calcium",
                biological_role="Helps support normal neurotransmission, muscle function, and overall daily nutritional adequacy.",
                nutrition_context="Helps support normal neurotransmission, muscle function, and overall daily nutritional adequacy.",
                top_food_sources=["Sesame Seeds", "Moringa", "Ragi", "Paneer", "Curd"]
            ),
            PhaseNutrientInfo(
                nutrient_id="carbohydrate_g",
                nutrient_name="Complex Carbohydrates",
                biological_role="Provides steady glucose release from whole grains and roots to maintain consistent daily energy.",
                nutrition_context="Provides steady glucose release from whole grains and roots to maintain consistent daily energy.",
                top_food_sources=["Sweet Potato", "Whole Wheat", "Rolled Oats", "Bajra", "Jowar"]
            )
        ],
        "tags": ["magnesium", "vitamin_b6", "calcium", "complex_carbs", "luteal_phase", "pms_support"],
        "dietary_tips": [
            "Choose unrefined carbohydrates (such as sweet potatoes, ragi, and oats) over refined sugars for sustained energy.",
            "Enjoy a handful of roasted pumpkin seeds, nuts, or seeds for healthy fats and natural minerals.",
            "Stay mindful of excessive caffeine and high-sodium snacks to support comfort and fluid balance."
        ]
    }
}

class CycleService:
    @staticmethod
    def calculate_cycle_phase(last_period_start_str: str, cycle_length: int = 28) -> CyclePhaseResponse:
        try:
            start_date = datetime.strptime(last_period_start_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD")

        today = date.today()
        days_elapsed = (today - start_date).days
        if days_elapsed < 0:
            cycle_day = 1
        else:
            cycle_day = (days_elapsed % cycle_length) + 1

        # Phase thresholds scaled by cycle length
        # Standard 28-day reference: Menstrual 1-5, Follicular 6-13, Ovulatory 14-16, Luteal 17-28
        ovulation_day = max(12, cycle_length - 14)
        
        if cycle_day <= 5:
            phase_key = "menstrual"
        elif cycle_day < ovulation_day:
            phase_key = "follicular"
        elif cycle_day <= ovulation_day + 2:
            phase_key = "ovulatory"
        else:
            phase_key = "luteal"

        config = PHASE_CONFIGS[phase_key]

        return CyclePhaseResponse(
            estimated_cycle_day=cycle_day,
            cycle_length_days=cycle_length,
            phase_id=config["id"],
            phase_name=config["name"],
            phase_day_range=config["day_range"],
            description=config["description"],
            nutrition_focus=config.get("nutrition_focus", config["tags"]),
            nutrition_context=config.get("nutrition_context", []),
            priority_nutrients=config["nutrients"],
            recommended_tags=config["tags"],
            dietary_tips=config["dietary_tips"]
        )

    @staticmethod
    def get_all_phases():
        return list(PHASE_CONFIGS.values())
