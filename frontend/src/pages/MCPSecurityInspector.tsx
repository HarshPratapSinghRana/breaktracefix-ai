import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MCPInspectionReport } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Cpu, Play, ShieldAlert, CheckCircle2, AlertTriangle, Code } from 'lucide-react';

export const MCPSecurityInspector: React.FC = () => {
  const [manifestText, setManifestText] = useState('');
  const [report, setReport] = useState<MCPInspectionReport | null>(null);
  const [inspecting, setInspecting] = useState(false);

  useEffect(() => {
    loadSample();
  }, []);

  const loadSample = async () => {
    try {
      const sample = await api.getSampleMCP();
      setManifestText(JSON.stringify(sample, null, 2));
    } catch (err) {
      console.error(err);
    }
  };

  const handleInspect = async () => {
    setInspecting(true);
    try {
      const parsed = JSON.parse(manifestText);
      const res = await api.inspectMCP(parsed, parsed.server || 'Custom-MCP-Server');
      setReport(res);
    } catch (err: any) {
      alert(`Invalid JSON manifest: ${err.message}`);
    } finally {
      setInspecting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            Model Context Protocol (MCP) Security Inspector
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit MCP server manifests for excessive agency, parameter schema bounds, and destructive tool paths
          </p>
        </div>
        <button
          onClick={handleInspect}
          disabled={inspecting}
          className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-950 transition cursor-pointer disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {inspecting ? 'Auditing Manifest...' : 'Audit MCP Manifest'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Manifest JSON Input */}
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-[#090d19] p-4 flex flex-col space-y-2">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="text-xs font-mono text-slate-300 font-bold">MCP Tool Manifest (JSON)</span>
            <button onClick={loadSample} className="text-[10px] text-cyan-400 hover:underline cursor-pointer">
              Reset to Sample
            </button>
          </div>
          <textarea
            value={manifestText}
            onChange={(e) => setManifestText(e.target.value)}
            rows={20}
            className="w-full flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed resize-none"
          />
        </div>

        {/* Audit Results */}
        <div className="lg:col-span-7 space-y-4">
          {report ? (
            <div className="space-y-4">
              {/* Overall Risk Header Card */}
              <div className="p-4 rounded-xl border border-slate-800 bg-[#090d19] flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">SERVER: {report.server_name}</span>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-2xl font-black text-white">{report.overall_risk_score}/100</span>
                    <SeverityBadge severity={report.overall_risk_level} />
                  </div>
                  <span className="text-xs text-slate-400 mt-1 block">
                    {report.total_tools} Tools Audited &bull; {report.high_risk_tools} High-Risk Tools Flagged
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-cyan-300 font-mono">Excessive Agency Evaluator</span>
                </div>
              </div>

              {/* Tools Analysis List */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                {report.tools.map((t, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-800 bg-[#090d19] space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-xs font-mono">{t.tool_name}</span>
                        <span className={`px-2 py-0.2 rounded text-[10px] font-mono ${
                          t.requires_approval === 'YES' ? 'bg-amber-950 text-amber-300 border border-amber-700' : 'bg-slate-800 text-slate-400'
                        }`}>
                          Approval: {t.requires_approval}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-slate-400 font-bold">{t.risk_score} pts</span>
                        <SeverityBadge severity={t.risk_level} />
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-400">{t.description}</p>

                    {/* Risk Factors */}
                    {t.risk_factors.length > 0 && (
                      <div className="space-y-1">
                        {t.risk_factors.map((rf, fIdx) => (
                          <div key={fIdx} className="text-[11px] text-rose-300 bg-rose-950/30 p-1.5 rounded border border-rose-900/40 flex items-center gap-1.5">
                            <ShieldAlert className="w-3 h-3 text-rose-400 flex-shrink-0" />
                            {rf}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Argument Warnings */}
                    {t.argument_warnings.length > 0 && (
                      <div className="space-y-1">
                        {t.argument_warnings.map((aw, wIdx) => (
                          <div key={wIdx} className="text-[11px] text-amber-300 bg-amber-950/30 p-1.5 rounded border border-amber-900/40 flex items-center gap-1.5">
                            <AlertTriangle className="w-3 h-3 text-amber-400 flex-shrink-0" />
                            {aw}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
              Audit the MCP manifest to calculate permission risk scores and excessive agency flags.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

