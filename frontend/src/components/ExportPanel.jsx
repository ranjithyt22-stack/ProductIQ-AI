import React from 'react';
import { apiService } from '../services/api';

export function ExportPanel({ productId, record }) {
  if (!productId || !record) return null;

  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(record, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `${productId}_intelligence.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleDownloadCsv = () => {
    const specs = record.specifications || [];
    let csvContent = "attribute,value,unit,confidence,page,status,review_status\n";
    specs.forEach(s => {
      csvContent += `"${s.name}","${s.value}","${s.unit || ''}","${s.confidence || 0}","${s.page || 1}","${s.status || 'PASS'}","${s.review_status || 'ai_extracted'}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", url);
    downloadAnchor.setAttribute("download", `${productId}_specifications.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 12px 0', fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
        Export & Intelligence Downloads
      </h3>
      <p style={{ margin: '0 0 16px 0', fontSize: '13px', color: '#94A3B8' }}>
        Download full intelligence record in JSON or tabular specifications in CSV format.
      </p>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={handleDownloadJson}
          style={{
            background: '#1E293B',
            border: '1px solid #334155',
            color: '#38BDF8',
            borderRadius: '6px',
            padding: '10px 18px',
            fontWeight: '700',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          Download Full Intelligence JSON
        </button>

        <button
          onClick={handleDownloadCsv}
          style={{
            background: '#1E293B',
            border: '1px solid #334155',
            color: '#34D399',
            borderRadius: '6px',
            padding: '10px 18px',
            fontWeight: '700',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          Download Attributes CSV
        </button>
      </div>

      <div style={{ marginTop: '16px' }}>
        <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
          Raw Intelligence JSON Output
        </div>
        <pre style={{
          background: '#020617',
          border: '1px solid #1E293B',
          borderRadius: '6px',
          padding: '12px',
          color: '#38BDF8',
          fontSize: '12px',
          maxHeight: '260px',
          overflowY: 'auto'
        }}>
          {JSON.stringify(record, null, 2)}
        </pre>
      </div>
    </div>
  );
}
