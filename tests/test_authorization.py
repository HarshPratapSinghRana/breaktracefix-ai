import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.services.auth_intelligence.evaluator import AuthIntelligenceEngine
from backend.app.schemas.authorization import AuthContextRequest
from backend.app.models.authorization import AuthDecisionLog

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_authorized_public_read():
    db = SessionLocal()
    try:
        req = AuthContextRequest(
            actor_id="user-001",
            actor_role="researcher",
            tenant_id="tenant-default-001",
            resource_id="doc:user_guide",
            action="read",
            data_classification="Internal",
            purpose="customer_support",
            recipient="user",
            has_approval=False
        )
        res = AuthIntelligenceEngine.evaluate(db, req)
        assert res.decision == "ALLOW"
        assert res.matched_policy_id == "policy-001"
        assert len(res.evaluation_steps) >= 5
        assert len(res.visual_context["nodes"]) == 6
    finally:
        db.close()

def test_cross_tenant_access_denied():
    db = SessionLocal()
    try:
        req = AuthContextRequest(
            actor_id="user-001",
            actor_role="researcher",
            tenant_id="tenant-default-001",
            resource_id="tenant:external:foreign_document",
            action="read",
            data_classification="Internal"
        )
        res = AuthIntelligenceEngine.evaluate(db, req)
        assert res.decision == "DENY"
        assert "Cross-tenant access forbidden" in res.reason
    finally:
        db.close()

def test_missing_approval_on_destructive_action():
    db = SessionLocal()
    try:
        # Destructive tool without approval
        req = AuthContextRequest(
            actor_id="user-admin-001",
            actor_role="admin",
            tenant_id="tenant-default-001",
            resource_id="tool:destructive:purge_logs",
            action="execute",
            data_classification="Restricted",
            purpose="admin",
            recipient="internal",
            has_approval=False  # Missing approval
        )
        res = AuthIntelligenceEngine.evaluate(db, req)
        assert res.decision == "DENY"
        assert "requires explicit human approval" in res.reason

        # With approval granted
        req.has_approval = True
        res_approved = AuthIntelligenceEngine.evaluate(db, req)
        assert res_approved.decision == "ALLOW"
    finally:
        db.close()

def test_data_classification_ceiling_enforced():
    db = SessionLocal()
    try:
        # Policy-001 only permits max classification "Internal".
        # Requesting "Restricted" doc with policy-001 should fail the classification check.
        req = AuthContextRequest(
            actor_id="user-002",
            actor_role="researcher",
            tenant_id="tenant-default-001",
            resource_id="doc:confidential_roadmap",
            action="read",
            data_classification="Restricted",  # Exceeds Internal ceiling
            purpose="customer_support",
            recipient="user"
        )
        res = AuthIntelligenceEngine.evaluate(db, req)
        assert res.decision == "DENY"
        assert "Default-Deny" in res.reason
    finally:
        db.close()

def test_decision_log_persisted():
    db = SessionLocal()
    try:
        count_before = db.query(AuthDecisionLog).count()
        req = AuthContextRequest(
            actor_id="user-audit-test",
            actor_role="auditor",
            tenant_id="tenant-default-001",
            resource_id="doc:audit_sample",
            action="read",
            data_classification="Public"
        )
        res = AuthIntelligenceEngine.evaluate(db, req)
        count_after = db.query(AuthDecisionLog).count()
        assert count_after == count_before + 1

        last_log = db.query(AuthDecisionLog).order_by(AuthDecisionLog.created_at.desc()).first()
        assert last_log.actor_id == "user-audit-test"
        assert last_log.decision == "ALLOW"
    finally:
        db.close()

def test_authorization_api_endpoints():
    client = TestClient(app)

    # API Evaluation
    res = client.post("/api/v1/authorization/evaluate", json={
        "actor_id": "api-tester",
        "actor_role": "researcher",
        "tenant_id": "tenant-default-001",
        "resource_id": "doc:api_specs",
        "action": "read",
        "data_classification": "Internal"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["decision"] == "ALLOW"
    assert "visual_context" in data

    # API List Policies
    policies_res = client.get("/api/v1/authorization/policies")
    assert policies_res.status_code == 200
    assert len(policies_res.json()["data"]) >= 3

    # API Query Decision Logs
    decisions_res = client.get("/api/v1/authorization/decisions")
    assert decisions_res.status_code == 200
    assert len(decisions_res.json()["data"]) >= 1

