# BreakTraceFix AI - REST API Reference

## Base Endpoints
- Base path: `/api/v1`
- OpenAPI Documentation: `/api/docs`
- Health check: `/api/health`

## Key Resources
- `POST /api/v1/auth/login`: User authentication & JWT issuance.
- `GET, POST /api/v1/assessments`: Assessment engagement management.
- `GET, POST /api/v1/attacks`: Catalog queries and simulation triggers.
- `POST /api/v1/authorization/evaluate`: 8-axis context evaluation.
- `GET, POST /api/v1/traces`: 11-stage trace query and pipeline execution.
- `POST /api/v1/reproduction/validate-patch`: Dual-run patch verification.
- `POST /api/v1/source-analyzer/scan`: Semgrep-powered SAST scanning.
- `POST /api/v1/mcp-inspector/inspect`: MCP manifest auditing.
- `POST /api/v1/rag-auditor/audit`: RAG chunk security scanning.
- `GET /api/v1/reports/json/{id}`, `/html/{id}`: Security report generation.

