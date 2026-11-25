from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1

class HealthStatus(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    project: str = "BreakTraceFix AI"
    database: str = "connected"
    environment: str = "development"

