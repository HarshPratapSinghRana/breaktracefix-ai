# BreakTraceFix AI - System Architecture Document

**Author:** Harsh Pratap Singh Rana  
**Version:** 1.0.0 (Clean-Room Design)  
**Product:** BreakTraceFix AI — Break It. Trace It. Fix It.  

---

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                           BREAKTRACEFIX AI FRONTEND                               |
|        React 18 + TypeScript + Vite + Tailwind CSS + Recharts + Lucide Icons       |
|                                                                                   |
|  [Overview] [Assessments] [Attack Sim] [Vuln Explorer] [Trace Explorer] [Auth Intel]|
|  [Code Analyzer] [MCP Inspector] [RAG Auditor] [Patch Workbench] [Reports] [Config]|
+------------------------------------------+----------------------------------------+
                                           | REST API / JSON
                                           v
+-----------------------------------------------------------------------------------+
|                        FASTAPI BACKEND APPLICATION CORE                           |
|       (Dual Deployment: Vercel Serverless Function /api + Standalone Uvicorn)     |
+-----------------------------------------------------------------------------------+
| API Routing & Middleware:                                                         |
| - Authentication & RBAC (Bearer JWT / API Keys)                                    |
| - Request Context & Tenant Isolation Middleware                                   |
| - OpenTelemetry Tracer & Structured Audit Logger                                  |
| - Automatic Sensitive Data Redaction Pipeline                                     |
+------------------------------------------+----------------------------------------+
|                                          |
+-------------------+----------------------+-------------------+--------------------+
|                   |                      |                   |                    |
v                   v                      v                   v                    v
[MODULE 1]          [MODULE 2]             [MODULE 3]          [MODULE 4]           [MODULE 5 & 6]
Attack Simulation   Authorization          Data Flow & Trace   Vulnerability Repro  Source Code Analyzer
Engine              Intelligence Engine    Engine (11-Stages)  & Patch Workbench    & Reporting Engine
- Scenario Registry - ABAC / RBAC Policy   - Pipeline Tracing  - Dual Run Executor  - Semgrep Scanner
- 14 Threat Vectors - 8-Axis Context Eval  - PII Redactor      - Invariant Checker  - SARIF 2.1 Parser
- Safe Test Runners - Decision Auditor     - Timeline Builder  - Regression Gen     - Multi-format Export
- Pre/Post Asserts  - Context Visualizer   - OTel Spans        - Diff Analyzer      (JSON, HTML, SARIF)
+-------------------+----------------------+-------------------+--------------------+
|                   |                      |                   |
v                   v                      v                   v
[FEATURE A]         [FEATURE B]            [FEATURE C]         [DATA & STORAGE]
MCP Security        RAG Security           AI Permission Risk  SQLAlchemy 2.0 ORM
Inspector           Auditor                Scoring Engine      - SQLite (Vercel)
- Config Scanner    - Vector ACL Auditor   - 0-100 Risk Model  - PostgreSQL (Docker)
- Agency Evaluator  - Poison Detector      - Explainability    - Alembic Migrations
- Arg Type Checker  - Context Slicer       - Decision Matrix   - Seed Data Fixtures
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 API Layer (`backend/app/api/` & `api/index.py`)
- **Vercel Serverless Gateway:** `api/index.py` exposes the ASGI FastAPI application instance to Vercel's Python runtime.
- **Endpoints (`api/v1/`):**
  - `/auth`: Login, token refresh, current user profile, tenant context.
  - `/assessments`: CRUD for security assessment sessions and targets.
  - `/attacks`: Catalog of 14 attack scenarios, execution trigger, batch runs.
  - `/authorization`: Policy evaluation, 8-axis context checks, policy CRUD, decision logs.
  - `/traces`: 11-stage trace inspection, timeline generation, span tree query, PII redaction.
  - `/reproduction`: Dual-run execution (vulnerable vs protected), invariant verification, patch validation.
  - `/source-analyzer`: Semgrep file scanning, rule matching, SARIF upload/download.
  - `/mcp-inspector`: MCP tool schema audit, excessive agency scoring, argument validation.
  - `/rag-auditor`: Document ACL verification, chunk poisoning heuristic scan.
  - `/reports`: Multi-format report compilation (JSON, HTML, Executive Summary, SARIF).

### 2.2 Domain Engines (`backend/app/services/`)

