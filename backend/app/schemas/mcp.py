from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class MCPToolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = {}
    requires_approval: str
    permission_scope: str
    agency_risk_score: float
    risk_reasons: List[str] = []

class MCPServerCreate(BaseModel):
    name: str
    server_type: str = "stdio"
    endpoint_or_command: str
    config: Dict[str, Any] = {}

class MCPServerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    server_type: str
    endpoint_or_command: str
    config: Dict[str, Any] = {}
    risk_score: float
    risk_level: str
    created_at: datetime
    tools: List[MCPToolRead] = []

class MCPInspectRequest(BaseModel):
    manifest_json: Dict[str, Any]
    server_name: Optional[str] = "Inspected-MCP-Server"
