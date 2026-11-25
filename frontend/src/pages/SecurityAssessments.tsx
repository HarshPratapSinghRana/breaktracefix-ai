import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Assessment } from '../types';
import { Target, Plus, RefreshCw, Shield, Trash2, ExternalLink } from 'lucide-react';

interface Props {
  onSelectAssessment: (assessment: Assessment) => void;
  selectedId: string;
}

export const SecurityAssessments: React.FC<Props> = ({ onSelectAssessment, selectedId }) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [targetType, setTargetType] = useState<'agent' | 'rag' | 'mcp_server' | 'llm_pipeline'>('agent');
  const [endpoint, setEndpoint] = useState('https://api.internal.ai/v1/agent');

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    setLoading(true);
    try {
      const data = await api.listAssessments();
      setAssessments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api.createAssessment({
        name,
        description,
        target_type: targetType,
        target_endpoint: endpoint,
        target_config: { model: 'gpt-4o', secure_mode: false }
      });
      setShowCreateModal(false);
      setName('');
      setDescription('');
      await loadAssessments();
      onSelectAssessment(created);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-cyan-400" />
            Security Assessment Engagements
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Manage target AI agents, RAG collections, and MCP server endpoints</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadAssessments}
            className="p-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white transition cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-900/30 transition cursor-pointer"
          >
            <Plus className="w-4 h-4" /> New Assessment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {assessments.map((a) => {
          const isSelected = a.id === selectedId;
          return (
            <div
              key={a.id}
              onClick={() => onSelectAssessment(a)}
              className={`p-5 rounded-xl border bg-[#090d19] transition cursor-pointer relative overflow-hidden flex flex-col justify-between ${
                isSelected
                  ? 'border-cyan-500 ring-2 ring-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-cyan-300 border border-slate-700 font-mono">
                    {a.target_type}
                  </span>
                  <span className={`text-xs font-bold ${a.risk_score >= 70 ? 'text-rose-400' : 'text-amber-400'}`}>
                    Risk: {a.risk_score}/100
                  </span>
                </div>
                <h3 className="font-bold text-white text-base mb-1">{a.name}</h3>
                <p className="text-xs text-slate-400 line-clamp-2">{a.description || 'No description provided.'}</p>
                {a.target_endpoint && (
                  <p className="text-[11px] text-slate-500 font-mono mt-2 truncate">URL: {a.target_endpoint}</p>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                <span>Status: <strong className="text-slate-300 uppercase">{a.status}</strong></span>
                <span className="font-mono text-[10px]">{new Date(a.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          );
        })}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-4">Create New Security Assessment</h3>
            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Assessment Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Autonomous Support Agent v3"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Type</label>
                <select
                  value={targetType}
                  onChange={(e) => setTargetType(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="agent">Autonomous Agent</option>
                  <option value="rag">RAG Pipeline</option>
                  <option value="mcp_server">MCP Server</option>
                  <option value="llm_pipeline">Custom LLM Pipeline</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Endpoint</label>
                <input
                  type="text"
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold cursor-pointer"
                >
                  Create Assessment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

