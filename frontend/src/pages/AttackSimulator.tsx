import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AttackScenario, Assessment, SimulationRun } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Flame, Play, Shield, RefreshCw, CheckCircle2, XCircle, Search, Filter } from 'lucide-react';

interface Props {
  selectedAssessment: Assessment | null;
}

export const AttackSimulator: React.FC<Props> = ({ selectedAssessment }) => {
  const [scenarios, setScenarios] = useState<AttackScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<AttackScenario | null>(null);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [mode, setMode] = useState<'vulnerable' | 'protected'>('vulnerable');
  const [customInput, setCustomInput] = useState('');
  const [running, setRunning] = useState(false);
  const [latestRun, setLatestRun] = useState<SimulationRun | null>(null);

  useEffect(() => {
    loadScenarios();
  }, [categoryFilter, severityFilter]);

  const loadScenarios = async () => {
    try {
      const data = await api.listScenarios(categoryFilter || undefined, severityFilter || undefined);
      setScenarios(data);
      if (data.length > 0 && !selectedScenario) {
        setSelectedScenario(data[0]);
        setCustomInput(data[0].attack_input);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectScenario = (sc: AttackScenario) => {
    setSelectedScenario(sc);
    setCustomInput(sc.attack_input);
    setLatestRun(null);
  };

  const handleExecute = async () => {
    if (!selectedAssessment || !selectedScenario) return;
    setRunning(true);
    try {
      const res = await api.simulateAttack({
        assessment_id: selectedAssessment.id,
        scenario_id: selectedScenario.id,
        mode: mode,
        custom_input: customInput
      });
      setLatestRun(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-400" />
          AI Security Attack Simulation Engine
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Execute isolated, reproducible security attack vectors against target environments across OWASP Top 10 categories
        </p>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-3 p-3 rounded-xl border border-slate-800 bg-[#090d19]">
        <div className="flex items-center gap-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400 font-semibold uppercase text-[10px]">Filter:</span>
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
        >
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
        </select>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
        >
          <option value="">All Categories</option>
          <option value="Prompt Injection">Prompt Injection</option>
          <option value="Agency">Excessive Agency</option>
          <option value="Disclosure">Information Disclosure</option>
          <option value="SSRF">SSRF & Traversal</option>
          <option value="Authorization">Authorization</option>
        </select>
        <div className="ml-auto text-xs text-slate-400 font-mono">
          Showing {scenarios.length} scenarios
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scenarios Catalog Column */}
        <div className="lg:col-span-5 space-y-2 max-h-[640px] overflow-y-auto pr-1">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario?.id === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => handleSelectScenario(sc)}
                className={`p-3.5 rounded-xl border text-left cursor-pointer transition ${
                  isSelected
                    ? 'border-cyan-500 bg-cyan-950/20 shadow-[inset_0_0_8px_rgba(6,182,212,0.1)]'
                    : 'border-slate-800 bg-[#090d19] hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-[10px] text-cyan-400 font-bold">{sc.id}</span>
                  <SeverityBadge severity={sc.severity} />
                </div>
                <h4 className="text-xs font-bold text-white mb-1">{sc.name}</h4>
                <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between">
                  <span>{sc.owasp_category}</span>
                  <span>{sc.cwe_id}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Attack Execution Panel */}
        <div className="lg:col-span-7 space-y-4">
          {selectedScenario && (
            <div className="rounded-xl border border-slate-800 bg-[#090d19] p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">{selectedScenario.id}</span>
                  <h3 className="text-base font-extrabold text-white mt-0.5">{selectedScenario.name}</h3>
                  <p className="text-xs text-slate-400 mt-1">{selectedScenario.threat_model}</p>
                </div>
                <SeverityBadge severity={selectedScenario.severity} />
              </div>

              {/* Execution Mode Selector */}
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-white block">Execution Mode</span>
                  <span className="text-[11px] text-slate-400">Choose whether to run in vulnerable baseline or protected mode</span>
                </div>
                <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                  <button
                    onClick={() => setMode('vulnerable')}
                    className={`px-3 py-1 rounded text-xs font-bold transition cursor-pointer ${
                      mode === 'vulnerable' ? 'bg-rose-900/80 text-rose-200 border border-rose-700' : 'text-slate-400'
                    }`}
                  >
                    Vulnerable
                  </button>
                  <button
                    onClick={() => setMode('protected')}
                    className={`px-3 py-1 rounded text-xs font-bold transition cursor-pointer ${
                      mode === 'protected' ? 'bg-emerald-900/80 text-emerald-200 border border-emerald-700' : 'text-slate-400'
                    }`}
                  >
                    Protected
                  </button>
                </div>
              </div>

              {/* Attack Input Payload */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Attack Input Payload</label>
                <textarea
                  value={customInput}
                  onChange={(e) => setCustomInput(e.target.value)}
                  rows={4}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Trigger Button */}
              <button
                onClick={handleExecute}
                disabled={running}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-orange-600 to-rose-600 hover:from-orange-500 hover:to-rose-500 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg shadow-rose-950/30 transition disabled:opacity-50 cursor-pointer"
              >
                <Play className="w-4 h-4 fill-current" />
                {running ? 'Executing Attack Simulation...' : `Execute Attack (${mode.toUpperCase()} MODE)`}
              </button>

              {/* Results & Invariant Verification Output */}
              {latestRun && (
                <div className="mt-4 p-4 rounded-xl border border-slate-800 bg-slate-950 space-y-3 text-xs">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="font-bold text-white flex items-center gap-2">
                      Execution Result:
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        latestRun.status === 'success_exploited'
                          ? 'bg-rose-950 text-rose-300 border border-rose-700'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                      }`}>
                        {latestRun.status.toUpperCase()}
                      </span>
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">{latestRun.execution_time_ms} ms</span>
                  </div>

                  <div>
                    <span className="text-slate-400 font-semibold block mb-1">Model / Tool Response:</span>
                    <div className="p-3 rounded bg-slate-900 border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap">
                      {latestRun.output_response || 'No output emitted.'}
                    </div>
                  </div>

                  {/* Invariant Verification Checks */}
                  <div>
                    <span className="text-slate-400 font-semibold block mb-1">Security Defense Invariants:</span>
                    <div className="space-y-1.5">
                      {latestRun.invariant_results.map((inv, i) => (
                        <div
                          key={i}
                          className={`p-2 rounded border flex items-center justify-between ${
                            inv.passed
                              ? 'bg-emerald-950/30 border-emerald-800/50 text-emerald-300'
                              : 'bg-rose-950/30 border-rose-800/50 text-rose-300'
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            {inv.passed ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-rose-400" />}
                            <span className="font-mono text-[11px] font-bold">{inv.invariant_name}</span>
                          </div>
                          <span className="text-[10px] font-bold uppercase">{inv.passed ? 'PASSED' : 'VIOLATED'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

