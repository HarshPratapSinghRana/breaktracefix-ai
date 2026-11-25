import time
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.core.redaction import redact_data
from backend.app.core.telemetry import tracer
from backend.app.models.trace import ExecutionTrace, TraceSpan
from backend.app.schemas.trace import TimelineStage

PIPELINE_STAGES = [
    (1, "User Input", "Capture raw user prompt and metadata"),
    (2, "Input Validation", "Adversarial prompt injection & toxicity scanning"),
    (3, "Prompt Construction", "System template assembly & developer boundary markers"),
    (4, "Retrieval", "RAG vector retrieval & tenant boundary filtering"),
    (5, "Context Assembly", "Knowledge chunk ranking and prompt context insertion"),
    (6, "Model Invocation", "LLM reasoning and token generation"),
    (7, "Tool Selection", "Model tool selection and argument parsing"),
    (8, "Authorization", "8-Axis ABAC/RBAC authorization evaluation"),
    (9, "Tool Execution", "Sandboxed tool execution and argument verification"),
    (10, "Output Validation", "XSS/injection scanning & sensitive data scrubbing"),
    (11, "Final Response", "Client dispatch of sanitized response payload")
]

class TraceCollector:
    """Collects, scrubs, and persists 11-stage execution traces with OpenTelemetry compliance."""

    def __init__(self, trace_name: str, simulation_run_id: Optional[str] = None):
        self.trace_id = f"btf-trc-{str(uuid.uuid4())[:16]}"
        self.trace_name = trace_name
        self.simulation_run_id = simulation_run_id
        self.spans: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.has_violation = "NO"

    def record_stage(
        self,
        stage_index: int,
        stage_name: str,
        input_data: Any,
        output_data: Any,
        status: str = "OK",  # OK, ERROR, VIOLATION
        duration_ms: float = 10.0,
        security_event: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        # Mandatory PII and credential scrubbing before storage
        clean_input = redact_data(input_data)
        clean_output = redact_data(output_data)
        clean_attrs = redact_data(attributes or {})

        if status == "VIOLATION":
            self.has_violation = "YES"

        span_id = f"spn-{str(uuid.uuid4())[:8]}"
        self.spans.append({
            "span_id": span_id,
            "stage_index": stage_index,
            "stage_name": stage_name,
            "status": status,
            "duration_ms": duration_ms,
            "input_data": clean_input if isinstance(clean_input, dict) else {"payload": clean_input},
            "output_data": clean_output if isinstance(clean_output, dict) else {"payload": clean_output},
            "security_event": security_event,
            "attributes": clean_attrs
        })

    def save_to_db(self, db: Session) -> ExecutionTrace:
        total_duration = sum(s["duration_ms"] for s in self.spans)
        
        trace = ExecutionTrace(
            id=str(uuid.uuid4()),
            simulation_run_id=self.simulation_run_id,
            trace_id=self.trace_id,
            name=self.trace_name,
            total_duration_ms=round(total_duration, 2),
            has_violation=self.has_violation,
            summary=f"11-Stage Pipeline Trace: {len(self.spans)} stages recorded. Violations: {self.has_violation}."
        )
        db.add(trace)

        db_spans = []
        for s in self.spans:
            db_spans.append(TraceSpan(
                id=str(uuid.uuid4()),
                trace_id_fk=trace.id,
                span_id=s["span_id"],
                stage_name=s["stage_name"],
                stage_index=s["stage_index"],
                status=s["status"],
                duration_ms=s["duration_ms"],
                input_data=s["input_data"],
                output_data=s["output_data"],
                security_event=s["security_event"],
                attributes=s["attributes"]
            ))
        db.add_all(db_spans)
        db.commit()
        db.refresh(trace)
        return trace

    @staticmethod
    def build_timeline(trace: ExecutionTrace) -> List[TimelineStage]:
        """Convert trace spans to timeline representation for visualization."""
        timeline = []
        for span in sorted(trace.spans, key=lambda s: s.stage_index):
            in_preview = str(span.input_data)[:120] if span.input_data else "Empty"
            out_preview = str(span.output_data)[:120] if span.output_data else "Empty"
            timeline.append(TimelineStage(
                index=span.stage_index,
                name=span.stage_name,
                status=span.status,
                duration_ms=span.duration_ms,
                security_flag=span.security_event,
                input_preview=in_preview,
                output_preview=out_preview
            ))
        return timeline

    @staticmethod
    def export_otel(trace: ExecutionTrace) -> Dict[str, Any]:
        """Export trace in standard OpenTelemetry ResourceSpans JSON structure."""
        otel_spans = []
        for span in trace.spans:
            otel_spans.append({
                "traceId": trace.trace_id,
                "spanId": span.span_id,
                "name": f"Stage:{span.stage_name}",
                "kind": "SPAN_KIND_INTERNAL",
                "status": {"code": 1 if span.status == "OK" else 2, "message": span.security_event},
                "attributes": [
                    {"key": "stage.index", "value": {"intValue": span.stage_index}},
                    {"key": "stage.name", "value": {"stringValue": span.stage_name}},
                    {"key": "stage.duration_ms", "value": {"doubleValue": span.duration_ms}},
                    {"key": "security.violation", "value": {"boolValue": span.status == "VIOLATION"}}
                ]
            })

        return {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "breaktracefix-ai"}},
                            {"key": "trace.name", "value": {"stringValue": trace.name}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "breaktracefix.pipeline.tracer", "version": "1.0.0"},
                            "spans": otel_spans
                        }
                    ]
                }
            ]
        }

