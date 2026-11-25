# BreakTraceFix AI - Patch Validation & Regression Generation

## Verification Workflow
For confirmed security vulnerabilities:
1. **Run 1 (Vulnerable Mode)**: Proves exploitability and records baseline evidence.
2. **Apply Mitigation**: Applies code diff, guardrail, or policy rule.
3. **Run 2 (Protected Mode)**: Executes the identical attack payload against the patched environment.
4. **Invariant Assertion**: Evaluates formal defense rules. Errors or crashes are rejected as fixes.
5. **Confidence Scoring**: Assigns verification score based on invariant satisfaction.
6. **Regression Code**: Auto-generates standalone `pytest` test templates.

