import React from 'react';
import { GitCompare, AlertTriangle, CheckCircle } from 'lucide-react';

export function SourceComparison({ rawSources = [], validations = [], specifications = [] }) {
  // Extract conflict warnings from validations or specs
  const conflictValidations = validations.filter(
    (v) => (v.rule || '').toLowerCase().includes('conflict') || v.severity === 'HIGH' || v.status === 'WARNING' || v.status === 'REVIEW'
  );

  const hasMultipleSources = rawSources && rawSources.length > 1;

  if (!hasMultipleSources && conflictValidations.length === 0) {
    return null;
  }

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <GitCompare size={20} color="#38BDF8" />
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
          Multi-Source Provenance & Conflict Analysis
        </h3>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '8px' }}>
          Active Ingested Sources ({rawSources.length})
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {rawSources.map((src, i) => (
            <div
              key={i}
              style={{
                background: '#1E293B',
                border: '1px solid #334155',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '13px',
                color: '#F8FAFC',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span style={{
                fontSize: '11px',
                background: '#0F172A',
                padding: '2px 6px',
                borderRadius: '4px',
                color: '#60A5FA',
                fontWeight: '700',
                textTransform: 'uppercase'
              }}>
                {src.source_type || 'SOURCE'} {i + 1}
              </span>
              <span>{src.filename || src.source_name || 'Document'}</span>
            </div>
          ))}
        </div>
      </div>

      {conflictValidations.length > 0 ? (
        <div>
          <div style={{ fontSize: '12px', color: '#F59E0B', fontWeight: '700', textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={14} color="#F59E0B" />
            Detected Source Discrepancies ({conflictValidations.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {conflictValidations.map((c, i) => (
              <div
                key={i}
                style={{
                  background: '#1E293B',
                  borderLeft: '4px solid #F59E0B',
                  borderRadius: '4px',
                  padding: '12px 14px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontSize: '13px', fontWeight: '700', color: '#F8FAFC' }}>
                    Field: {c.field || 'Attribute'}
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '700',
                    color: '#F59E0B',
                    background: '#0F172A',
                    padding: '2px 8px',
                    borderRadius: '4px'
                  }}>
                    STATUS: REQUIRES MANUAL REVIEW
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#E2E8F0', lineHeight: '1.4' }}>
                  {c.message}
                </div>
                <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '6px' }}>
                  Recommended Action: Verify with primary manufacturer datasheet or apply Human Review override.
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{
          background: '#1E293B',
          border: '1px solid #10B981',
          borderRadius: '6px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle size={16} color="#10B981" />
          <span style={{ fontSize: '13px', color: '#34D399', fontWeight: '600' }}>
            No cross-source conflicts detected. All extracted values agree across active inputs.
          </span>
        </div>
      )}
    </div>
  );
}
