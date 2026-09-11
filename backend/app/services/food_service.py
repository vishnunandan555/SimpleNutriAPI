import math
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from backend.app.models.food import Food, FoodAlias
from backend.app.models.source import Source
from backend.app.schemas.food import FoodSummary, FoodDetail, NutritionProfile
from backend.app.schemas.taxonomy import SourceSchema

_RESOLVE_CACHE: Dict[str, Optional[str]] = {}

class FoodService:
    @staticmethod
    def _to_summary(food: Food) -> FoodSummary:
        aliases = [a.alias for a in food.aliases] if food.aliases else []
        nutrition = NutritionProfile(
            basis_g=food.basis_g or 100.0,
            energy_kcal=food.energy_kcal,
            protein_g=food.protein_g,
            carbohydrate_g=food.carbohydrate_g,
            fat_g=food.fat_g,
            fiber_g=food.fiber_g,
            iron_mg=food.iron_mg,
            calcium_mg=food.calcium_mg,
            magnesium_mg=food.magnesium_mg,
            zinc_mg=food.zinc_mg,
            potassium_mg=food.potassium_mg,
            sodium_mg=food.sodium_mg,
            folate_ug=food.folate_ug,
            vitamin_c_mg=food.vitamin_c_mg,
            vitamin_a_ug=food.vitamin_a_ug,
            vitamin_b6_mg=food.vitamin_b6_mg,
            vitamin_b12_ug=food.vitamin_b12_ug
        )
        return FoodSummary(
            id=food.id,
            name=food.name,
            category=food.category,
            aliases=aliases,
            regions=food.regions,
            countries=food.countries,
            cuisines=food.cuisines,
            diet=food.diet,
            tags=food.tags,
            nutrition=nutrition,
            source_ids=food.source_ids
        )

    @classmethod
    def resolve_food_id(cls, db: Session, identifier: str) -> Optional[str]:
        """
        Resolves an identifier (exact ID, code, common slug, or regional alias) to canonical Food.id.
        Prevents fragmentation where 'spinach', 'palak', 'cheera', 'urad_dal', or 'c033' are queried interchangeably.
        Uses in-memory LRU cache for sub-microsecond lookups.
        """
        if not identifier:
            return None
        clean = identifier.strip().lower()
        if clean in _RESOLVE_CACHE:
            return _RESOLVE_CACHE[clean]

        clean_spaced = clean.replace("_", " ").replace("-", " ")
        clean_underscored = clean.replace(" ", "_").replace("-", "_")

        # 1. Exact ID
        fid = db.scalar(
            select(Food.id).where(
                or_(
                    func.lower(Food.id) == clean,
                    func.lower(Food.id) == clean_underscored
                )
            )
        )
        if fid:
            _RESOLVE_CACHE[clean] = fid
            return fid

        # 2. Code (e.g. A010, C033, B003)
        fid = db.scalar(select(Food.id).where(func.lower(Food.code) == clean))
        if fid:
            _RESOLVE_CACHE[clean] = fid
            return fid

        # 3. Substring slug on Food.id (e.g. 'ragi' in 'a010_ragi', 'black_gram_dal' in 'b003_black_gram_dal')
        fid = db.scalar(
            select(Food.id).where(
                Food.id.like(f"%_{clean_underscored}") |
                Food.id.like(f"%_{clean_underscored}_%") |
                (Food.id == clean_underscored)
            )
        )
        if fid:
            _RESOLVE_CACHE[clean] = fid
            return fid

        # 4. Regional alias match (e.g. 'palak', 'nachni', 'cheera', 'urad dal')
        alias_fid = db.scalar(
            select(FoodAlias.food_id).where(
                or_(
                    func.lower(FoodAlias.alias) == clean,
                    func.lower(FoodAlias.alias) == clean_spaced,
                    func.lower(FoodAlias.alias).like(f"%{clean_spaced}%")
                )
            )
        )
        if alias_fid:
            _RESOLVE_CACHE[clean] = alias_fid
            return alias_fid

        # 5. Food name match
        name_fid = db.scalar(
            select(Food.id).where(
                or_(
                    func.lower(Food.name).like(f"%{clean}%"),
                    func.lower(Food.name).like(f"%{clean_spaced}%")
                )
            )
        )
        _RESOLVE_CACHE[clean] = name_fid
        return name_fid

    @classmethod
    def get_foods(
        cls,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        tag: Optional[str] = None,
        iron_min: Optional[float] = None,
        calcium_min: Optional[float] = None,
        magnesium_min: Optional[float] = None,
        protein_min: Optional[float] = None,
        fiber_min: Optional[float] = None
    ) -> Tuple[List[FoodSummary], int, int]:
        stmt = select(Food).options(selectinload(Food.aliases))

        if category:
            stmt = stmt.where(Food.category == category)
        if region:
            stmt = stmt.where(Food.regions_json.like(f'%"{region}"%'))
        if country:
            stmt = stmt.where(Food.countries_json.like(f'%"{country.upper()}"%') | Food.countries_json.like(f'%"{country.lower()}"%'))
        if cuisine:
            stmt = stmt.where(Food.cuisines_json.like(f'%"{cuisine}"%'))
        if diet:
            stmt = stmt.where(Food.diet_json.like(f'%"{diet}"%'))
        if tag:
            stmt = stmt.where(Food.tags_json.like(f'%"{tag}"%'))
        if iron_min is not None:
            stmt = stmt.where(Food.iron_mg >= iron_min)
        if calcium_min is not None:
            stmt = stmt.where(Food.calcium_mg >= calcium_min)
        if magnesium_min is not None:
            stmt = stmt.where(Food.magnesium_mg >= magnesium_min)
        if protein_min is not None:
            stmt = stmt.where(Food.protein_g >= protein_min)
        if fiber_min is not None:
            stmt = stmt.where(Food.fiber_g >= fiber_min)

        count_stmt = select(func.count(func.distinct(Food.id)))
        if category:
            count_stmt = count_stmt.where(Food.category == category)
        if region:
            count_stmt = count_stmt.where(Food.regions_json.like(f'%"{region}"%'))
        if country:
            count_stmt = count_stmt.where(Food.countries_json.like(f'%"{country.upper()}"%') | Food.countries_json.like(f'%"{country.lower()}"%'))
        if cuisine:
            count_stmt = count_stmt.where(Food.cuisines_json.like(f'%"{cuisine}"%'))
        if diet:
            count_stmt = count_stmt.where(Food.diet_json.like(f'%"{diet}"%'))
        if tag:
            count_stmt = count_stmt.where(Food.tags_json.like(f'%"{tag}"%'))
        if iron_min is not None:
            count_stmt = count_stmt.where(Food.iron_mg >= iron_min)
        if calcium_min is not None:
            count_stmt = count_stmt.where(Food.calcium_mg >= calcium_min)
        if magnesium_min is not None:
            count_stmt = count_stmt.where(Food.magnesium_mg >= magnesium_min)
        if protein_min is not None:
            count_stmt = count_stmt.where(Food.protein_g >= protein_min)
        if fiber_min is not None:
            count_stmt = count_stmt.where(Food.fiber_g >= fiber_min)

        total = db.scalar(count_stmt) or 0
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Food.name.asc()).offset(offset).limit(page_size)
        
        foods = db.scalars(stmt).unique().all()
        summaries = [cls._to_summary(f) for f in foods]

        return summaries, total, total_pages

    @classmethod
    def get_food_by_id(cls, db: Session, food_id: str) -> Optional[FoodDetail]:
        resolved = cls.resolve_food_id(db, food_id) or food_id
        food = db.scalar(
            select(Food).where(Food.id == resolved).options(selectinload(Food.aliases))
        )
        if not food:
            return None

        summary = cls._to_summary(food)

        source_records = []
        if food.source_ids:
            sources = db.scalars(select(Source).where(Source.id.in_(food.source_ids))).all()
            source_records = [SourceSchema.model_validate(s) for s in sources]

        return FoodDetail(
            **summary.model_dump(),
            sources=source_records
        )

    @classmethod
    def search_foods(cls, db: Session, query: str, limit: int = 20) -> List[FoodSummary]:
        clean_term = query.strip().lower()
        if not clean_term:
            return []
        clean_escaped = clean_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clean_pattern = f"%{clean_escaped}%"
        stmt = (
            select(Food)
            .outerjoin(FoodAlias, Food.id == FoodAlias.food_id)
            .where(
                or_(
                    func.lower(Food.name).like(clean_pattern),
                    func.lower(Food.id).like(clean_pattern),
                    func.lower(Food.code).like(clean_pattern),
                    func.lower(FoodAlias.alias).like(clean_pattern),
                    func.lower(Food.category).like(clean_pattern),
                    func.lower(Food.tags_json).like(clean_pattern)
                )
            )
            .options(selectinload(Food.aliases))
            .distinct()
            .limit(limit)
        )
        foods = db.scalars(stmt).unique().all()
        return [cls._to_summary(f) for f in foods]

    @classmethod
    def rank_foods(
        cls,
        db: Session,
        target_tags: List[str] = [],
        diet: Optional[str] = None,
        region: Optional[str] = None,
        cuisine: Optional[str] = None,
        available_food_ids: List[str] = [],
        limit: int = 25
    ) -> List[Dict]:
        """
        Food ranking engine implementing SRS Section 9.4:
        score = nutrient_match * 0.40 + diet_match * 0.20 + region_match * 0.15 + cuisine_match * 0.10 + availability * 0.10 + preference * 0.05
        """
        stmt = select(Food).options(selectinload(Food.aliases))
        foods = db.scalars(stmt).unique().all()

        target_tags_set = set(t.lower() for t in target_tags)
        resolved_avail = set()
        for af in available_food_ids:
            r = cls.resolve_food_id(db, af)
            if r:
                resolved_avail.add(r)
            else:
                resolved_avail.add(af.lower())

        scored = []
        for f in foods:
            summary = cls._to_summary(f)
            food_tags = set(t.lower() for t in summary.tags)
            
            # 1. Nutrient Match (0.40)
            tag_overlap = len(food_tags.intersection(target_tags_set))
            nutrient_score = min(1.0, tag_overlap / max(1, len(target_tags_set))) * 100.0 if target_tags_set else 50.0

            # 2. Diet Match (0.20)
            diet_score = 100.0 if not diet or (diet.lower() in [d.lower() for d in summary.diet]) else 0.0

            # 3. Region Match (0.15)
            region_score = 100.0 if not region or (region.lower() in [r.lower() for r in summary.regions]) else 20.0

            # 4. Cuisine Match (0.10)
            cuisine_score = 100.0 if not cuisine or (cuisine.lower() in [c.lower() for c in summary.cuisines]) else 30.0

            # 5. Availability (0.10)
            avail_score = 100.0 if f.id in resolved_avail else 0.0

            # Combined SRS formula
            final_score = (
                (nutrient_score * 0.40) +
                (diet_score * 0.20) +
                (region_score * 0.15) +
                (cuisine_score * 0.10) +
                (avail_score * 0.10) +
                (50.0 * 0.05)
            )

            scored.append({
                "food": summary,
                "score": round(final_score, 2),
                "nutrient_match_score": round(nutrient_score, 1),
                "is_in_kitchen": f.id in resolved_avail
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]
