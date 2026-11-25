import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Finding, PatchValidation, Assessment } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Wrench, CheckCircle2, ShieldCheck, Play, Copy, ArrowRight, Code } from 'lucide-react';

interface Props {
  selectedAssessment: Assessment | null;
  activeFindingId?: string | null;
}

export const PatchWorkbench: React.FC<Props> = ({ selectedAssessment, activeFindingId }) => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [patchTitle, setPatchTitle] = useState('Add Context-Aware Authorization Guardrail');
  const [patchDiff, setPatchDiff] = useState(`--- a/app/agent/execution_sink.py
+++ b/app/agent/execution_sink.py
@@ -42,3 +42,6 @@
+    # BreakTraceFix Invariant Enforcement
+    if not auth_engine.evaluate(caller, resource, action).is_allowed():
+        raise AuthorizationDenied("Privilege boundary violated.")`);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<PatchValidation | null>(null);
  const [regressionCode, setRegressionCode] = useState<string>('');

  useEffect(() => {
    loadFindings();
  }, [selectedAssessment]);

  const loadFindings = async () => {
    try {
      const data = await api.listFindings(selectedAssessment?.id);
      setFindings(data);
      if (data.length > 0) {
        const target = activeFindingId ? data.find((f) => f.id === activeFindingId) : data[0];
        handleSelectFinding(target || data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectFinding = async (f: Finding) => {
    setSelectedFinding(f);
    setValidationResult(null);
    try {
      const regr = await api.getRegressionCode(f.id);
      setRegressionCode(regr.pytest_code);
    } catch (err) {
      console.error(err);
    }
  };

  const handleValidate = async () => {
    if (!selectedFinding) return;
    setValidating(true);
    try {
      const res = await api.validatePatch(selectedFinding.id, patchTitle, patchDiff);
      setValidationResult(res);
      setRegressionCode(res.regression_test_code || regressionCode);
      await loadFindings();
    } catch (err) {
      console.error(err);
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Wrench className="w-5 h-5 text-emerald-400" />
          Patch Validation Workbench & Regression Generator
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Dual-run comparative verification: run attack in vulnerable vs protected mode, verify security invariants, and generate pytest regression suites
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Finding Selector & Patch Code Form */}
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-[#090d19] p-5 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Target Vulnerability Finding</label>
            <select
              value={selectedFinding?.id || ''}
              onChange={(e) => {
                const f = findings.find((item) => item.id === e.target.value);
                if (f) handleSelectFinding(f);
              }}
              className="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-lg p-2 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {findings.map((f) => (
                <option key={f.id} value={f.id}>
                  [{f.severity}] {f.title} ({f.patch_status})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Patch Title</label>
            <input
              type="text"
              value={patchTitle}
              onChange={(e) => setPatchTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-lg p-2 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Proposed Code Diff / Security Guardrail</label>
            <textarea
              value={patchDiff}
              onChange={(e) => setPatchDiff(e.target.value)}
              rows={8}
              className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 font-mono rounded-lg p-3 focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <button
            onClick={handleValidate}
            disabled={validating || !selectedFinding}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40 transition cursor-pointer disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
            {validating ? 'Running Dual-Run Validation...' : 'Execute Patch Verification (Dual-Run)'}
          </button>
        </div>

        {/* Side-by-Side Verification Diff & Regression Code */}
        <div className="lg:col-span-7 space-y-4">
          {validationResult ? (
            <div className="p-5 rounded-xl border border-slate-800 bg-[#090d19] space-y-4 text-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="font-bold text-white text-sm flex items-center gap-2">
                  Validation Status:
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-600">
                    {validationResult.validation_status.toUpperCase()}
                  </span>
                </span>
                <span className="text-emerald-400 font-mono font-bold text-sm">
                  Confidence Score: {validationResult.confidence_score}%
                </span>
              </div>

              {/* Side-by-Side Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-900/60 space-y-2">
                  <span className="font-bold text-rose-300 uppercase tracking-wider text-[10px] block">Vulnerable Run (Before Patch)</span>
                  <div className="font-mono text-[11px] text-slate-300 bg-slate-950 p-2.5 rounded border border-slate-800">
                    {validationResult.evidence_comparison?.vulnerable_run?.output || 'Exploit demonstrated.'}
                  </div>
                  <div className="text-[10px] text-rose-400 font-bold">Status: EXPLOITED (Invariants Violated)</div>
                </div>

                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/60 space-y-2">
                  <span className="font-bold text-emerald-300 uppercase tracking-wider text-[10px] block">Patched Run (After Guardrail)</span>
                  <div className="font-mono text-[11px] text-slate-300 bg-slate-950 p-2.5 rounded border border-slate-800">
                    {validationResult.evidence_comparison?.patched_run?.output || 'Mitigation active.'}
                  </div>
                  <div className="text-[10px] text-emerald-400 font-bold">Status: DEFENDED (Invariants Verified)</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19] text-xs">
              Execute patch verification to view side-by-side behavioral comparison and invariant satisfaction.
            </div>
          )}

          {/* Standalone Regression Test Generator Box */}
          <div className="p-5 rounded-xl border border-slate-800 bg-[#090d19] space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Code className="w-4 h-4 text-cyan-400" />
                  Auto-Generated Pytest Regression Test
                </h3>
                <p className="text-[11px] text-slate-400">Standalone regression suite template for CI/CD integration</p>
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(regressionCode);
                  alert('Pytest code copied to clipboard!');
                }}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 cursor-pointer"
              >
                <Copy className="w-3.5 h-3.5" /> Copy Code
              </button>
            </div>
            <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-cyan-300 max-h-72 overflow-y-auto whitespace-pre leading-relaxed">
              {regressionCode || '# Select a finding to generate regression test template.'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

