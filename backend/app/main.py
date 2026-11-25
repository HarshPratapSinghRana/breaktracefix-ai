import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.api.v1.router import api_router
from backend.app.schemas.common import HealthStatus, ResponseEnvelope

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("breaktracefix")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info("Initializing BreakTraceFix AI database and seed catalogs...")
    try:
        init_db()
        db = SessionLocal()
        seed_database(db)
        db.close()
        logger.info("Database initialized and seeded successfully.")
    except Exception as e:
        logger.error(f"Error during startup database initialization: {e}")
    yield
    logger.info("BreakTraceFix AI shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BreakTraceFix AI - Break It. Trace It. Fix It. GenAI Security Research, Vulnerability Assessment & Runtime Defense Platform.",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An internal server error occurred.", "error": str(exc)}
    )

# Health Check
@app.get("/api/health", response_model=ResponseEnvelope[HealthStatus], tags=["System"])
def health_check():
    return ResponseEnvelope(
        data=HealthStatus(
            status="ok",
            version=settings.VERSION,
            project=settings.PROJECT_NAME,
            database="connected",
            environment=settings.ENVIRONMENT
        ),
        message="BreakTraceFix AI API is fully operational."
    )

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