#### 1. Attack Simulation Engine (`services/attack_engine/`)
- `AttackRegistry`: Singleton registry holding attack scenario definitions.
- `BaseAttackScenario`: Abstract class defining `id`, `name`, `category`, `severity`, `cwe`, `owasp`, `threat_model`, `preconditions`, `run_vulnerable()`, `run_secure()`, and `verify_invariants()`.
- Built-in scenarios covering all 14 required categories.
- Safe execution harness utilizing mock agents and simulated tools with zero real-world exfiltration or destruction.

#### 2. Authorization Intelligence Engine (`services/auth_intelligence/`)
- `ContextEvaluator`: Takes `AuthorizationContext` (actor, tenant, resource, action, classification, purpose, recipient, approval).
- `PolicyEngine`: Evaluates RBAC roles, tenant isolation boundaries, resource ownership, and ABAC purpose/recipient constraints.
- `AuditLogger`: Records structured decision entries with matched policies and detailed deny/allow rationale.

#### 3. Data Flow & Execution Tracing Engine (`services/tracing/`)
- `TraceManager`: Records execution steps across the 11-stage lifecycle:
  `user_input -> input_validation -> prompt_construction -> retrieval -> context_assembly -> model_invocation -> tool_selection -> authorization -> tool_execution -> output_validation -> final_response`.
- `RedactionPipeline`: Regex and pattern-based sanitizer for credit cards, SSNs, API tokens (OpenAI, Anthropic, AWS, GitHub), bearer headers, and emails.
- `SpanExporter`: Converts traces to OpenTelemetry-compliant span schemas.

#### 4. Vulnerability Reproduction & Patch Validation (`services/reproduction/`)
- `DualRunExecutor`: Coordinates back-to-back runs of a target scenario under vulnerable vs patched configurations.
- `InvariantChecker`: Verifies assertion outcomes (e.g. `AssertNotExecuted`, `AssertSanitized`, `AssertDenied`).
- `RegressionGenerator`: Auto-synthesizes standalone `pytest` Python code representing the regression test.

#### 5. Source Code Security Analyzer (`services/source_analyzer/`)
- `SemgrepRunner`: Invokes Semgrep CLI or built-in AST rule matcher when CLI is in environment, with bundled rules for GenAI security weaknesses.
- `SARIFParser`: Ingests and generates OASIS SARIF v2.1.0 output.

#### 6. MCP & RAG Security Modules (`services/mcp_inspector/` & `services/rag_auditor/`)
- `MCPInspector`: Analyzes MCP server manifest JSON, parses tool descriptions for prompt injection indicators, evaluates argument schemas for lack of type constraints, and computes Excessive Agency Risk scores.
- `RAGAuditor`: Tests document vector metadata for missing tenant IDs, evaluates document-level ACLs, and flags known instruction hijacking signatures inside retrieved chunks.

### 2.3 Data & Persistence Layer (`backend/app/models/` & `backend/app/db/`)
- SQLAlchemy 2.0 Declarative Models:
  - `Tenant`: Multi-tenant organization boundaries.
  - `User`: Roles (`admin`, `auditor`, `researcher`, `developer`).
  - `Assessment`: Security assessment engagements.
  - `AttackScenario`: Scenarios and metadata.
  - `SimulationRun`: Execution records with status, execution time, result.
  - `ExecutionTrace`: Root trace records.
  - `TraceSpan`: Individual stage spans (11 stages).
  - `Finding`: Confirmed security vulnerabilities, severities, CWE, OWASP, code locations.
  - `PatchValidation`: Before/after verification records and invariant assertions.
  - `AuthPolicy`: ABAC/RBAC policy definitions.
  - `AuthDecisionLog`: Complete audit trail of authorization calls.

### 2.4 Frontend Layer (`frontend/src/`)
- Modern Vite + React 18 + TypeScript + Tailwind CSS application.
- Theme: Professional Dark Cyber/SecOps (Dark Slate/Zinc background, Cyan/Blue accents, Rose/Amber status badges).
- Modular design:
  - `components/`: Navbar, Sidebar, SeverityBadge, MetricCard, TraceGraph, TimelineView, DiffViewer, AuthVisualizer, RiskMeter, CodeBlock.
  - `pages/`: 12 designated security operations pages.
  - `services/`: Typed Axios/Fetch API client.
  - `types/`: Complete TypeScript interfaces matching backend Pydantic schemas.

