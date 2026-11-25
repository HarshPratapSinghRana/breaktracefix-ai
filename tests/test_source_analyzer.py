import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app
from backend.app.services.source_analyzer.analyzer import SourceCodeAnalyzer, RULES_FILE

VULNERABLE_CODE_SAMPLE = '''
import os
import requests
import logging

logger = logging.getLogger("agent")

def agent_handler(user_input, api_token):
    # Insecure logging of sensitive token
    logger.info(f"Processing query with token {api_token}")
    
    # Direct untrusted prompt concatenation
    prompt = f"System: summarize this user prompt: {user_input}"
    
    # SSRF vulnerability in web fetch
    response = requests.get(user_input)
    
    return prompt

def read_file_tool(file_path):
    # Path traversal vulnerability
    with open(file_path, "r") as f:
        return f.read()

def execute_tool(tool_name, tool_args):
    # Missing authorization check before tool call
    return eval(tool_name)(**tool_args)
'''

def test_static_analyzer_detects_vulnerabilities():
    findings = SourceCodeAnalyzer.scan_code_snippet(VULNERABLE_CODE_SAMPLE, filename="vulnerable_agent.py")
    assert len(findings) >= 4

    rule_ids = [f.rule_id for f in findings]
    assert "btf-genai-prompt-template-injection" in rule_ids
    assert "btf-genai-insecure-logging-secrets" in rule_ids
    assert "btf-genai-path-traversal-tool" in rule_ids
    assert "btf-genai-ssrf-web-fetch" in rule_ids
    assert "btf-genai-unauthorized-tool-call" in rule_ids

    # Check finding fields
    for f in findings:
        assert f.finding_type == "STATIC_ANALYSIS"
        assert f.cwe_id.startswith("CWE-")
        assert f.line_start > 0
        assert f.remediation is not None
        assert f.source_location is not None
        assert f.sink_location is not None

def test_sarif_v2_export_compliance():
    findings = SourceCodeAnalyzer.scan_code_snippet(VULNERABLE_CODE_SAMPLE, filename="vulnerable_agent.py")
    sarif = SourceCodeAnalyzer.export_sarif_v2(findings)

    assert sarif["version"] == "2.1.0"
    assert "$schema" in sarif
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "BreakTraceFix AI Static Analyzer"
    assert len(run["tool"]["driver"]["rules"]) >= 4
    assert len(run["results"]) == len(findings)

    first_result = run["results"][0]
    assert "ruleId" in first_result
    assert "locations" in first_result
    assert "physicalLocation" in first_result["locations"][0]

def test_semgrep_rules_yaml_validity():
    assert RULES_FILE.exists()
    content = RULES_FILE.read_text(encoding="utf-8")
    assert "rules:" in content
    assert "btf-genai-prompt-template-injection" in content
    assert "btf-genai-unauthorized-tool-call" in content

def test_source_analyzer_api_endpoints():
    client = TestClient(app)

    # Scan API
    scan_res = client.post("/api/v1/source-analyzer/scan", json={
        "code": VULNERABLE_CODE_SAMPLE,
        "filename": "api_test.py"
    })
    assert scan_res.status_code == 200
    data = scan_res.json()["data"]
    assert len(data) >= 4

    # Rules API
    rules_res = client.get("/api/v1/source-analyzer/rules")
    assert rules_res.status_code == 200
    assert rules_res.json()["data"]["rules_count"] >= 5

    # SARIF Export API
    sarif_res = client.post("/api/v1/source-analyzer/export-sarif", json={
        "code": VULNERABLE_CODE_SAMPLE,
        "filename": "sarif_test.py"
    })
    assert sarif_res.status_code == 200
    sarif_data = sarif_res.json()["data"]
    assert sarif_data["version"] == "2.1.0"
    assert len(sarif_data["runs"][0]["results"]) >= 4

