import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.services.attack_engine.registry import AttackRegistry
from backend.app.services.attack_engine.runner import AttackRunner
import backend.app.services.attack_engine.scenarios
from backend.app.models.assessment import Assessment
from backend.app.models.attack import SimulationRun
from backend.app.models.finding import Finding
from backend.app.models.trace import ExecutionTrace, TraceSpan

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_registry_contains_all_14_scenarios():
    scenarios = AttackRegistry.list_all()
    scenario_ids = [s.id for s in scenarios]
    assert len(scenario_ids) == 14
    
    expected_ids = [f"BTF-ATK-{i:03d}" for i in range(1, 15)]
    for exp_id in expected_ids:
        assert exp_id in scenario_ids, f"Scenario {exp_id} missing from registry"

def test_individual_scenario_dual_execution():
    """Verify each of the 14 scenarios behaves correctly in both vulnerable and protected modes."""
    scenarios = AttackRegistry.list_all()
    for s in scenarios:
        # Vulnerable run
        vuln_res = s.run(mode="vulnerable")
        assert vuln_res.status == "success_exploited", f"{s.id} failed vulnerable execution"
        assert len(vuln_res.invariants) >= 1
        assert any(not inv.passed for inv in vuln_res.invariants), f"{s.id} invariant should fail in vulnerable mode"

        # Protected run
        prot_res = s.run(mode="protected")
        assert prot_res.status == "success_defended", f"{s.id} failed protected execution"
        assert len(prot_res.invariants) >= 1
        assert all(inv.passed for inv in prot_res.invariants), f"{s.id} invariant should pass in protected mode"

def test_attack_runner_database_and_trace_persistence():
    db = SessionLocal()
    try:
        assessment = db.query(Assessment).first()
        assert assessment is not None

        # Execute BTF-ATK-001 (Direct Prompt Injection) in vulnerable mode
        run = AttackRunner.run_simulation(
            db=db,
            assessment_id=assessment.id,
            scenario_id="BTF-ATK-001",
            mode="vulnerable"
        )
        assert run.id is not None
        assert run.status == "success_exploited"

        # Verify trace generation
        trace = db.query(ExecutionTrace).filter(ExecutionTrace.simulation_run_id == run.id).first()
        assert trace is not None
        assert trace.has_violation == "YES"
        
        # Verify 11 pipeline spans exist
        spans = db.query(TraceSpan).filter(TraceSpan.trace_id_fk == trace.id).order_by(TraceSpan.stage_index).all()
        assert len(spans) == 11
        assert spans[0].stage_name == "User Input"
        assert spans[10].stage_name == "Final Response"

        # Verify finding was created
        finding = db.query(Finding).filter(Finding.simulation_run_id == run.id).first()
        assert finding is not None
        assert "Direct Prompt Injection" in finding.title
        assert finding.cwe_id == "CWE-20"
        assert finding.patch_status == "unpatched"
    finally:
        db.close()

def test_attack_simulator_api_endpoints():
    client = TestClient(app)
    
    # List scenarios
    res = client.get("/api/v1/attacks")
    assert res.status_code == 200
    scenarios = res.json()["data"]
    assert len(scenarios) == 14

    # Filter scenarios by severity
    crit_res = client.get("/api/v1/attacks?severity=Critical")
    assert crit_res.status_code == 200
    crit_scenarios = crit_res.json()["data"]
    assert len(crit_scenarios) >= 4
    for s in crit_scenarios:
        assert s["severity"] == "Critical"

    # Get single scenario
    single_res = client.get("/api/v1/attacks/scenarios/BTF-ATK-007")
    assert single_res.status_code == 200
    assert single_res.json()["data"]["name"] == "Unauthorized Tool Execution via Privilege Bypass"

    # Execute simulation via API
    db = SessionLocal()
    assessment = db.query(Assessment).first()
    db.close()
    
    sim_res = client.post("/api/v1/attacks/simulate", json={
        "assessment_id": assessment.id,
        "scenario_id": "BTF-ATK-010",
        "mode": "protected"
    })
    assert sim_res.status_code == 200
    sim_data = sim_res.json()["data"]
    assert sim_data["status"] == "success_defended"
    assert "REQUEST BLOCKED" in sim_data["output_response"]

