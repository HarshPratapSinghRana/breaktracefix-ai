from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AuthContextRequest(BaseModel):
    actor_id: str = Field(..., description="User or Agent identity")
    actor_role: str = Field(..., description="Role of the actor, e.g. admin, agent, customer_support")
    tenant_id: str = Field(..., description="Tenant organization ID")
    resource_id: str = Field(..., description="Target tool, document, or endpoint")
    action: str = Field(..., description="Operation: read, write, execute, delete")
    data_classification: str = Field(default="Internal", description="Public, Internal, Confidential, Restricted")
    purpose: Optional[str] = Field(default="customer_support", description="Business justification")
    recipient: Optional[str] = Field(default="user", description="Intended receiver of data")
    has_approval: bool = Field(default=False, description="Whether explicit human approval was obtained")

class AuthDecisionResponse(BaseModel):
    decision: str  # ALLOW, DENY
    reason: str
    actor_id: str
    tenant_id: str
    resource_id: str
    action: str
    matched_policy_id: Optional[str] = None
    evaluation_steps: List[str] = []
    visual_context: Dict[str, Any] = {}

class AuthPolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    effect: str = "ALLOW"
    role_pattern: str = "*"
    resource_pattern: str = "*"
    action_pattern: str = "*"
    max_data_classification: str = "Confidential"
    allowed_purposes: List[str] = ["*"]
    allowed_recipients: List[str] = ["*"]
    requires_approval: bool = False
    priority: str = "100"

class AuthPolicyRead(AuthPolicyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime

class AuthDecisionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    actor_id: str
    actor_role: str
    resource_id: str
    action: str
    data_classification: str
    purpose: Optional[str]
    recipient: Optional[str]
    approval_granted: bool
    decision: str
    reason: str
    matched_policy_id: Optional[str]
    created_at: datetime
