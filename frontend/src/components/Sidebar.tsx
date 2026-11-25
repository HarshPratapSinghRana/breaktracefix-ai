import React from 'react';
import {
  LayoutDashboard,
  Target,
  Flame,
  Bug,
  Activity,
  KeyRound,
  FileCode2,
  Cpu,
  Layers,
  Wrench,
  FileText,
  Settings,
  ShieldAlert
} from 'lucide-react';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<Props> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'assessments', label: 'Security Assessments', icon: <Target className="w-4 h-4" /> },
    { id: 'simulator', label: 'Attack Simulator', icon: <Flame className="w-4 h-4" /> },
    { id: 'vulnerabilities', label: 'Vulnerability Explorer', icon: <Bug className="w-4 h-4" /> },
    { id: 'traces', label: 'Execution Traces', icon: <Activity className="w-4 h-4" /> },
    { id: 'authorization', label: 'Authorization Intelligence', icon: <KeyRound className="w-4 h-4" /> },
    { id: 'source-analyzer', label: 'Source Code Analyzer', icon: <FileCode2 className="w-4 h-4" /> },
    { id: 'mcp-inspector', label: 'MCP Security Inspector', icon: <Cpu className="w-4 h-4" /> },
    { id: 'rag-auditor', label: 'RAG Security Auditor', icon: <Layers className="w-4 h-4" /> },
    { id: 'patch-workbench', label: 'Patch Workbench', icon: <Wrench className="w-4 h-4" /> },
    { id: 'reports', label: 'Security Reports', icon: <FileText className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings & Integrations', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-[#090d19] border-r border-slate-800/80 flex flex-col flex-shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center text-white shadow-[0_0_15px_rgba(6,182,212,0.3)]">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-sm text-white tracking-wide flex items-center gap-1.5">
            BreakTraceFix <span className="text-cyan-400 text-xs px-1.5 py-0.2 rounded bg-cyan-950/80 border border-cyan-800">AI</span>
          </h1>
          <p className="text-[10px] text-slate-400 font-medium tracking-tight">Break It. Trace It. Fix It.</p>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {menuItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all text-left ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-[inset_0_0_8px_rgba(6,182,212,0.1)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <span className={isActive ? 'text-cyan-400' : 'text-slate-500'}>{item.icon}</span>
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Author & Status Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 text-[11px] text-slate-500">
        <div className="flex items-center justify-between mb-1">
          <span className="font-semibold text-slate-400">Author:</span>
          <span className="text-cyan-300 font-mono">Harsh P. S. Rana</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          Engine Online &bull; v1.0.0
        </div>
      </div>
    </aside>
  );
};

