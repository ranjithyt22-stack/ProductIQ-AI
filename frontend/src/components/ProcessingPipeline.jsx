import React from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export function ProcessingPipeline({ isProcessing = false, isCompleted = true }) {
  const steps = [
    { name: 'Source Ingestion', description: 'Multi-source document and URL parsing' },
    { name: 'Content Extraction', description: 'Layout-aware text and tabular extraction' },
    { name: 'Product Identification', description: 'Brand, SKU, and model parsing' },
    { name: 'Attribute Extraction', description: 'Technical parameter identification' },
    { name: 'Normalization', description: 'Unit standardization and formatting' },
    { name: 'Validation', description: 'Rule consistency and range checks' },
    { name: 'Evidence Mapping', description: 'Verbatim text source isolation' },
    { name: 'AI Enrichment', description: 'Taxonomy and search term generation' },
    { name: 'Quality Scoring', description: 'Multi-dimensional readiness scoring' },
    { name: 'Commerce Readiness', description: 'Catalog-ready payload assembly' },
  ];

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: '#F8FAFC' }}>
          Intelligence Processing Pipeline
        </h3>
        <span style={{
          fontSize: '12px',
          fontWeight: '700',
          color: isProcessing ? '#38BDF8' : (isCompleted ? '#34D399' : '#94A3B8'),
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {isProcessing ? 'Processing in progress' : (isCompleted ? 'Pipeline Complete (10/10)' : 'Standby')}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '10px'
      }}>
        {steps.map((step, idx) => {
          const stepDone = isCompleted && !isProcessing;
          const stepActive = isProcessing && idx <= 4;

          return (
            <div
              key={idx}
              style={{
                background: '#1E293B',
                border: `1px solid ${stepDone ? '#10B981' : (stepActive ? '#3B82F6' : '#334155')}`,
                borderRadius: '6px',
                padding: '10px 12px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px'
              }}
            >
              <div style={{ marginTop: '2px' }}>
                {stepDone ? (
                  <CheckCircle2 size={16} color="#10B981" />
                ) : stepActive ? (
                  <Loader2 size={16} color="#3B82F6" style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <Circle size={16} color="#64748B" />
                )}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#F8FAFC' }}>
                  {idx + 1}. {step.name}
                </div>
                <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px', lineHeight: '1.3' }}>
                  {step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
