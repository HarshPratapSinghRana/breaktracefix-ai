import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Assessment, Finding, SimulationRun } from '../types';
import { MetricCard } from '../components/MetricCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { Shield, Flame, Activity, Wrench, AlertTriangle, ArrowUpRight, Play, CheckCircle } from 'lucide-react';

interface Props {
  selectedAssessment: Assessment | null;
  onNavigate: (tab: string) => void;
}

export const OverviewDashboard: React.FC<Props> = ({ selectedAssessment, onNavigate }) => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [runs, setRuns] = useState<SimulationRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [batchRunning, setBatchRunning] = useState<boolean>(false);

  useEffect(() => {
    loadData();
  }, [selectedAssessment]);

  const loadData = async () => {
    setLoading(true);
    try {
      const fList = await api.listFindings(selectedAssessment?.id);
      const rList = await api.listRuns(selectedAssessment?.id);
      setFindings(fList);
      setRuns(rList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAllAttacks = async () => {
    if (!selectedAssessment) return;
    setBatchRunning(true);
    try {
      await api.batchSimulate(selectedAssessment.id, 'vulnerable');
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setBatchRunning(false);
    }
  };

  const criticalCount = findings.filter((f) => f.severity === 'Critical').length;
  const highCount = findings.filter((f) => f.severity === 'High').length;
  const fixedCount = findings.filter((f) => f.patch_status === 'verified_fixed').length;

  return (
    <div className="space-y-6">
      {/* Target Banner */}
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-[#0b1120] via-slate-900 to-[#0e172a] p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-cyan-950 text-cyan-400 border border-cyan-800">
                ACTIVE TARGET ENGAGEMENT
              </span>
              <span className="text-xs text-slate-400 font-mono">ID: {selectedAssessment?.id}</span>
            </div>
            <h2 className="text-2xl font-black text-white tracking-tight">{selectedAssessment?.name || 'Primary Agent'}</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              {selectedAssessment?.description || 'Automated multi-vector GenAI vulnerability evaluation and trace verification.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRunAllAttacks}
              disabled={batchRunning}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-rose-950/40 transition disabled:opacity-50 cursor-pointer"
            >
              <Flame className="w-4 h-4" />
              {batchRunning ? 'Simulating All 14 Attacks...' : 'Execute 14-Vector Assessment'}
            </button>
            <button
              onClick={() => onNavigate('reports')}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition cursor-pointer"
            >
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Overall Target Risk Score"
          value={`${selectedAssessment?.risk_score || 0}/100`}
          subtitle="Based on OWASP LLM severity weights"
          icon={<Shield className="w-5 h-5" />}
          color="from-rose-950/20 to-slate-900/40"
        />
        <MetricCard
          title="Critical / High Findings"
          value={`${criticalCount} / ${highCount}`}
          subtitle="Awaiting patch validation"
          icon={<AlertTriangle className="w-5 h-5 text-rose-400" />}
          color="from-orange-950/20 to-slate-900/40"
        />
        <MetricCard
          title="Simulations Executed"
          value={runs.length}
          subtitle="Reproduced in controlled harness"
          icon={<Activity className="w-5 h-5 text-cyan-400" />}
          color="from-cyan-950/20 to-slate-900/40"
        />
        <MetricCard
          title="Verified Fixed Patches"
          value={`${fixedCount}`}
          subtitle="Dual-run verified invariants"
          icon={<CheckCircle className="w-5 h-5 text-emerald-400" />}
          color="from-emerald-950/20 to-slate-900/40"
        />
      </div>

      {/* Two-Column Findings & Quick Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Confirmed Findings Table */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#090d19] p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Confirmed Vulnerabilities</h3>
              <p className="text-xs text-slate-400">Dynamically verified security findings for target</p>
            </div>
            <button
              onClick={() => onNavigate('vulnerabilities')}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
            >
              View All <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 text-[11px] uppercase font-mono">
                <tr>
                  <th className="pb-2.5">Severity</th>
                  <th className="pb-2.5">Vulnerability Title</th>
                  <th className="pb-2.5">CWE / OWASP</th>
                  <th className="pb-2.5">Patch Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {findings.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-slate-500">
                      No confirmed vulnerabilities found. Run an attack simulation above to begin auditing.
                    </td>
                  </tr>
                ) : (
                  findings.slice(0, 5).map((f) => (
                    <tr key={f.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3">
                        <SeverityBadge severity={f.severity} />
                      </td>
                      <td className="py-3 font-semibold text-slate-200">
                        {f.title}
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">{f.affected_component}</div>
                      </td>
                      <td className="py-3 text-slate-400 font-mono text-[11px]">
                        {f.cwe_id || 'CWE-20'}
                        <div className="text-[10px] text-slate-500">{f.owasp_category}</div>
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          f.patch_status === 'verified_fixed'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                            : 'bg-rose-950 text-rose-300 border border-rose-700'
                        }`}>
                          {f.patch_status.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Action Box: 14 Core Capabilities Quick Launch */}
        <div className="rounded-xl border border-slate-800 bg-[#090d19] p-5 shadow-sm space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Engine Navigation</h3>
            <p className="text-xs text-slate-400">Direct access to research & defense tools</p>
          </div>

          <div className="space-y-2">
            {[
              { id: 'simulator', title: 'Attack Simulator (14 Vectors)', desc: 'Run jailbreak, prompt injection & tool abuse', icon: <Flame className="w-4 h-4 text-orange-400" /> },
              { id: 'traces', title: '11-Stage Trace Explorer', desc: 'Inspect data transformations & OTel spans', icon: <Activity className="w-4 h-4 text-cyan-400" /> },
              { id: 'authorization', title: '8-Axis Auth Intelligence', desc: 'Test RBAC/ABAC and decision graphs', icon: <Shield className="w-4 h-4 text-indigo-400" /> },
              { id: 'patch-workbench', title: 'Patch Validation Workbench', desc: 'Dual-run comparative verification & test gen', icon: <Wrench className="w-4 h-4 text-emerald-400" /> },
            ].map((tool) => (
              <button
                key={tool.id}
                onClick={() => onNavigate(tool.id)}
                className="w-full p-3 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-slate-700 text-left transition flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-slate-950 border border-slate-800">{tool.icon}</div>
                  <div>
                    <p className="text-xs font-bold text-white">{tool.title}</p>
                    <p className="text-[11px] text-slate-400">{tool.desc}</p>
                  </div>
                </div>
                <ArrowUpRight className="w-4 h-4 text-slate-500" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

