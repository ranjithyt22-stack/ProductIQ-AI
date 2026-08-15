import React from 'react';
import { Layers, CheckCircle2, AlertCircle } from 'lucide-react';

export function CompletenessPanel({ product = {}, specifications = [], qualityScore = {} }) {
  const reqFields = [
    { key: 'product_name', label: 'Product Name', value: product.product_name },
    { key: 'manufacturer', label: 'Manufacturer', value: product.manufacturer },
    { key: 'product_code', label: 'Part / SKU Code', value: product.product_code },
    { key: 'category', label: 'Category', value: product.category },
    { key: 'description', label: 'Description', value: product.description },
  ];

  const presentReqCount = reqFields.filter(
    (f) => f.value && !['null', 'none', 'not found', ''].includes(String(f.value).trim().toLowerCase())
  ).length;

  const totalReqCount = reqFields.length;
  const reqPercentage = Math.round((presentReqCount / totalReqCount) * 100);

  const missingFields = reqFields.filter(
    (f) => !f.value || ['null', 'none', 'not found', ''].includes(String(f.value).trim().toLowerCase())
  );

  const totalSpecsCount = specifications.length;
  const completenessScore = qualityScore.completeness !== undefined ? qualityScore.completeness : reqPercentage;

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={20} color="#38BDF8" />
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
            Data Completeness & Schema Audit
          </h3>
        </div>
        <span style={{
          fontSize: '18px',
          fontWeight: '800',
          color: completenessScore >= 80 ? '#34D399' : (completenessScore >= 60 ? '#FBBF24' : '#F87171')
        }}>
          {completenessScore}% Complete
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Required Identity Fields
          </div>
          <div style={{ fontSize: '20px', fontWeight: '800', color: '#F8FAFC', marginTop: '4px' }}>
            {presentReqCount} / {totalReqCount}
          </div>
        </div>

        <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Extracted Technical Attributes
          </div>
          <div style={{ fontSize: '20px', fontWeight: '800', color: '#38BDF8', marginTop: '4px' }}>
            {totalSpecsCount} Parameters
          </div>
        </div>

        <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Evidence Backing Ratio
          </div>
          <div style={{ fontSize: '20px', fontWeight: '800', color: '#34D399', marginTop: '4px' }}>
            {qualityScore.evidence_coverage || 100}%
          </div>
        </div>
      </div>

      {/* Field checklist */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
        {reqFields.map((f, i) => {
          const isPresent = f.value && !['null', 'none', 'not found', ''].includes(String(f.value).trim().toLowerCase());
          return (
            <div
              key={i}
              style={{
                background: '#1E293B',
                padding: '8px 12px',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '12px'
              }}
            >
              <span style={{ color: '#E2E8F0' }}>{f.label}</span>
              {isPresent ? (
                <span style={{ color: '#34D399', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={14} /> FOUND
                </span>
              ) : (
                <span style={{ color: '#F87171', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <AlertCircle size={14} /> MISSING
                </span>
              )}
            </div>
          );
        })}
      </div>

      {missingFields.length > 0 && (
        <div style={{ marginTop: '12px', fontSize: '12px', color: '#F87171' }}>
          Missing critical information: {missingFields.map((m) => m.label).join(', ')}. Consider adding supplementary text or metadata hints.
        </div>
      )}
    </div>
  );
}
