import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import { Assessment } from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';

// 12 Pages
import { OverviewDashboard } from './pages/OverviewDashboard';
import { SecurityAssessments } from './pages/SecurityAssessments';
import { AttackSimulator } from './pages/AttackSimulator';
import { VulnerabilityExplorer } from './pages/VulnerabilityExplorer';
import { ExecutionTraceExplorer } from './pages/ExecutionTraceExplorer';
import { AuthorizationIntelligence } from './pages/AuthorizationIntelligence';
import { SourceCodeAnalyzer } from './pages/SourceCodeAnalyzer';
import { MCPSecurityInspector } from './pages/MCPSecurityInspector';
import { RAGSecurityAuditor } from './pages/RAGSecurityAuditor';
import { PatchWorkbench } from './pages/PatchWorkbench';
import { SecurityReports } from './pages/SecurityReports';
import { SettingsIntegrations } from './pages/SettingsIntegrations';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<string>('');
  const [workbenchFindingId, setWorkbenchFindingId] = useState<string | null>(null);

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    try {
      const data = await api.listAssessments();
      setAssessments(data);
      if (data.length > 0 && !selectedAssessmentId) {
        setSelectedAssessmentId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const selectedAssessment = assessments.find((a) => a.id === selectedAssessmentId) || assessments[0] || null;

  const handleNavigateToWorkbench = (findingId: string) => {
    setWorkbenchFindingId(findingId);
    setActiveTab('patch-workbench');
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewDashboard selectedAssessment={selectedAssessment} onNavigate={setActiveTab} />;
      case 'assessments':
        return (
          <SecurityAssessments
            selectedId={selectedAssessmentId}
            onSelectAssessment={(a) => setSelectedAssessmentId(a.id)}
          />
        );
      case 'simulator':
        return <AttackSimulator selectedAssessment={selectedAssessment} />;
      case 'vulnerabilities':
        return (
          <VulnerabilityExplorer
            selectedAssessment={selectedAssessment}
            onNavigateToWorkbench={handleNavigateToWorkbench}
          />
        );
      case 'traces':
        return <ExecutionTraceExplorer />;
      case 'authorization':
        return <AuthorizationIntelligence />;
      case 'source-analyzer':
        return <SourceCodeAnalyzer />;
      case 'mcp-inspector':
        return <MCPSecurityInspector />;
      case 'rag-auditor':
        return <RAGSecurityAuditor />;
      case 'patch-workbench':
        return (
          <PatchWorkbench
            selectedAssessment={selectedAssessment}
            activeFindingId={workbenchFindingId}
          />
        );
      case 'reports':
        return <SecurityReports selectedAssessment={selectedAssessment} />;
      case 'settings':
        return <SettingsIntegrations />;
      default:
        return <OverviewDashboard selectedAssessment={selectedAssessment} onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070a12] text-slate-100 font-sans">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          assessments={assessments}
          selectedAssessmentId={selectedAssessmentId}
          setSelectedAssessmentId={setSelectedAssessmentId}
        />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#070a12]/95">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
};

export default App;

