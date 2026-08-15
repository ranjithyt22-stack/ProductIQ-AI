import React, { useState, useEffect } from 'react';
import { ProductAnalyzer } from './pages/ProductAnalyzer';
import { CatalogEngine } from './pages/CatalogEngine';
import { ReviewCenter } from './pages/ReviewCenter';
import EvaluationDashboard from './pages/EvaluationDashboard';
import Overview from './pages/Overview';
import DataQuality from './pages/DataQuality';
import AIGovernance from './pages/AIGovernance';
import ProductSearch from './pages/ProductSearch';
import SystemHealth from './pages/SystemHealth';
import AuditLog from './pages/AuditLog';

import AppSidebar from './components/AppSidebar';
import AppHeader from './components/AppHeader';
import AppStatusBar from './components/AppStatusBar';
import { apiService } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [apiHealth, setApiHealth] = useState({ status: 'checking', ollama: 'checking' });
  const [openReviewCount, setOpenReviewCount] = useState(0);
  const [globalSearchTerm, setGlobalSearchTerm] = useState('');

  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await apiService.healthCheck();
        setApiHealth(res);

        try {
          const revRes = await apiService.listReviews({ status: 'OPEN' });
          if (revRes && revRes.count !== undefined) {
            setOpenReviewCount(revRes.count);
          }
        } catch (e) {
          // ignore
        }
      } catch (err) {
        setApiHealth({ status: 'offline', ollama: 'unavailable' });
      }
    }
    checkBackend();
  }, []);

  const handleGlobalSearch = (query) => {
    setGlobalSearchTerm(query);
    setActiveTab('search');
  };

  return (
    <div className="app-shell" style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0F172A', color: '#F8FAFC' }}>
      {/* Collapsible Left Navigation */}
      <AppSidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        openReviewCount={openReviewCount}
      />

      {/* Main Content Area */}
      <div className="app-main-wrapper" style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, paddingBottom: '36px' }}>
        <AppHeader apiHealth={apiHealth} onGlobalSearch={handleGlobalSearch} />

        <main className="app-workspace-content" style={{ flex: 1, padding: '24px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
          {activeTab === 'overview' && <Overview onNavigateTab={setActiveTab} />}
          {activeTab === 'analyzer' && <ProductAnalyzer onNavigateToReview={() => setActiveTab('review')} />}
          {activeTab === 'catalog' && <CatalogEngine />}
          {activeTab === 'review' && <ReviewCenter />}
          {activeTab === 'quality' && <DataQuality onNavigateTab={setActiveTab} />}
          {activeTab === 'evaluation' && <EvaluationDashboard />}
          {activeTab === 'governance' && <AIGovernance />}
          {activeTab === 'search' && <ProductSearch initialQuery={globalSearchTerm} />}
          {activeTab === 'health' && <SystemHealth />}
          {activeTab === 'audit' && <AuditLog />}
        </main>
      </div>

      {/* Fixed Bottom Status Bar */}
      <AppStatusBar
        latency="3ms"
        model="llama3.2:3b"
        storage="SQLite Relational DB"
        version="2.5.0"
      />
    </div>
  );
}

export default App;
