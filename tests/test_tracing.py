import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.services.tracing.pipeline import TraceCollector, PIPELINE_STAGES
from backend.app.models.trace import ExecutionTrace, TraceSpan

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_trace_collector_11_stages_and_redaction():
    db = SessionLocal()
    try:
        collector = TraceCollector(trace_name="Test Redacted Trace")
        
        # Feed sensitive tokens to verify redaction before persistence
        raw_secret_data = {
            "api_key": "sk-proj-supersecretkey1234567890",
            "prompt": "Call API with key sk-ant-anthropicsecret12345 and CC 4111-2222-3333-4444"
        }

        for idx, name, desc in PIPELINE_STAGES:
            status = "VIOLATION" if idx == 8 else "OK"
            collector.record_stage(
                stage_index=idx,
                stage_name=name,
                input_data=raw_secret_data if idx == 1 else {"stage": name},
                output_data={"result": "OK"},
                status=status,
                duration_ms=15.0
            )

        trace = collector.save_to_db(db)
        assert trace.id is not None
        assert trace.has_violation == "YES"

        # Verify all 11 spans persisted
        spans = db.query(TraceSpan).filter(TraceSpan.trace_id_fk == trace.id).order_by(TraceSpan.stage_index).all()
        assert len(spans) == 11
        assert spans[0].stage_name == "User Input"
        assert spans[10].stage_name == "Final Response"

        # Verify sensitive input was redacted in span 1
        span1_input = spans[0].input_data
        assert "sk-proj" not in str(span1_input)
        assert "[REDACTED_SENSITIVE_FIELD]" in str(span1_input) or "[REDACTED_API_KEY]" in str(span1_input)
        assert "[REDACTED_CREDIT_CARD]" in str(span1_input)
    finally:
        db.close()

def test_timeline_and_otel_export():
    db = SessionLocal()
    try:
        trace = db.query(ExecutionTrace).first()
        assert trace is not None

        timeline = TraceCollector.build_timeline(trace)
        assert len(timeline) == 11
        assert timeline[0].index == 1
        assert timeline[0].name == "User Input"

        otel_data = TraceCollector.export_otel(trace)
        assert "resourceSpans" in otel_data
        assert len(otel_data["resourceSpans"]) >= 1
        scope_spans = otel_data["resourceSpans"][0]["scopeSpans"][0]["spans"]
        assert len(scope_spans) == 11
        assert scope_spans[0]["name"] == "Stage:User Input"
    finally:
        db.close()

def test_traces_api_endpoints():
    client = TestClient(app)

    # Execute sample pipeline via API
    exec_res = client.post("/api/v1/traces/execute-pipeline?prompt=TestPromptWithSecret_sk-proj-12345678901234567890&simulate_violation=true")
    assert exec_res.status_code == 200
    trace_data = exec_res.json()["data"]
    assert trace_data["has_violation"] == "YES"
    assert len(trace_data["spans"]) == 11
    trace_id = trace_data["trace_id"]

    # List traces
    list_res = client.get("/api/v1/traces")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # Get single trace
    get_res = client.get(f"/api/v1/traces/{trace_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["trace_id"] == trace_id

    # Get timeline
    time_res = client.get(f"/api/v1/traces/{trace_id}/timeline")
    assert time_res.status_code == 200
    assert len(time_res.json()["data"]) == 11

    # Get OTel export
    otel_res = client.get(f"/api/v1/traces/{trace_id}/otel")
    assert otel_res.status_code == 200
    assert "resourceSpans" in otel_res.json()["data"]

