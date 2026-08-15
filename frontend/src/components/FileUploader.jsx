import React, { useRef } from 'react';

export function FileUploader({ files, onFilesSelected, onRemoveFile }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = Array.from(e.target.files);
      onFilesSelected(selected);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const dropped = Array.from(e.dataTransfer.files);
      onFilesSelected(dropped);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', color: '#E2E8F0', fontSize: '14px' }}>
        Product Document / Datasheet Upload
      </label>
      
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
        style={{
          border: '2px dashed #334155',
          borderRadius: '8px',
          padding: '24px',
          textAlign: 'center',
          background: '#0F172A',
          cursor: 'pointer',
          transition: 'border-color 0.2s',
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept=".pdf,.docx,.csv,.xlsx,.xls,.txt,.md,.png,.jpg,.jpeg"
          style={{ display: 'none' }}
        />
        <div style={{ fontSize: '14px', color: '#94A3B8', fontWeight: '500' }}>
          Drag and drop product files here, or click to browse
        </div>
        <div style={{ fontSize: '12px', color: '#64748B', marginTop: '4px' }}>
          Supported: PDF, DOCX, CSV, XLSX, TXT, MD, PNG, JPG (Max 50MB)
        </div>
      </div>

      {files && files.length > 0 && (
        <div style={{ marginTop: '12px' }}>
          {files.map((file, idx) => (
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
              <div>
                <span style={{ fontWeight: '600', color: '#F8FAFC' }}>{file.name}</span>
                <span style={{ marginLeft: '10px', color: '#94A3B8', fontSize: '12px' }}>
                  ({formatFileSize(file.size)})
                </span>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveFile(idx);
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#EF4444',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '13px',
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
