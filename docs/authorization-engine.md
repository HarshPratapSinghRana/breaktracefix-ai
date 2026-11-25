# BreakTraceFix AI - Context-Aware Authorization Engine

## Overview
The Authorization Intelligence Engine in BreakTraceFix AI enforces multi-tenant, attribute-based (ABAC) and role-based (RBAC) access controls across all agent actions, document retrievals, and tool executions.

## The 8 Evaluation Axes
Every request evaluates:
1. **Actor**: Who is initiating the request (identity & role).
2. **Tenant**: Organizational boundary. Cross-tenant access is denied by default.
3. **Resource**: Target document, model, or tool interface.
4. **Action**: Requested operation (`read`, `write`, `execute`, `delete`).
5. **Data Classification**: `Public` (0), `Internal` (1), `Confidential` (2), `Restricted` (3).
6. **Purpose**: Business justification (e.g., `customer_support`, `maintenance`).
7. **Recipient**: Intended consumer of data.
8. **Approval**: Whether human-in-the-loop sign-off is required and granted.

## Policy Engine Structure
- `ALLOW` and `DENY` policies with pattern matching.
- Explicit `DENY` rules always take precedence over `ALLOW` rules.
- Fallback: Deny-by-default when no rule explicitly permits the operation.
- Every decision produces an audit log record and a graph node structure for visualization.

