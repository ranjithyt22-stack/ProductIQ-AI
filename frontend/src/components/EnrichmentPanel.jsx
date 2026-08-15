import React from 'react';

export function EnrichmentPanel({ enrichment }) {
  if (!enrichment) return null;

  const categoryPath = enrichment.category_path || ['Industrial Equipment'];
  const searchTerms = enrichment.search_terms || [];
  const applications = enrichment.suggested_applications || [];
  const summary = enrichment.search_summary || '';

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
          AI Taxonomy & Search Enrichment
        </h3>
        <span style={{ fontSize: '11px', background: '#1E293B', color: '#94A3B8', padding: '4px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
          AI-Generated Taxonomy (Distinct from Source Facts)
        </span>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
          Taxonomy Category Hierarchy Path
        </div>
        <div style={{ background: '#1E293B', padding: '10px 14px', borderRadius: '6px', color: '#60A5FA', fontWeight: '600', fontSize: '14px' }}>
          {categoryPath.join(' > ')}
        </div>
      </div>

      {searchTerms.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
            Commerce Search Keywords & Synonyms
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {searchTerms.map((term, i) => (
              <span key={i} style={{ background: '#1E293B', border: '1px solid #334155', color: '#E2E8F0', padding: '4px 10px', borderRadius: '16px', fontSize: '12px' }}>
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      {applications.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
            Suggested Industrial Applications
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px', color: '#E2E8F0', fontSize: '14px', lineHeight: '1.6' }}>
            {applications.map((app, i) => (
              <li key={i}>{app}</li>
            ))}
          </ul>
        </div>
      )}

      {summary && (
        <div>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
            Commerce Search Summary
          </div>
          <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px', color: '#CBD5E1', fontSize: '13px', lineHeight: '1.5' }}>
            {summary}
          </div>
        </div>
      )}
    </div>
  );
}
