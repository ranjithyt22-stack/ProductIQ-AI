import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';

export function ReviewQueue({ conflicts = [], onSelectConflict }) {
  if (!conflicts || conflicts.length === 0) {
    return (
      <div style={{
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '8px',
        padding: '36px',
        textAlign: 'center',
        color: '#94A3B8'
      }}>
        <CheckCircle2 size={32} color="#34D399" style={{ margin: '0 auto 12px auto' }} />
        <h4 style={{ margin: 0, fontSize: '16px', color: '#F8FAFC', fontWeight: '700' }}>
          All Clear — No Open Conflicts
        </h4>
        <p style={{ margin: '6px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
          All cross-source specifications are verified or successfully resolved.
        </p>
      </div>
    );
  }

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return { bg: 'rgba(239, 68, 68, 0.2)', text: '#F87171', border: '#EF4444' };
      case 'HIGH':
        return { bg: 'rgba(249, 115, 22, 0.2)', text: '#FB923C', border: '#F97316' };
      case 'MEDIUM':
        return { bg: 'rgba(251, 191, 36, 0.2)', text: '#FBBF24', border: '#F59E0B' };
      default:
        return { bg: 'rgba(56, 189, 248, 0.2)', text: '#38BDF8', border: '#0284C7' };
    }
  };

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      overflowX: 'auto'
    }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #334155', color: '#94A3B8' }}>
            <th style={{ padding: '10px' }}>Product</th>
            <th style={{ padding: '10px' }}>Attribute</th>
            <th style={{ padding: '10px' }}>Conflict Type</th>
            <th style={{ padding: '10px' }}>Severity</th>
            <th style={{ padding: '10px' }}>Source A vs Source B</th>
            <th style={{ padding: '10px' }}>Confidence</th>
            <th style={{ padding: '10px' }}>Status</th>
            <th style={{ padding: '10px', textAlign: 'right' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {conflicts.map((c, i) => {
            const sevStyle = getSeverityBadge(c.severity);
            const valA = `${c.value_a || (c.source_a && c.source_a.value) || ''} ${c.unit_a || (c.source_a && c.source_a.unit) || ''}`.strip();
            const valB = `${c.value_b || (c.source_b && c.source_b.value) || ''} ${c.unit_b || (c.source_b && c.source_b.unit) || ''}`.strip();

            return (
              <tr
                key={c.conflict_id || i}
                onClick={() => onSelectConflict(c)}
                style={{
                  borderBottom: '1px solid #1E293B',
                  color: '#F8FAFC',
                  cursor: 'pointer',
                  transition: 'background 0.2s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#1E293B'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '12px 10px', fontWeight: '700', color: '#38BDF8' }}>
                  {c.product_id}
                </td>
                <td style={{ padding: '12px 10px', fontWeight: '700' }}>
                  {c.attribute_name}
                </td>
                <td style={{ padding: '12px 10px', color: '#94A3B8' }}>
                  {c.conflict_type}
                </td>
                <td style={{ padding: '12px 10px' }}>
                  <span style={{
                    background: sevStyle.bg,
                    color: sevStyle.text,
                    border: `1px solid ${sevStyle.border}`,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '800'
                  }}>
                    {c.severity}
                  </span>
                </td>
                <td style={{ padding: '12px 10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                    <span style={{ color: '#38BDF8', fontWeight: '600' }}>{valA || 'Val A'}</span>
                    <span style={{ color: '#64748B' }}>≠</span>
                    <span style={{ color: '#A78BFA', fontWeight: '600' }}>{valB || 'Val B'}</span>
                  </div>
                </td>
                <td style={{ padding: '12px 10px', fontWeight: '700', color: c.confidence >= 80 ? '#34D399' : '#FBBF24' }}>
                  {c.confidence}%
                </td>
                <td style={{ padding: '12px 10px' }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '700',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: c.status === 'RESOLVED' ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: c.status === 'RESOLVED' ? '#34D399' : '#F87171'
                  }}>
                    {c.status}
                  </span>
                </td>
                <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectConflict(c);
                    }}
                    style={{
                      background: '#2563EB',
                      border: 'none',
                      color: '#FFF',
                      padding: '6px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: '700',
                      cursor: 'pointer'
                    }}
                  >
                    {c.status === 'RESOLVED' ? 'View Details' : 'Resolve Conflict'}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
