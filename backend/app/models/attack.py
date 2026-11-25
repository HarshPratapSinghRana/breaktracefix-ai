import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class AttackScenario(Base):
    """Attack scenario catalog specification."""
    __tablename__ = "attack_scenarios"

    id = Column(String(50), primary_key=True)  # e.g., BTF-ATK-001
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="Medium")  # Critical, High, Medium, Low
    cwe_id = Column(String(50), nullable=True)
    owasp_category = Column(String(100), nullable=True)
    threat_model = Column(Text, nullable=False)
    preconditions = Column(Text, nullable=True)
    attack_input = Column(Text, nullable=False)
    expected_vulnerable_behavior = Column(Text, nullable=False)
    expected_secure_behavior = Column(Text, nullable=False)
    reproduction_instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    simulation_runs = relationship("SimulationRun", back_populates="scenario")

class SimulationRun(Base):
    """Instance of an attack scenario execution against an assessment target."""
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(50), ForeignKey("attack_scenarios.id", ondelete="RESTRICT"), nullable=False)
    mode = Column(String(20), default="vulnerable", nullable=False)  # vulnerable, protected, comparison
    status = Column(String(30), default="pending", nullable=False)   # pending, running, success_exploited, success_defended, error
    input_payload = Column(Text, nullable=False)
    output_response = Column(Text, nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    evidence = Column(JSON, default=dict)
    invariant_results = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    assessment = relationship("Assessment", back_populates="simulation_runs")
    scenario = relationship("AttackScenario", back_populates="simulation_runs")
    traces = relationship("ExecutionTrace", back_populates="simulation_run", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="simulation_run")

