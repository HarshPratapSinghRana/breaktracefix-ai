import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class PatchValidation(Base):
    """Side-by-side patch verification record comparing vulnerable vs patched execution."""
    __tablename__ = "patch_validations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(String(50), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    patch_title = Column(String(200), nullable=False)
    patch_diff = Column(Text, nullable=True)
    vulnerable_run_id = Column(String(36), nullable=True)
    patched_run_id = Column(String(36), nullable=True)
    invariants_verified = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(Float, default=0.0)
    validation_status = Column(String(30), default="passed", nullable=False)  # passed, failed, partial
    evidence_comparison = Column(JSON, default=dict)
    regression_test_code = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    finding = relationship("Finding", back_populates="patches")

