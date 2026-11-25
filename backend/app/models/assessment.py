import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Assessment(Base):
    """Security assessment target and overall audit engagement."""
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_type = Column(String(50), default="agent", nullable=False)  # agent, rag, mcp_server, llm_pipeline
    target_endpoint = Column(String(500), nullable=True)
    target_config = Column(JSON, default=dict)
    status = Column(String(50), default="ready", nullable=False)  # ready, in_progress, completed, failed
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="assessments")
    creator = relationship("User", back_populates="assessments")
    simulation_runs = relationship("SimulationRun", back_populates="assessment", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="assessment", cascade="all, delete-orphan")

