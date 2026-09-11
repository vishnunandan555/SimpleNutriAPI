import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.app.core.config import settings
from backend.app.routers.health import router as health_router
from backend.app.routers.taxonomy import router as taxonomy_router
from backend.app.routers.foods import router as foods_router
from backend.app.routers.ingredients import router as ingredients_router
from backend.app.routers.nutrients import router as nutrients_router
from backend.app.routers.recipes import router as recipes_router
from backend.app.routers.recommendations import router as recommendations_router
from backend.scripts.seed_db import seed_database

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

TAGS_METADATA = [
    {
        "name": "Health & Versioning",
        "description": "System health monitoring, uptime probes, and authoritative dataset provenance/version metadata.",
    },
    {
        "name": "Foods",
        "description": "Authoritative food composition database (ICMR-NIN IFCT 2017 & USDA FDC). Portions per 100g.",
    },
    {
        "name": "Ingredients",
        "description": "Standardized kitchen ingredients with sub-50ms autocomplete across 14 Indian languages.",
    },
    {
        "name": "Nutrients",
        "description": "Master catalog of 21 tracked nutrients, standard units, and highest-density food rankings.",
    },
    {
        "name": "Recipes",
        "description": "Curated Indian and global recipes with canonical ingredient linkages and dietary properties.",
    },
    {
        "name": "Cycle & Recommendations",
        "description": "Cycle-aligned nutritional priorities, 6-factor food ranking, kitchen recipe matching, and deduplicated shopping lists.",
    },
    {
        "name": "Taxonomy",
        "description": "System classification categories, geographical regions, countries, cuisines, and diets.",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize and seed DB on startup
    try:
        seed_database()
    except Exception as e:
        print(f"Startup DB initialization notice: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Gzip compression for payloads >= 1KB (reduces network transfer by 70-80%)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware for open API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("simplenutri")

# Latency tracking and security headers middleware
@app.middleware("http")
async def add_security_and_timing_headers(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "status_code": 422}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "status_code": 500}
    )

# Register API Routers
app.include_router(health_router)
app.include_router(taxonomy_router)
app.include_router(foods_router)
app.include_router(ingredients_router)
app.include_router(nutrients_router)
app.include_router(recipes_router)
app.include_router(recommendations_router)

# Mount Frontend static assets if available
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {
            "message": "SimpleNutri API is running.",
            "docs_url": "/docs",
            "health_url": "/health"
        }
else:
    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_root():
        return {
            "message": "SimpleNutri API is running.",
            "docs_url": "/docs",
            "health_url": "/health"
        }
