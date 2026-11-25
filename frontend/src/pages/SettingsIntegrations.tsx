import React from 'react';
import { Settings, Shield, Terminal, Key, Database, Globe } from 'lucide-react';

export const SettingsIntegrations: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          Settings & Environment Integrations
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Clean-room development configuration, model providers, telemetry, and tenant boundaries
        </p>
      </div>

      <div className="space-y-4 text-xs">
        {/* Project Attribution & License Card */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#090d19] space-y-3">
          <h3 className="font-bold text-white uppercase tracking-wider text-xs flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" /> Clean-Room Project Metadata
          </h3>
          <div className="grid grid-cols-2 gap-4 text-slate-300 font-mono text-[11px]">
            <div>
              <span className="text-slate-500 block">Project Name:</span>
              <span className="text-white font-bold">BreakTraceFix AI</span>
            </div>
            <div>
              <span className="text-slate-500 block">Author:</span>
              <span className="text-cyan-300 font-bold">Harsh Pratap Singh Rana</span>
            </div>
            <div>
              <span className="text-slate-500 block">Tagline:</span>
              <span className="text-white font-bold">Break It. Trace It. Fix It.</span>
            </div>
            <div>
              <span className="text-slate-500 block">License:</span>
              <span className="text-emerald-300 font-bold">MIT License (Independent Implementation)</span>
            </div>
          </div>
        </div>

        {/* Deployment & Runtime Configuration */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#090d19] space-y-4">
          <h3 className="font-bold text-white uppercase tracking-wider text-xs flex items-center gap-2">
            <Globe className="w-4 h-4 text-cyan-400" /> Deployment Architecture
          </h3>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-white font-bold block">Vercel Serverless Backend</span>
                <span className="text-slate-400 text-[11px]">Entrypoint /api/index.py with vercel.json routing</span>
              </div>
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                ACTIVE
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-white font-bold block">OpenTelemetry Tracing</span>
                <span className="text-slate-400 text-[11px]">OASIS/OTel ResourceSpans JSON export enabled</span>
              </div>
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                READY
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-white font-bold block">Semgrep Static Analysis Engine</span>
                <span className="text-slate-400 text-[11px]">Bundled GenAI rule definitions in YAML</span>
              </div>
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                INTEGRATED
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

