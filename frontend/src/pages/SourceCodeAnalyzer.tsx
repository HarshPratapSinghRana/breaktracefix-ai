import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { StaticFinding } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { FileCode2, Play, Download, Shield, AlertTriangle, Code, Terminal } from 'lucide-react';

const DEFAULT_CODE_SAMPLE = `import os
import requests
import logging

logger = logging.getLogger("agent")

def handle_user_query(user_input, api_token):
    # Insecure logging of sensitive token
    logger.info(f"Processing query with token {api_token}")
    
    # Direct untrusted prompt concatenation
    prompt = f"System: summarize this user prompt: {user_input}"
    
    # SSRF vulnerability in web fetch
    response = requests.get(user_input)
    
    return prompt

def read_file_tool(file_path):
    # Path traversal vulnerability
    with open(file_path, "r") as f:
        return f.read()

def execute_tool(tool_name, tool_args):
    # Missing authorization check before tool call
    return eval(tool_name)(**tool_args)
`;

export const SourceCodeAnalyzer: React.FC = () => {
  const [code, setCode] = useState(DEFAULT_CODE_SAMPLE);
  const [filename, setFilename] = useState('agent_pipeline.py');
  const [findings, setFindings] = useState<StaticFinding[]>([]);
  const [scanning, setScanning] = useState(false);
  const [sarifModal, setSarifModal] = useState(false);
  const [sarifOutput, setSarifOutput] = useState<any>(null);

  const handleScan = async () => {
    setScanning(true);
    try {
      const res = await api.scanCode(code, filename);
      setFindings(res);
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  };

  const handleExportSarif = async () => {
    try {
      const sarif = await api.exportSarif(code, filename);
      setSarifOutput(sarif);
      setSarifModal(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileCode2 className="w-5 h-5 text-cyan-400" />
            Source Code Security Analyzer (Semgrep & SARIF 2.1.0)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Static security analysis for missing authorization, prompt injection sinks, insecure logging, and SSRF
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportSarif}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" /> Export SARIF 2.1.0
          </button>
          <button
            onClick={handleScan}
            disabled={scanning}
            className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-950 transition cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {scanning ? 'Analyzing Code...' : 'Run Static Scan'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Source Code Editor */}
        <div className="lg:col-span-6 rounded-xl border border-slate-800 bg-[#090d19] p-4 flex flex-col space-y-2">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="text-xs font-mono text-cyan-400 font-bold flex items-center gap-1.5">
              <Code className="w-3.5 h-3.5" /> {filename}
            </span>
            <span className="text-[10px] text-slate-500 uppercase font-mono">Python 3.12+</span>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={22}
            className="w-full flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed resize-none"
          />
        </div>

        {/* Static Findings List */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Static Findings ({findings.length})
            </h3>
            <span className="text-[10px] font-mono text-slate-500">OASIS SARIF Rule Engine</span>
          </div>

          <div className="space-y-3 max-h-[580px] overflow-y-auto pr-1">
            {findings.length === 0 ? (
              <div className="p-8 text-center text-slate-500 border border-slate-800 rounded-xl bg-[#090d19]">
                Click "Run Static Scan" above to scan the editor code for GenAI security anti-patterns.
              </div>
            ) : (
              findings.map((f) => (
                <div key={f.finding_id} className="p-4 rounded-xl border border-slate-800 bg-[#090d19] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-cyan-400 font-bold">{f.rule_id}</span>
                    <SeverityBadge severity={f.severity} />
                  </div>
                  <h4 className="text-xs font-bold text-white">{f.title}</h4>
                  <p className="text-[11px] text-slate-400">{f.explanation}</p>
                  
                  {/* Code snippet & location */}
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono text-rose-300">
                    <span className="text-slate-500 text-[10px] block mb-1">Lines {f.line_start}-{f.line_end}:</span>
                    {f.code_snippet}
                  </div>

                  <div className="text-[11px] text-cyan-300 bg-cyan-950/20 p-2 rounded border border-cyan-800/40">
                    <strong>Remediation:</strong> {f.remediation}
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/60">
                    <span>{f.cwe_id} &bull; {f.owasp_category}</span>
                    <span className="text-slate-400 font-bold">STATIC ANALYSIS</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* SARIF Modal */}
      {sarifModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono">OASIS SARIF 2.1.0 Export</h3>
              <button onClick={() => setSarifModal(false)} className="text-slate-400 hover:text-white text-xs cursor-pointer">
                Close
              </button>
            </div>
            <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 max-h-96 overflow-y-auto">
              {JSON.stringify(sarifOutput, null, 2)}
            </pre>
            <div className="flex justify-end">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(sarifOutput, null, 2));
                  alert('SARIF JSON copied to clipboard!');
                }}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg cursor-pointer"
              >
                Copy SARIF
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

