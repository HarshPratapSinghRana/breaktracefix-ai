import os
import re
import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

RULES_DIR = Path(__file__).resolve().parent / "rules"
RULES_FILE = RULES_DIR / "genai_rules.yaml"

class StaticFinding(BaseModel):
    finding_id: str
    rule_id: str
    title: str
    severity: str  # Critical, High, Medium, Low
    cwe_id: str
    owasp_category: str
    file_path: str
    line_start: int
    line_end: int
    column_start: int
    column_end: int
    code_snippet: str
    source_location: str
    sink_location: str
    explanation: str
    remediation: str
    finding_type: str = "STATIC_ANALYSIS"

class SourceCodeAnalyzer:
    """Static application security testing (SAST) engine for GenAI codebases using Semgrep & SARIF 2.1.0."""

    @classmethod
    def scan_code_snippet(cls, code: str, filename: str = "agent_pipeline.py") -> List[StaticFinding]:
        """Perform targeted pattern-based AST analysis on a code string."""
        findings: List[StaticFinding] = []
        lines = code.split("\n")

        prompt_regex = re.compile(r'(f["\'].*\{.*(user_input|prompt|query|input).*\}.*["\']|\.format\(.*(user_input|prompt|query).*\))')
        logging_regex = re.compile(r'(logger\.(info|debug|warning|error)|print)\s*\(.*?(api_key|token|password|secret|bearer).*?\)', re.IGNORECASE)
        path_traversal = re.compile(r'open\s*\(\s*(file_path|path|filename)\s*[,)]')
        ssrf_regex = re.compile(r'(requests|httpx)\.get\s*\(\s*(url|target_url|endpoint|user_input|target|query)\s*[,)]')

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Rule 1: Prompt Injection
            if prompt_regex.search(stripped) and ("message" in code or "prompt" in code or "user_input" in code):
                findings.append(StaticFinding(
                    finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                    rule_id="btf-genai-prompt-template-injection",
                    title="Direct Untrusted Input Concatenation into Prompt",
                    severity="High",
                    cwe_id="CWE-20",
                    owasp_category="LLM01: Prompt Injection",
                    file_path=filename,
                    line_start=idx,
                    line_end=idx,
                    column_start=1,
                    column_end=len(line),
                    code_snippet=stripped,
                    source_location=f"{filename}:{idx} (input param)",
                    sink_location=f"{filename}:{idx} (prompt concatenation)",
                    explanation="User input is directly concatenated into a prompt template, creating an injection sink.",
                    remediation="Use system boundary delimiters and parameterized prompt templates."
                ))

            # Rule 2: Insecure Logging
            if logging_regex.search(stripped):
                findings.append(StaticFinding(
                    finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                    rule_id="btf-genai-insecure-logging-secrets",
                    title="Logging Sensitive Parameter Without Redaction",
                    severity="Medium",
                    cwe_id="CWE-532",
                    owasp_category="LLM02: Sensitive Information Disclosure",
                    file_path=filename,
                    line_start=idx,
                    line_end=idx,
                    column_start=1,
                    column_end=len(line),
                    code_snippet=stripped,
                    source_location=f"{filename}:{idx} (secret variable)",
                    sink_location=f"{filename}:{idx} (log sink)",
                    explanation="Sensitive credential or token is passed directly to logging output without redaction.",
                    remediation="Apply BreakTraceFix RedactionPipeline prior to logging."
                ))

            # Rule 3: Path Traversal
            if path_traversal.search(stripped) and "sandbox" not in code.lower() and "canonical" not in code.lower():
                findings.append(StaticFinding(
                    finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                    rule_id="btf-genai-path-traversal-tool",
                    title="Unsanitized File Path in Tool Argument",
                    severity="High",
                    cwe_id="CWE-22",
                    owasp_category="LLM06: Excessive Agency",
                    file_path=filename,
                    line_start=idx,
                    line_end=idx,
                    column_start=1,
                    column_end=len(line),
                    code_snippet=stripped,
                    source_location=f"{filename}:{idx} (path argument)",
                    sink_location=f"{filename}:{idx} (open call)",
                    explanation="Tool directly opens file path without verifying it is sandboxed within workspace.",
                    remediation="Resolve canonical path and check that it is within the authorized root."
                ))

            # Rule 4: SSRF
            if ssrf_regex.search(stripped) and "metadata" not in code.lower() and "filter" not in code.lower():
                findings.append(StaticFinding(
                    finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                    rule_id="btf-genai-ssrf-web-fetch",
                    title="Unrestricted Network Request via Web Tool",
                    severity="Critical",
                    cwe_id="CWE-918",
                    owasp_category="LLM06: Excessive Agency",
                    file_path=filename,
                    line_start=idx,
                    line_end=idx,
                    column_start=1,
                    column_end=len(line),
                    code_snippet=stripped,
                    source_location=f"{filename}:{idx} (target URL)",
                    sink_location=f"{filename}:{idx} (HTTP client get)",
                    explanation="Web retrieval tool connects to unvalidated target URL without blocking metadata addresses.",
                    remediation="Block loopback (127.0.0.1) and metadata (169.254.169.254) addresses."
                ))

        # Rule 5: Missing Tool Auth
        if "def execute_tool" in code and "auth_engine.verify" not in code and "check_permission" not in code:
            # Locate line index of execute_tool
            line_no = 1
            for l_idx, l in enumerate(lines, start=1):
                if "def execute_tool" in l:
                    line_no = l_idx
                    break
            findings.append(StaticFinding(
                finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                rule_id="btf-genai-unauthorized-tool-call",
                title="Missing Authorization Check on Tool Execution",
                severity="Critical",
                cwe_id="CWE-862",
                owasp_category="LLM06: Excessive Agency",
                file_path=filename,
                line_start=line_no,
                line_end=min(len(lines), line_no + 5),
                column_start=1,
                column_end=50,
                code_snippet="def execute_tool(...): ...",
                source_location=f"{filename}:{line_no} (tool dispatch)",
                sink_location=f"{filename}:{line_no + 1} (tool execution)",
                explanation="Tool execution function delegates tool invocation without verifying actor permissions.",
                remediation="Integrate Authorization Intelligence Engine check before tool dispatch."
            ))

        return findings

    @classmethod
    def scan_path_with_semgrep(cls, target_path: str) -> List[StaticFinding]:
        """Execute Semgrep CLI if available, falling back to Python AST scanner."""
        try:
            cmd = ["semgrep", "scan", "--config", str(RULES_FILE), "--json", target_path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode in [0, 1] and proc.stdout:
                data = json.loads(proc.stdout)
                results = []
                for item in data.get("results", []):
                    results.append(StaticFinding(
                        finding_id=f"BTF-SAST-{str(uuid.uuid4())[:8].upper()}",
                        rule_id=item.get("check_id", "semgrep-rule"),
                        title=item.get("extra", {}).get("metadata", {}).get("title", item.get("check_id")),
                        severity=item.get("extra", {}).get("severity", "WARNING").title(),
                        cwe_id=item.get("extra", {}).get("metadata", {}).get("cwe", "CWE-20"),
                        owasp_category=item.get("extra", {}).get("metadata", {}).get("owasp", "LLM01"),
                        file_path=item.get("path", target_path),
                        line_start=item.get("start", {}).get("line", 1),
                        line_end=item.get("end", {}).get("line", 1),
                        column_start=item.get("start", {}).get("col", 1),
                        column_end=item.get("end", {}).get("col", 1),
                        code_snippet=item.get("extra", {}).get("lines", ""),
                        source_location=f"{item.get('path')}:{item.get('start', {}).get('line')}",
                        sink_location=f"{item.get('path')}:{item.get('end', {}).get('line')}",
                        explanation=item.get("extra", {}).get("message", ""),
                        remediation=item.get("extra", {}).get("metadata", {}).get("remediation", "Apply security control.")
                    ))
                if results:
                    return results
        except Exception:
            pass

        p = Path(target_path)
        all_findings = []
        if p.is_file():
            try:
                code = p.read_text(encoding="utf-8", errors="ignore")
                all_findings.extend(cls.scan_code_snippet(code, filename=str(p)))
            except Exception:
                pass
        elif p.is_dir():
            for py_file in p.rglob("*.py"):
                try:
                    code = py_file.read_text(encoding="utf-8", errors="ignore")
                    all_findings.extend(cls.scan_code_snippet(code, filename=str(py_file)))
                except Exception:
                    continue
        return all_findings

    @classmethod
    def export_sarif_v2(cls, findings: List[StaticFinding]) -> Dict[str, Any]:
        """Convert findings into OASIS SARIF v2.1.0 JSON format."""
        rules = []
        rule_ids_seen = set()
        results = []

        for f in findings:
            if f.rule_id not in rule_ids_seen:
                rule_ids_seen.add(f.rule_id)
                rules.append({
                    "id": f.rule_id,
                    "name": f.title,
                    "shortDescription": {"text": f.title},
                    "fullDescription": {"text": f.explanation},
                    "help": {"text": f.remediation},
                    "properties": {
                        "cwe": f.cwe_id,
                        "owasp": f.owasp_category,
                        "security-severity": "8.0" if f.severity in ["Critical", "High"] else "5.0"
                    }
                })

            results.append({
                "ruleId": f.rule_id,
                "message": {"text": f.explanation},
                "level": "error" if f.severity in ["Critical", "High"] else "warning",
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f.file_path},
                            "region": {
                                "startLine": f.line_start,
                                "endLine": f.line_end,
                                "startColumn": f.column_start,
                                "endColumn": f.column_end,
                                "snippet": {"text": f.code_snippet}
                            }
                        }
                    }
                ]
            })

        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "BreakTraceFix AI Static Analyzer",
                            "version": "1.0.0",
                            "informationUri": "https://breaktracefix.ai",
                            "rules": rules
                        }
                    },
                    "results": results
                }
            ]
        }
