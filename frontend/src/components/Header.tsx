import React from 'react';
import { ShieldCheck, Search, Bell, Radio } from 'lucide-react';
import { Assessment } from '../types';

interface Props {
  assessments: Assessment[];
  selectedAssessmentId: string;
  setSelectedAssessmentId: (id: string) => void;
}

export const Header: React.FC<Props> = ({
  assessments,
  selectedAssessmentId,
  setSelectedAssessmentId
}) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#090d19]/80 backdrop-blur px-6 flex items-center justify-between flex-shrink-0 z-10">
      <div className="flex items-center gap-4">
        {/* Active Target Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target:</span>
          <select
            value={selectedAssessmentId}
            onChange={(e) => setSelectedAssessmentId(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 text-xs font-medium text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            {assessments.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} ({a.target_type}) - Risk: {a.risk_score}/100
              </option>
            ))}
          </select>
        </div>

        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-700/50 text-[11px] text-emerald-300 font-mono">
          <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
          Runtime Defense Active
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search findings, CWE, traces..."
            className="bg-slate-900 border border-slate-700/80 text-xs text-slate-200 pl-8 pr-3 py-1.5 rounded-lg focus:outline-none focus:border-cyan-500 w-64 placeholder-slate-500"
          />
        </div>

        {/* Tenant Pill */}
        <div className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono text-cyan-300 font-semibold">default-tenant</span>
        </div>
      </div>
    </header>
  );
};

