import math
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from backend.app.models.recipe import Recipe, RecipeIngredient
from backend.app.models.food import Food
from backend.app.models.source import Source
from backend.app.schemas.recipe import (
    RecipeSummary, RecipeDetail, RecipeIngredientItem,
    RankedRecipe, ShoppingListResponse, ShoppingListItem
)
from backend.app.schemas.taxonomy import SourceSchema
from backend.app.services.food_service import FoodService

class RecipeService:
    @staticmethod
    def _to_summary(recipe: Recipe) -> RecipeSummary:
        ingredients = []
        for ing in recipe.ingredients:
            food_name = ing.food.name if ing.food else ing.food_id
            ingredients.append(
                RecipeIngredientItem(
                    food_id=ing.food_id,
                    food_name=food_name,
                    quantity=ing.quantity,
                    unit=ing.unit
                )
            )

        return RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            region=recipe.region,
            country=recipe.country,
            cuisine=recipe.cuisine,
            diet=recipe.diet,
            prep_time_min=recipe.prep_time_min,
            cook_time_min=recipe.cook_time_min,
            servings=recipe.servings,
            tags=recipe.tags,
            meal_type=recipe.meal_type,
            instructions=recipe.instructions,
            ingredients=ingredients,
            source_ids=recipe.source_ids
        )

    @staticmethod
    def _is_ingredient_matched(
        ing: RecipeIngredient,
        available_set: set,
        resolved_available_ids: set
    ) -> bool:
        """
        Determines if a recipe ingredient is satisfied by the user's available inventory.
        Matches exact IDs, resolved canonical IDs, ingredient token slugs, or regional aliases.
        """
        fid = ing.food_id.lower()
        if fid in available_set or fid in resolved_available_ids:
            return True

        for af in available_set:
            clean_af = af.replace("-", "_").strip()
            if not clean_af:
                continue

            # Check token overlap e.g. "rice" in "a015_rice_raw_milled"
            tokens = [t for t in fid.split("_") if len(t) > 2]
            if clean_af in tokens or any(t == clean_af for t in tokens):
                return True

            if ing.food:
                name_clean = ing.food.name.lower()
                clean_spaced = clean_af.replace("_", " ")
                if clean_spaced in name_clean:
                    return True
                for al in ing.food.aliases:
                    if clean_spaced in al.alias.lower():
                        return True
        return False

    @classmethod
    def get_recipes(
        cls,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        region: Optional[str] = None,
        country: Optional[str] = None,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        tag: Optional[str] = None,
        ingredient_food_id: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> Tuple[List[RecipeSummary], int, int]:
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.food)
            )
        )

        if region:
            stmt = stmt.where(Recipe.region == region)
        if country:
            stmt = stmt.where(Recipe.country == country)
        if cuisine:
            stmt = stmt.where(Recipe.cuisine == cuisine)
        if diet:
            stmt = stmt.where(Recipe.diet_json.like(f'%"{diet}"%'))
        if tag:
            stmt = stmt.where(Recipe.tags_json.like(f'%"{tag}"%'))
        if meal_type:
            stmt = stmt.where(Recipe.meal_type_json.like(f'%"{meal_type}"%'))
        if ingredient_food_id:
            resolved_ing = FoodService.resolve_food_id(db, ingredient_food_id) or ingredient_food_id
            stmt = stmt.join(Recipe.ingredients).where(
                or_(
                    RecipeIngredient.food_id == resolved_ing,
                    RecipeIngredient.food_id.like(f"%{ingredient_food_id.replace('-', '_')}%")
                )
            )

        count_stmt = select(func.count(func.distinct(Recipe.id)))
        if region:
            count_stmt = count_stmt.where(Recipe.region == region)
        if country:
            count_stmt = count_stmt.where(Recipe.country == country)
        if cuisine:
            count_stmt = count_stmt.where(Recipe.cuisine == cuisine)
        if diet:
            count_stmt = count_stmt.where(Recipe.diet_json.like(f'%"{diet}"%'))
        if tag:
            count_stmt = count_stmt.where(Recipe.tags_json.like(f'%"{tag}"%'))
        if meal_type:
            count_stmt = count_stmt.where(Recipe.meal_type_json.like(f'%"{meal_type}"%'))
        if ingredient_food_id:
            resolved_ing = FoodService.resolve_food_id(db, ingredient_food_id) or ingredient_food_id
            count_stmt = count_stmt.join(Recipe.ingredients).where(
                or_(
                    RecipeIngredient.food_id == resolved_ing,
                    RecipeIngredient.food_id.like(f"%{ingredient_food_id.replace('-', '_')}%")
                )
            )

        total = db.scalar(count_stmt) or 0
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Recipe.name.asc()).offset(offset).limit(page_size)

        recipes = db.scalars(stmt).unique().all()
        summaries = [cls._to_summary(r) for r in recipes]

        return summaries, total, total_pages

    @classmethod
    def get_recipe_by_id(cls, db: Session, recipe_id: str) -> Optional[RecipeDetail]:
        clean = recipe_id.strip().lower()
        recipe = db.scalar(
            select(Recipe)
            .where(
                or_(
                    func.lower(Recipe.id) == clean,
                    func.lower(Recipe.id) == clean.replace("-", "_"),
                    func.lower(Recipe.name).like(f"%{clean.replace('_', ' ')}%")
                )
            )
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.food)
            )
        )
        if not recipe:
            return None

        summary = cls._to_summary(recipe)

        source_records = []
        if recipe.source_ids:
            sources = db.scalars(select(Source).where(Source.id.in_(recipe.source_ids))).all()
            source_records = [SourceSchema.model_validate(s) for s in sources]

        return RecipeDetail(
            **summary.model_dump(),
            sources=source_records
        )

    @classmethod
    def search_recipes(cls, db: Session, query: str, limit: int = 20) -> List[RecipeSummary]:
        clean_term = query.strip().lower()
        if not clean_term:
            return []
        clean_escaped = clean_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clean_pattern = f"%{clean_escaped}%"
        stmt = (
            select(Recipe)
            .where(
                or_(
                    func.lower(Recipe.name).like(clean_pattern),
                    func.lower(Recipe.description).like(clean_pattern),
                    func.lower(Recipe.cuisine).like(clean_pattern),
                    func.lower(Recipe.tags_json).like(clean_pattern)
                )
            )
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.food)
            )
            .distinct()
            .limit(limit)
        )
        recipes = db.scalars(stmt).unique().all()
        return [cls._to_summary(r) for r in recipes]

    @classmethod
    def rank_recipes(
        cls,
        db: Session,
        available_food_ids: List[str],
        target_tags: List[str] = [],
        diet: Optional[str] = None,
        cuisine: Optional[str] = None,
        region: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> List[RankedRecipe]:
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.food)
            )
        )

        if diet:
            stmt = stmt.where(Recipe.diet_json.like(f'%"{diet}"%'))
        if cuisine:
            stmt = stmt.where(Recipe.cuisine == cuisine)
        if region:
            stmt = stmt.where(Recipe.region == region)
        if meal_type:
            stmt = stmt.where(Recipe.meal_type_json.like(f'%"{meal_type}"%'))

        recipes = db.scalars(stmt).unique().all()

        available_set = set(f.strip().lower() for f in available_food_ids if f.strip())
        resolved_available_ids = set()
        for af in available_food_ids:
            r = FoodService.resolve_food_id(db, af)
            if r:
                resolved_available_ids.add(r.lower())

        target_tags_set = set(t.strip().lower() for t in target_tags)

        ranked = []
        for r in recipes:
            summary = cls._to_summary(r)
            ing_ids = [ing.food_id.lower() for ing in summary.ingredients]
            total_ings = len(ing_ids) if ing_ids else 1

            ing_map = {i.food_id: i for i in r.ingredients}
            matched = []
            missing = []
            for ing in summary.ingredients:
                model_ing = ing_map.get(ing.food_id)
                if model_ing and cls._is_ingredient_matched(model_ing, available_set, resolved_available_ids):
                    matched.append(ing.food_id)
                else:
                    missing.append(ing)

            match_pct = round((len(matched) / total_ings) * 100, 1)

            # Nutrition relevance bonus
            recipe_tags = set(t.lower() for t in summary.tags)
            tag_overlap = len(recipe_tags.intersection(target_tags_set))
            nutrition_score = tag_overlap * 20.0

            # Score formula based on SRS Section 10:
            # Score = (Kitchen Match % * 0.6) + (Nutrition Tag Score * 0.4) - (Missing count * 5)
            score = (match_pct * 0.6) + (nutrition_score * 0.4) - (len(missing) * 5.0)

            ranked.append(
                RankedRecipe(
                    recipe=summary,
                    match_percentage=match_pct,
                    matching_ingredients=matched,
                    missing_ingredients=missing,
                    score=round(score, 2)
                )
            )

        # Sort by score descending
        ranked.sort(key=lambda x: x.score, reverse=True)
        return ranked

    @classmethod
    def generate_shopping_list(
        cls,
        db: Session,
        selected_recipe_ids: List[str],
        kitchen_inventory_food_ids: List[str] = []
    ) -> ShoppingListResponse:
        recipes = db.scalars(
            select(Recipe)
            .where(
                or_(
                    Recipe.id.in_(selected_recipe_ids),
                    Recipe.id.in_([r.replace("-", "_") for r in selected_recipe_ids])
                )
            )
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.food)
            )
        ).unique().all()

        kitchen_set = set(f.strip().lower() for f in kitchen_inventory_food_ids if f.strip())
        resolved_kitchen_ids = set()
        for kf in kitchen_inventory_food_ids:
            r = FoodService.resolve_food_id(db, kf)
            if r:
                resolved_kitchen_ids.add(r.lower())

        missing_map: Dict[str, ShoppingListItem] = {}

        for r in recipes:
            for ing in r.ingredients:
                if cls._is_ingredient_matched(ing, kitchen_set, resolved_kitchen_ids):
                    continue  # already present in kitchen pantry

                fid = ing.food_id.lower()
                food_name = ing.food.name if ing.food else ing.food_id
                food_cat = ing.food.category if ing.food else "general"

                if fid in missing_map:
                    # Deduplicate & add quantity if same unit
                    if missing_map[fid].unit == ing.unit:
                        missing_map[fid].quantity += ing.quantity
                else:
                    missing_map[fid] = ShoppingListItem(
                        food_id=ing.food_id,
                        food_name=food_name,
                        quantity=ing.quantity,
                        unit=ing.unit,
                        category=food_cat
                    )

        items = list(missing_map.values())
        items.sort(key=lambda x: (x.category or "", x.food_name))

        return ShoppingListResponse(
            items=items,
            selected_recipe_count=len(recipes),
            total_missing_items=len(items)
        )
