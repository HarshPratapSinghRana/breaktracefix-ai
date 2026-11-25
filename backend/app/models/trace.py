import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class ExecutionTrace(Base):
    """Root trace record spanning the entire 11-stage GenAI execution lifecycle."""
    __tablename__ = "execution_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_run_id = Column(String(36), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    trace_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    total_duration_ms = Column(Float, default=0.0)
    has_violation = Column(String(10), default="NO")  # YES, NO
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    simulation_run = relationship("SimulationRun", back_populates="traces")
    spans = relationship("TraceSpan", back_populates="trace", cascade="all, delete-orphan", order_by="TraceSpan.stage_index")

class TraceSpan(Base):
    """Individual span representing one of the 11 stages in data flow."""
    __tablename__ = "trace_spans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id_fk = Column(String(36), ForeignKey("execution_traces.id", ondelete="CASCADE"), nullable=False, index=True)
    span_id = Column(String(64), nullable=False)
    parent_span_id = Column(String(64), nullable=True)
    stage_name = Column(String(100), nullable=False)
    stage_index = Column(Integer, nullable=False)
    status = Column(String(20), default="OK", nullable=False)  # OK, ERROR, VIOLATION
    duration_ms = Column(Float, default=0.0)
    input_data = Column(JSON, default=dict)   # Pre-redacted
    output_data = Column(JSON, default=dict)  # Pre-redacted
    security_event = Column(String(255), nullable=True)
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    trace = relationship("ExecutionTrace", back_populates="spans")

