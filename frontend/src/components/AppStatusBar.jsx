import React from 'react';
import { Terminal, Shield, Database, Cpu } from 'lucide-react';

export default function AppStatusBar({ latency = '3ms', model = 'llama3.2:3b', storage = 'SQLite Relational', version = '2.5.0' }) {
  return (
    <footer style={{
      height: '30px',
      backgroundColor: '#0F172A',
      borderTop: '1px solid #1E293B',
      padding: '0 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '11px',
      color: '#64748B',
      fontFamily: 'monospace',
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Terminal size={12} color="#06B6D4" /> ProductIQ Enterprise
        </span>
        <span>Storage: {storage}</span>
        <span>Active Model: {model}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span>API Latency: {latency}</span>
        <span style={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Shield size={12} /> Local Zero-Exfiltration
        </span>
        <span>Build: v{version}</span>
      </div>
    </footer>
  );
}
