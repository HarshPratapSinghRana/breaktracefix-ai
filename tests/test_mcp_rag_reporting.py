import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.models.assessment import Assessment
from backend.app.services.mcp_inspector.inspector import MCPSecurityInspector
from backend.app.services.rag_auditor.auditor import RAGSecurityAuditor
from backend.app.services.reporting.engine import SecurityReportGenerator
from backend.app.api.v1.mcp_inspector import SAMPLE_MCP_MANIFEST
from backend.app.api.v1.rag_auditor import SAMPLE_RAG_CHUNKS

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_mcp_security_inspector():
    report = MCPSecurityInspector.inspect_manifest(SAMPLE_MCP_MANIFEST, server_name="Test-SQL-MCP")
    assert report.total_tools == 3
    assert report.overall_risk_score >= 40.0
    assert report.high_risk_tools >= 1

    # Check delete_all_users tool analysis
    delete_tool = next((t for t in report.tools if t.tool_name == "delete_all_users"), None)
    assert delete_tool is not None
    assert delete_tool.risk_level in ["Critical", "High"]
    assert any("destructive" in f for f in delete_tool.risk_factors)

    # Check execute_query tool
    query_tool = next((t for t in report.tools if t.tool_name == "execute_query"), None)
    assert query_tool is not None
    assert any("SQL" in f or "execution" in f for f in query_tool.risk_factors)

def test_rag_security_auditor():
    report = RAGSecurityAuditor.audit_chunks(
        chunks=SAMPLE_RAG_CHUNKS,
        collection_name="Test Corp KB",
        current_tenant_id="tenant-default-001"
    )
    assert report.total_chunks == 3
    assert report.poisoned_chunks_count == 1
    assert report.unisolated_chunks_count == 1
    assert report.overall_rag_risk_score > 30.0

    # Check poisoned chunk details
    poisoned_chunk = next((c for c in report.audit_findings if c.chunk_id == "chk-002"), None)
    assert poisoned_chunk is not None
    assert poisoned_chunk.is_poisoned is True
    assert poisoned_chunk.poison_indicators[0].pattern_name == "System Directive Inversion"

    # Check cross-tenant chunk
    cross_tenant_chunk = next((c for c in report.audit_findings if c.chunk_id == "chk-003"), None)
    assert cross_tenant_chunk is not None
    assert cross_tenant_chunk.tenant_isolated is False

def test_security_reporting_engine():
    db = SessionLocal()
    try:
        assessment = db.query(Assessment).first()
        assert assessment is not None

        # Generate JSON report
        json_report = SecurityReportGenerator.generate_json_report(db, assessment.id)
        assert json_report["assessment_name"] == assessment.name
        assert json_report["author"] == "Harsh Pratap Singh Rana"
        assert "severity_summary" in json_report

        # Generate HTML report
        html_report = SecurityReportGenerator.generate_html_report(db, assessment.id)
        assert "<!DOCTYPE html>" in html_report
        assert "Harsh Pratap Singh Rana" in html_report
        assert "BreakTraceFix AI" in html_report
    finally:
        db.close()

def test_mcp_rag_reporting_api_endpoints():
    client = TestClient(app)

    db = SessionLocal()
    assessment = db.query(Assessment).first()
    db.close()

    # MCP API
    mcp_res = client.post("/api/v1/mcp-inspector/inspect", json={
        "manifest_json": SAMPLE_MCP_MANIFEST,
        "server_name": "API-MCP-Test"
    })
    assert mcp_res.status_code == 200
    assert mcp_res.json()["data"]["total_tools"] == 3

    # RAG API
    rag_res = client.post("/api/v1/rag-auditor/audit", json={
        "collection_name": "API-RAG-Test",
        "current_tenant_id": "tenant-default-001",
        "chunks": SAMPLE_RAG_CHUNKS
    })
    assert rag_res.status_code == 200
    assert rag_res.json()["data"]["poisoned_chunks_count"] == 1

    # Report JSON API
    rep_json = client.get(f"/api/v1/reports/json/{assessment.id}")
    assert rep_json.status_code == 200
    assert rep_json.json()["data"]["author"] == "Harsh Pratap Singh Rana"

    # Report HTML API
    rep_html = client.get(f"/api/v1/reports/html/{assessment.id}")
    assert rep_html.status_code == 200
    assert "text/html" in rep_html.headers["content-type"]
    assert "BreakTraceFix AI" in rep_html.text
