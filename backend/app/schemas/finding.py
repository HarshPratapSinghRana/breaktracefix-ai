from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class FindingBase(BaseModel):
    title: str
    severity: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    affected_component: str
    source_location: Optional[str] = None
    sink_location: Optional[str] = None
    attack_vector: str
    reproduction_steps: Optional[str] = None
    evidence: Dict[str, Any] = {}
    root_cause: Optional[str] = None
    impact: Optional[str] = None
    remediation: Optional[str] = None
    patch_status: str = "unpatched"

class FindingCreate(FindingBase):
    assessment_id: str
    simulation_run_id: Optional[str] = None

class FindingUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    patch_status: Optional[str] = None
    remediation: Optional[str] = None

class FindingRead(FindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    simulation_run_id: Optional[str] = None
    created_at: datetime
