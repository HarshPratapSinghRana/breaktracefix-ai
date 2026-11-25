# BreakTraceFix AI - Attack Catalog Specification

## Overview
BreakTraceFix AI includes 14 built-in security simulation scenarios registered with the `AttackRegistry`.

## Supported Scenarios
- `BTF-ATK-001`: Direct Prompt Injection (Instruction Override) - CWE-20, LLM01
- `BTF-ATK-002`: Indirect Prompt Injection via RAG Document - CWE-20, LLM01
- `BTF-ATK-003`: System Prompt Extraction via Linguistic Inversion - CWE-200, LLM07
- `BTF-ATK-004`: Sensitive Information Disclosure (PII / Secrets) - CWE-359, LLM02
- `BTF-ATK-005`: RAG Knowledge Base Document Poisoning - CWE-345, LLM04
- `BTF-ATK-006`: Excessive Agency (Unapproved Action) - CWE-250, LLM06
- `BTF-ATK-007`: Unauthorized Tool Execution via Privilege Bypass - CWE-862, LLM06
- `BTF-ATK-008`: Insecure Output Handling (Stored XSS) - CWE-79, LLM05
- `BTF-ATK-009`: Cross-Tenant Information Disclosure - CWE-284, LLM02
- `BTF-ATK-010`: Server-Side Request Forgery via Web Tool - CWE-918, LLM06
- `BTF-ATK-011`: Path Traversal via Tool Arguments - CWE-22, LLM06
- `BTF-ATK-012`: Model Context Protocol Tool Abuse - CWE-285, LLM06
- `BTF-ATK-013`: Improper Authorization on Document Retrieval - CWE-862, LLM06
- `BTF-ATK-014`: Sensitive Information Exposure in Logs - CWE-532, LLM02

Each scenario implements `execute_vulnerable` and `execute_secure` methods along with formal invariant verification.

