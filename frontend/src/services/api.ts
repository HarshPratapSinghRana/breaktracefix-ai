import {
  Assessment,
  AttackScenario,
  SimulationRun,
  Finding,
  PatchValidation,
  ExecutionTrace,
  TimelineStage,
  AuthContextRequest,
  AuthDecisionResponse,
  AuthPolicy,
  StaticFinding,
  MCPInspectionReport,
  RAGAuditReport,
  SecurityReport
} from '../types';

const API_BASE = '/api/v1';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    }
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.message || errorBody.detail || `Request failed with status ${res.status}`);
  }
  const envelope = await res.json();
  return envelope.data !== undefined ? envelope.data : envelope;
}

export const api = {
  // System Health
  async getHealth(): Promise<{ status: string; project: string }> {
    const res = await fetch('/api/health');
    const data = await res.json();
    return data.data;
  },

  // Assessments
  async listAssessments(): Promise<Assessment[]> {
    return fetchJSON<Assessment[]>('/assessments');
  },
  async getAssessment(id: string): Promise<Assessment> {
    return fetchJSON<Assessment>(`/assessments/${id}`);
  },
  async createAssessment(payload: Partial<Assessment>): Promise<Assessment> {
    return fetchJSON<Assessment>('/assessments', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Attacks
  async listScenarios(category?: string, severity?: string): Promise<AttackScenario[]> {
    let url = '/attacks';
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (severity) params.append('severity', severity);
    if (params.toString()) url += `?${params.toString()}`;
    return fetchJSON<AttackScenario[]>(url);
  },
  async getScenario(id: string): Promise<AttackScenario> {
    return fetchJSON<AttackScenario>(`/attacks/scenarios/${id}`);
  },
  async simulateAttack(payload: { assessment_id: string; scenario_id: string; mode: string; custom_input?: string }): Promise<SimulationRun> {
    return fetchJSON<SimulationRun>('/attacks/simulate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  async batchSimulate(assessmentId: string, mode: string = 'vulnerable'): Promise<SimulationRun[]> {
    return fetchJSON<SimulationRun[]>(`/attacks/batch-simulate/${assessmentId}?mode=${mode}`, {
      method: 'POST'
    });
  },
  async listRuns(assessmentId?: string): Promise<SimulationRun[]> {
    const url = assessmentId ? `/attacks/runs?assessment_id=${assessmentId}` : '/attacks/runs';
    return fetchJSON<SimulationRun[]>(url);
  },

  // Traces
  async listTraces(violationOnly: boolean = false): Promise<ExecutionTrace[]> {
    return fetchJSON<ExecutionTrace[]>(`/traces?violation_only=${violationOnly}`);
  },
  async getTrace(traceId: string): Promise<ExecutionTrace> {
    return fetchJSON<ExecutionTrace>(`/traces/${traceId}`);
  },
  async getTimeline(traceId: string): Promise<TimelineStage[]> {
    return fetchJSON<TimelineStage[]>(`/traces/${traceId}/timeline`);
  },
  async getOtelTrace(traceId: string): Promise<any> {
    return fetchJSON<any>(`/traces/${traceId}/otel`);
  },
  async executeLivePipeline(prompt: string, simulateViolation: boolean = false): Promise<ExecutionTrace> {
    return fetchJSON<ExecutionTrace>(`/traces/execute-pipeline?prompt=${encodeURIComponent(prompt)}&simulate_violation=${simulateViolation}`, {
      method: 'POST'
    });
  },

  // Authorization Intelligence
  async evaluateAuth(req: AuthContextRequest): Promise<AuthDecisionResponse> {
    return fetchJSON<AuthDecisionResponse>('/authorization/evaluate', {
      method: 'POST',
      body: JSON.stringify(req)
    });
  },
  async listPolicies(): Promise<AuthPolicy[]> {
    return fetchJSON<AuthPolicy[]>('/authorization/policies');
  },
  async createPolicy(policy: Partial<AuthPolicy>): Promise<AuthPolicy> {
    return fetchJSON<AuthPolicy>('/authorization/policies', {
      method: 'POST',
      body: JSON.stringify(policy)
    });
  },
  async listDecisionLogs(): Promise<any[]> {
    return fetchJSON<any[]>('/authorization/decisions');
  },

  // Reproduction & Patch Workbench
  async listFindings(assessmentId?: string): Promise<Finding[]> {
    const url = assessmentId ? `/reproduction/findings?assessment_id=${assessmentId}` : '/reproduction/findings';
    return fetchJSON<Finding[]>(url);
  },
  async validatePatch(findingId: string, patchTitle: string, patchDiff?: string): Promise<PatchValidation> {
    return fetchJSON<PatchValidation>('/reproduction/validate-patch', {
      method: 'POST',
      body: JSON.stringify({ finding_id: findingId, patch_title: patchTitle, patch_diff: patchDiff })
    });
  },
  async getRegressionCode(findingId: string): Promise<{ finding_id: string; pytest_code: string }> {
    return fetchJSON<{ finding_id: string; pytest_code: string }>(`/reproduction/findings/${findingId}/regression-test`);
  },

  // Source Analyzer
  async scanCode(code: string, filename: string = 'agent.py'): Promise<StaticFinding[]> {
    return fetchJSON<StaticFinding[]>('/source-analyzer/scan', {
      method: 'POST',
      body: JSON.stringify({ code, filename })
    });
  },
  async getSemgrepRules(): Promise<{ rules_yaml: string; rules_count: number }> {
    return fetchJSON<{ rules_yaml: string; rules_count: number }>('/source-analyzer/rules');
  },
  async exportSarif(code: string, filename: string = 'agent.py'): Promise<any> {
    return fetchJSON<any>('/source-analyzer/export-sarif', {
      method: 'POST',
      body: JSON.stringify({ code, filename })
    });
  },

  // MCP Inspector
  async getSampleMCP(): Promise<any> {
    return fetchJSON<any>('/mcp-inspector/sample-manifest');
  },
  async inspectMCP(manifest: any, serverName?: string): Promise<MCPInspectionReport> {
    return fetchJSON<MCPInspectionReport>('/mcp-inspector/inspect', {
      method: 'POST',
      body: JSON.stringify({ manifest_json: manifest, server_name: serverName })
    });
  },

  // RAG Auditor
  async getSampleRAGChunks(): Promise<any[]> {
    return fetchJSON<any[]>('/rag-auditor/sample-chunks');
  },
  async auditRAG(chunks: any[], collectionName?: string): Promise<RAGAuditReport> {
    return fetchJSON<RAGAuditReport>('/rag-auditor/audit', {
      method: 'POST',
      body: JSON.stringify({ chunks, collection_name: collectionName })
    });
  },

  // Reports
  async getJsonReport(assessmentId: string): Promise<SecurityReport> {
    return fetchJSON<SecurityReport>(`/reports/json/${assessmentId}`);
  },
  getHtmlReportUrl(assessmentId: string): string {
    return `${API_BASE}/reports/html/${assessmentId}`;
  }
};

