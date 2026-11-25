# BreakTraceFix AI - Product Requirements Document (PRD)

**Project Name:** BreakTraceFix AI  
**Tagline:** Break It. Trace It. Fix It.  
**Author:** Harsh Pratap Singh Rana  
**Status:** Approved Architecture & Specification (Phase 1 Clean-Room)  
**Classification:** GenAI Security Research, Vulnerability Assessment & Runtime Defense Platform  

---

## 1. Executive Summary & Vision

Generative AI applications, autonomous agents, and RAG pipelines interact directly with untrusted user inputs, corporate databases, internal tools, and external APIs. Traditional application security tools are blind to the unique failure modes of LLMs: prompt injections, indirect context manipulation, excessive agentic autonomy, tool misuse, poisoned retrieval contexts, and broken multi-tenant authorization boundaries.

**BreakTraceFix AI** provides an end-to-end security research and assurance platform built on the core paradigm:
1. **Break It:** Simulate realistic, controlled GenAI attack scenarios spanning the OWASP LLM Top 10 and CWE categories.
2. **Trace It:** Deeply inspect the 11-stage execution and data-flow pipeline from user input through retrieval, context assembly, model invocation, authorization, and tool execution with sensitive data redaction.
3. **Fix It:** Verify security controls via side-by-side comparative execution, validate security patches, enforce context-aware authorization policies, and auto-generate regression tests.

---

## 2. Core Functional Requirements

### 2.1 Module 1: Attack Simulation Engine
- **Extensible Scenario Registry:** Decoupled registry allowing dynamic registration and execution of security test scenarios.
- **14 Threat Categories Supported:**
  1. Direct Prompt Injection (jailbreaks, instruction overriding)
  2. Indirect Prompt Injection (manipulated web/document content)
  3. System Prompt Extraction (reconnaissance, confidentiality bypass)
  4. Sensitive Information Disclosure (PII, credentials, internal prompts)
  5. RAG Document Poisoning (injected instructions inside knowledge bases)
  6. Excessive Agency (unbounded tool calling, autonomous drift)
  7. Unauthorized Tool Execution (calling privileged tools without rights)
  8. Insecure Output Handling (XSS / command injection via unescaped LLM response)
  9. Cross-Tenant Information Disclosure (tenant boundary leakage)
  10. Server-Side Request Forgery via Agents (SSRF via unvalidated tool inputs)
  11. Path Traversal via Tool Arguments (directory traversal attempts)
  12. MCP Tool Abuse (improper capability negotiation and parameter manipulation)
  13. Improper Authorization (missing role or resource checks)
  14. Privilege Escalation (horizontal and vertical authorization bypass)
- **Standardized Scenario Metadata:** Unique ID, Title, Category, Severity (Critical, High, Medium, Low), Preconditions, Threat Model, Attack Inputs, Expected Vulnerable Behavior, Expected Secure Behavior, CWE Mappings, OWASP LLM Mappings, and Invariant Definitions.
- **Safety Boundary:** All simulations execute within controlled sandboxed environments with mock tool interfaces and synthetic payloads.

### 2.2 Module 2: Authorization Intelligence Engine
- **Context-Aware Evaluation Matrix:** Evaluates 8 distinct contextual axes:
  1. `Actor`: User/Agent identity and roles
  2. `Tenant`: Organizational isolation boundary
  3. `Resource`: Target document, model, or tool
  4. `Action`: Requested operation (read, write, invoke, delete)
  5. `Classification`: Data sensitivity tier (Public, Internal, Confidential, Restricted)
  6. `Purpose`: Business justification (e.g., customer_support, audit)
  7. `Recipient`: Intended destination of data (internal agent, external user, third party)
  8. `Approval`: Requirement for explicit human-in-the-loop sign-off
- **Dual Policy Evaluation:** Attribute-Based Access Control (ABAC) layered over Role-Based Access Control (RBAC).
- **Decision Audit Trail:** Complete tamper-evident audit log of every evaluation with step-by-step rule reasoning.

