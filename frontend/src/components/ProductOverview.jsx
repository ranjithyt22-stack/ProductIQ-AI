import React from 'react';
import { ShieldCheck, Sparkles, Building2, Tag, Box, FileText } from 'lucide-react';

export function ProductOverview({ product = {}, enrichment = {} }) {
  if (!product) return null;

  const {
    manufacturer = '—',
    product_name = '—',
    product_code = '—',
    category = 'Industrial Equipment',
    description = 'No description provided.',
  } = product;

  const categoryPath = enrichment && enrichment.category_path && enrichment.category_path.length > 0
    ? enrichment.category_path.join(' > ')
    : category;

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '24px',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
        Product Overview & Metadata Architecture
      </h3>

      {/* SECTION 1: Source-Backed Information */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: '#34D399',
          fontWeight: '700',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          marginBottom: '12px'
        }}>
          <ShieldCheck size={16} />
          Source-Backed Extraction (Directly Verified from Ingested Sources)
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px'
        }}>
          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Box size={12} color="#60A5FA" />
              Product Name
            </div>
            <div style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC', marginTop: '4px' }}>
              {product_name}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Building2 size={12} color="#60A5FA" />
              Manufacturer / Brand
            </div>
            <div style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC', marginTop: '4px' }}>
              {manufacturer}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Tag size={12} color="#60A5FA" />
              Part / SKU Code
            </div>
            <div style={{ fontSize: '15px', fontWeight: '700', color: '#60A5FA', marginTop: '4px' }}>
              {product_code}
            </div>
          </div>
        </div>

        <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155', marginTop: '12px' }}>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <FileText size={12} color="#60A5FA" />
            Extracted Product Description
          </div>
          <div style={{ fontSize: '13px', color: '#E2E8F0', lineHeight: '1.5' }}>
            {description}
          </div>
        </div>
      </div>

      {/* SECTION 2: AI-Generated / Enriched Information */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: '#A78BFA',
          fontWeight: '700',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          marginBottom: '12px'
        }}>
          <Sparkles size={16} />
          AI-Enriched Taxonomy & Inferred Metadata (Non-Source Derived)
        </div>

        <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #4C1D95' }}>
          <div style={{ fontSize: '11px', color: '#A78BFA', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' }}>
            Standardized Industry Category Path
          </div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC' }}>
            {categoryPath}
          </div>
          {enrichment && enrichment.search_summary && (
            <div style={{ fontSize: '12px', color: '#CBD5E1', marginTop: '8px', fontStyle: 'italic', borderTop: '1px solid #334155', paddingTop: '8px' }}>
              AI Search Summary: {enrichment.search_summary}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
