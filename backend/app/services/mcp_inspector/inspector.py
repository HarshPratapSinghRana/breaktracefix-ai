from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MCPToolAnalysis(BaseModel):
    tool_name: str
    description: str
    risk_score: float
    risk_level: str  # Critical, High, Medium, Low
    requires_approval: str
    permission_scope: str
    risk_factors: List[str]
    argument_warnings: List[str]

class MCPInspectionReport(BaseModel):
    server_name: str
    total_tools: int
    overall_risk_score: float
    overall_risk_level: str
    high_risk_tools: int
    tools: List[MCPToolAnalysis]
    recommendations: List[str]

class MCPSecurityInspector:
    """Audits Model Context Protocol (MCP) tool configurations, schemas, and excessive agency."""

    DESTRUCTIVE_KEYWORDS = ["delete", "remove", "drop", "terminate", "kill", "purge", "destroy", "format", "wipe"]
    EXECUTION_KEYWORDS = ["exec", "eval", "shell", "bash", "command", "run_script", "system", "sql"]
    NETWORK_KEYWORDS = ["http", "curl", "fetch", "request", "download", "webhook", "socket"]

    @classmethod
    def inspect_manifest(cls, manifest_json: Dict[str, Any], server_name: str = "MCP-Server") -> MCPInspectionReport:
        tools_list = manifest_json.get("tools", [])
        analyzed_tools: List[MCPToolAnalysis] = []
        total_risk = 0.0

        for t in tools_list:
            name = t.get("name", "unknown_tool")
            desc = t.get("description", "")
            schema = t.get("inputSchema", t.get("parameters", {}))
            
            risk_score = 10.0  # Base risk
            factors = []
            arg_warnings = []

            # 1. Destructive Operation Detection
            lower_name = name.lower()
            lower_desc = desc.lower()
            if any(k in lower_name or k in lower_desc for k in cls.DESTRUCTIVE_KEYWORDS):
                risk_score += 35.0
                factors.append("Tool performs irreversible or destructive mutations.")

            # 2. Arbitrary Command Execution Risk
            if any(k in lower_name or k in lower_desc for k in cls.EXECUTION_KEYWORDS):
                risk_score += 40.0
                factors.append("Tool facilitates arbitrary script, SQL, or shell execution.")

            # 3. External Network Reach
            if any(k in lower_name or k in lower_desc for k in cls.NETWORK_KEYWORDS):
                risk_score += 20.0
                factors.append("Tool opens network connections, introducing SSRF and exfiltration risks.")

            # 4. Argument Schema Rigor Check
            props = schema.get("properties", {})
            if not props and schema.get("type") == "object":
                risk_score += 15.0
                arg_warnings.append("Tool accepts unbounded open-ended object arguments without property definitions.")
            
            for p_name, p_spec in props.items():
                if p_spec.get("type") == "string":
                    if "enum" not in p_spec and "maxLength" not in p_spec and "pattern" not in p_spec:
                        risk_score += 5.0
                        arg_warnings.append(f"Argument '{p_name}' lacks regex, length, or enum constraints.")

            # 5. Approval Requirements
            req_approval = "YES" if (risk_score >= 60.0 or "approval" in t) else "NO"
            if req_approval == "NO" and risk_score >= 50.0:
                factors.append("High-risk tool currently lacks mandatory human-in-the-loop approval gate.")

            # Bound score to 100
            final_tool_score = min(100.0, max(0.0, risk_score))
            level = "Critical" if final_tool_score >= 80 else ("High" if final_tool_score >= 60 else ("Medium" if final_tool_score >= 35 else "Low"))

            analyzed_tools.append(MCPToolAnalysis(
                tool_name=name,
                description=desc,
                risk_score=round(final_tool_score, 1),
                risk_level=level,
                requires_approval=req_approval,
                permission_scope="read_only" if final_tool_score < 40 else "read_write_privilege",
                risk_factors=factors,
                argument_warnings=arg_warnings
            ))
            total_risk += final_tool_score

        overall_score = round(total_risk / max(1, len(analyzed_tools)), 1)
        overall_level = "Critical" if overall_score >= 75 else ("High" if overall_score >= 55 else ("Medium" if overall_score >= 35 else "Low"))
        high_risk_count = sum(1 for at in analyzed_tools if at.risk_level in ["Critical", "High"])

        recs = [
            "Enforce strict JSON schema types (regex, maxLength, enum) on all string arguments.",
            "Mandate Human-in-the-Loop approval tokens for tools performing delete, update, or shell operations.",
            "Confine database MCP tools to read-only query scopes with parameterized query builders."
        ]

        return MCPInspectionReport(
            server_name=server_name,
            total_tools=len(analyzed_tools),
            overall_risk_score=overall_score,
            overall_risk_level=overall_level,
            high_risk_tools=high_risk_count,
            tools=analyzed_tools,
            recommendations=recs
        )

