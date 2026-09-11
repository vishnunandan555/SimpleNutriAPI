from datetime import date, datetime
from backend.app.schemas.cycle import CyclePhaseResponse, PhaseNutrientInfo

PHASE_CONFIGS = {
    "menstrual": {
        "id": "menstrual",
        "name": "Menstrual Phase",
        "day_range": "Days 1 – 5",
        "description": "Uterine lining shedding with active micronutrient losses (particularly iron). Prioritize replenishing iron, anti-inflammatory foods, magnesium for muscle relaxation, and vitamin C to enhance iron bioavailability.",
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="iron_mg",
                nutrient_name="Iron",
                biological_role="Essential for replenishing hemoglobin losses during menstruation and preventing fatigue.",
                top_food_sources=["Cheera (Amaranth)", "Palak (Spinach)", "Bajra", "Ragi", "Moringa", "Chickpeas"]
            ),
            PhaseNutrientInfo(
                nutrient_id="vitamin_c_mg",
                nutrient_name="Vitamin C",
                biological_role="Significantly enhances gastrointestinal absorption of non-heme plant iron by reducing ferric to ferrous iron.",
                top_food_sources=["Amla", "Papaya", "Moringa Leaves", "Tomatoes", "Citrus"]
            ),
            PhaseNutrientInfo(
                nutrient_id="magnesium_mg",
                nutrient_name="Magnesium",
                biological_role="Acts as a natural neuromuscular relaxant, helping alleviate uterine cramping and smooth muscle contractions.",
                top_food_sources=["Pumpkin Seeds", "Almonds", "Ragi", "Spinach", "Moong Dal"]
            )
        ],
        "tags": ["iron", "vitamin_c", "magnesium", "anti_inflammatory", "menstrual_phase"],
        "dietary_tips": [
            "Pair iron-rich lentils or greens with vitamin-C sources (e.g. lemon juice on dal or amla) to multiply absorption.",
            "Incorporate warming spices like ginger and turmeric which contain natural anti-inflammatory compounds.",
            "Stay well hydrated with warm soups, broths, and tender coconut water."
        ]
    },
    "follicular": {
        "id": "follicular",
        "name": "Follicular Phase",
        "day_range": "Days 6 – 13",
        "description": "Estrogen levels rise steadily as follicles mature. Metabolism favors energy utilization and tissue repair. Focus on lean protein, B-vitamins for cellular energy, and zinc for follicular development.",
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="protein_g",
                nutrient_name="Quality Protein",
                biological_role="Provides amino acid building blocks for cellular growth, follicular development, and sustained stamina.",
                top_food_sources=["Moong Dal", "Eggs", "Chickpeas", "Paneer", "Quinoa", "Salmon"]
            ),
            PhaseNutrientInfo(
                nutrient_id="folate_ug",
                nutrient_name="Folate & B-Vitamins",
                biological_role="Crucial for DNA synthesis, rapid cell turnover, and neurotransmitter regulation.",
                top_food_sources=["Whole Green Moong", "Chickpeas", "Spinach", "Oats", "Beetroot"]
            ),
            PhaseNutrientInfo(
                nutrient_id="zinc_mg",
                nutrient_name="Zinc",
                biological_role="Supports healthy hormone receptor signaling and enzymatic antioxidant defenses.",
                top_food_sources=["Pumpkin Seeds", "Sesame Seeds", "Bajra", "Eggs"]
            )
        ],
        "tags": ["protein", "folate", "zinc", "b_vitamins", "follicular_phase"],
        "dietary_tips": [
            "Incorporate fresh sprouted beans (like green moong) for higher enzyme and bioavailable B-vitamin content.",
            "Focus on vibrant salads, lightly steamed veggies, and whole ancient grains like oats and foxtail millet.",
            "Support gut health with probiotic curd/yogurt to assist optimal estrogen metabolism."
        ]
    },
    "ovulatory": {
        "id": "ovulatory",
        "name": "Ovulatory Phase",
        "day_range": "Days 14 – 16",
        "description": "Luteinizing Hormone (LH) and estrogen surge to trigger ovulation. Support liver detoxification of excess estrogen and cellular protection with dietary fiber, glutathione precursors, and zinc.",
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="fiber_g",
                nutrient_name="Dietary Fiber",
                biological_role="Binds metabolized estrogen in the digestive tract to facilitate healthy excretion and maintain hormonal equilibrium.",
                top_food_sources=["Chia Seeds", "Rolled Oats", "Ragi", "Chickpeas", "Kidney Beans"]
            ),
            PhaseNutrientInfo(
                nutrient_id="zinc_mg",
                nutrient_name="Zinc",
                biological_role="Assists follicle rupture and promotes healthy progesterone production from the corpus luteum.",
                top_food_sources=["Sesame Seeds", "Pumpkin Seeds", "Bajra", "Whole Wheat"]
            ),
            PhaseNutrientInfo(
                nutrient_id="potassium_mg",
                nutrient_name="Potassium & Electrolytes",
                biological_role="Counters fluid retention and supports vascular smooth muscle tone during peak estrogen.",
                top_food_sources=["Beetroot", "Sweet Potato", "Spinach", "Coconut", "Lentils"]
            )
        ],
        "tags": ["fiber", "zinc", "antioxidant", "potassium", "ovulatory_phase"],
        "dietary_tips": [
            "Consume cruciferous and sulfur-rich vegetables (garlic, onions, greens) to assist hepatic estrogen processing.",
            "Add chia or flax seeds to meals to ensure adequate soluble fiber and plant lignans.",
            "Maintain moderate hydration with antioxidant-rich fruits and herbal infusions."
        ]
    },
    "luteal": {
        "id": "luteal",
        "name": "Luteal Phase",
        "day_range": "Days 17 – Cycle End",
        "description": "Progesterone dominates, resting metabolic rate modestly increases, and insulin sensitivity may slightly decrease. Prioritize magnesium, vitamin B6, calcium, and complex carbs to stabilize mood, minimize water retention, and ease PMS.",
        "nutrients": [
            PhaseNutrientInfo(
                nutrient_id="magnesium_mg",
                nutrient_name="Magnesium",
                biological_role="Essential cofactor for neurotransmitter synthesis (GABA, serotonin) and reducing premenstrual tension and fluid retention.",
                top_food_sources=["Pumpkin Seeds", "Almonds", "Ragi", "Jowar", "Spinach"]
            ),
            PhaseNutrientInfo(
                nutrient_id="vitamin_b6_mg",
                nutrient_name="Vitamin B6 (Pyridoxine)",
                biological_role="Works synergistically with magnesium to synthesize dopamine and serotonin, modulating premenstrual mood shifts.",
                top_food_sources=["Garlic", "Salmon", "Chickpeas", "Sweet Potato", "Turmeric"]
            ),
            PhaseNutrientInfo(
                nutrient_id="calcium_mg",
                nutrient_name="Calcium",
                biological_role="Clinically shown in dietary trials to diminish physical and emotional symptoms of luteal phase syndrome.",
                top_food_sources=["Sesame Seeds", "Moringa", "Ragi", "Paneer", "Curd"]
            ),
            PhaseNutrientInfo(
                nutrient_id="carbohydrate_g",
                nutrient_name="Complex Carbohydrates",
                biological_role="Provides sustained glucose release to prevent reactive hypoglycemia and carb cravings while supporting serotonin production.",
                top_food_sources=["Sweet Potato", "Whole Wheat", "Rolled Oats", "Bajra", "Jowar"]
            )
        ],
        "tags": ["magnesium", "vitamin_b6", "calcium", "complex_carbs", "luteal_phase", "pms_support"],
        "dietary_tips": [
            "Choose unrefined whole grains and roots (sweet potato, ragi, jowar) over refined sugars to prevent energy crashes.",
            "Incorporate a handful of roasted pumpkin seeds and almonds for concentrated magnesium and healthy fats.",
            "Moderate caffeine and high sodium intake to reduce fluid retention and breast tenderness."
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
            priority_nutrients=config["nutrients"],
            recommended_tags=config["tags"],
            dietary_tips=config["dietary_tips"]
        )

    @staticmethod
    def get_all_phases():
        return list(PHASE_CONFIGS.values())
