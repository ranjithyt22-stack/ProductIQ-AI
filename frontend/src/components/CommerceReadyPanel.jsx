import React from 'react';
import { ShoppingBag, CheckCircle2, ShieldCheck, Tag, Box } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function CommerceReadyPanel({ record = {} }) {
  if (!record || !record.product) return null;

  const { product = {}, specifications = [], enrichment = {}, quality_score = {} } = record;
  const { product_name, manufacturer, product_code, category, description } = product;

  const score = quality_score.overall_score || 0;
  const statusCategory = quality_score.status_category || 'REQUIRES MANUAL REVIEW';
  const isCommerceReady = statusCategory === 'READY FOR COMMERCE';

  const categoryPath = enrichment.category_path && enrichment.category_path.length > 0
    ? enrichment.category_path.join(' > ')
    : (category || 'Industrial Equipment');

  const topSpecs = specifications.slice(0, 8);

  return (
    <div style={{
      background: '#0F172A',
      border: `2px solid ${isCommerceReady ? '#10B981' : '#F59E0B'}`,
      borderRadius: '8px',
      padding: '24px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <ShoppingBag size={20} color={isCommerceReady ? '#10B981' : '#F59E0B'} />
            <span style={{ fontSize: '12px', fontWeight: '800', textTransform: 'uppercase', color: '#94A3B8', letterSpacing: '1px' }}>
              Commerce-Ready Syndication Payload
            </span>
          </div>
          <h3 style={{ margin: 0, fontSize: '22px', fontWeight: '800', color: '#F8FAFC' }}>
            {product_name || 'Industrial Product Record'}
          </h3>
          <div style={{ fontSize: '13px', color: '#38BDF8', marginTop: '4px', fontWeight: '600' }}>
            Category Taxonomy: {categoryPath}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase' }}>
              READINESS SCORE
            </div>
            <div style={{ fontSize: '24px', fontWeight: '900', color: isCommerceReady ? '#34D399' : '#FBBF24' }}>
              {score} / 100
            </div>
          </div>
          <StatusBadge status={statusCategory} />
        </div>
      </div>

      {/* Structured Card Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        {/* Identity & Description */}
        <div style={{ background: '#1E293B', padding: '16px', borderRadius: '6px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Box size={14} color="#60A5FA" />
            Catalog Identity
          </div>
          <div style={{ fontSize: '13px', color: '#E2E8F0', marginBottom: '6px' }}>
            <strong>Manufacturer:</strong> {manufacturer || '—'}
          </div>
          <div style={{ fontSize: '13px', color: '#E2E8F0', marginBottom: '6px' }}>
            <strong>Part / SKU Code:</strong> <span style={{ color: '#60A5FA', fontWeight: '600' }}>{product_code || '—'}</span>
          </div>
          <div style={{ fontSize: '13px', color: '#E2E8F0', marginTop: '10px', lineHeight: '1.4' }}>
            <strong>Commerce Description:</strong>
            <p style={{ margin: '4px 0 0 0', color: '#CBD5E1', fontSize: '13px' }}>
              {description || 'No description available.'}
            </p>
          </div>
        </div>

        {/* Structured Spec Snapshot */}
        <div style={{ background: '#1E293B', padding: '16px', borderRadius: '6px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={14} color="#34D399" />
            Normalized Technical Specs ({specifications.length})
          </div>
          {topSpecs.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {topSpecs.map((s, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', paddingBottom: '4px', borderBottom: '1px solid #334155' }}>
                  <span style={{ color: '#94A3B8' }}>{s.name}</span>
                  <span style={{ color: '#F8FAFC', fontWeight: '600' }}>
                    {s.value} {s.unit || ''}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '13px', color: '#94A3B8' }}>No technical specifications extracted.</div>
          )}
        </div>
      </div>

      {/* Target Applications & Keywords */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {enrichment.suggested_applications && enrichment.suggested_applications.length > 0 && (
          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
            <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Tag size={14} color="#F59E0B" />
              Target Industrial Applications
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {enrichment.suggested_applications.map((app, i) => (
                <span key={i} style={{ background: '#0F172A', border: '1px solid #334155', color: '#F8FAFC', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                  {app}
                </span>
              ))}
            </div>
          </div>
        )}

        {enrichment.search_terms && enrichment.search_terms.length > 0 && (
          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
            <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Tag size={14} color="#38BDF8" />
              SEO & Commerce Search Keywords
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {enrichment.search_terms.map((kw, i) => (
                <span key={i} style={{ background: '#0F172A', border: '1px solid #334155', color: '#38BDF8', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
