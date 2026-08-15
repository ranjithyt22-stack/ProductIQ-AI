import React from 'react';
import { History, CheckCircle2, User, Clock, ArrowRight } from 'lucide-react';

export function ReviewHistory({ audits = [] }) {
  if (!audits || audits.length === 0) {
    return (
      <div style={{
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '8px',
        padding: '30px',
        textAlign: 'center',
        color: '#94A3B8'
      }}>
        No review resolution history recorded yet. All resolutions are recorded immutably in this audit trail.
      </div>
    );
  }

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <History size={18} color="#38BDF8" />
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: '#F8FAFC' }}>
          Immutable Resolution Audit Trail ({audits.length})
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {audits.map((a, i) => (
          <div
            key={i}
            style={{
              background: '#1E293B',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '16px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontWeight: '700', color: '#F8FAFC', fontSize: '14px' }}>
                  {a.attribute_name}
                </span>
                <span style={{
                  fontSize: '11px',
                  fontWeight: '700',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'rgba(56, 189, 248, 0.15)',
                  color: '#38BDF8'
                }}>
                  {a.action}
                </span>
                <span style={{ fontSize: '12px', color: '#94A3B8' }}>
                  Product: <strong style={{ color: '#E2E8F0' }}>{a.product_id}</strong>
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#94A3B8' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <User size={13} color="#94A3B8" />
                  {a.reviewer || 'Reviewer 1'}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Clock size={13} color="#94A3B8" />
                  {a.timestamp ? new Date(a.timestamp).toLocaleString() : 'Recent'}
                </span>
              </div>
            </div>

            {/* Value Transformation */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', margin: '8px 0', background: '#0F172A', padding: '10px 14px', borderRadius: '4px' }}>
              <span style={{ color: '#94A3B8' }}>Previous Value:</span>
              <span style={{ color: '#F87171', fontWeight: '600' }}>{a.old_value || 'None'}</span>
              <ArrowRight size={14} color="#64748B" />
              <span style={{ color: '#94A3B8' }}>Resolved Value:</span>
              <span style={{ color: '#34D399', fontWeight: '700' }}>{a.new_value}</span>
            </div>

            {/* Reason & Notes */}
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '6px' }}>
              <div><strong>Reason:</strong> {a.reason || 'Human engineer verification'}</div>
              {a.notes && <div style={{ marginTop: '2px' }}><strong>Notes:</strong> {a.notes}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
