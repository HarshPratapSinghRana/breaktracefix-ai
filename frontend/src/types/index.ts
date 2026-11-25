export type Severity = 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';

export interface Assessment {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  target_type: 'agent' | 'rag' | 'mcp_server' | 'llm_pipeline';
  target_endpoint?: string;
  target_config: Record<string, any>;
  status: 'ready' | 'in_progress' | 'completed' | 'failed';
  risk_score: number;
  created_at: string;
  updated_at: string;
}

export interface InvariantResult {
  invariant_name: string;
  passed: boolean;
  description: string;
  actual_value?: any;
  expected_value?: any;
}

export interface AttackScenario {
  id: string;
  name: string;
  category: string;
  severity: Severity;
  cwe_id?: string;
  owasp_category?: string;
  threat_model: string;
  preconditions?: string;
  attack_input: string;
  expected_vulnerable_behavior: string;
  expected_secure_behavior: string;
  reproduction_instructions?: string;
  is_active: boolean;
}

export interface SimulationRun {
  id: string;
  assessment_id: string;
  scenario_id: string;
  mode: 'vulnerable' | 'protected';
  status: 'success_exploited' | 'success_defended' | 'error' | 'pending';
  input_payload: string;
  output_response?: string;
  execution_time_ms: number;
  evidence: Record<string, any>;
  invariant_results: InvariantResult[];
  created_at: string;
}

export interface Finding {
  id: string;
  assessment_id: string;
  simulation_run_id?: string;
  title: string;
  severity: Severity;
  cwe_id?: string;
  owasp_category?: string;
  affected_component: string;
  source_location?: string;
  sink_location?: string;
  attack_vector: string;
  reproduction_steps?: string;
  evidence: Record<string, any>;
  root_cause?: string;
  impact?: string;
  remediation?: string;
  patch_status: 'unpatched' | 'patch_tested' | 'verified_fixed' | 'regressed';
  created_at: string;
}

export interface PatchValidation {
  id: string;
  finding_id: string;
  patch_title: string;
  patch_diff?: string;
  vulnerable_run_id?: string;
  patched_run_id?: string;
  invariants_verified: boolean;
  confidence_score: number;
  validation_status: 'passed' | 'failed' | 'partial';
  evidence_comparison: Record<string, any>;
  regression_test_code?: string;
  created_at: string;
}

export interface TraceSpan {
  id: string;
  span_id: string;
  stage_name: string;
  stage_index: number;
  status: 'OK' | 'ERROR' | 'VIOLATION';
  duration_ms: number;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  security_event?: string;
  attributes: Record<string, any>;
  created_at: string;
}

export interface ExecutionTrace {
  id: string;
  simulation_run_id?: string;
  trace_id: string;
  name: string;
  total_duration_ms: number;
  has_violation: 'YES' | 'NO';
  summary?: string;
  created_at: string;
  spans: TraceSpan[];
}

export interface TimelineStage {
  index: number;
  name: string;
  status: 'OK' | 'ERROR' | 'VIOLATION';
  duration_ms: number;
  security_flag?: string;
  input_preview: string;
  output_preview: string;
}

export interface AuthContextRequest {
  actor_id: string;
  actor_role: string;
  tenant_id: string;
  resource_id: string;
  action: string;
  data_classification: string;
  purpose?: string;
  recipient?: string;
  has_approval: boolean;
}

export interface AuthDecisionResponse {
  decision: 'ALLOW' | 'DENY';
  reason: string;
  actor_id: string;
  tenant_id: string;
  resource_id: string;
  action: string;
  matched_policy_id?: string;
  evaluation_steps: string[];
  visual_context: {
    nodes: Array<{ id: string; label: string; type: string; status: string }>;
    edges: Array<{ source: string; target: string }>;
  };
}

export interface AuthPolicy {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  effect: 'ALLOW' | 'DENY';
  role_pattern: string;
  resource_pattern: string;
  action_pattern: string;
  max_data_classification: string;
  allowed_purposes: string[];
  allowed_recipients: string[];
  requires_approval: boolean;
  priority: string;
  is_active: boolean;
  created_at: string;
}

export interface StaticFinding {
  finding_id: string;
  rule_id: string;
  title: string;
  severity: Severity;
  cwe_id: string;
  owasp_category: string;
  file_path: string;
  line_start: number;
  line_end: number;
  column_start: number;
  column_end: number;
  code_snippet: string;
  source_location: string;
  sink_location: string;
  explanation: string;
  remediation: string;
  finding_type: string;
}

export interface MCPToolAnalysis {
  tool_name: string;
  description: string;
  risk_score: number;
  risk_level: Severity;
  requires_approval: string;
  permission_scope: string;
  risk_factors: string[];
  argument_warnings: string[];
}

export interface MCPInspectionReport {
  server_name: string;
  total_tools: number;
  overall_risk_score: number;
  overall_risk_level: string;
  high_risk_tools: number;
  tools: MCPToolAnalysis[];
  recommendations: string[];
}

export interface RAGChunkAudit {
  chunk_id: string;
  title: string;
  classification: string;
  is_poisoned: boolean;
  allowed_roles: string[];
  tenant_isolated: boolean;
  poison_indicators: Array<{
    pattern_name: string;
    matched_snippet: string;
    severity: string;
    remediation: string;
  }>;
}

export interface RAGAuditReport {
  collection_name: string;
  total_chunks: number;
  poisoned_chunks_count: number;
  unisolated_chunks_count: number;
  overall_rag_risk_score: number;
  audit_findings: RAGChunkAudit[];
  security_summary: string;
}

export interface SecurityReport {
  report_id: string;
  assessment_id: string;
  assessment_name: string;
  target_type: string;
  generated_at: string;
  author: string;
  platform: string;
  overall_risk_score: number;
  overall_status: string;
  severity_summary: Record<string, number>;
  total_findings: number;
  simulations_executed: number;
  patches_verified: number;
  findings: Finding[];
  methodology: string;
}

