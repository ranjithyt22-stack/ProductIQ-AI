import React from 'react';
import { StatusBadge } from './StatusBadge';

export function ValidationPanel({ validationResults = [] }) {
  if (!validationResults || validationResults.length === 0) {
    return (
      <div style={{ padding: '20px', background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#94A3B8', textAlign: 'center' }}>
        No validation results recorded.
      </div>
    );
  }

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
        Validation & Consistency Check ({validationResults.length} Rules Executed)
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {validationResults.map((val, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              background: '#1E293B',
              padding: '12px 16px',
              borderRadius: '6px',
              borderLeft: `4px solid ${
                val.status === 'PASS' ? '#22C55E' : (val.status === 'WARNING' ? '#F59E0B' : '#EF4444')
              }`
            }}
          >
            <div>
              <div style={{ fontWeight: '700', color: '#F8FAFC', fontSize: '14px' }}>
                {val.rule || 'Rule Check'} {val.field ? `(${val.field})` : ''}
              </div>
              <div style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
                {val.message}
              </div>
            </div>
            <StatusBadge status={val.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
