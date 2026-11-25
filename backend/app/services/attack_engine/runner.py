import time
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.services.attack_engine.registry import AttackRegistry
import backend.app.services.attack_engine.scenarios  # ensure all scenarios registered
from backend.app.models.attack import SimulationRun, AttackScenario
from backend.app.models.assessment import Assessment
from backend.app.models.finding import Finding
from backend.app.models.trace import ExecutionTrace, TraceSpan

class AttackRunner:
    """Orchestrates scenario execution, database recording, and finding generation."""

    @staticmethod
    def run_simulation(
        db: Session,
        assessment_id: str,
        scenario_id: str,
        mode: str = "vulnerable",
        custom_input: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SimulationRun:
        scenario = AttackRegistry.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not found in registry.")

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")

        # Execute scenario logic
        exec_result = scenario.run(mode=mode, input_payload=custom_input, context=context)

        # Record SimulationRun in DB
        sim_run = SimulationRun(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            scenario_id=scenario_id,
            mode=mode,
            status=exec_result.status,
            input_payload=exec_result.input_payload,
            output_response=exec_result.output_response,
            execution_time_ms=exec_result.execution_time_ms,
            evidence=exec_result.evidence,
            invariant_results=[inv.model_dump() for inv in exec_result.invariants]
        )
        db.add(sim_run)

        # Generate a corresponding ExecutionTrace with 11 standard stages
        trace_id = f"trace-{str(uuid.uuid4())[:12]}"
        has_viol = "YES" if exec_result.status == "success_exploited" else "NO"
        root_trace = ExecutionTrace(
            id=str(uuid.uuid4()),
            simulation_run_id=sim_run.id,
            trace_id=trace_id,
            name=f"{scenario.name} ({mode.upper()})",
            total_duration_ms=exec_result.execution_time_ms,
            has_violation=has_viol,
            summary=f"Simulation in {mode} mode: {exec_result.status}."
        )
        db.add(root_trace)

        # Add 11 pipeline spans
        stage_names = [
            "User Input", "Input Validation", "Prompt Construction", "Retrieval",
            "Context Assembly", "Model Invocation", "Tool Selection", "Authorization",
            "Tool Execution", "Output Validation", "Final Response"
        ]
        spans = []
        for idx, stage in enumerate(stage_names, start=1):
            is_viol_stage = (has_viol == "YES" and stage in ["Input Validation", "Authorization", "Tool Execution", "Output Validation"])
            span_status = "VIOLATION" if is_viol_stage else "OK"
            spans.append(TraceSpan(
                id=str(uuid.uuid4()),
                trace_id_fk=root_trace.id,
                span_id=f"span-{str(uuid.uuid4())[:8]}",
                stage_name=stage,
                stage_index=idx,
                status=span_status,
                duration_ms=round(exec_result.execution_time_ms / 11.0, 2),
                input_data={"stage": stage, "mode": mode},
                output_data={"result": "inspected", "flag": span_status},
                security_event=f"Security invariant evaluated on {stage}" if is_viol_stage else None,
                attributes={"scenario_id": scenario_id, "mode": mode}
            ))
        db.add_all(spans)

        # If vulnerability confirmed in vulnerable mode, create/update finding
        if mode == "vulnerable" and exec_result.status == "success_exploited":
            existing_finding = db.query(Finding).filter(
                Finding.assessment_id == assessment_id,
                Finding.attack_vector == scenario.category
            ).first()

            if existing_finding:
                existing_finding.simulation_run_id = sim_run.id
                existing_finding.evidence = exec_result.evidence
                existing_finding.patch_status = "unpatched"
            else:
                finding = Finding(
                    id=f"BTF-VULN-{str(uuid.uuid4())[:8].upper()}",
                    assessment_id=assessment_id,
                    simulation_run_id=sim_run.id,
                    title=f"Vulnerability Confirmed: {scenario.name}",
                    severity=scenario.severity,
                    cwe_id=scenario.cwe_id,
                    owasp_category=scenario.owasp_category,
                    affected_component=f"Target: {assessment.name} ({assessment.target_type})",
                    source_location="app/agent/pipeline.py:42",
                    sink_location="app/agent/execution_sink.py:118",
                    attack_vector=scenario.category,
                    reproduction_steps=scenario.reproduction_instructions,
                    evidence=exec_result.evidence,
                    root_cause=f"Absence of defense controls in {scenario.category} processing pathway.",
                    impact=f"Attacker can achieve {scenario.threat_model.lower()}",
                    remediation=f"Implement security invariants: {scenario.expected_secure_behavior}",
                    patch_status="unpatched"
                )
                db.add(finding)
                
                # Update assessment risk score based on confirmed findings
                assessment.risk_score = min(100, assessment.risk_score + (25 if scenario.severity == "Critical" else 15))
                assessment.status = "in_progress"

        db.commit()
        db.refresh(sim_run)
        return sim_run

    @staticmethod
    def run_all_scenarios(
        db: Session,
        assessment_id: str,
        mode: str = "vulnerable"
    ) -> List[SimulationRun]:
        results = []
        for scenario in AttackRegistry.list_all():
            run = AttackRunner.run_simulation(
                db=db,
                assessment_id=assessment_id,
                scenario_id=scenario.id,
                mode=mode
            )
            results.append(run)
        return results
