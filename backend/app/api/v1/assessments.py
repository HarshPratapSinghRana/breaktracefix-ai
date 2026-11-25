from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.assessment import Assessment
from backend.app.models.user import User
from backend.app.schemas.assessment import AssessmentCreate, AssessmentRead, AssessmentUpdate
from backend.app.schemas.common import ResponseEnvelope, PaginatedResponse
from backend.app.api.deps import get_current_user_optional

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=ResponseEnvelope[List[AssessmentRead]])
def list_assessments(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve security assessments list."""
    assessments = db.query(Assessment).offset(skip).limit(limit).all()
    return ResponseEnvelope(data=assessments)

@router.post("", response_model=ResponseEnvelope[AssessmentRead])
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional)
):
    """Create a new security assessment."""
    tenant_id = user.tenant_id if user else "tenant-default-001"
    creator_id = user.id if user else None
    
    assessment = Assessment(
        tenant_id=tenant_id,
        creator_id=creator_id,
        name=payload.name,
        description=payload.description,
        target_type=payload.target_type,
        target_endpoint=payload.target_endpoint,
        target_config=payload.target_config,
        status="ready",
        risk_score=0
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return ResponseEnvelope(data=assessment, message="Assessment created successfully.")

@router.get("/{assessment_id}", response_model=ResponseEnvelope[AssessmentRead])
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve an assessment by ID."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return ResponseEnvelope(data=assessment)

@router.patch("/{assessment_id}", response_model=ResponseEnvelope[AssessmentRead])
def update_assessment(
    assessment_id: str,
    payload: AssessmentUpdate,
    db: Session = Depends(get_db)
):
    """Update assessment metadata."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if payload.name is not None:
        assessment.name = payload.name
    if payload.description is not None:
        assessment.description = payload.description
    if payload.status is not None:
        assessment.status = payload.status
    if payload.risk_score is not None:
        assessment.risk_score = payload.risk_score
    if payload.target_config is not None:
        assessment.target_config = payload.target_config
        
    db.commit()
    db.refresh(assessment)
    return ResponseEnvelope(data=assessment, message="Assessment updated.")

@router.delete("/{assessment_id}", response_model=ResponseEnvelope[dict])
def delete_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Delete an assessment and its associated runs/findings."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(assessment)
    db.commit()
    return ResponseEnvelope(data={"id": assessment_id}, message="Assessment deleted.")

