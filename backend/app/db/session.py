from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from backend.app.core.config import settings

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30
else:
    # Production PostgreSQL connection pool settings for Render
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_recycle": 300,
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Optimize SQLite performance with WAL mode and memory cache
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA cache_size = -64000;")  # 64MB cache
            cursor.execute("PRAGMA temp_store = MEMORY;")
        except Exception:
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
