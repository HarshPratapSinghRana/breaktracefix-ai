import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure root is on path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.app.core.redaction import redact_text, redact_data
from backend.app.core.telemetry import tracer
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.models.tenant import Tenant
from backend.app.models.user import User
from backend.app.models.attack import AttackScenario
from backend.app.models.authorization import AuthPolicy

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_security_hashing():
    password = "SuperSecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_flow():
    token = create_access_token(subject="user-123", tenant_id="tenant-456", role="admin")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["tenant_id"] == "tenant-456"
    assert payload["role"] == "admin"

def test_redaction_pipeline():
    raw_text = "My OpenAI key is sk-proj-1234567890abcdef12345 and email is user@example.com with CC 4111-2222-3333-4444"
    scrubbed = redact_text(raw_text)
    assert "sk-proj" not in scrubbed
    assert "[REDACTED_API_KEY]" in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_CREDIT_CARD]" in scrubbed

    nested = {
        "api_key": "sk-ant-12345678901234567890",
        "nested": {"user_email": "test@corp.com", "public_id": "ABC-123"}
    }
    cleaned = redact_data(nested)
    assert cleaned["api_key"] == "[REDACTED_SENSITIVE_FIELD]"
    assert "[REDACTED_EMAIL]" in cleaned["nested"]["user_email"]
    assert cleaned["nested"]["public_id"] == "ABC-123"

def test_telemetry_span():
    span = tracer.start_span("test-stage")
    span.set_attribute("stage.name", "input_validation")
    span.add_event("validation_passed")
    span.end(status="OK")
    data = span.to_dict()
    assert data["name"] == "test-stage"
    assert data["status"] == "OK"
    assert data["attributes"]["stage.name"] == "input_validation"
    assert len(data["events"]) == 1

def test_seed_database_contents():
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        assert tenant is not None
        assert tenant.name == "Default Organization"

        admin = db.query(User).filter(User.email == "admin@breaktracefix.ai").first()
        assert admin is not None
        assert admin.role == "admin"

        scenarios = db.query(AttackScenario).all()
        assert len(scenarios) == 14
        
        # Verify specific scenarios are present
        cat_ids = [s.id for s in scenarios]
        assert "BTF-ATK-001" in cat_ids
        assert "BTF-ATK-007" in cat_ids
        assert "BTF-ATK-010" in cat_ids
        assert "BTF-ATK-014" in cat_ids

        policies = db.query(AuthPolicy).filter(AuthPolicy.tenant_id == tenant.id).all()
        assert len(policies) >= 3
    finally:
        db.close()

def test_fastapi_endpoints():
    client = TestClient(app)
    
    # Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "ok"
    assert json_data["data"]["project"] == "BreakTraceFix AI"

    # Login check
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@breaktracefix.ai",
        "password": "admin123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Current user profile
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "admin@breaktracefix.ai"

    # List assessments
    assess_res = client.get("/api/v1/assessments", headers={"Authorization": f"Bearer {token}"})
    assert assess_res.status_code == 200
    assert len(assess_res.json()["data"]) >= 1