### 2.3 Module 3: Data Flow & Execution Tracing System
- **11-Stage Pipeline Observability:**
  1. `User Input`
  2. `Input Validation`
  3. `Prompt Construction`
  4. `Retrieval`
  5. `Context Assembly`
  6. `Model Invocation`
  7. `Tool Selection`
  8. `Authorization Check`
  9. `Tool Execution`
  10. `Output Validation`
  11. `Final Response`
- **Data Protection & Privacy:** Automatic PII and credential redaction (regex + pattern masking for API keys, bearer tokens, SSNs, credit cards, emails) before persisting or displaying traces.
- **OpenTelemetry Standard Compatibility:** Standard span attributes, trace IDs, parent-child spans, duration, and error records.
- **Visual Timeline & Execution Graph:** Interactive representation of the entire lifecycle.

### 2.4 Module 4: Vulnerability Reproduction & Patch Validation Engine
- **Side-by-Side Dual Run:** Executes target scenario in `Vulnerable Mode` (controls disabled) and `Protected Mode` (guardrails/policies enabled).
- **Security Invariant Verification:** Evaluates assertion rules (e.g., `tool_not_executed`, `output_sanitized`, `tenant_isolated`, `authorization_denied`).
- **Regression Test Generator:** Auto-generates executable test templates (`pytest`) from verified findings.

### 2.5 Module 5: Source Code Security Analyzer
- **Static Analysis Integration:** Semgrep rule engine integration supporting custom rules tailored to LLM security vulnerabilities.
- **SARIF 2.1.0 Compliance:** Standardized import/export of static security findings.
- **Source-to-Sink Pathing:** Pinpoint exact file, line ranges, source inputs, and vulnerable sinks (e.g., unvalidated prompt template injection, unsanitized tool calls).

### 2.6 Module 6: Security Reporting Engine
- **Multi-Format Export:** Executive Summary, Technical Report, JSON, HTML, and SARIF formats.
- **Finding Completeness:** ID, Title, Severity, CWE, OWASP, Component, Location, Reproduction Steps, Evidence Log, Root Cause, Impact, Remediation, and Patch Validation Status.

### 2.7 Advanced Differentiating Capabilities
- **MCP Security Inspector:** Analyzes Model Context Protocol (MCP) server definitions, tool declarations, permission scopes, argument boundary types, and excessive agency risk.
- **RAG Security Auditor:** Audits document-level ACLs, cross-tenant vector partition leaks, and poisoned instruction patterns inside retrieval chunks.
- **AI Permission Risk Scoring:** Transparent 0–100 risk score based on tool destructive potential, data classification, network reach, and approval requirements.
- **Authorization Context Visualizer:** Visual flowchart: `Actor -> Tenant -> Resource -> Action -> Policy -> Decision`.
- **Patch Validation Workbench:** Side-by-side evidence diff showing raw request, trace comparison, invariant verification, and patch confidence score.

---

## 3. Technology Stack & Deployment Strategy

- **Backend:** Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite (development/serverless) & PostgreSQL (production), Alembic.
- **Serverless & Cloud:** Vercel serverless deployment support via `/api` entrypoints and `vercel.json` routing configuration; standalone Docker Compose for containerized enterprise environments.
- **Frontend:** React 18+, TypeScript, Vite, Tailwind CSS, Recharts (metrics and radar charts), Lucide icons, Dark theme default.
- **Static Analysis & Standards:** Semgrep, SARIF 2.1.0, OWASP Top 10 for LLM (2025), CWE mappings (CWE-20, CWE-79, CWE-200, CWE-285, CWE-862, CWE-918, CWE-22, etc.).

---

## 4. Non-Functional & Quality Standards
- **Clean-Room Independent Implementation:** 100% original architecture, code, schema, rules, and UI.
- **Safe Testing Guarantee:** Synthetic, harmless security test probes and mock environments only.
- **Reproducibility:** Deterministic test outcomes with complete audit trails.
- **Zero-Trust Defaults:** Deny-by-default authorization and default redaction of sensitive trace fields.

