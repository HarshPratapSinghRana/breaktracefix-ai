from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AttackScenarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    severity: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    threat_model: str
    preconditions: Optional[str] = None
    attack_input: str
    expected_vulnerable_behavior: str
    expected_secure_behavior: str
    reproduction_instructions: Optional[str] = None
    is_active: bool

class SimulationRunCreate(BaseModel):
    assessment_id: str
    scenario_id: str
    mode: str = "vulnerable"  # vulnerable, protected, comparison
    custom_input: Optional[str] = None

class SimulationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    scenario_id: str
    mode: str
    status: str
    input_payload: str
    output_response: Optional[str] = None
    execution_time_ms: float
    evidence: Dict[str, Any] = {}
    invariant_results: List[Dict[str, Any]] = []
    created_at: datetime
