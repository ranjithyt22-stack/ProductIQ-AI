import React from 'react';

export function SourceList({ files = [], urls = [], text = '', onRemoveFile, onRemoveUrl, onClearText }) {
  const hasSources = files.length > 0 || urls.length > 0 || text.trim().length > 0;

  if (!hasSources) {
    return (
      <div style={{
        padding: '16px',
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '6px',
        color: '#64748B',
        fontSize: '13px',
        textAlign: 'center'
      }}>
        No sources active. Upload a document file, add a website URL, or enter text description above.
      </div>
    );
  }

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '20px'
    }}>
      <div style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC', marginBottom: '12px' }}>
        Active Source Documents ({files.length + urls.length + (text ? 1 : 0)})
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {files.map((file, i) => (
          <div key={`file-${i}`} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            background: '#1E293B', padding: '8px 12px', borderRadius: '6px', fontSize: '13px'
          }}>
            <div>
              <span style={{ fontWeight: '600', color: '#38BDF8', marginRight: '8px' }}>[FILE]</span>
              <span style={{ color: '#F8FAFC' }}>{file.name}</span>
            </div>
            <button onClick={() => onRemoveFile(i)} style={{ background: 'transparent', border: 'none', color: '#EF4444', cursor: 'pointer', fontWeight: '600' }}>
              Remove
            </button>
          </div>
        ))}

        {urls.map((url, i) => (
          <div key={`url-${i}`} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            background: '#1E293B', padding: '8px 12px', borderRadius: '6px', fontSize: '13px'
          }}>
            <div>
              <span style={{ fontWeight: '600', color: '#818CF8', marginRight: '8px' }}>[URL]</span>
              <span style={{ color: '#F8FAFC', wordBreak: 'break-all' }}>{url}</span>
            </div>
            <button onClick={() => onRemoveUrl(i)} style={{ background: 'transparent', border: 'none', color: '#EF4444', cursor: 'pointer', fontWeight: '600' }}>
              Remove
            </button>
          </div>
        ))}

        {text.trim().length > 0 && (
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            background: '#1E293B', padding: '8px 12px', borderRadius: '6px', fontSize: '13px'
          }}>
            <div>
              <span style={{ fontWeight: '600', color: '#34D399', marginRight: '8px' }}>[TEXT]</span>
              <span style={{ color: '#F8FAFC' }}>Pasted Text ({text.trim().length} chars)</span>
            </div>
            <button onClick={onClearText} style={{ background: 'transparent', border: 'none', color: '#EF4444', cursor: 'pointer', fontWeight: '600' }}>
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
