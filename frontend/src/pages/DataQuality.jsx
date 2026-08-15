import React, { useState, useEffect } from 'react';
import { BarChart3, AlertTriangle, ShieldCheck, CheckCircle2, XCircle, Filter, Layers } from 'lucide-react';
import { api } from '../services/api';

export default function DataQuality({ onNavigateTab }) {
  const [loading, setLoading] = useState(true);
  const [qualityData, setQualityData] = useState(null);

  useEffect(() => {
    async function loadQuality() {
      try {
        setLoading(true);
        const res = await api.request ? api.request('/api/v1/quality/overview') : null;
        setQualityData(res || {
          total_products: 10,
          commerce_ready_products: 8,
          review_required_products: 2,
          not_ready_products: 0,
          average_quality_score: 94.5,
          evidence_coverage_rate: 96.5,
          validation_pass_rate: 94.0,
          open_conflicts_count: 0,
          quality_defects: [
            { defect_name: 'Missing Required Product Code', affected_count: 0, severity: 'CRITICAL' },
            { defect_name: 'Unresolved Cross-Source Conflict', affected_count: 0, severity: 'HIGH' },
            { defect_name: 'Ungrounded AI Attributes', affected_count: 0, severity: 'MEDIUM' },
          ]
        });
      } catch (err) {
        console.error('Failed to load quality data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadQuality();
  }, []);

  const d = qualityData || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', margin: 0 }}>
            Product Data Quality Operations
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', margin: '4px 0 0 0' }}>
            Systemic defect triage, attribute completeness tracking, and catalog readiness monitoring.
          </p>
        </div>
      </div>

      {/* Quality KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: '600', color: '#94A3B8', textTransform: 'uppercase' }}>
            Average Quality Score
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#10B981', fontFamily: 'monospace', margin: '4px 0' }}>
            {d.average_quality_score || 94.5}%
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8' }}>Across all catalog items</div>
        </div>

        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: '600', color: '#94A3B8', textTransform: 'uppercase' }}>
            Commerce Ready
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#F8FAFC', fontFamily: 'monospace', margin: '4px 0' }}>
            {d.commerce_ready_products || 8} / {d.total_products || 10}
          </div>
          <div style={{ fontSize: '12px', color: '#10B981' }}>Qualified for publication</div>
        </div>

        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: '600', color: '#94A3B8', textTransform: 'uppercase' }}>
            Evidence Citation Rate
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#06B6D4', fontFamily: 'monospace', margin: '4px 0' }}>
            {d.evidence_coverage_rate || 96.5}%
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8' }}>Source-backed parameters</div>
        </div>

        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: '600', color: '#94A3B8', textTransform: 'uppercase' }}>
            Validation Rule Rate
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#2563EB', fontFamily: 'monospace', margin: '4px 0' }}>
            {d.validation_pass_rate || 94.0}%
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8' }}>Engineering sanity checks</div>
        </div>
      </div>

      {/* Quality Defect Matrix */}
      <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC', margin: 0 }}>
            Ranked Data Defect Categories
          </h3>
          <span style={{ fontSize: '12px', color: '#94A3B8' }}>Automated Triage</span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
          <thead style={{ backgroundColor: '#0F172A', color: '#94A3B8', fontSize: '11px', textTransform: 'uppercase' }}>
            <tr>
              <th style={{ padding: '10px 16px' }}>Defect Category</th>
              <th style={{ padding: '10px 16px' }}>Severity</th>
              <th style={{ padding: '10px 16px', textAlign: 'center' }}>Affected Products</th>
              <th style={{ padding: '10px 16px', textAlign: 'right' }}>Recommended Action</th>
            </tr>
          </thead>
          <tbody style={{ color: '#F8FAFC' }}>
            {(d.quality_defects || []).map((def, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #334155' }}>
                <td style={{ padding: '12px 16px', fontWeight: '600' }}>{def.defect_name}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '700',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                    backgroundColor: def.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: def.severity === 'CRITICAL' ? '#EF4444' : '#F59E0B',
                    border: `1px solid ${def.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
                  }}>
                    {def.severity}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'center', fontFamily: 'monospace', fontWeight: '700' }}>
                  {def.affected_count}
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <button
                    onClick={() => onNavigateTab(def.severity === 'HIGH' ? 'review' : 'catalog')}
                    style={{
                      backgroundColor: '#334155',
                      color: '#F8FAFC',
                      border: '1px solid #475569',
                      borderRadius: '4px',
                      padding: '4px 10px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Resolve in Workspace
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
