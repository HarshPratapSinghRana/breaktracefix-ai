from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.finding import Finding
from backend.app.models.patch import PatchValidation
from backend.app.schemas.patch import PatchValidationRequest, PatchValidationRead
from backend.app.schemas.finding import FindingRead
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.reproduction.workbench import PatchWorkbenchService
from backend.app.services.reproduction.generator import RegressionGenerator
from backend.app.services.attack_engine.registry import AttackRegistry

router = APIRouter(prefix="/reproduction", tags=["Reproduction & Patch Validation"])

@router.get("/findings", response_model=ResponseEnvelope[List[FindingRead]])
def list_findings(
    assessment_id: Optional[str] = Query(None),
    patch_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List findings available for reproduction and patch validation."""
    query = db.query(Finding)
    if assessment_id:
        query = query.filter(Finding.assessment_id == assessment_id)
    if patch_status:
        query = query.filter(Finding.patch_status == patch_status)
    findings = query.order_by(Finding.created_at.desc()).all()
    return ResponseEnvelope(data=findings)

@router.post("/validate-patch", response_model=ResponseEnvelope[PatchValidationRead])
def validate_patch(
    payload: PatchValidationRequest,
    db: Session = Depends(get_db)
):
    """Execute dual-run patch validation (vulnerable vs patched), verify invariants, and generate regression tests."""
    try:
        validation = PatchWorkbenchService.validate_patch(
            db=db,
            finding_id=payload.finding_id,
            patch_title=payload.patch_title,
            patch_diff=payload.patch_diff
        )
        return ResponseEnvelope(
            data=validation,
            message=f"Patch validation completed: {validation.validation_status.upper()} (Confidence: {validation.confidence_score}%)."
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/validations/{validation_id}", response_model=ResponseEnvelope[PatchValidationRead])
def get_validation(validation_id: str, db: Session = Depends(get_db)):
    """Retrieve details and side-by-side comparison for a patch validation."""
    val = db.query(PatchValidation).filter(PatchValidation.id == validation_id).first()
    if not val:
        raise HTTPException(status_code=404, detail="Patch validation record not found")
    return ResponseEnvelope(data=val)

@router.get("/findings/{finding_id}/regression-test", response_model=ResponseEnvelope[Dict[str, str]])
def get_regression_test_code(finding_id: str, db: Session = Depends(get_db)):
    """Generate or retrieve standalone pytest regression test code for a confirmed finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    scenario = None
    for s in AttackRegistry.list_all():
        if s.category == finding.attack_vector or s.id in finding.title:
            scenario = s
            break
    if not scenario:
        scenario = AttackRegistry.list_all()[0]

    code = RegressionGenerator.generate_pytest_template(
        finding_id=finding.id,
        title=finding.title,
        cwe_id=finding.cwe_id or "CWE-20",
        owasp_category=finding.owasp_category or "LLM01",
        scenario_id=scenario.id,
        input_payload=scenario.default_attack_input,
        expected_secure_behavior=scenario.expected_secure_behavior,
        invariant_name=scenario.category
    )
    return ResponseEnvelope(data={"finding_id": finding_id, "pytest_code": code})

