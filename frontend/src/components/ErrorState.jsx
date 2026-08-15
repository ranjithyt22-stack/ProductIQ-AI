import React from 'react';

export function ErrorState({ title = 'Operation Error', message, onRetry }) {
  return (
    <div style={{
      padding: '20px',
      background: '#450A0A',
      border: '1px solid #991B1B',
      borderRadius: '8px',
      color: '#FECACA',
      marginBottom: '16px'
    }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: '700', color: '#FCA5A5' }}>
        {title}
      </h4>
      <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>
        {message || 'An unexpected error occurred. Please verify input sources and try again.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '12px',
            padding: '6px 14px',
            background: '#991B1B',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '13px'
          }}
        >
          Try Again
        </button>
      )}
    </div>
  );
}
