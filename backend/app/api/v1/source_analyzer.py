from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.source_analyzer.analyzer import SourceCodeAnalyzer, StaticFinding, RULES_FILE

router = APIRouter(prefix="/source-analyzer", tags=["Source Code Analyzer"])

class CodeScanRequest(BaseModel):
    code: str
    filename: Optional[str] = "agent_app.py"

@router.post("/scan", response_model=ResponseEnvelope[List[StaticFinding]])
def scan_code(payload: CodeScanRequest):
    """Perform static analysis on code snippet using GenAI security rules."""
    findings = SourceCodeAnalyzer.scan_code_snippet(payload.code, filename=payload.filename or "agent_app.py")
    return ResponseEnvelope(
        data=findings,
        message=f"Static code analysis completed: {len(findings)} issues identified."
    )

@router.get("/rules", response_model=ResponseEnvelope[Dict[str, Any]])
def list_analyzer_rules():
    """Retrieve active Semgrep GenAI rule definitions."""
    if RULES_FILE.exists():
        content = RULES_FILE.read_text(encoding="utf-8")
        return ResponseEnvelope(data={"rules_yaml": content, "rules_count": 5})
    return ResponseEnvelope(data={"rules_yaml": "", "rules_count": 0})

@router.post("/export-sarif", response_model=ResponseEnvelope[Dict[str, Any]])
def export_sarif(payload: CodeScanRequest):
    """Scan code and export results formatted as standard SARIF 2.1.0."""
    findings = SourceCodeAnalyzer.scan_code_snippet(payload.code, filename=payload.filename or "agent_app.py")
    sarif = SourceCodeAnalyzer.export_sarif_v2(findings)
    return ResponseEnvelope(data=sarif)

