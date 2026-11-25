from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class TraceSpanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    span_id: str
    parent_span_id: Optional[str] = None
    stage_name: str
    stage_index: int
    status: str
    duration_ms: float
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    security_event: Optional[str] = None
    attributes: Dict[str, Any] = {}
    created_at: datetime

class ExecutionTraceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    simulation_run_id: Optional[str] = None
    trace_id: str
    name: str
    total_duration_ms: float
    has_violation: str
    summary: Optional[str] = None
    created_at: datetime
    spans: List[TraceSpanRead] = []

class TimelineStage(BaseModel):
    index: int
    name: str
    status: str
    duration_ms: float
    security_flag: Optional[str] = None
    input_preview: str
    output_preview: str
