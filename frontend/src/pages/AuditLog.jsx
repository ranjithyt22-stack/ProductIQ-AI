import React, { useState, useEffect } from 'react';
import { History, Shield, Filter } from 'lucide-react';
import { api } from '../services/api';

export default function AuditLog() {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAudits() {
      try {
        setLoading(true);
        const res = await (api.getReviewAudits ? api.getReviewAudits() : null);
        if (res && res.audits) {
          setAudits(res.audits);
        }
      } catch (err) {
        console.error('Failed to load audit logs:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAudits();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', margin: 0 }}>
          Immutable Human Review Audit Log
        </h1>
        <p style={{ fontSize: '13px', color: '#94A3B8', margin: '4px 0 0 0' }}>
          Cryptographically recorded provenance of all human parameter overrides, conflict resolutions, and version creations.
        </p>
      </div>

      <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #334155', fontSize: '12px', color: '#94A3B8' }}>
          Total Logged Actions: {audits.length}
        </div>

        {audits.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead style={{ backgroundColor: '#0F172A', color: '#94A3B8', fontSize: '11px', textTransform: 'uppercase' }}>
              <tr>
                <th style={{ padding: '10px 16px' }}>Timestamp</th>
                <th style={{ padding: '10px 16px' }}>Reviewer</th>
                <th style={{ padding: '10px 16px' }}>Action</th>
                <th style={{ padding: '10px 16px' }}>Product / Attribute</th>
                <th style={{ padding: '10px 16px' }}>Previous Value</th>
                <th style={{ padding: '10px 16px' }}>Resolved Value</th>
                <th style={{ padding: '10px 16px' }}>Reason</th>
              </tr>
            </thead>
            <tbody style={{ color: '#F8FAFC' }}>
              {audits.map((a, i) => (
                <tr key={a.audit_id || i} style={{ borderBottom: '1px solid #334155' }}>
                  <td style={{ padding: '12px 16px', fontFamily: 'monospace', color: '#94A3B8', fontSize: '11px' }}>
                    {a.created_at ? new Date(a.created_at).toLocaleString() : 'N/A'}
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: '600' }}>{a.reviewer || 'Engineer'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: '700',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(37, 99, 235, 0.15)',
                      color: '#2563EB',
                      fontFamily: 'monospace'
                    }}>
                      {a.action}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>{a.attribute_name}</td>
                  <td style={{ padding: '12px 16px', color: '#EF4444', fontFamily: 'monospace' }}>{a.previous_value || '-'}</td>
                  <td style={{ padding: '12px 16px', color: '#10B981', fontFamily: 'monospace' }}>{a.new_value || '-'}</td>
                  <td style={{ padding: '12px 16px', color: '#94A3B8', fontSize: '12px' }}>{a.reason || 'Manual Verification'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 16px', color: '#64748B', fontSize: '13px' }}>
            No audit records yet. All actions in Review Center are automatically logged here.
          </div>
        )}
      </div>
    </div>
  );
}
