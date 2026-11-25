from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.schemas.common import ResponseEnvelope
from backend.app.schemas.mcp import MCPInspectRequest
from backend.app.services.mcp_inspector.inspector import MCPSecurityInspector, MCPInspectionReport

router = APIRouter(prefix="/mcp-inspector", tags=["MCP Security Inspector"])

SAMPLE_MCP_MANIFEST = {
    "server": "sqlite-tools",
    "version": "1.0.0",
    "tools": [
        {
            "name": "execute_query",
            "description": "Execute arbitrary SQL statement on database.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string"}
                },
                "required": ["sql"]
            }
        },
        {
            "name": "read_records",
            "description": "Read records matching filter query.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "table": {"type": "string", "maxLength": 50},
                    "limit": {"type": "integer"}
                }
            }
        },
        {
            "name": "delete_all_users",
            "description": "Permanently wipe and destroy users table records.",
            "inputSchema": {"type": "object"}
        }
    ]
}

@router.get("/sample-manifest", response_model=ResponseEnvelope[dict])
def get_sample_manifest():
    """Retrieve sample MCP server manifest for inspection."""
    return ResponseEnvelope(data=SAMPLE_MCP_MANIFEST)

@router.post("/inspect", response_model=ResponseEnvelope[MCPInspectionReport])
def inspect_mcp_server(payload: MCPInspectRequest):
    """Audit MCP tool manifest for excessive agency, parameter boundaries, and destructive actions."""
    report = MCPSecurityInspector.inspect_manifest(
        manifest_json=payload.manifest_json,
        server_name=payload.server_name or "Inspected-MCP-Server"
    )
    return ResponseEnvelope(
        data=report,
        message=f"MCP audit completed: Risk Score {report.overall_risk_score}/100 ({report.overall_risk_level})."
    )

