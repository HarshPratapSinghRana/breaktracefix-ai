import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ExecutionTrace, TimelineStage } from '../types';
import { TraceTimeline } from '../components/TraceTimeline';
import { Activity, Play, Download, Search, AlertCircle, ShieldAlert, CheckCircle } from 'lucide-react';

export const ExecutionTraceExplorer: React.FC = () => {
  const [traces, setTraces] = useState<ExecutionTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<ExecutionTrace | null>(null);
  const [timeline, setTimeline] = useState<TimelineStage[]>([]);
  const [violationFilter, setViolationFilter] = useState(false);
  const [livePrompt, setLivePrompt] = useState('Process document query for client with token sk-proj-supertoken123');
  const [simViolation, setSimViolation] = useState(true);
  const [liveRunning, setLiveRunning] = useState(false);
  const [showOtelModal, setShowOtelModal] = useState(false);
  const [otelData, setOtelData] = useState<any>(null);

  useEffect(() => {
    loadTraces();
  }, [violationFilter]);

  const loadTraces = async () => {
    try {
      const data = await api.listTraces(violationFilter);
      setTraces(data);
      if (data.length > 0 && !selectedTrace) {
        handleSelectTrace(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectTrace = async (tr: ExecutionTrace) => {
    setSelectedTrace(tr);
    try {
      const stages = await api.getTimeline(tr.id);
      setTimeline(stages);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunLivePipeline = async () => {
    setLiveRunning(true);
    try {
      const newTrace = await api.executeLivePipeline(livePrompt, simViolation);
      await loadTraces();
      handleSelectTrace(newTrace);
    } catch (err) {
      console.error(err);
    } finally {
      setLiveRunning(false);
    }
  };

  const handleExportOtel = async () => {
    if (!selectedTrace) return;
    try {
      const otel = await api.getOtelTrace(selectedTrace.id);
      setOtelData(otel);
      setShowOtelModal(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            11-Stage Data Flow & Execution Tracing
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full lifecycle inspection: User Input &rarr; Prompt &rarr; Retrieval &rarr; Model &rarr; Tool &rarr; Output Validation
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViolationFilter(!violationFilter)}
            className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition cursor-pointer ${
              violationFilter ? 'bg-rose-950 text-rose-300 border-rose-700' : 'bg-slate-900 text-slate-300 border-slate-700'
            }`}
          >
            {violationFilter ? 'Showing Violations Only' : 'Filter Violations'}
          </button>
          <button
            onClick={handleExportOtel}
            disabled={!selectedTrace}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" /> Export OTel JSON
          </button>
        </div>
      </div>

      {/* Live Pipeline Execution Card */}
      <div className="p-4 rounded-xl border border-slate-800 bg-[#090d19] space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Run Live 11-Stage Traced Request</span>
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={simViolation}
              onChange={(e) => setSimViolation(e.target.checked)}
              className="accent-cyan-500 rounded"
            />
            Simulate Security Boundary Violation
          </label>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={livePrompt}
            onChange={(e) => setLivePrompt(e.target.value)}
            placeholder="Type prompt with potential secrets or commands..."
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleRunLivePipeline}
            disabled={liveRunning}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg flex items-center gap-1.5 shadow-md shadow-cyan-950 transition cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {liveRunning ? 'Tracing Pipeline...' : 'Execute & Trace'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Trace List Column */}
        <div className="lg:col-span-4 space-y-2 max-h-[640px] overflow-y-auto pr-1">
          {traces.map((tr) => {
            const isSelected = selectedTrace?.id === tr.id;
            const isViolation = tr.has_violation === 'YES';
            return (
              <div
                key={tr.id}
                onClick={() => handleSelectTrace(tr)}
                className={`p-3.5 rounded-xl border text-left cursor-pointer transition ${
                  isSelected
                    ? 'border-cyan-500 bg-cyan-950/20 shadow-[inset_0_0_8px_rgba(6,182,212,0.1)]'
                    : 'border-slate-800 bg-[#090d19] hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-[10px] text-cyan-400 font-bold">{tr.trace_id}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    isViolation ? 'bg-rose-950 text-rose-300 border border-rose-700' : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                  }`}>
                    {isViolation ? 'VIOLATION' : 'CLEAN'}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white mb-1 truncate">{tr.name}</h4>
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-2">
                  <span>{tr.total_duration_ms} ms</span>
                  <span>{new Date(tr.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Trace Interactive Timeline & Span Tree */}
        <div className="lg:col-span-8 space-y-4">
          {selectedTrace ? (
            <div className="rounded-xl border border-slate-800 bg-[#090d19] p-5 space-y-5">
              <div className="flex items-start justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="font-mono text-[11px] text-cyan-400 font-bold">TRACE ID: {selectedTrace.trace_id}</span>
                  <h3 className="text-base font-extrabold text-white mt-0.5">{selectedTrace.name}</h3>
                  <p className="text-xs text-slate-400 mt-1">{selectedTrace.summary}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono text-cyan-300 font-bold block">{selectedTrace.total_duration_ms} ms</span>
                  <span className="text-[10px] text-slate-500">Total Lifecycle Duration</span>
                </div>
              </div>

              {/* 11-Stage Interactive Timeline */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">11-Stage Execution Pipeline</h4>
                <TraceTimeline stages={timeline} />
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
              Select a trace record to view the 11-stage timeline.
            </div>
          )}
        </div>
      </div>

      {/* OTel Export Modal */}
      {showOtelModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono">OpenTelemetry ResourceSpans JSON</h3>
              <button onClick={() => setShowOtelModal(false)} className="text-slate-400 hover:text-white text-xs cursor-pointer">
                Close
              </button>
            </div>
            <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 max-h-96 overflow-y-auto">
              {JSON.stringify(otelData, null, 2)}
            </pre>
            <div className="flex justify-end">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(otelData, null, 2));
                  alert('OTel JSON copied to clipboard!');
                }}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg cursor-pointer"
              >
                Copy to Clipboard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

