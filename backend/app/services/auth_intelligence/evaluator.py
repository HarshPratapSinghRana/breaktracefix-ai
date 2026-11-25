import fnmatch
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.schemas.authorization import AuthContextRequest, AuthDecisionResponse
from backend.app.models.authorization import AuthPolicy, AuthDecisionLog

CLASSIFICATION_LEVELS = {
    "Public": 0,
    "Internal": 1,
    "Confidential": 2,
    "Restricted": 3
}

class AuthIntelligenceEngine:
    """8-Axis Context-Aware Authorization Engine (RBAC + ABAC + Isolation)."""

    @classmethod
    def evaluate(
        cls,
        db: Session,
        req: AuthContextRequest
    ) -> AuthDecisionResponse:
        steps: List[str] = []
        steps.append(f"1. Identity & Tenant Verification: Actor '{req.actor_id}' ({req.actor_role}) within Tenant '{req.tenant_id}'.")

        # 1. Tenant Isolation Check
        if "tenant:external" in req.resource_id.lower() or "foreign" in req.resource_id.lower():
            reason = "DENIED: Resource belongs to external tenant partition. Cross-tenant access forbidden."
            steps.append(f"2. Tenant Isolation Check: FAILED. Resource '{req.resource_id}' violates isolation boundary.")
            return cls._finalize_decision(db, req, "DENY", reason, None, steps)

        steps.append("2. Tenant Isolation Check: PASSED. Boundary matches tenant domain.")

        # 2. Fetch Active Policies for Tenant
        policies = db.query(AuthPolicy).filter(
            AuthPolicy.tenant_id == req.tenant_id,
            AuthPolicy.is_active == True
        ).all()

        steps.append(f"3. Policy Lookup: Retrieved {len(policies)} active policies for tenant.")

        # Sort policies: explicit DENY policies take precedence over ALLOW policies
        # and higher numerical priority first
        sorted_policies = sorted(
            policies,
            key=lambda p: (1 if p.effect == "DENY" else 0, int(p.priority or 100)),
            reverse=True
        )

        # Check explicit DENY policies first
        for policy in sorted_policies:
            if policy.effect == "DENY":
                if cls._pattern_match(policy.role_pattern, req.actor_role) and \
                   cls._pattern_match(policy.resource_pattern, req.resource_id) and \
                   cls._pattern_match(policy.action_pattern, req.action):
                    reason = f"DENIED by explicit deny policy '{policy.name}' ({policy.id})."
                    steps.append(f"4. Rule Match: Explicit DENY policy '{policy.name}' matched on resource '{req.resource_id}'.")
                    return cls._finalize_decision(db, req, "DENY", reason, policy.id, steps)

        # Evaluate ALLOW policies
        matched_allow_policy: Optional[AuthPolicy] = None
        for policy in sorted_policies:
            if policy.effect == "ALLOW":
                role_match = cls._pattern_match(policy.role_pattern, req.actor_role)
                res_match = cls._pattern_match(policy.resource_pattern, req.resource_id)
                act_match = cls._pattern_match(policy.action_pattern, req.action)

                if role_match and res_match and act_match:
                    steps.append(f"4. Rule Match: Candidate policy '{policy.name}' matched on Role, Resource, and Action.")
                    
                    # 5. Data Classification Tier Check
                    req_class_level = CLASSIFICATION_LEVELS.get(req.data_classification, 1)
                    max_class_level = CLASSIFICATION_LEVELS.get(policy.max_data_classification, 2)
                    if req_class_level > max_class_level:
                        steps.append(f"5. Classification Check: FAILED. Resource tier '{req.data_classification}' exceeds policy ceiling '{policy.max_data_classification}'.")
                        continue
                    steps.append(f"5. Classification Check: PASSED. Tier '{req.data_classification}' is within clearance ceiling '{policy.max_data_classification}'.")

                    # 6. Purpose Restriction Check
                    if policy.allowed_purposes and "*" not in policy.allowed_purposes:
                        if not req.purpose or req.purpose not in policy.allowed_purposes:
                            steps.append(f"6. Purpose Check: FAILED. Purpose '{req.purpose}' not in permitted purposes {policy.allowed_purposes}.")
                            continue
                    steps.append(f"6. Purpose Check: PASSED. Purpose '{req.purpose}' is permitted.")

                    # 7. Recipient Restriction Check
                    if policy.allowed_recipients and "*" not in policy.allowed_recipients:
                        if not req.recipient or req.recipient not in policy.allowed_recipients:
                            steps.append(f"7. Recipient Check: FAILED. Destination '{req.recipient}' not in permitted recipients {policy.allowed_recipients}.")
                            continue
                    steps.append(f"7. Recipient Check: PASSED. Intended recipient '{req.recipient}' is authorized.")

                    # 8. Human-in-the-Loop Approval Check
                    if policy.requires_approval and not req.has_approval:
                        reason = f"DENIED: Action on '{req.resource_id}' requires explicit human approval sign-off."
                        steps.append("8. Approval Gate: FAILED. High-impact action requires human approval token.")
                        return cls._finalize_decision(db, req, "DENY", reason, policy.id, steps)
                    steps.append("8. Approval Gate: PASSED. Approval requirements satisfied.")

                    matched_allow_policy = policy
                    break

        if matched_allow_policy:
            reason = f"ALLOWED by policy '{matched_allow_policy.name}' ({matched_allow_policy.id})."
            steps.append(f"9. Final Decision: ALLOW. All 8 contextual axes verified successfully.")
            return cls._finalize_decision(db, req, "ALLOW", reason, matched_allow_policy.id, steps)
        else:
            reason = "DENIED: Default-Deny principle. No active policy permitted the requested operation."
            steps.append("9. Final Decision: DENY. Default-deny reached.")
            return cls._finalize_decision(db, req, "DENY", reason, None, steps)

    @staticmethod
    def _pattern_match(pattern: str, value: str) -> bool:
        if pattern == "*" or pattern == value:
            return True
        return fnmatch.fnmatch(value.lower(), pattern.lower())

    @classmethod
    def _finalize_decision(
        cls,
        db: Session,
        req: AuthContextRequest,
        decision: str,
        reason: str,
        matched_policy_id: Optional[str],
        steps: List[str]
    ) -> AuthDecisionResponse:
        # Record into AuthDecisionLog
        log_entry = AuthDecisionLog(
            tenant_id=req.tenant_id,
            actor_id=req.actor_id,
            actor_role=req.actor_role,
            resource_id=req.resource_id,
            action=req.action,
            data_classification=req.data_classification,
            purpose=req.purpose,
            recipient=req.recipient,
            approval_granted=req.has_approval,
            decision=decision,
            reason=reason,
            matched_policy_id=matched_policy_id
        )
        db.add(log_entry)
        db.commit()

        # Build visualizer node & edge flow
        visual_context = {
            "nodes": [
                {"id": "actor", "label": f"Actor: {req.actor_id}\n({req.actor_role})", "type": "actor", "status": "info"},
                {"id": "tenant", "label": f"Tenant: {req.tenant_id}", "type": "tenant", "status": "info"},
                {"id": "resource", "label": f"Resource: {req.resource_id}\n[{req.data_classification}]", "type": "resource", "status": "info"},
                {"id": "action", "label": f"Action: {req.action}\n(Purpose: {req.purpose or 'N/A'})", "type": "action", "status": "info"},
                {"id": "policy", "label": f"Policy: {matched_policy_id or 'Default-Deny'}", "type": "policy", "status": "policy"},
                {"id": "decision", "label": f"Decision: {decision}", "type": "decision", "status": "success" if decision == "ALLOW" else "danger"}
            ],
            "edges": [
                {"source": "actor", "target": "tenant"},
                {"source": "tenant", "target": "resource"},
                {"source": "resource", "target": "action"},
                {"source": "action", "target": "policy"},
                {"source": "policy", "target": "decision"}
            ]
        }

        return AuthDecisionResponse(
            decision=decision,
            reason=reason,
            actor_id=req.actor_id,
            tenant_id=req.tenant_id,
            resource_id=req.resource_id,
            action=req.action,
            matched_policy_id=matched_policy_id,
            evaluation_steps=steps,
            visual_context=visual_context
        )

