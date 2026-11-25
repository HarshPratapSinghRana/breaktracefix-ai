from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class PatchValidationRequest(BaseModel):
    finding_id: str
    patch_title: str
    patch_diff: Optional[str] = None
    retest_mode: str = "comparison"

class PatchValidationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    finding_id: str
    patch_title: str
    patch_diff: Optional[str] = None
    vulnerable_run_id: Optional[str] = None
    patched_run_id: Optional[str] = None
    invariants_verified: bool
    confidence_score: float
    validation_status: str
    evidence_comparison: Dict[str, Any] = {}
    regression_test_code: Optional[str] = None
    created_at: datetime
