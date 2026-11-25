import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AuthContextRequest, AuthDecisionResponse, AuthPolicy } from '../types';
import { AuthVisualizer } from '../components/AuthVisualizer';
import { KeyRound, Shield, CheckCircle2, XCircle, Play, Plus, RefreshCw, AlertTriangle } from 'lucide-react';

export const AuthorizationIntelligence: React.FC = () => {
  const [policies, setPolicies] = useState<AuthPolicy[]>([]);
  const [decisionLogs, setDecisionLogs] = useState<any[]>([]);
  const [decisionResult, setDecisionResult] = useState<AuthDecisionResponse | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  // 8-Axis Form State
  const [actorId, setActorId] = useState('user-researcher-001');
  const [actorRole, setActorRole] = useState('researcher');
  const [tenantId, setTenantId] = useState('tenant-default-001');
  const [resourceId, setResourceId] = useState('doc:user_guide');
  const [action, setAction] = useState('read');
  const [dataClass, setDataClass] = useState('Internal');
  const [purpose, setPurpose] = useState('customer_support');
  const [recipient, setRecipient] = useState('user');
  const [hasApproval, setHasApproval] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const pList = await api.listPolicies();
      const dList = await api.listDecisionLogs();
      setPolicies(pList);
      setDecisionLogs(dList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setEvaluating(true);
    try {
      const res = await api.evaluateAuth({
        actor_id: actorId,
        actor_role: actorRole,
        tenant_id: tenantId,
        resource_id: resourceId,
        action: action,
        data_classification: dataClass,
        purpose: purpose,
        recipient: recipient,
        has_approval: hasApproval
      });
      setDecisionResult(res);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-indigo-400" />
          Context-Aware Authorization Intelligence Engine
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          8-Axis context evaluation matrix: Actor, Tenant, Resource, Action, Classification, Purpose, Recipient, and Approval
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 8-Axis Evaluation Form */}
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-[#090d19] p-5 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Evaluate 8-Axis Access Request</h3>
          
          <form onSubmit={handleEvaluate} className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Actor ID</label>
                <input
                  type="text"
                  value={actorId}
                  onChange={(e) => setActorId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Actor Role</label>
                <select
                  value={actorRole}
                  onChange={(e) => setActorRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="researcher">researcher</option>
                  <option value="admin">admin</option>
                  <option value="developer">developer</option>
                  <option value="auditor">auditor</option>
                  <option value="agent">agent (autonomous)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Tenant ID</label>
                <input
                  type="text"
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Action</label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="read">read</option>
                  <option value="write">write</option>
                  <option value="execute">execute</option>
                  <option value="delete">delete</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Target Resource ID</label>
              <input
                type="text"
                value={resourceId}
                onChange={(e) => setResourceId(e.target.value)}
                placeholder="doc:user_guide or tool:destructive:purge"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 font-mono text-[11px]"
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Classification</label>
                <select
                  value={dataClass}
                  onChange={(e) => setDataClass(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="Public">Public</option>
                  <option value="Internal">Internal</option>
                  <option value="Confidential">Confidential</option>
                  <option value="Restricted">Restricted</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Purpose</label>
                <input
                  type="text"
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 text-[11px]"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Recipient</label>
                <input
                  type="text"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500 text-[11px]"
                />
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-white font-semibold block text-[11px]">Human-in-the-Loop Sign-off</span>
                <span className="text-[10px] text-slate-400">Explicit approval token for high-impact actions</span>
              </div>
              <input
                type="checkbox"
                checked={hasApproval}
                onChange={(e) => setHasApproval(e.target.checked)}
                className="accent-cyan-500 w-4 h-4 cursor-pointer"
              />
            </div>

            <button
              type="submit"
              disabled={evaluating}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-950/40 transition cursor-pointer disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-current" />
              {evaluating ? 'Evaluating Context Rules...' : 'Evaluate Access Request'}
            </button>
          </form>
        </div>

        {/* Visual Context Flow & Decision Breakdown */}
        <div className="lg:col-span-7 space-y-4">
          {decisionResult ? (
            <div className="space-y-4">
              <AuthVisualizer
                nodes={decisionResult.visual_context.nodes}
                edges={decisionResult.visual_context.edges}
                decision={decisionResult.decision}
                reason={decisionResult.reason}
              />

              {/* Step-by-Step Rule Evaluation Log */}
              <div className="p-4 rounded-xl border border-slate-800 bg-[#090d19] space-y-2 text-xs">
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[11px]">Step-by-Step Policy Evaluation</h4>
                <div className="space-y-1 font-mono text-[11px]">
                  {decisionResult.evaluation_steps.map((st, i) => (
                    <div key={i} className="p-2 rounded bg-slate-950 border border-slate-800/80 text-slate-300">
                      {st}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
              Submit an 8-axis access request on the left to visualize the decision flow and policy evaluation steps.
            </div>
          )}

          {/* Active Policies Table */}
          <div className="p-4 rounded-xl border border-slate-800 bg-[#090d19] text-xs">
            <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[11px] mb-2">Active ABAC/RBAC Policies</h4>
            <div className="space-y-1.5">
              {policies.map((p) => (
                <div key={p.id} className="p-2.5 rounded bg-slate-950 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white block">{p.name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Role: {p.role_pattern} &bull; Resource: {p.resource_pattern} &bull; Action: {p.action_pattern}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    p.effect === 'ALLOW' ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' : 'bg-rose-950 text-rose-300 border border-rose-700'
                  }`}>
                    {p.effect}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

