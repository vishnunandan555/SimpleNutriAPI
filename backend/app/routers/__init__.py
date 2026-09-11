from backend.app.routers.health import router as health_router
from backend.app.routers.taxonomy import router as taxonomy_router
from backend.app.routers.foods import router as foods_router
from backend.app.routers.ingredients import router as ingredients_router
from backend.app.routers.nutrients import router as nutrients_router
from backend.app.routers.recipes import router as recipes_router
from backend.app.routers.recommendations import router as recommendations_router

__all__ = [
    "health_router",
    "taxonomy_router",
    "foods_router",
    "ingredients_router",
    "nutrients_router",
    "recipes_router",
    "recommendations_router"
]
