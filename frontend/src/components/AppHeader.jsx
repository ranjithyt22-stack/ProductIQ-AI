import React, { useState } from 'react';
import { Search, Database, Cpu } from 'lucide-react';

export default function AppHeader({
  apiHealth = {},
  onGlobalSearch = null
}) {
  const [searchVal, setSearchVal] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();

    if (onGlobalSearch && searchVal.trim()) {
      onGlobalSearch(searchVal.trim());
    }
  };

  // Backend is connected when the API is responding.
  // "degraded" still means the backend itself is reachable.
  const isBackendOk =
    apiHealth.status === 'ok' ||
    apiHealth.status === 'healthy' ||
    apiHealth.status === 'degraded';

  // Gemini AI status comes from the backend health response.
  // Example:
  // {
  //   "ai": "connected",
  //   "provider": "Gemini",
  //   "model": "gemini-3.5-flash-lite"
  // }
  const isAiOk =
    apiHealth.ai === 'connected' ||
    apiHealth.ai === 'available';

  // Get provider/model from backend.
  const provider = apiHealth.provider || 'Gemini';
  const model = apiHealth.model || 'gemini-3.5-flash-lite';

  // Vite automatically sets PROD for production builds.
  const environment = import.meta.env.PROD
    ? 'Production'
    : 'Local';

  return (
    <header
      style={{
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
      }}
    >
      {/* Global Quick Search */}
      <form
        onSubmit={handleSearchSubmit}
        style={{
          display: 'flex',
          alignItems: 'center',
          width: '360px',
          position: 'relative'
        }}
      >
        <Search
          size={16}
          style={{
            position: 'absolute',
            left: '12px',
            color: '#64748B'
          }}
        />

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
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            fontFamily: 'monospace'
          }}
        >
          {/* Backend Status */}
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: '4px',
              backgroundColor: isBackendOk
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(239, 68, 68, 0.1)',
              color: isBackendOk
                ? '#10B981'
                : '#EF4444',
              border: `1px solid ${
                isBackendOk
                  ? 'rgba(16, 185, 129, 0.3)'
                  : 'rgba(239, 68, 68, 0.3)'
              }`
            }}
          >
            <Database size={12} />

            Backend:{' '}
            {isBackendOk
              ? 'Connected'
              : 'Offline'}
          </span>

          {/* Gemini AI Status */}
          <span
            title={`Provider: ${provider} | Model: ${model}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: '4px',
              backgroundColor: isAiOk
                ? 'rgba(6, 182, 212, 0.1)'
                : 'rgba(245, 158, 11, 0.1)',
              color: isAiOk
                ? '#06B6D4'
                : '#F59E0B',
              border: `1px solid ${
                isAiOk
                  ? 'rgba(6, 182, 212, 0.3)'
                  : 'rgba(245, 158, 11, 0.3)'
              }`
            }}
          >
            <Cpu size={12} />

            AI Engine:{' '}
            {isAiOk
              ? provider
              : 'Unavailable'}
          </span>

          {/* Environment */}
          <span
            style={{
              padding: '3px 8px',
              borderRadius: '4px',
              backgroundColor: '#334155',
              color: '#94A3B8'
            }}
          >
            Env: {environment}
          </span>
        </div>
      </div>
    </header>
  );
}
