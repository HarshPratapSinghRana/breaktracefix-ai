from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class RAGDocumentCreate(BaseModel):
    title: str
    source_uri: Optional[str] = None
    content_chunk: str
    allowed_roles: List[str] = ["*"]
    data_classification: str = "Internal"

class RAGDocumentRead(RAGDocumentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    collection_id: str
    is_poisoned: bool
    poison_indicators: List[str] = []

class RAGCollectionCreate(BaseModel):
    name: str
    vector_store_type: str = "memory"
    isolation_mode: str = "tenant_filtered"

class RAGCollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    vector_store_type: str
    isolation_mode: str
    document_count: int
    poisoning_risk_score: int
    created_at: datetime
    documents: List[RAGDocumentRead] = []

class RAGAuditRequest(BaseModel):
    collection_id: str
    query: str
    actor_tenant_id: str
    actor_role: str
