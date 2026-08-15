import React from 'react';

export function LoadingState({ message = 'Analyzing product intelligence...' }) {
  return (
    <div style={{
      padding: '32px',
      textAlign: 'center',
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      color: '#94A3B8'
    }}>
      <div className="spinner" style={{
        display: 'inline-block',
        width: '32px',
        height: '32px',
        border: '3px solid #3B82F6',
        borderTopColor: 'transparent',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '16px'
      }} />
      <div style={{ fontSize: '15px', fontWeight: '600', color: '#F8FAFC' }}>{message}</div>
      <div style={{ fontSize: '13px', marginTop: '6px', color: '#64748B' }}>
        Executing local extraction, normalization, and validation rules
      </div>
    </div>
  );
}
