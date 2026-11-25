import time
import uuid
from typing import Optional, Dict, Any

class MockSpan:
    """Lightweight OpenTelemetry-compatible span wrapper for structured tracing."""
    def __init__(self, name: str, trace_id: str, span_id: str, parent_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.events: list[dict] = []
        self.status: str = "UNSET"
        self.error_message: Optional[str] = None

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })

    def end(self, status: str = "OK", error: Optional[str] = None) -> None:
        self.end_time = time.time()
        self.status = status
        self.error_message = error

    def to_dict(self) -> Dict[str, Any]:
        duration_ms = ((self.end_time or time.time()) - self.start_time) * 1000.0
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round(duration_ms, 2),
            "status": self.status,
            "error_message": self.error_message,
            "attributes": self.attributes,
            "events": self.events
        }

class TelemetryTracer:
    """OTel-aligned Tracer for BreakTraceFix AI pipelines."""
    def __init__(self, service_name: str = "breaktracefix-tracer"):
        self.service_name = service_name

    def start_span(self, name: str, trace_id: Optional[str] = None, parent_id: Optional[str] = None) -> MockSpan:
        t_id = trace_id or str(uuid.uuid4())
        s_id = str(uuid.uuid4())[:16]
        span = MockSpan(name=name, trace_id=t_id, span_id=s_id, parent_id=parent_id)
        span.set_attribute("service.name", self.service_name)
        return span

tracer = TelemetryTracer()

