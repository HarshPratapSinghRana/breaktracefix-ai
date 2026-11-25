import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.base import Base

# Database engine config
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized: bool = False

def init_db() -> None:
    """Initialize database tables."""
    # Import all models so Base has them registered
    import backend.app.models.tenant  # noqa
    import backend.app.models.user  # noqa
    import backend.app.models.assessment  # noqa
    import backend.app.models.attack  # noqa
    import backend.app.models.authorization  # noqa
    import backend.app.models.trace  # noqa
    import backend.app.models.finding  # noqa
    import backend.app.models.patch  # noqa
    import backend.app.models.mcp  # noqa
    import backend.app.models.rag  # noqa
    
    Base.metadata.create_all(bind=engine)

def ensure_db_ready() -> None:
    """Ensure database tables and initial seed data are populated (serverless cold-start safe)."""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            db = SessionLocal()
            from backend.app.db.seed import seed_database
            seed_database(db)
            db.close()
            _db_initialized = True
        except Exception:
            pass

def get_db():
    """FastAPI dependency for database session."""
    ensure_db_ready()
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

