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

def get_db():
    """FastAPI dependency for database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

