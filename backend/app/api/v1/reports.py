from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.reporting.engine import SecurityReportGenerator

router = APIRouter(prefix="/reports", tags=["Security Reports"])

@router.get("/json/{assessment_id}", response_model=ResponseEnvelope[dict])
def get_json_report(assessment_id: str, db: Session = Depends(get_db)):
    """Generate comprehensive JSON security report for an assessment."""
    try:
        report = SecurityReportGenerator.generate_json_report(db, assessment_id)
        return ResponseEnvelope(data=report)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/html/{assessment_id}")
def get_html_report(assessment_id: str, db: Session = Depends(get_db)):
    """Generate and return styled technical HTML report."""
    try:
        html = SecurityReportGenerator.generate_html_report(db, assessment_id)
        return Response(content=html, media_type="text/html")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

