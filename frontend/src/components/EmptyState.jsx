import React from 'react';
import { FileText, ArrowUpCircle, Sparkles } from 'lucide-react';

export function EmptyState({ onLoadSample }) {
  return (
    <div style={{
      background: '#0F172A',
      border: '1px dashed #334155',
      borderRadius: '8px',
      padding: '48px 24px',
      textAlign: 'center',
      color: '#64748B',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: '#1E293B',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#38BDF8'
        }}>
          <FileText size={32} />
        </div>
      </div>

      <h3 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: '700', color: '#F8FAFC' }}>
        No Product Analysis Available
      </h3>
      <p style={{ margin: '0 auto 20px auto', fontSize: '14px', lineHeight: '1.6', maxWidth: '480px', color: '#94A3B8' }}>
        Upload a product datasheet (PDF, DOCX, CSV, Excel, TXT, Image), add a webpage URL, or paste supplementary text specifications above, then click <strong>Analyze Single Product with AI</strong>.
      </p>

      {onLoadSample && (
        <button
          onClick={onLoadSample}
          style={{
            background: '#1E293B',
            border: '1px solid #334155',
            color: '#38BDF8',
            borderRadius: '6px',
            padding: '10px 18px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background 0.2s'
          }}
        >
          <Sparkles size={16} /> Load Demo Pneumatic Cylinder Sample
        </button>
      )}
    </div>
  );
}
