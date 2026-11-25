from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AssessmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_type: str = "agent"  # agent, rag, mcp_server, llm_pipeline
    target_endpoint: Optional[str] = None
    target_config: Dict[str, Any] = {}

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_score: Optional[int] = None
    target_config: Optional[Dict[str, Any]] = None

class AssessmentRead(AssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    creator_id: Optional[str] = None
    status: str
    risk_score: int
    created_at: datetime
    updated_at: datetime
