import React, { useState } from 'react';
import { StatusBadge } from './StatusBadge';
import { ShieldCheck, AlertTriangle, FileText, CheckCircle2, XCircle, Sparkles, Scale, Info, ArrowRight, UserCheck, X } from 'lucide-react';

export function AttributeIntelligence({ attribute, explainability, onClose, onSaveReview }) {
  if (!attribute) return null;

  const exp = explainability || {};
  const [reviewedVal, setReviewedVal] = useState(attribute.value || '');
  const [reviewedUnit, setReviewedUnit] = useState(attribute.unit || '');
  const [reviewNote, setReviewNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (onSaveReview) {
      setSubmitting(true);
      await onSaveReview({
        attribute_name: attribute.name,
        reviewed_value: reviewedVal,
        reviewed_unit: reviewedUnit,
        verification_note: reviewNote
      });
      setSubmitting(false);
    }
  };

  const confidenceScore = Math.round(attribute.confidence || exp.confidence || 0);
  const confidenceLevel = attribute.confidence_level || exp.confidence_level || 'HIGH';
  const matchStatus = attribute.match_status || exp.evidence_status || 'VERIFIED';
  const evidenceType = attribute.evidence_type || exp.evidence_type || 'DIRECT';
  const reviewRequired = attribute.review_required || exp.review_required || false;
  const reviewReason = attribute.review_reason || exp.review_reason || '';

  const getConfColor = (score) => {
    if (score >= 90) return '#34D399';
    if (score >= 70) return '#38BDF8';
    if (score >= 50) return '#FBBF24';
    return '#F87171';
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: '520px',
      maxWidth: '90vw',
      height: '100vh',
      background: '#0B0F19',
      borderLeft: '1px solid #1E293B',
      boxShadow: '-10px 0 30px rgba(0,0,0,0.7)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      overflowY: 'auto'
    }}>
      {/* Drawer Header */}
      <div style={{
        padding: '20px',
        borderBottom: '1px solid #1E293B',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#0F172A'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldCheck size={22} color="#38BDF8" />
          <div>
            <h3 style={{ margin: 0, fontSize: '17px', fontWeight: '700', color: '#F8FAFC' }}>
              Attribute Intelligence
            </h3>
            <span style={{ fontSize: '12px', color: '#94A3B8' }}>
              Explainability & Grounding Audit
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94A3B8',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '6px',
            display: 'flex'
          }}
        >
          <X size={20} />
        </button>
      </div>

      <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* Attribute Title & Final Value */}
        <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
          <div style={{ fontSize: '12px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: '700' }}>
            Specification Parameter
          </div>
          <div style={{ fontSize: '20px', fontWeight: '700', color: '#F8FAFC', marginTop: '4px' }}>
            {attribute.name}
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
            <span style={{ fontSize: '14px', color: '#94A3B8' }}>Final Value:</span>
            <span style={{ fontSize: '18px', fontWeight: '700', color: '#38BDF8' }}>
              {attribute.value || 'Not present'} {attribute.unit || ''}
            </span>
          </div>
        </div>

        {/* Diagnostic Review Alert if Required */}
        {reviewRequired && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '14px',
            display: 'flex',
            gap: '12px'
          }}>
            <AlertTriangle size={20} color="#F87171" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: '700', color: '#FCA5A5', fontSize: '13px' }}>
                Why Human Review is Required
              </div>
              <div style={{ fontSize: '13px', color: '#FECACA', marginTop: '4px', lineHeight: '1.4' }}>
                {reviewReason || 'Attribute confidence or validation indicates verification is necessary.'}
              </div>
            </div>
          </div>
        )}

        {/* Multi-Factor Confidence Metric */}
        <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: '600', color: '#94A3B8' }}>Deterministic Confidence Score</span>
            <span style={{
              fontSize: '18px',
              fontWeight: '800',
              color: getConfColor(confidenceScore)
            }}>
              {confidenceScore}% ({confidenceLevel})
            </span>
          </div>
          <div style={{ height: '8px', background: '#1E293B', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${confidenceScore}%`,
              background: getConfColor(confidenceScore),
              transition: 'width 0.4s ease'
            }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '12px', fontSize: '12px', color: '#94A3B8' }}>
            <div>Evidence Status: <strong style={{ color: '#F8FAFC' }}>{matchStatus}</strong></div>
            <div>Evidence Type: <strong style={{ color: '#F8FAFC' }}>{evidenceType}</strong></div>
            <div>Validation Rule: <strong style={{ color: '#F8FAFC' }}>{attribute.status || 'PASS'}</strong></div>
            <div>Source Reliability: <strong style={{ color: '#F8FAFC' }}>{attribute.source_reliability || 'OFFICIAL_DATASHEET'}</strong></div>
          </div>
        </div>

        {/* Transparent Normalization Details */}
        <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Scale size={16} color="#A78BFA" />
            <span style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC' }}>Normalization Lineage</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '10px', alignItems: 'center' }}>
            <div style={{ background: '#1E293B', padding: '10px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8' }}>Raw Extracted Value</div>
              <div style={{ fontWeight: '600', color: '#F8FAFC', marginTop: '2px', fontSize: '13px' }}>
                {attribute.raw_value || attribute.original_value || attribute.value || 'None'}
              </div>
            </div>
            <ArrowRight size={16} color="#64748B" />
            <div style={{ background: '#1E293B', padding: '10px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8' }}>Normalized Commerce Value</div>
              <div style={{ fontWeight: '600', color: '#38BDF8', marginTop: '2px', fontSize: '13px' }}>
                {attribute.normalized_value || attribute.value} {attribute.unit || ''}
              </div>
            </div>
          </div>
          {attribute.normalization_rule && (
            <div style={{ marginTop: '10px', fontSize: '12px', color: '#94A3B8' }}>
              Rule Applied: <code style={{ color: '#A78BFA', background: '#1E293B', padding: '2px 6px', borderRadius: '4px' }}>{attribute.normalization_rule}</code>
            </div>
          )}
        </div>

        {/* Verbatim Source Evidence Citation */}
        <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
            <FileText size={16} color="#38BDF8" />
            <span style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC' }}>Verbatim Source Evidence</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8', marginBottom: '8px' }}>
            <span>Source: <strong style={{ color: '#F8FAFC' }}>{attribute.source_name || 'Datasheet.pdf'}</strong></span>
            <span>Page: <strong style={{ color: '#F8FAFC' }}>{attribute.page ? `Page ${attribute.page}` : 'Document'}</strong></span>
          </div>
          <div style={{
            background: '#1E293B',
            borderLeft: '4px solid #38BDF8',
            padding: '12px',
            borderRadius: '4px',
            color: '#E2E8F0',
            fontStyle: 'italic',
            fontSize: '13px',
            lineHeight: '1.5'
          }}>
            {attribute.evidence ? `"${attribute.evidence}"` : 'No direct verbatim evidence snippet found in provided sources.'}
          </div>
        </div>

        {/* Human-in-the-Loop Override Form */}
        <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <UserCheck size={16} color="#34D399" />
            <span style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC' }}>Human Verification Override</span>
          </div>
          <form onSubmit={handleReviewSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Value</label>
                <input
                  type="text"
                  value={reviewedVal}
                  onChange={(e) => setReviewedVal(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#1E293B',
                    border: '1px solid #334155',
                    color: '#F8FAFC',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    fontSize: '13px'
                  }}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Unit</label>
                <input
                  type="text"
                  value={reviewedUnit}
                  onChange={(e) => setReviewedUnit(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#1E293B',
                    border: '1px solid #334155',
                    color: '#F8FAFC',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    fontSize: '13px'
                  }}
                />
              </div>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Verification Note</label>
              <input
                type="text"
                placeholder="e.g. Verified against lab calibration sheet"
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid #334155',
                  color: '#F8FAFC',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  fontSize: '13px'
                }}
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              style={{
                marginTop: '6px',
                background: '#2563EB',
                border: 'none',
                color: '#FFF',
                padding: '10px 16px',
                borderRadius: '6px',
                fontWeight: '600',
                fontSize: '13px',
                cursor: submitting ? 'not-allowed' : 'pointer'
              }}
            >
              {submitting ? 'Saving Review...' : 'Approve & Mark Human Verified (100%)'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
