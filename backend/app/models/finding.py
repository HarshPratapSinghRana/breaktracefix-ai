import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Finding(Base):
    """Confirmed security finding / vulnerability record."""
    __tablename__ = "findings"

    id = Column(String(50), primary_key=True, default=lambda: f"BTF-VULN-{str(uuid.uuid4())[:8].upper()}")
    assessment_id = Column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    simulation_run_id = Column(String(36), ForeignKey("simulation_runs.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # Critical, High, Medium, Low, Info
    cwe_id = Column(String(50), nullable=True)
    owasp_category = Column(String(100), nullable=True)
    affected_component = Column(String(200), nullable=False)
    source_location = Column(String(300), nullable=True)  # e.g., app/agent.py:42
    sink_location = Column(String(300), nullable=True)
    attack_vector = Column(String(100), nullable=False)
    reproduction_steps = Column(Text, nullable=True)
    evidence = Column(JSON, default=dict)
    root_cause = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    patch_status = Column(String(30), default="unpatched")  # unpatched, patch_tested, verified_fixed, regressed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    assessment = relationship("Assessment", back_populates="findings")
    simulation_run = relationship("SimulationRun", back_populates="findings")
    patches = relationship("PatchValidation", back_populates="finding", cascade="all, delete-orphan")

