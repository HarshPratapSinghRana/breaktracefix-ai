# BreakTraceFix AI - Testing & Quality Assurance

## Running Backend Test Suite
```bash
python -m pytest breaktracefix-ai/tests -v
```

All 31 automated test cases across 8 test suites:
- `test_foundation.py`: Database, hashing, JWT, redaction, telemetry.
- `test_attack_engine.py`: 14 attack scenarios, registry, runner.
- `test_authorization.py`: 8-axis matrix, policies, audit logging.
- `test_tracing.py`: 11 stages, timeline, OpenTelemetry export.
- `test_reproduction.py`: Dual-run validation, regression generator.
- `test_source_analyzer.py`: Semgrep SAST rules, SARIF 2.1.0 output.
- `test_mcp_rag_reporting.py`: MCP inspection, RAG auditing, reports.
- `test_e2e_workflow.py`: Complete lifecycle integration test.

## Running Frontend Build
```bash
cd breaktracefix-ai/frontend
npm run build
```
Type checks and bundles production assets via Vite.

