from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.trace import ExecutionTrace
from backend.app.schemas.trace import ExecutionTraceRead, TimelineStage
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.tracing.pipeline import TraceCollector, PIPELINE_STAGES
from backend.app.core.redaction import redact_text

router = APIRouter(prefix="/traces", tags=["Execution Traces"])

@router.get("", response_model=ResponseEnvelope[List[ExecutionTraceRead]])
def list_traces(
    violation_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List execution traces with violation filtering."""
    query = db.query(ExecutionTrace)
    if violation_only:
        query = query.filter(ExecutionTrace.has_violation == "YES")
    traces = query.order_by(ExecutionTrace.created_at.desc()).limit(limit).all()
    return ResponseEnvelope(data=traces)

@router.get("/{trace_id}", response_model=ResponseEnvelope[ExecutionTraceRead])
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Retrieve full trace tree by trace_id or primary key ID."""
    trace = db.query(ExecutionTrace).filter(
        (ExecutionTrace.trace_id == trace_id) | (ExecutionTrace.id == trace_id)
    ).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Execution trace not found")
    return ResponseEnvelope(data=trace)

@router.get("/{trace_id}/timeline", response_model=ResponseEnvelope[List[TimelineStage]])
def get_trace_timeline(trace_id: str, db: Session = Depends(get_db)):
    """Retrieve interactive timeline events for trace."""
    trace = db.query(ExecutionTrace).filter(
        (ExecutionTrace.trace_id == trace_id) | (ExecutionTrace.id == trace_id)
    ).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Execution trace not found")
    timeline = TraceCollector.build_timeline(trace)
    return ResponseEnvelope(data=timeline)

@router.get("/{trace_id}/otel", response_model=ResponseEnvelope[Dict[str, Any]])
def export_trace_otel(trace_id: str, db: Session = Depends(get_db)):
    """Export trace in standard OpenTelemetry ResourceSpans format."""
    trace = db.query(ExecutionTrace).filter(
        (ExecutionTrace.trace_id == trace_id) | (ExecutionTrace.id == trace_id)
    ).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Execution trace not found")
    otel_payload = TraceCollector.export_otel(trace)
    return ResponseEnvelope(data=otel_payload)

@router.post("/execute-pipeline", response_model=ResponseEnvelope[ExecutionTraceRead])
def execute_sample_pipeline(
    prompt: str = Query(..., description="Prompt to run through 11-stage tracer"),
    simulate_violation: bool = Query(False, description="Whether to simulate a security boundary violation"),
    db: Session = Depends(get_db)
):
    """Execute all 11 stages of a GenAI request lifecycle, capturing spans with automatic redaction."""
    collector = TraceCollector(trace_name="Live 11-Stage Inspection")
    
    for idx, name, desc in PIPELINE_STAGES:
        is_violation = simulate_violation and idx in [2, 8]  # input validation or auth violation
        status = "VIOLATION" if is_violation else "OK"
        sec_event = f"Adversarial anomaly detected at stage {name}" if is_violation else None
        
        collector.record_stage(
            stage_index=idx,
            stage_name=name,
            input_data={"prompt": prompt, "stage_description": desc},
            output_data={"processed": True, "redacted_sample": redact_text(prompt)},
            status=status,
            duration_ms=round(12.5 + (idx * 2.1), 2),
            security_event=sec_event
        )

    saved_trace = collector.save_to_db(db)
    return ResponseEnvelope(data=saved_trace, message="11-Stage trace generated and persisted.")

