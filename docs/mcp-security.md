# BreakTraceFix AI - MCP & RAG Security Auditing

## MCP Security Inspector
The Model Context Protocol (MCP) Security Inspector parses server manifests and evaluates:
- Destructive operation keywords (delete, drop, kill, wipe).
- Arbitrary script/SQL/command execution risks.
- External network requests and SSRF exposure.
- Argument schema validation (missing length, pattern, or enum boundaries).
- Transparent Excessive Agency scoring (0-100) with explainable factors.

## RAG Security Auditor
The RAG Security Auditor inspects knowledge bases for:
- Indirect prompt injection signatures (e.g., `[SYSTEM DIRECTIVE]`, override triggers).
- Cross-tenant vector partition leaks.
- Document-level classification clearances.

