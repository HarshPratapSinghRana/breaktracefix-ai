import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class MCPServer(Base):
    """Model Context Protocol (MCP) server configuration."""
    __tablename__ = "mcp_servers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    server_type = Column(String(50), default="stdio")  # stdio, sse, http
    endpoint_or_command = Column(String(500), nullable=False)
    config = Column(JSON, default=dict)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="Low")  # Critical, High, Medium, Low
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tools = relationship("MCPTool", back_populates="server", cascade="all, delete-orphan")

class MCPTool(Base):
    """Tool exposed by an MCP server."""
    __tablename__ = "mcp_tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    server_id = Column(String(36), ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    input_schema = Column(JSON, default=dict)
    requires_approval = Column(String(10), default="NO")
    permission_scope = Column(String(100), default="read_only")
    agency_risk_score = Column(Float, default=0.0)
    risk_reasons = Column(JSON, default=list)

    server = relationship("MCPServer", back_populates="tools")

