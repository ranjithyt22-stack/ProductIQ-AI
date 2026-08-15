import React from 'react';
import { StatusBadge } from './StatusBadge';
import { ShieldCheck, Info } from 'lucide-react';

export function Specifications({ specifications = [], onSelectAttribute, selectedAttributeName }) {
  if (!specifications || specifications.length === 0) {
    return (
      <div style={{ padding: '20px', background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#94A3B8', textAlign: 'center' }}>
        No specifications extracted yet.
      </div>
    );
  }

  const getConfColor = (score) => {
    if (score >= 90) return '#34D399';
    if (score >= 70) return '#38BDF8';
    if (score >= 50) return '#FBBF24';
    return '#F87171';
  };

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
            Technical Specifications ({specifications.length})
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#94A3B8' }}>
            Click any specification row to open deep Attribute Intelligence & Explainability.
          </p>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #334155', color: '#94A3B8' }}>
              <th style={{ padding: '10px' }}>Attribute</th>
              <th style={{ padding: '10px' }}>Value</th>
              <th style={{ padding: '10px' }}>Unit</th>
              <th style={{ padding: '10px' }}>Confidence</th>
              <th style={{ padding: '10px' }}>Source</th>
              <th style={{ padding: '10px' }}>Page</th>
              <th style={{ padding: '10px' }}>Evidence</th>
              <th style={{ padding: '10px' }}>Validation</th>
              <th style={{ padding: '10px' }}>Review Status</th>
            </tr>
          </thead>
          <tbody>
            {specifications.map((spec, i) => {
              const isSelected = selectedAttributeName && selectedAttributeName.toLowerCase() === spec.name.toLowerCase();
              const conf = Math.round(spec.confidence || 0);

              return (
                <tr
                  key={i}
                  onClick={() => onSelectAttribute && onSelectAttribute(spec)}
                  style={{
                    borderBottom: '1px solid #1E293B',
                    color: '#F8FAFC',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                    transition: 'background 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.background = '#1E293B';
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <td style={{ padding: '10px', fontWeight: '600' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {spec.name}
                      {spec.review_required && (
                        <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#F87171', display: 'inline-block' }} />
                      )}
                    </div>
                  </td>
                  <td style={{ padding: '10px', color: '#38BDF8', fontWeight: '600' }}>
                    {spec.value || '—'}
                  </td>
                  <td style={{ padding: '10px', color: '#94A3B8' }}>
                    {spec.unit || '—'}
                  </td>
                  <td style={{ padding: '10px' }}>
                    <span style={{ fontWeight: '700', color: getConfColor(conf) }}>
                      {conf}%
                    </span>
                  </td>
                  <td style={{ padding: '10px', color: '#94A3B8', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {spec.source_name || 'Datasheet'}
                  </td>
                  <td style={{ padding: '10px', color: '#94A3B8' }}>
                    {spec.page ? `P.${spec.page}` : '—'}
                  </td>
                  <td style={{ padding: '10px' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: '600',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: spec.match_status === 'VERIFIED' ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      color: spec.match_status === 'VERIFIED' ? '#34D399' : '#F87171'
                    }}>
                      {spec.match_status || 'VERIFIED'}
                    </span>
                  </td>
                  <td style={{ padding: '10px' }}>
                    <StatusBadge status={spec.status || 'PASS'} />
                  </td>
                  <td style={{ padding: '10px' }}>
                    <StatusBadge status={spec.review_status || 'ai_extracted'} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
