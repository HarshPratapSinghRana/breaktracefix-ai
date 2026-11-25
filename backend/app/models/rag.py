import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class RAGCollection(Base):
    """Knowledge collection audited for RAG security."""
    __tablename__ = "rag_collections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    vector_store_type = Column(String(50), default="memory")  # memory, pgvector, chromadb, qdrant
    isolation_mode = Column(String(50), default="tenant_filtered")  # namespace, tenant_filtered, shared_unisolated
    document_count = Column(Integer, default=0)
    poisoning_risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    documents = relationship("RAGDocument", back_populates="collection", cascade="all, delete-orphan")

class RAGDocument(Base):
    """Document / chunk inside a RAG collection."""
    __tablename__ = "rag_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String(36), ForeignKey("rag_collections.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    source_uri = Column(String(500), nullable=True)
    content_chunk = Column(Text, nullable=False)
    allowed_roles = Column(JSON, default=lambda: ["*"])
    data_classification = Column(String(50), default="Internal")
    is_poisoned = Column(Boolean, default=False)
    poison_indicators = Column(JSON, default=list)

    collection = relationship("RAGCollection", back_populates="documents")

