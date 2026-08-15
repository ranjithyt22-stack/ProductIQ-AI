import React from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, FileText } from 'lucide-react';

export default function TrustReport({ product = null, readiness = null }) {
  if (!product) return null;

  const status = readiness?.status || product.commerce_readiness || 'REVIEW_REQUIRED';
  const isReady = status === 'READY_FOR_COMMERCE';
  const checks = readiness?.checks || [];
  const blockers = readiness?.blockers || [];

  return (
    <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={20} color={isReady ? '#10B981' : '#F59E0B'} />
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC', margin: 0 }}>
            Commerce Trust & Readiness Qualification Report
          </h3>
        </div>
        <span style={{
          fontSize: '11px',
          fontWeight: '800',
          padding: '4px 10px',
          borderRadius: '4px',
          fontFamily: 'monospace',
          backgroundColor: isReady ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
          color: isReady ? '#10B981' : '#F59E0B',
          border: `1px solid ${isReady ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
        }}>
          {status}
        </span>
      </div>

      <div style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '16px', lineHeight: 1.4 }}>
        {isReady
          ? 'This product satisfies all industrial commerce gating criteria: identity established, all critical attributes backed by verbatim evidence quotes, zero unresolved supplier conflicts, and passing engineering validation rules.'
          : 'This product has pending qualification requirements before it can be exported to downstream ERP/eCommerce systems.'}
      </div>

      {blockers.length > 0 && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '6px',
          padding: '12px 16px',
          marginBottom: '16px'
        }}>
          <div style={{ fontSize: '12px', fontWeight: '700', color: '#EF4444', marginBottom: '6px' }}>
            QUALIFICATION BLOCKERS
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '12px', color: '#F8FAFC' }}>
            {blockers.map((b, i) => (
              <li key={i} style={{ marginBottom: '4px' }}>{b}</li>
            ))}
          </ul>
        </div>
      )}

      {checks.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '8px' }}>
          {checks.map((c, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: '#0F172A',
              borderRadius: '6px',
              fontSize: '12px'
            }}>
              {c.passed ? <CheckCircle2 size={14} color="#10B981" /> : <XCircle size={14} color="#EF4444" />}
              <span style={{ color: '#F8FAFC' }}>{c.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
