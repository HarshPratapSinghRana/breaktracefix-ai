from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.authorization import AuthPolicy, AuthDecisionLog
from backend.app.schemas.authorization import (
    AuthContextRequest,
    AuthDecisionResponse,
    AuthPolicyCreate,
    AuthPolicyRead,
    AuthDecisionLogRead
)
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.auth_intelligence.evaluator import AuthIntelligenceEngine

router = APIRouter(prefix="/authorization", tags=["Authorization Intelligence"])

@router.post("/evaluate", response_model=ResponseEnvelope[AuthDecisionResponse])
def evaluate_authorization(
    payload: AuthContextRequest,
    db: Session = Depends(get_db)
):
    """Evaluate an 8-axis context-aware authorization request and return decision with visual context."""
    decision_resp = AuthIntelligenceEngine.evaluate(db, payload)
    return ResponseEnvelope(
        data=decision_resp,
        message=f"Authorization evaluated: {decision_resp.decision}."
    )

@router.get("/policies", response_model=ResponseEnvelope[List[AuthPolicyRead]])
def list_policies(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List authorization policies for tenant."""
    query = db.query(AuthPolicy).filter(AuthPolicy.is_active == True)
    if tenant_id:
        query = query.filter(AuthPolicy.tenant_id == tenant_id)
    policies = query.order_by(AuthPolicy.priority.desc()).all()
    return ResponseEnvelope(data=policies)

@router.post("/policies", response_model=ResponseEnvelope[AuthPolicyRead])
def create_policy(
    payload: AuthPolicyCreate,
    tenant_id: Optional[str] = Query("tenant-default-001"),
    db: Session = Depends(get_db)
):
    """Create a new context-aware ABAC/RBAC authorization policy."""
    policy = AuthPolicy(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        effect=payload.effect,
        role_pattern=payload.role_pattern,
        resource_pattern=payload.resource_pattern,
        action_pattern=payload.action_pattern,
        max_data_classification=payload.max_data_classification,
        allowed_purposes=payload.allowed_purposes,
        allowed_recipients=payload.allowed_recipients,
        requires_approval=payload.requires_approval,
        priority=payload.priority
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return ResponseEnvelope(data=policy, message="Policy created successfully.")

@router.get("/decisions", response_model=ResponseEnvelope[List[AuthDecisionLogRead]])
def list_decision_logs(
    limit: int = 50,
    decision_filter: Optional[str] = Query(None, description="ALLOW or DENY"),
    db: Session = Depends(get_db)
):
    """Retrieve audit trail of authorization decisions."""
    query = db.query(AuthDecisionLog)
    if decision_filter:
        query = query.filter(AuthDecisionLog.decision == decision_filter.upper())
    logs = query.order_by(AuthDecisionLog.created_at.desc()).limit(limit).all()
    return ResponseEnvelope(data=logs)

