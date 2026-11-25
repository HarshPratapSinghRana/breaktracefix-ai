import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { RAGAuditReport } from '../types';
import { Layers, Play, AlertTriangle, ShieldCheck, ShieldAlert, FileText } from 'lucide-react';

export const RAGSecurityAuditor: React.FC = () => {
  const [chunks, setChunks] = useState<any[]>([]);
  const [collectionName, setCollectionName] = useState('Enterprise Knowledge Base');
  const [tenantId, setTenantId] = useState('tenant-default-001');
  const [report, setReport] = useState<RAGAuditReport | null>(null);
  const [auditing, setAuditing] = useState(false);

  useEffect(() => {
    loadSample();
  }, []);

  const loadSample = async () => {
    try {
      const data = await api.getSampleRAGChunks();
      setChunks(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAudit = async () => {
    setAuditing(true);
    try {
      const res = await api.auditRAG(chunks, collectionName);
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAuditing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            RAG Security Auditor
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit knowledge chunks for indirect prompt injection, cross-tenant isolation, and poisoned directives
          </p>
        </div>
        <button
          onClick={handleAudit}
          disabled={auditing}
          className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-purple-950 transition cursor-pointer disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {auditing ? 'Auditing Vector Chunks...' : 'Audit Knowledge Base'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Knowledge Chunks Input / Review */}
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-[#090d19] p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Retrieved Chunks ({chunks.length})</h3>
            <span className="text-[10px] text-slate-500 font-mono">Tenant: {tenantId}</span>
          </div>

          <div className="space-y-3 max-h-[580px] overflow-y-auto pr-1">
            {chunks.map((chk, i) => (
              <div key={i} className="p-3 rounded-lg border border-slate-800 bg-slate-950 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-xs">{chk.title}</span>
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">{chk.classification}</span>
                </div>
                <p className="text-slate-300 font-mono text-[11px] bg-slate-900 p-2 rounded border border-slate-800 break-words">
                  {chk.text}
                </p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>ID: {chk.id}</span>
                  <span>Tenant: {chk.tenant_id}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Audit Results */}
        <div className="lg:col-span-7 space-y-4">
          {report ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl border border-slate-800 bg-[#090d19] flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">COLLECTION: {report.collection_name}</span>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-2xl font-black text-white">{report.overall_rag_risk_score}/100</span>
                    <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                      report.overall_rag_risk_score >= 50 ? 'bg-rose-950 text-rose-300 border border-rose-700' : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    }`}>
                      {report.overall_rag_risk_score >= 50 ? 'HIGH POISON RISK' : 'SECURE'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{report.security_summary}</p>
                </div>
              </div>

              {/* Chunk Findings */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                {report.audit_findings.map((af) => (
                  <div
                    key={af.chunk_id}
                    className={`p-4 rounded-xl border ${
                      af.is_poisoned || !af.tenant_isolated
                        ? 'border-rose-900/60 bg-rose-950/20'
                        : 'border-slate-800 bg-[#090d19]'
                    } space-y-2 text-xs`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-xs">{af.title}</span>
                      <div className="flex items-center gap-1.5">
                        {!af.tenant_isolated && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-950 text-orange-300 border border-orange-700">
                            CROSS-TENANT
                          </span>
                        )}
                        {af.is_poisoned ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-300 border border-rose-700">
                            POISONED
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                            VERIFIED CLEAN
                          </span>
                        )}
                      </div>
                    </div>

                    {af.poison_indicators.map((pi, pIdx) => (
                      <div key={pIdx} className="p-2 rounded bg-rose-950/40 border border-rose-800 text-[11px] text-rose-200 space-y-1">
                        <div className="flex items-center gap-1.5 font-bold">
                          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                          {pi.pattern_name} ({pi.severity})
                        </div>
                        <div className="font-mono text-[10px] text-rose-300">Snippet: "{pi.matched_snippet}"</div>
                        <div className="text-[10px] text-slate-300">Action: {pi.remediation}</div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
              Audit the knowledge base to inspect document ACLs and detect indirect prompt poisoning.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

