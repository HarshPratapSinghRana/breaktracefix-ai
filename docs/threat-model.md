# BreakTraceFix AI - Threat Model & Vulnerability Taxonomy

**Author:** Harsh Pratap Singh Rana  
**Version:** 1.0.0  
**Framework Mappings:** OWASP Top 10 for LLM Applications (2025), MITRE ATLAS, CWE  

---

## 1. Threat Landscape Overview

Autonomous agents, LLM applications, and Retrieval-Augmented Generation (RAG) systems introduce unique trust-boundary failures. Unlike standard client-server applications where code and data are strictly segregated, Generative AI models mix instructions (prompts) and untrusted data in the same context window.

BreakTraceFix AI models threats across four primary boundaries:
1. **User-to-Agent Boundary:** Direct prompt injections, jailbreaks, prompt extraction.
2. **Context-to-Agent Boundary:** Indirect prompt injection via poisoned documents, web scrapes, or user-supplied attachments.
3. **Agent-to-Tool Boundary:** Excessive agency, SSRF, unauthorized tool execution, path traversal via tool arguments, MCP abuse.
4. **Agent-to-Data Boundary:** Cross-tenant information leakage, unauthorized vector retrieval, sensitive data exposure in execution logs.

---

## 2. 14 Core Attack Scenarios & Vulnerability Taxonomy

| ID | Attack Name | OWASP LLM (2025) | CWE Mapping | Severity | Threat Model Description |
|---|---|---|---|---|---|
| `BTF-ATK-001` | Direct Prompt Injection | LLM01: Prompt Injection | CWE-20 (Improper Input Validation) | High | Attacker provides crafted prompt text that overrides system developer instructions and causes the agent to ignore safety guidelines. |
| `BTF-ATK-002` | Indirect Prompt Injection | LLM01: Prompt Injection | CWE-20 (Improper Input Validation) | Critical | Untrusted external data retrieved via RAG or web search contains hidden instructions that hijack the model's reasoning flow. |
| `BTF-ATK-003` | System Prompt Extraction | LLM07: System Prompt Leakage | CWE-200 (Exposure of Sensitive Information) | Medium | Attacker employs linguistic inversion techniques to force the model into revealing its internal system prompts and business rules. |
| `BTF-ATK-004` | Sensitive Information Disclosure | LLM02: Sensitive Information Disclosure | CWE-359 (Exposure of Private Personal Info) | Critical | Model outputs internal API keys, database credentials, or customer PII that were erroneously included in prompt context. |
| `BTF-ATK-005` | RAG Document Poisoning | LLM04: Data and Model Poisoning | CWE-345 (Insufficient Verification of Data) | High | Knowledge base chunks contain malicious payloads disguised as factual data to manipulate downstream model conclusions. |
| `BTF-ATK-006` | Excessive Agency | LLM06: Excessive Agency | CWE-250 (Execution with Unnecessary Privileges) | High | Agent has autonomy to invoke destructive or high-impact tools without required human-in-the-loop approvals. |
| `BTF-ATK-007` | Unauthorized Tool Execution | LLM06: Excessive Agency | CWE-862 (Missing Authorization) | Critical | Agent invokes an internal tool on behalf of an actor who lacks necessary RBAC/ABAC permissions for that tool. |
| `BTF-ATK-008` | Insecure Output Handling | LLM05: Insecure Output Handling | CWE-79 / CWE-78 (Improper Neutralization) | High | Downstream application executes or renders agent outputs directly (e.g., executing raw shell or unescaped HTML) leading to XSS or RCE. |
| `BTF-ATK-009` | Cross-Tenant Information Disclosure | LLM02: Sensitive Information Disclosure | CWE-284 (Improper Access Control) | Critical | Tenant A queries the agent and receives vector embeddings, customer records, or context belonging to Tenant B due to missing tenant partition filters. |
| `BTF-ATK-010` | SSRF via Agent Tool Arguments | LLM06: Excessive Agency | CWE-918 (Server-Side Request Forgery) | Critical | Attacker instructs agent to browse or query an internal cloud metadata service (`http://169.254.169.254`) or loopback address via a generic HTTP/fetch tool. |
| `BTF-ATK-011` | Path Traversal via Tool Arguments | LLM06: Excessive Agency | CWE-22 (Path Traversal) | High | Agent accepts file path arguments containing `../` or absolute system paths to read or overwrite critical operating system files. |
| `BTF-ATK-012` | MCP Tool Abuse | LLM06: Excessive Agency / LLM10: Unbounded Consumption | CWE-285 (Improper Authorization) | High | Model Context Protocol server exposes high-privilege tools with broad definitions, allowing attackers to invoke unvalidated procedures. |
| `BTF-ATK-013` | Improper Authorization | LLM06: Excessive Agency | CWE-862 (Missing Authorization) | High | Agent accesses protected documents or resources without verifying user identity, role, or resource-level ACLs. |
| `BTF-ATK-014` | Log Information Exposure | LLM02: Sensitive Information Disclosure | CWE-532 (Insertion of Sensitive Info into Log) | Medium | Execution logs, debug traces, and telemetry store raw user secrets, API keys, and session tokens without automated redaction. |

---

## 3. Defense Invariants & Verification Model

For each vulnerability, BreakTraceFix AI defines formal security invariants:

1. **Input Invariant (`Inv-Input`):** Adversarial instructions in untrusted data must not alter system intent.
2. **Context Invariant (`Inv-Context`):** Context boundaries must strictly separate untrusted data from system instructions.
3. **Authorization Invariant (`Inv-Auth`):** Every tool invocation and document retrieval must verify `Actor`, `Tenant`, `Resource`, `Action`, and `Approval`.
4. **Data Isolation Invariant (`Inv-Isolation`):** Multi-tenant partitions must never return cross-tenant data.
5. **Output Invariant (`Inv-Output`):** All output leaving the model must be validated against schema and sanitized against injection sinks.
6. **Telemetry Invariant (`Inv-Telemetry`):** Sensitive credentials and PII must be redacted prior to persistence or telemetry dispatch.

