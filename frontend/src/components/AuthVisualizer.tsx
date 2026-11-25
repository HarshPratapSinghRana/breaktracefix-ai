import React from 'react';
import { ArrowRight, User, Building, Database, Zap, ShieldCheck, ShieldAlert } from 'lucide-react';

interface VisualNode {
  id: string;
  label: string;
  type: string;
  status: string;
}

interface Props {
  nodes: VisualNode[];
  edges: Array<{ source: string; target: string }>;
  decision: 'ALLOW' | 'DENY';
  reason: string;
}

export const AuthVisualizer: React.FC<Props> = ({ nodes, decision, reason }) => {
  const isAllow = decision === 'ALLOW';

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'actor': return <User className="w-4 h-4 text-cyan-400" />;
      case 'tenant': return <Building className="w-4 h-4 text-blue-400" />;
      case 'resource': return <Database className="w-4 h-4 text-purple-400" />;
      case 'action': return <Zap className="w-4 h-4 text-amber-400" />;
      case 'policy': return <ShieldCheck className="w-4 h-4 text-indigo-400" />;
      default: return isAllow ? <ShieldCheck className="w-4 h-4 text-emerald-400" /> : <ShieldAlert className="w-4 h-4 text-rose-400" />;
    }
  };

  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Authorization Context Flow</h4>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
          isAllow ? 'bg-emerald-950 text-emerald-300 border border-emerald-600' : 'bg-rose-950 text-rose-300 border border-rose-600'
        }`}>
          DECISION: {decision}
        </span>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto py-2">
        {nodes.map((node, index) => {
          const isLast = index === nodes.length - 1;
          const isDecisionNode = node.id === 'decision';

          let borderStyle = 'border-slate-700 bg-slate-950';
          if (isDecisionNode) {
            borderStyle = isAllow
              ? 'border-emerald-600 bg-emerald-950/40 text-emerald-200'
              : 'border-rose-600 bg-rose-950/40 text-rose-200';
          }

          return (
            <React.Fragment key={node.id}>
              <div className={`p-3 rounded-lg border flex-shrink-0 min-w-[140px] text-xs ${borderStyle}`}>
                <div className="flex items-center gap-1.5 mb-1 text-[11px] font-semibold text-slate-400 uppercase">
                  {getNodeIcon(node.type)}
                  {node.type}
                </div>
                <div className="font-mono text-slate-200 whitespace-pre-line text-[11px] font-medium leading-tight">
                  {node.label}
                </div>
              </div>
              {!isLast && (
                <ArrowRight className="w-4 h-4 text-cyan-600/70 flex-shrink-0 mx-1" />
              )}
            </React.Fragment>
          );
        })}
      </div>

      <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
        <span className="font-semibold text-slate-400">Decision Rationale: </span>
        <span className={isAllow ? 'text-emerald-300' : 'text-rose-300'}>{reason}</span>
      </div>
    </div>
  );
};

