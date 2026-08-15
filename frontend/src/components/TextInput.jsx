import React from 'react';

export function TextInput({ value, onChange }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', color: '#E2E8F0', fontSize: '14px' }}>
        Supplementary Product Specifications / Text
      </label>
      <textarea
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste supplementary product specifications, operating parameters, or technical notes here..."
        style={{
          width: '100%',
          background: '#0F172A',
          border: '1px solid #334155',
          borderRadius: '6px',
          padding: '10px 12px',
          color: '#F8FAFC',
          fontSize: '14px',
          fontFamily: 'sans-serif',
          resize: 'vertical',
          boxSizing: 'border-box'
        }}
      />
    </div>
  );
}
