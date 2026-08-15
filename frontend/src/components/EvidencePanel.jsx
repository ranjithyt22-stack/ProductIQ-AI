import React, { useState } from 'react';
import { ShieldCheck, Sparkles, AlertTriangle, XCircle, FileText, CheckCircle2 } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function EvidencePanel({ specifications = [], sources = [], enrichment = {} }) {
  const [activeTab, setActiveTab] = useState('verified');

  if (!specifications || specifications.length === 0) {
    return (
      <div style={{ padding: '20px', background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#94A3B8', textAlign: 'center' }}>
        No specification evidence available yet.
      </div>
    );
  }

  // 1. Verified Source Facts (Direct manufacturer evidence matching)
  const verifiedFacts = specifications.filter(
    (s) => s.match_status === 'VERIFIED' && s.evidence && s.status !== 'REVIEW'
  );

  // 2. AI-Enriched Information (Taxonomy, categories, keywords, applications)
  const enrichedCategories = enrichment.category_path || [];
  const searchKeywords = enrichment.search_terms || [];
  const suggestedApps = enrichment.suggested_applications || [];

  // 3. Unverified Information (No direct source citation found)
  const unverifiedItems = specifications.filter(
    (s) => s.match_status === 'NOT_FOUND' || s.evidence_type === 'UNVERIFIED' || !s.evidence || s.confidence < 50
  );

  // 4. Conflicting Information (Multi-source conflict flags)
  const conflictingItems = specifications.filter(
    (s) => s.status === 'REVIEW' || s.match_status === 'CONFLICTING'
  );

  const tabs = [
    { id: 'verified', label: `Verified Source Facts (${verifiedFacts.length})`, count: verifiedFacts.length, icon: ShieldCheck, color: '#34D399' },
    { id: 'enriched', label: `AI-Enriched Information (${enrichedCategories.length + searchKeywords.length})`, count: enrichedCategories.length + searchKeywords.length, icon: Sparkles, color: '#A78BFA' },
    { id: 'unverified', label: `Unverified Items (${unverifiedItems.length})`, count: unverifiedItems.length, icon: AlertTriangle, color: unverifiedItems.length > 0 ? '#F87171' : '#94A3B8' },
    { id: 'conflicting', label: `Conflicting Information (${conflictingItems.length})`, count: conflictingItems.length, icon: XCircle, color: conflictingItems.length > 0 ? '#FBBF24' : '#94A3B8' }
  ];

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
          Evidence Verification & Source Grounding
        </h3>
        <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
          Strictly separates manufacturer-verified facts from AI inferred taxonomy and unverified claims.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #334155', paddingBottom: '10px', marginBottom: '16px', overflowX: 'auto' }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: isActive ? '#1E293B' : 'transparent',
                border: isActive ? '1px solid #38BDF8' : '1px solid transparent',
                color: isActive ? '#F8FAFC' : '#94A3B8',
                padding: '8px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                whiteSpace: 'nowrap'
              }}
            >
              <Icon size={16} color={tab.color} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Verified Source Facts */}
      {activeTab === 'verified' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {verifiedFacts.length === 0 ? (
            <div style={{ padding: '20px', color: '#94A3B8', textAlign: 'center', background: '#1E293B', borderRadius: '6px' }}>
              No verified source facts identified.
            </div>
          ) : (
            verifiedFacts.map((spec, i) => (
              <div key={i} style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: '700', color: '#F8FAFC', fontSize: '14px' }}>{spec.name}</span>
                    <span style={{ color: '#38BDF8', fontWeight: '700', fontSize: '14px' }}>
                      {spec.value} {spec.unit || ''}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '12px', color: '#94A3B8' }}>{spec.source_name || 'Datasheet'}</span>
                    <span style={{ fontSize: '12px', color: '#94A3B8' }}>Page {spec.page || 1}</span>
                    <span style={{ fontSize: '12px', fontWeight: '700', color: '#34D399' }}>{Math.round(spec.confidence || 0)}%</span>
                  </div>
                </div>
                <div style={{
                  background: '#0F172A',
                  borderLeft: '3px solid #34D399',
                  padding: '10px 12px',
                  borderRadius: '4px',
                  color: '#E2E8F0',
                  fontStyle: 'italic',
                  fontSize: '13px'
                }}>
                  "{spec.evidence}"
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: AI Enriched Information */}
      {activeTab === 'enriched' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ background: 'rgba(167, 139, 250, 0.08)', border: '1px solid rgba(167, 139, 250, 0.3)', padding: '12px', borderRadius: '6px', fontSize: '13px', color: '#DDD6FE' }}>
            <strong>Notice:</strong> AI-enriched taxonomy and search keywords are generated from model context and are never presented as direct manufacturer facts.
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
            <div style={{ fontSize: '13px', fontWeight: '700', color: '#F8FAFC', marginBottom: '8px' }}>Commerce Category Hierarchy</div>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {enrichedCategories.map((c, i) => (
                <span key={i} style={{ background: '#0F172A', color: '#A78BFA', padding: '4px 10px', borderRadius: '4px', fontSize: '12px', border: '1px solid #334155' }}>
                  {c}
                </span>
              ))}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px' }}>
            <div style={{ fontSize: '13px', fontWeight: '700', color: '#F8FAFC', marginBottom: '8px' }}>Syndication & Search Keywords</div>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {searchKeywords.map((k, i) => (
                <span key={i} style={{ background: '#0F172A', color: '#38BDF8', padding: '4px 10px', borderRadius: '4px', fontSize: '12px', border: '1px solid #334155' }}>
                  {k}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Unverified Information */}
      {activeTab === 'unverified' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {unverifiedItems.length === 0 ? (
            <div style={{ padding: '20px', color: '#34D399', textAlign: 'center', background: '#1E293B', borderRadius: '6px' }}>
              All extracted specifications are successfully verified against source documents.
            </div>
          ) : (
            unverifiedItems.map((spec, i) => (
              <div key={i} style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: '700', color: '#FCA5A5', fontSize: '14px' }}>{spec.name}</span>
                  <span style={{ color: '#F87171', fontWeight: '700', fontSize: '13px' }}>
                    Confidence: {Math.round(spec.confidence || 0)}% (UNVERIFIED)
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#E2E8F0', marginBottom: '8px' }}>
                  Extracted Value: <strong>{spec.value || 'Null'} {spec.unit || ''}</strong>
                </div>
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px', color: '#FECACA' }}>
                  {spec.review_reason || 'Evidence was not found in the supplied source documents. Value requires manual verification.'}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 4: Conflicting Information */}
      {activeTab === 'conflicting' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {conflictingItems.length === 0 ? (
            <div style={{ padding: '20px', color: '#34D399', textAlign: 'center', background: '#1E293B', borderRadius: '6px' }}>
              No conflicting multi-source specifications detected.
            </div>
          ) : (
            conflictingItems.map((spec, i) => (
              <div key={i} style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid rgba(251, 191, 36, 0.4)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: '700', color: '#FDE68A', fontSize: '14px' }}>{spec.name}</span>
                  <span style={{ color: '#FBBF24', fontWeight: '700', fontSize: '13px' }}>
                    Status: REQUIRES MANUAL REVIEW
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#E2E8F0', marginBottom: '8px' }}>
                  Extracted Value: <strong>{spec.value} {spec.unit || ''}</strong>
                </div>
                <div style={{ background: 'rgba(251, 191, 36, 0.1)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px', color: '#FEF3C7' }}>
                  {spec.review_reason || 'Conflicting values reported across ingested sources. Manual human verification required.'}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
