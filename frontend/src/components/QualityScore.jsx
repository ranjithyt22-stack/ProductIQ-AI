import React from 'react';

export function QualityScore({ scoreObj }) {
  if (!scoreObj) return null;

  const score = scoreObj.overall_score || 0;
  const status = scoreObj.readiness_status || 'REQUIRES MANUAL REVIEW';
  const breakdown = scoreObj.score_breakdown || {};

  const getScoreColor = () => {
    if (score >= 90) return '#22C55E';
    if (score >= 70) return '#F59E0B';
    return '#EF4444';
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
            Product Quality & Commerce Readiness Score
          </h3>
          <div style={{ fontSize: '13px', color: '#94A3B8', marginTop: '2px' }}>
            Status: <span style={{ fontWeight: '700', color: getScoreColor() }}>{status}</span>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '32px', fontWeight: '800', color: getScoreColor() }}>
            {Math.round(score)} <span style={{ fontSize: '14px', color: '#64748B' }}>/ 100</span>
          </div>
        </div>
      </div>

      {breakdown && Object.keys(breakdown).length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
          {Object.entries(breakdown).map(([key, val], i) => (
            <div key={i} style={{ background: '#1E293B', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: '700' }}>
                {key.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: '#F8FAFC', marginTop: '4px' }}>
                {typeof val === 'number' ? Math.round(val) : val}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
