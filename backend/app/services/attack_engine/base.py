from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class InvariantResult(BaseModel):
    invariant_name: str
    passed: bool
    description: str
    actual_value: Any = None
    expected_value: Any = None

class SimulationResult(BaseModel):
    scenario_id: str
    scenario_name: str
    mode: str  # vulnerable, protected
    status: str  # success_exploited, success_defended, error
    input_payload: str
    output_response: str
    execution_time_ms: float
    evidence: Dict[str, Any] = Field(default_factory=dict)
    invariants: List[InvariantResult] = Field(default_factory=list)
    trace_events: List[Dict[str, Any]] = Field(default_factory=list)

class BaseScenario(ABC):
    """Abstract base class for all BreakTraceFix AI attack scenarios."""
    
    id: str
    name: str
    category: str
    severity: str  # Critical, High, Medium, Low
    cwe_id: str
    owasp_category: str
    threat_model: str
    preconditions: str
    default_attack_input: str
    expected_vulnerable_behavior: str
    expected_secure_behavior: str
    reproduction_instructions: str

    @abstractmethod
    def execute_vulnerable(self, input_payload: str, context: Optional[Dict[str, Any]] = None) -> SimulationResult:
        """Simulate vulnerable execution pathway with controls disabled."""
        pass

    @abstractmethod
    def execute_secure(self, input_payload: str, context: Optional[Dict[str, Any]] = None) -> SimulationResult:
        """Simulate defended execution pathway with security controls active."""
        pass

    def run(self, mode: str = "vulnerable", input_payload: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> SimulationResult:
        """Execute scenario in specified mode."""
        payload = input_payload or self.default_attack_input
        ctx = context or {}
        if mode == "protected" or mode == "secure":
            return self.execute_secure(payload, ctx)
        return self.execute_vulnerable(payload, ctx)

