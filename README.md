# BreakTraceFix AI

> **Break It. Trace It. Fix It.**  
> Author: **Harsh Pratap Singh Rana**  
> Platform: GenAI Security Research, Vulnerability Assessment & Runtime Defense Platform

---

## Overview

**BreakTraceFix AI** is an independent security research and runtime defense platform designed to discover, trace, reproduce, and remediate security vulnerabilities across Generative AI applications, autonomous agents, RAG pipelines, and MCP servers.

The platform provides a complete triad:
1. **Break It**: Simulate 14 attack scenarios spanning OWASP Top 10 for LLMs (2025) and CWE standards in controlled, sandboxed test environments.
2. **Trace It**: Deeply observe the 11-stage GenAI execution lifecycle from input ingestion to final response, with automated sensitive data scrubbing and OpenTelemetry compliance.
3. **Fix It**: Verify security controls via side-by-side comparative execution, validate patches against formal invariants, and auto-generate standalone pytest regression suites.

---

## Architecture & Technology Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite (development/serverless) & PostgreSQL (production).
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, Dark cyber-defense UI theme.
- **Security & SAST**: Semgrep GenAI rule engine, OASIS SARIF v2.1.0, OpenTelemetry tracing.
- **Deployment**: Vercel Serverless Function (`api/index.py` + `vercel.json`) & Multi-stage Docker Compose.

---

## 14 Core Attack Simulation Scenarios

| Scenario ID | Name | OWASP Category | CWE Mapping | Severity |
|---|---|---|---|---|
| `BTF-ATK-001` | Direct Prompt Injection | LLM01: Prompt Injection | CWE-20 | High |
| `BTF-ATK-002` | Indirect Prompt Injection | LLM01: Prompt Injection | CWE-20 | Critical |
| `BTF-ATK-003` | System Prompt Extraction | LLM07: System Prompt Leakage | CWE-200 | Medium |
| `BTF-ATK-004` | Sensitive Information Disclosure | LLM02: Sensitive Info Disclosure | CWE-359 | Critical |
| `BTF-ATK-005` | RAG Document Poisoning | LLM04: Data & Model Poisoning | CWE-345 | High |
| `BTF-ATK-006` | Excessive Agency | LLM06: Excessive Agency | CWE-250 | High |
| `BTF-ATK-007` | Unauthorized Tool Execution | LLM06: Excessive Agency | CWE-862 | Critical |
| `BTF-ATK-008` | Insecure Output Handling | LLM05: Insecure Output Handling | CWE-79 | High |
| `BTF-ATK-009` | Cross-Tenant Information Disclosure | LLM02: Sensitive Info Disclosure | CWE-284 | Critical |
| `BTF-ATK-010` | SSRF via Web Tool | LLM06: Excessive Agency | CWE-918 | Critical |
| `BTF-ATK-011` | Path Traversal via Tool Arguments | LLM06: Excessive Agency | CWE-22 | High |
| `BTF-ATK-012` | MCP Tool Abuse | LLM06: Excessive Agency | CWE-285 | High |
| `BTF-ATK-013` | Improper Authorization Retrieval | LLM06: Excessive Agency | CWE-862 | High |
| `BTF-ATK-014` | Log Information Exposure | LLM02: Sensitive Info Disclosure | CWE-532 | Medium |

---

## 12 Frontend Operational Views

1. **Overview Dashboard**: Top-level posture metrics, target risk score, confirmed vulnerabilities summary.
2. **Security Assessments**: Target engagement manager (Agents, RAG, MCP servers).
3. **Attack Simulator**: 14-vector execution engine with dual-mode simulation (vulnerable vs protected).
4. **Vulnerability Explorer**: Filterable confirmed findings with root-cause analysis and evidence.
5. **Execution Trace Explorer**: 11-stage pipeline timeline with OpenTelemetry export.
6. **Authorization Intelligence**: 8-axis context evaluation tester with policy rule list and graph flow.
7. **Source Code Analyzer**: Semgrep SAST scanner with code editor and SARIF 2.1.0 output.
8. **MCP Security Inspector**: Model Context Protocol manifest parser with Excessive Agency scoring.
9. **RAG Security Auditor**: Knowledge chunk auditor for indirect prompt poisoning.
10. **Patch Workbench**: Side-by-side patch validation with auto-generated pytest regression tests.
11. **Security Reports**: Multi-format technical reporting in JSON and HTML.
12. **Settings & Integrations**: Clean-room project metadata, deployment config, and telemetry settings.

---

## Quick Start

### Backend
```bash
cd breaktracefix-ai
$env:PYTHONPATH = "."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI available at: `http://127.0.0.1:8000/api/docs`

### Frontend
```bash
cd breaktracefix-ai/frontend
npm run dev
```
Dashboard available at: `http://localhost:5173`

### Run Automated Tests
```bash
python -m pytest breaktracefix-ai/tests -v
```

---

## License

Developed independently by **Harsh Pratap Singh Rana**. Licensed under the BreakTraceFix AI License. See `LICENSE` for details.

