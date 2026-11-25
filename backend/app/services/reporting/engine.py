import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.assessment import Assessment
from backend.app.models.finding import Finding
from backend.app.models.attack import SimulationRun
from backend.app.models.patch import PatchValidation

class SecurityReportGenerator:
    """Generates multi-format security assessment reports (JSON, HTML, SARIF 2.1.0, Technical & Executive)."""

    @classmethod
    def generate_json_report(cls, db: Session, assessment_id: str) -> Dict[str, Any]:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")

        findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
        runs = db.query(SimulationRun).filter(SimulationRun.assessment_id == assessment_id).all()
        patches = db.query(PatchValidation).all()

        findings_data = []
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        
        for f in findings:
            sev = f.severity.title() if f.severity else "Medium"
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            findings_data.append({
                "finding_id": f.id,
                "title": f.title,
                "severity": f.severity,
                "cwe_id": f.cwe_id,
                "owasp_category": f.owasp_category,
                "affected_component": f.affected_component,
                "source_location": f.source_location,
                "sink_location": f.sink_location,
                "attack_vector": f.attack_vector,
                "reproduction_steps": f.reproduction_steps,
                "evidence": f.evidence,
                "root_cause": f.root_cause,
                "impact": f.impact,
                "remediation": f.remediation,
                "patch_status": f.patch_status
            })

        return {
            "report_id": f"BTF-REP-{assessment.id[:8].upper()}",
            "assessment_id": assessment.id,
            "assessment_name": assessment.name,
            "target_type": assessment.target_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "author": "Harsh Pratap Singh Rana",
            "platform": "BreakTraceFix AI - Break It. Trace It. Fix It.",
            "overall_risk_score": assessment.risk_score,
            "overall_status": assessment.status,
            "severity_summary": severity_counts,
            "total_findings": len(findings),
            "simulations_executed": len(runs),
            "patches_verified": len([f for f in findings if f.patch_status == "verified_fixed"]),
            "findings": findings_data,
            "methodology": "OWASP Top 10 for LLM Applications (2025) & CWE Invariant Verification"
        }

    @classmethod
    def generate_html_report(cls, db: Session, assessment_id: str) -> str:
        data = cls.generate_json_report(db, assessment_id)
        
        findings_html = ""
        for f in data["findings"]:
            badge_color = "#ef4444" if f["severity"] == "Critical" else ("#f97316" if f["severity"] == "High" else "#eab308")
            findings_html += f"""
            <div style="background: #1e293b; border-left: 4px solid {badge_color}; padding: 16px; margin-bottom: 16px; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: #f8fafc; margin: 0;">{f['title']}</h3>
                    <span style="background: {badge_color}; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">{f['severity']}</span>
                </div>
                <p style="color: #94a3b8; font-size: 13px; margin: 6px 0;"><strong>ID:</strong> {f['finding_id']} | <strong>CWE:</strong> {f['cwe_id']} | <strong>OWASP:</strong> {f['owasp_category']}</p>
                <p style="color: #cbd5e1; margin: 8px 0;"><strong>Root Cause:</strong> {f['root_cause']}</p>
                <p style="color: #cbd5e1; margin: 8px 0;"><strong>Impact:</strong> {f['impact']}</p>
                <div style="background: #0f172a; padding: 10px; border-radius: 4px; color: #38bdf8; font-family: monospace; font-size: 12px; margin: 8px 0;">
                    Remediation: {f['remediation']}
                </div>
                <p style="color: #64748b; font-size: 12px; margin-top: 8px;">Patch Status: <strong style="color: {'#22c55e' if f['patch_status'] == 'verified_fixed' else '#f59e0b'};">{f['patch_status'].upper()}</strong></p>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BreakTraceFix AI - Security Assessment Report: {data['assessment_name']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 32px; line-height: 1.5; }}
        .header {{ border-bottom: 2px solid #334155; padding-bottom: 20px; margin-bottom: 24px; }}
        .tagline {{ color: #38bdf8; font-weight: bold; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-card {{ background: #1e293b; padding: 16px; border-radius: 8px; flex: 1; text-align: center; border: 1px solid #334155; }}
        .metric-grid {{ display: flex; gap: 16px; margin: 24px 0; }}
        .metric-val {{ font-size: 28px; font-weight: bold; color: #38bdf8; }}
        .metric-lbl {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="tagline">Break It. Trace It. Fix It.</div>
        <h1 style="color: #f8fafc; margin: 8px 0;">BreakTraceFix AI - Security Assessment Report</h1>
        <p style="color: #94a3b8; margin: 0;">Target: <strong>{data['assessment_name']}</strong> ({data['target_type']}) | Author: {data['author']} | Generated: {data['generated_at']}</p>
    </div>

    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-val">{data['overall_risk_score']}/100</div>
            <div class="metric-lbl">Target Risk Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-val" style="color: #ef4444;">{data['severity_summary'].get('Critical', 0)}</div>
            <div class="metric-lbl">Critical Issues</div>
        </div>
        <div class="metric-card">
            <div class="metric-val" style="color: #f97316;">{data['severity_summary'].get('High', 0)}</div>
            <div class="metric-lbl">High Issues</div>
        </div>
        <div class="metric-card">
            <div class="metric-val" style="color: #22c55e;">{data['patches_verified']}</div>
            <div class="metric-lbl">Verified Patches</div>
        </div>
    </div>

    <h2 style="color: #f8fafc; border-bottom: 1px solid #334155; padding-bottom: 8px;">Confirmed Security Findings ({data['total_findings']})</h2>
    {findings_html if findings_html else '<p style="color: #94a3b8;">No confirmed findings recorded for this assessment.</p>'}

    <footer style="margin-top: 40px; border-top: 1px solid #334155; padding-top: 16px; color: #64748b; font-size: 12px; text-align: center;">
        Generated by BreakTraceFix AI &bull; Author: Harsh Pratap Singh Rana &bull; Methodology: OWASP LLM Top 10 (2025)
    </footer>
</body>
</html>"""
        return html

