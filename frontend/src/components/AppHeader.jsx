import React, { useState } from 'react';
import { Search, Activity, CheckCircle2, AlertCircle, Database, Cpu } from 'lucide-react';

export default function AppHeader({ apiHealth = {}, onGlobalSearch = null }) {
  const [searchVal, setSearchVal] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (onGlobalSearch && searchVal.trim()) {
      onGlobalSearch(searchVal.trim());
    }
  };

  const isBackendOk = apiHealth.status === 'ok' || apiHealth.status === 'healthy';
  const isOllamaOk = apiHealth.ollama === 'connected' || apiHealth.ollama === 'available';

  return (
    <header style={{
      height: '60px',
      backgroundColor: '#1E293B',
      borderBottom: '1px solid #334155',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 30
    }}>
      {/* Global Quick Search */}
      <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', width: '360px', position: 'relative' }}>
        <Search size={16} style={{ position: 'absolute', left: '12px', color: '#64748B' }} />
        <input
          type="text"
          placeholder="Search products, SKUs, specifications..."
          value={searchVal}
          onChange={(e) => setSearchVal(e.target.value)}
          style={{
            width: '100%',
            backgroundColor: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '7px 12px 7px 36px',
            fontSize: '12px',
            color: '#F8FAFC',
            outline: 'none'
          }}
        />
      </form>

      {/* Real-time Telemetry & Environment Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', fontFamily: 'monospace' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '4px',
            backgroundColor: isBackendOk ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            color: isBackendOk ? '#10B981' : '#EF4444',
            border: `1px solid ${isBackendOk ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
          }}>
            <Database size={12} />
            Backend: {isBackendOk ? 'Connected' : 'Offline'}
          </span>

          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '4px',
            backgroundColor: isOllamaOk ? 'rgba(6, 182, 212, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            color: isOllamaOk ? '#06B6D4' : '#F59E0B',
            border: `1px solid ${isOllamaOk ? 'rgba(6, 182, 212, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
          }}>
            <Cpu size={12} />
            AI Engine: {isOllamaOk ? 'Ollama' : 'Unavailable'}
          </span>

          <span style={{
            padding: '3px 8px',
            borderRadius: '4px',
            backgroundColor: '#334155',
            color: '#94A3B8'
          }}>
            Env: Local
          </span>
        </div>
      </div>
    </header>
  );
}
