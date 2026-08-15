import React from 'react';

export function StatusBadge({ status, type = 'readiness' }) {
  const getBadgeStyle = () => {
    const uppercaseStatus = (status || '').toUpperCase();
    if (uppercaseStatus === 'READY FOR COMMERCE' || uppercaseStatus === 'PASS' || uppercaseStatus === 'HUMAN_VERIFIED') {
      return { background: '#DCFCE7', color: '#166534', border: '1px solid #86EFAC' };
    }
    if (uppercaseStatus === 'REVIEW RECOMMENDED' || uppercaseStatus === 'WARNING' || uppercaseStatus === 'REVIEW_REQUIRED') {
      return { background: '#FEF3C7', color: '#92400E', border: '1px solid #FDE68A' };
    }
    if (uppercaseStatus === 'REQUIRES MANUAL REVIEW' || uppercaseStatus === 'FAIL' || uppercaseStatus === 'FAILED') {
      return { background: '#FEE2E2', color: '#991B1B', border: '1px solid #FCA5A5' };
    }
    return { background: '#F1F5F9', color: '#475569', border: '1px solid #CBD5E1' };
  };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '4px 10px',
        borderRadius: '6px',
        fontSize: '12px',
        fontWeight: '700',
        letterSpacing: '0.5px',
        ...getBadgeStyle(),
      }}
    >
      {status || 'UNKNOWN'}
    </span>
  );
}
