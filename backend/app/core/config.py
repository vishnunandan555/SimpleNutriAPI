import os
import shutil
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_PATH = BASE_DIR / "data" / "nutrition.db"

# Serverless environments (Vercel, AWS Lambda) have read-only root filesystems
if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) and not os.getenv("DATABASE_URL"):
    TMP_SQLITE_PATH = Path("/tmp/nutrition.db")
    if not TMP_SQLITE_PATH.exists() and DEFAULT_SQLITE_PATH.exists():
        try:
            shutil.copyfile(DEFAULT_SQLITE_PATH, TMP_SQLITE_PATH)
        except Exception:
            pass
    if TMP_SQLITE_PATH.exists():
        DEFAULT_SQLITE_PATH = TMP_SQLITE_PATH

class Settings(BaseSettings):
    PROJECT_NAME: str = "SimpleNutri API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Production REST API for Food Nutrition Knowledge Base, "
        "evidence-based cycle personalization, and kitchen inventory matching."
    )
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database config: default to SQLite nutrition.db, or Render/Supabase PostgreSQL URL
    raw_db_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
    
    @property
    def DATABASE_URL(self) -> str:
        url = self.raw_db_url
        # Render specifies postgres:// but SQLAlchemy requires postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    CORS_ORIGINS: list[str] = ["*"]

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
