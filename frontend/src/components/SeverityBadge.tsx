import React from 'react';
import { Severity } from '../types';

interface Props {
  severity: Severity | string;
  className?: string;
}

export const SeverityBadge: React.FC<Props> = ({ severity, className = '' }) => {
  const sev = (severity || 'Medium').toLowerCase();
  
  let bg = 'bg-slate-700 text-slate-200 border-slate-600';
  if (sev === 'critical') {
    bg = 'bg-rose-950/80 text-rose-300 border-rose-700/60 shadow-[0_0_8px_rgba(244,63,94,0.2)]';
  } else if (sev === 'high') {
    bg = 'bg-orange-950/80 text-orange-300 border-orange-700/60 shadow-[0_0_8px_rgba(249,115,22,0.2)]';
  } else if (sev === 'medium') {
    bg = 'bg-amber-950/80 text-amber-300 border-amber-700/60';
  } else if (sev === 'low') {
    bg = 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60';
  } else if (sev === 'info') {
    bg = 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${bg} ${className}`}>
      {severity}
    </span>
  );
};

