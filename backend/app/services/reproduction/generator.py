from typing import Dict, Any

class RegressionGenerator:
    """Generates standalone, executable pytest test templates based on confirmed security findings."""

    @staticmethod
    def generate_pytest_template(
        finding_id: str,
        title: str,
        cwe_id: str,
        owasp_category: str,
        scenario_id: str,
        input_payload: str,
        expected_secure_behavior: str,
        invariant_name: str
    ) -> str:
        escaped_input = input_payload.replace('"', '\\"').replace('\n', '\\n')
        escaped_expected = expected_secure_behavior.replace('"', '\\"')

        template = f'''# ==============================================================================
# BREAKTRACEFIX AI - AUTO-GENERATED SECURITY REGRESSION TEST
# Finding ID: {finding_id}
# Scenario ID: {scenario_id}
# Title: {title}
# CWE: {cwe_id} | OWASP: {owasp_category}
# ------------------------------------------------------------------------------
# NOTICE: Developer review required before incorporating into CI/CD regression suite.
# ==============================================================================

import pytest
from backend.app.services.attack_engine.registry import AttackRegistry

def test_regression_{finding_id.lower().replace("-", "_")}():
    """Verify security invariant '{invariant_name}' holds and prevents attack recurrence."""
    scenario = AttackRegistry.get("{scenario_id}")
    assert scenario is not None, "Attack scenario must exist in registry."

    attack_input = "{escaped_input}"

    # 1. Execute scenario with active security controls (Protected Mode)
    result = scenario.run(mode="protected", input_payload=attack_input)

    # 2. Assert protected execution completed without exploit success
    assert result.status == "success_defended", (
        f"Security regression detected! Status was {{result.status}}, expected 'success_defended'."
    )

    # 3. Verify all defined security defense invariants passed
    assert len(result.invariants) > 0, "At least one security invariant must be evaluated."
    for inv in result.invariants:
        assert inv.passed is True, (
            f"Security invariant '{{inv.invariant_name}}' failed: {{inv.actual_value}}"
        )

    # 4. Verify behavioral compliance
    assert "error" not in result.status.lower(), "Application must not crash or return unhandled errors."
'''
        return template

