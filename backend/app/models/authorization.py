import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class AuthPolicy(Base):
    """Fine-grained context-aware ABAC/RBAC authorization policy."""
    __tablename__ = "auth_policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    effect = Column(String(10), default="ALLOW", nullable=False)  # ALLOW, DENY
    role_pattern = Column(String(100), default="*", nullable=False)
    resource_pattern = Column(String(200), default="*", nullable=False)
    action_pattern = Column(String(100), default="*", nullable=False)
    max_data_classification = Column(String(50), default="Confidential")  # Public, Internal, Confidential, Restricted
    allowed_purposes = Column(JSON, default=lambda: ["*"])
    allowed_recipients = Column(JSON, default=lambda: ["*"])
    requires_approval = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(String(10), default="100")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="policies")

class AuthDecisionLog(Base):
    """Audit log of an 8-axis authorization decision."""
    __tablename__ = "auth_decision_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    resource_id = Column(String(200), nullable=False)
    action = Column(String(100), nullable=False)
    data_classification = Column(String(50), nullable=False)
    purpose = Column(String(100), nullable=True)
    recipient = Column(String(100), nullable=True)
    approval_granted = Column(Boolean, default=False)
    decision = Column(String(10), nullable=False)  # ALLOW, DENY
    reason = Column(Text, nullable=False)
    matched_policy_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

