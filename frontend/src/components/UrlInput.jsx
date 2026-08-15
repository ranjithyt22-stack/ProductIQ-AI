import React, { useState } from 'react';

export function UrlInput({ urls, onAddUrl, onRemoveUrl }) {
  const [inputVal, setInputVal] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleAdd = () => {
    const clean = inputVal.trim();
    if (!clean) return;

    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      setErrorMsg('URL must start with http:// or https://');
      return;
    }

    if (urls.includes(clean)) {
      setErrorMsg('This URL has already been added.');
      return;
    }

    setErrorMsg('');
    onAddUrl(clean);
    setInputVal('');
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', color: '#E2E8F0', fontSize: '14px' }}>
        Product Webpage URL(s)
      </label>
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={inputVal}
          onChange={(e) => {
            setInputVal(e.target.value);
            if (errorMsg) setErrorMsg('');
          }}
          placeholder="https://example.com/products/industrial-valve"
          style={{
            flex: 1,
            background: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '8px 12px',
            color: '#F8FAFC',
            fontSize: '14px',
          }}
        />
        <button
          type="button"
          onClick={handleAdd}
          style={{
            background: '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '13px',
          }}
        >
          Add URL
        </button>
      </div>

      {errorMsg && (
        <div style={{ color: '#FCA5A5', fontSize: '12px', marginTop: '4px' }}>{errorMsg}</div>
      )}

      {urls && urls.length > 0 && (
        <div style={{ marginTop: '10px' }}>
          {urls.map((url, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: '#1E293B',
                padding: '8px 12px',
                borderRadius: '6px',
                marginBottom: '6px',
                fontSize: '13px',
              }}
            >
              <span style={{ color: '#60A5FA', wordBreak: 'break-all' }}>{url}</span>
              <button
                type="button"
                onClick={() => onRemoveUrl(idx)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#EF4444',
                  cursor: 'pointer',
                  fontWeight: '600',
                  marginLeft: '12px',
                }}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
