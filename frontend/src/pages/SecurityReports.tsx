import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SecurityReport, Assessment } from '../types';
import { FileText, Download, ExternalLink, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface Props {
  selectedAssessment: Assessment | null;
}

export const SecurityReports: React.FC<Props> = ({ selectedAssessment }) => {
  const [reportData, setReportData] = useState<SecurityReport | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedAssessment) {
      loadReport(selectedAssessment.id);
    }
  }, [selectedAssessment]);

  const loadReport = async (assessmentId: string) => {
    setLoading(true);
    try {
      const data = await api.getJsonReport(assessmentId);
      setReportData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const htmlUrl = selectedAssessment ? api.getHtmlReportUrl(selectedAssessment.id) : '#';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Security Assessment Reports
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Technical and executive security assurance reports in JSON, HTML, and SARIF formats
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={htmlUrl}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <ExternalLink className="w-3.5 h-3.5" /> View HTML Report
          </a>
          <button
            onClick={() => {
              if (reportData) {
                const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `breaktracefix-report-${selectedAssessment?.id || 'export'}.json`;
                a.click();
              }
            }}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-950 transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" /> Download JSON Report
          </button>
        </div>
      </div>

      {reportData ? (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-[#090d19] space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">REPORT ID: {reportData.report_id}</span>
                <h3 className="text-lg font-black text-white mt-0.5">{reportData.assessment_name}</h3>
                <p className="text-xs text-slate-400">Author: {reportData.author} &bull; Generated: {new Date(reportData.generated_at).toLocaleString()}</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-2xl font-black text-white block">{reportData.overall_risk_score}/100</span>
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Target Risk Score</span>
                </div>
              </div>
            </div>

            {/* Severity Distribution */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-900/60">
                <span className="text-xl font-black text-rose-400 block">{reportData.severity_summary?.Critical || 0}</span>
                <span className="text-[10px] text-slate-400 uppercase font-bold">Critical</span>
              </div>
              <div className="p-3 rounded-lg bg-orange-950/20 border border-orange-900/60">
                <span className="text-xl font-black text-orange-400 block">{reportData.severity_summary?.High || 0}</span>
                <span className="text-[10px] text-slate-400 uppercase font-bold">High</span>
              </div>
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-900/60">
                <span className="text-xl font-black text-amber-400 block">{reportData.severity_summary?.Medium || 0}</span>
                <span className="text-[10px] text-slate-400 uppercase font-bold">Medium</span>
              </div>
              <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/60">
                <span className="text-xl font-black text-emerald-400 block">{reportData.patches_verified || 0}</span>
                <span className="text-[10px] text-slate-400 uppercase font-bold">Verified Fixed</span>
              </div>
            </div>
          </div>

          {/* Findings Table */}
          <div className="p-5 rounded-xl border border-slate-800 bg-[#090d19] space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Detailed Findings Breakdown</h3>
            <div className="space-y-3">
              {reportData.findings.map((f, i) => (
                <div key={i} className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-xs">{f.title}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      f.severity === 'Critical' ? 'bg-rose-950 text-rose-300' : 'bg-orange-950 text-orange-300'
                    }`}>
                      {f.severity}
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px]">{f.root_cause}</p>
                  <div className="p-2 rounded bg-slate-900 font-mono text-[10px] text-cyan-300 border border-slate-800">
                    Remediation: {f.remediation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
          Loading security assessment report...
        </div>
      )}
    </div>
  );
};

