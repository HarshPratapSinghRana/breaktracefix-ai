import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PoisonIndicator(BaseModel):
    pattern_name: str
    matched_snippet: str
    severity: str
    remediation: str

class RAGChunkAudit(BaseModel):
    chunk_id: str
    title: str
    classification: str
    is_poisoned: bool
    allowed_roles: List[str]
    tenant_isolated: bool
    poison_indicators: List[PoisonIndicator]

class RAGAuditReport(BaseModel):
    collection_name: str
    total_chunks: int
    poisoned_chunks_count: int
    unisolated_chunks_count: int
    overall_rag_risk_score: float
    audit_findings: List[RAGChunkAudit]
    security_summary: str

class RAGSecurityAuditor:
    """Audits RAG vector knowledge bases for cross-tenant isolation and indirect instruction poisoning."""

    POISON_PATTERNS = [
        (re.compile(r"\[SYSTEM\s+DIRECTIVE:.*?\]", re.IGNORECASE), "System Directive Inversion", "Critical", "Strip directive brackets from RAG context."),
        (re.compile(r"(ignore\s+all\s+previous\s+instructions|disregard\s+prior\s+guidelines)", re.IGNORECASE), "Instruction Override Signature", "High", "Quarantine document chunk."),
        (re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL), "Embedded HTML Script Tag", "High", "Sanitize HTML tags before vector indexing."),
        (re.compile(r"(EXFILTRATE|SEND_TO_SERVER|exfiltrate_key)", re.IGNORECASE), "Data Exfiltration Signature", "Critical", "Quarantine and alert security operations."),
        (re.compile(r"ADMIN_OVERRIDE_KEY\s*=\s*[A-Za-z0-9_-]+", re.IGNORECASE), "Hardcoded Override Secret", "High", "Remove administrative tokens from knowledge base.")
    ]

    @classmethod
    def audit_chunks(
        cls,
        chunks: List[Dict[str, Any]],
        collection_name: str = "Corporate Knowledge Base",
        current_tenant_id: str = "tenant-default-001"
    ) -> RAGAuditReport:
        audited_chunks: List[RAGChunkAudit] = []
        poisoned_count = 0
        unisolated_count = 0

        for idx, ch in enumerate(chunks, start=1):
            chunk_id = ch.get("id", f"chk-{idx:03d}")
            title = ch.get("title", f"Document Chunk #{idx}")
            content = ch.get("content", ch.get("text", ""))
            classification = ch.get("classification", "Internal")
            roles = ch.get("allowed_roles", ["*"])
            tenant_id = ch.get("tenant_id", current_tenant_id)

            tenant_isolated = (tenant_id == current_tenant_id)
            if not tenant_isolated:
                unisolated_count += 1

            indicators: List[PoisonIndicator] = []
            for pattern, name, sev, rem in cls.POISON_PATTERNS:
                match = pattern.search(content)
                if match:
                    indicators.append(PoisonIndicator(
                        pattern_name=name,
                        matched_snippet=match.group(0)[:80],
                        severity=sev,
                        remediation=rem
                    ))

            is_poisoned = len(indicators) > 0
            if is_poisoned:
                poisoned_count += 1

            audited_chunks.append(RAGChunkAudit(
                chunk_id=chunk_id,
                title=title,
                classification=classification,
                is_poisoned=is_poisoned,
                allowed_roles=roles,
                tenant_isolated=tenant_isolated,
                poison_indicators=indicators
            ))

        risk_score = 0.0
        if audited_chunks:
            poison_factor = (poisoned_count / len(audited_chunks)) * 60.0
            isolation_factor = (unisolated_count / len(audited_chunks)) * 40.0
            risk_score = min(100.0, poison_factor + isolation_factor)

        summary = (
            f"Audited {len(audited_chunks)} chunks: {poisoned_count} poisoned chunks detected, "
            f"{unisolated_count} cross-tenant partition violations found. Overall risk score: {round(risk_score, 1)}/100."
        )

        return RAGAuditReport(
            collection_name=collection_name,
            total_chunks=len(audited_chunks),
            poisoned_chunks_count=poisoned_count,
            unisolated_chunks_count=unisolated_count,
            overall_rag_risk_score=round(risk_score, 1),
            audit_findings=audited_chunks,
            security_summary=summary
        )

