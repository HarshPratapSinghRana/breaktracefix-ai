from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ReportRequest(BaseModel):
    assessment_id: str
    format: str = "json"  # json, html, sarif, markdown
    include_evidence: bool = True
    include_remediation: bool = True

class SecurityReportRead(BaseModel):
    report_id: str
    assessment_name: str
    generated_at: str
    executive_summary: Dict[str, Any]
    risk_score: int
    risk_level: str
    findings_summary: Dict[str, int]
    findings: List[Dict[str, Any]]
    methodology: str

