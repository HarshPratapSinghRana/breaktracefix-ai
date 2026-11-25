from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.assessments import router as assessments_router
from backend.app.api.v1.attacks import router as attacks_router
from backend.app.api.v1.authorization import router as auth_intel_router
from backend.app.api.v1.traces import router as traces_router
from backend.app.api.v1.reproduction import router as repro_router
from backend.app.api.v1.source_analyzer import router as source_router
from backend.app.api.v1.mcp_inspector import router as mcp_router
from backend.app.api.v1.rag_auditor import router as rag_router
from backend.app.api.v1.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(assessments_router)
api_router.include_router(attacks_router)
api_router.include_router(auth_intel_router)
api_router.include_router(traces_router)
api_router.include_router(repro_router)
api_router.include_router(source_router)
api_router.include_router(mcp_router)
api_router.include_router(rag_router)
api_router.include_router(reports_router)
