import React, { useState } from 'react';
import { TimelineStage } from '../types';
import { CheckCircle, AlertTriangle, XCircle, ArrowRight, Clock, ShieldAlert } from 'lucide-react';

interface Props {
  stages: TimelineStage[];
  onSelectStage?: (stage: TimelineStage) => void;
}

export const TraceTimeline: React.FC<Props> = ({ stages, onSelectStage }) => {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 overflow-x-auto pb-4 pt-2">
        {stages.map((stage) => {
          const isViolation = stage.status === 'VIOLATION';
          const isError = stage.status === 'ERROR';
          const isSelected = selectedIdx === stage.index;

          let badgeBorder = 'border-slate-700 bg-slate-900/90 hover:border-slate-600 text-slate-300';
          if (isViolation) {
            badgeBorder = 'border-rose-600 bg-rose-950/40 text-rose-300 shadow-[0_0_12px_rgba(244,63,94,0.3)] animate-pulse';
          } else if (isError) {
            badgeBorder = 'border-amber-600 bg-amber-950/40 text-amber-300';
          } else {
            badgeBorder = 'border-cyan-600/40 bg-cyan-950/20 text-cyan-300';
          }

          return (
            <div key={stage.index} className="flex items-center flex-shrink-0">
              <button
                onClick={() => {
                  setSelectedIdx(stage.index);
                  if (onSelectStage) onSelectStage(stage);
                }}
                className={`flex flex-col text-left px-3.5 py-2.5 rounded-lg border text-xs font-mono transition-all ${badgeBorder} ${
                  isSelected ? 'ring-2 ring-cyan-400 scale-105' : ''
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400 font-bold">#{stage.index}</span>
                  {isViolation ? (
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                  ) : isError ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  ) : (
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  )}
                  <span className="font-semibold truncate max-w-[120px]">{stage.name}</span>
                </div>
                <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                  <span className="flex items-center gap-0.5">
                    <Clock className="w-2.5 h-2.5" />
                    {stage.duration_ms}ms
                  </span>
                  {stage.security_flag && (
                    <span className="text-rose-400 font-bold uppercase truncate max-w-[80px]">FLAGGED</span>
                  )}
                </div>
              </button>
              {stage.index < stages.length && (
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 mx-1 flex-shrink-0" />
              )}
            </div>
          );
        })}
      </div>

      {selectedIdx !== null && (
        <div className="mt-4 p-4 rounded-xl border border-slate-800 bg-slate-900/90 text-xs">
          {(() => {
            const stg = stages.find((s) => s.index === selectedIdx);
            if (!stg) return null;
            return (
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3">
                  <span className="text-sm font-bold text-white flex items-center gap-2">
                    Stage #{stg.index}: {stg.name}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${stg.status === 'VIOLATION' ? 'bg-rose-950 text-rose-300 border border-rose-700' : 'bg-emerald-950 text-emerald-300 border border-emerald-700'}`}>
                      {stg.status}
                    </span>
                  </span>
                  <span className="text-slate-400 font-mono">Duration: {stg.duration_ms} ms</span>
                </div>
                {stg.security_flag && (
                  <div className="mb-3 p-2.5 rounded bg-rose-950/50 border border-rose-800 text-rose-200">
                    <strong>Security Flag:</strong> {stg.security_flag}
                  </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <p className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] mb-1">Pre-Redacted Input Data</p>
                    <pre className="text-slate-300 font-mono text-[11px] whitespace-pre-wrap break-all">{stg.input_preview}</pre>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <p className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] mb-1">Stage Output / Transition</p>
                    <pre className="text-slate-300 font-mono text-[11px] whitespace-pre-wrap break-all">{stg.output_preview}</pre>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

