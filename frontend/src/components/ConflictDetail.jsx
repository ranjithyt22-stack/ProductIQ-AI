import React, { useState } from 'react';
import {
  AlertTriangle, ShieldAlert, CheckCircle2, XCircle, FileText,
  ArrowRight, Scale, UserCheck, X, Check, HelpCircle
} from 'lucide-react';

export function ConflictDetail({ conflict, onClose, onResolve }) {
  if (!conflict) return null;

  const [mode, setMode] = useState('select'); // 'select' or 'custom'
  const [customValue, setCustomValue] = useState(conflict.value_a || '');
  const [customUnit, setCustomUnit] = useState(conflict.unit_a || '');
  const [reason, setReason] = useState('Verified against latest manufacturer documentation');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const srcA = conflict.source_a || {};
  const srcB = conflict.source_b || {};

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return { bg: 'rgba(239, 68, 68, 0.2)', text: '#F87171', border: '#EF4444' };
      case 'HIGH':
        return { bg: 'rgba(249, 115, 22, 0.2)', text: '#FB923C', border: '#F97316' };
      case 'MEDIUM':
        return { bg: 'rgba(251, 191, 36, 0.2)', text: '#FBBF24', border: '#F59E0B' };
      default:
        return { bg: 'rgba(56, 189, 248, 0.2)', text: '#38BDF8', border: '#0284C7' };
    }
  };

  const sevStyle = getSeverityBadge(conflict.severity);

  const handleAction = async (action, customVal = null, customU = null) => {
    if (submitting) return;
    setSubmitting(true);
    try {
      await onResolve(conflict.product_id, conflict.conflict_id, {
        action,
        resolution_value: customVal,
        resolution_unit: customU,
        reason: reason.trim(),
        notes: notes.trim(),
        reviewer: 'Reviewer 1'
      });
      onClose();
    } catch (err) {
      console.error('Resolution error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.75)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        background: '#0B0F19',
        border: '1px solid #1E293B',
        borderRadius: '10px',
        width: '840px',
        maxWidth: '95vw',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 20px 40px rgba(0,0,0,0.8)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #1E293B',
          background: '#0F172A',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={20} color={sevStyle.text} />
              <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '800', color: '#F8FAFC' }}>
                Cross-Source Conflict: {conflict.attribute_name}
              </h2>
              <span style={{
                background: sevStyle.bg,
                color: sevStyle.text,
                border: `1px solid ${sevStyle.border}`,
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '800'
              }}>
                {conflict.severity}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
              Product ID: <strong style={{ color: '#E2E8F0' }}>{conflict.product_id}</strong> | Type: {conflict.conflict_type} | Confidence: {conflict.confidence}%
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Reason Alert */}
          <div style={{
            background: 'rgba(249, 115, 22, 0.1)',
            border: '1px solid rgba(249, 115, 22, 0.3)',
            borderRadius: '6px',
            padding: '12px 16px',
            fontSize: '13px',
            color: '#FDBA74'
          }}>
            <strong>Conflict Summary:</strong> {conflict.reason}
          </div>

          {/* Side-by-Side Source Comparison Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

            {/* Source A Card */}
            <div style={{
              background: '#0F172A',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: '800', color: '#38BDF8', textTransform: 'uppercase' }}>
                    SOURCE A
                  </span>
                  <span style={{ fontSize: '11px', color: '#94A3B8', background: '#1E293B', padding: '2px 6px', borderRadius: '4px' }}>
                    {srcA.source_reliability || 'OFFICIAL_DATASHEET'}
                  </span>
                </div>

                <div style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC', marginBottom: '8px' }}>
                  {srcA.name || conflict.source_a_name || 'Manufacturer Datasheet'}
                </div>

                <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px', marginBottom: '10px' }}>
                  <div style={{ fontSize: '11px', color: '#94A3B8' }}>Reported Specification</div>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: '#38BDF8', marginTop: '2px' }}>
                    {srcA.value || conflict.value_a} {srcA.unit || conflict.unit_a || ''}
                  </div>
                </div>

                <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '8px' }}>
                  Citation: <strong>{srcA.page ? `Page ${srcA.page}` : 'Datasheet text'}</strong>
                </div>

                <div style={{
                  background: '#0B0F19',
                  borderLeft: '3px solid #38BDF8',
                  padding: '8px 10px',
                  borderRadius: '4px',
                  color: '#CBD5E1',
                  fontStyle: 'italic',
                  fontSize: '12px'
                }}>
                  "{srcA.evidence_quote || conflict.evidence_a || 'Evidence cited from source document.'}"
                </div>
              </div>

              <button
                onClick={() => handleAction('USE_SOURCE_A')}
                disabled={submitting}
                style={{
                  marginTop: '16px',
                  background: '#2563EB',
                  border: 'none',
                  color: '#FFFFFF',
                  padding: '10px',
                  borderRadius: '6px',
                  fontWeight: '700',
                  fontSize: '13px',
                  cursor: submitting ? 'not-allowed' : 'pointer'
                }}
              >
                Accept Source A Value ({srcA.value || conflict.value_a} {srcA.unit || conflict.unit_a || ''})
              </button>
            </div>

            {/* Source B Card */}
            <div style={{
              background: '#0F172A',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: '800', color: '#A78BFA', textTransform: 'uppercase' }}>
                    SOURCE B
                  </span>
                  <span style={{ fontSize: '11px', color: '#94A3B8', background: '#1E293B', padding: '2px 6px', borderRadius: '4px' }}>
                    {srcB.source_reliability || 'OFFICIAL_WEBSITE'}
                  </span>
                </div>

                <div style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC', marginBottom: '8px' }}>
                  {srcB.name || conflict.source_b_name || 'Manufacturer Website'}
                </div>

                <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px', marginBottom: '10px' }}>
                  <div style={{ fontSize: '11px', color: '#94A3B8' }}>Reported Specification</div>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: '#A78BFA', marginTop: '2px' }}>
                    {srcB.value || conflict.value_b} {srcB.unit || conflict.unit_b || ''}
                  </div>
                </div>

                <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '8px' }}>
                  Citation: <strong>{srcB.page ? `Page ${srcB.page}` : 'Webpage text'}</strong>
                </div>

                <div style={{
                  background: '#0B0F19',
                  borderLeft: '3px solid #A78BFA',
                  padding: '8px 10px',
                  borderRadius: '4px',
                  color: '#CBD5E1',
                  fontStyle: 'italic',
                  fontSize: '12px'
                }}>
                  "{srcB.evidence_quote || conflict.evidence_b || 'Evidence cited from web source.'}"
                </div>
              </div>

              <button
                onClick={() => handleAction('USE_SOURCE_B')}
                disabled={submitting}
                style={{
                  marginTop: '16px',
                  background: '#7C3AED',
                  border: 'none',
                  color: '#FFFFFF',
                  padding: '10px',
                  borderRadius: '6px',
                  fontWeight: '700',
                  fontSize: '13px',
                  cursor: submitting ? 'not-allowed' : 'pointer'
                }}
              >
                Accept Source B Value ({srcB.value || conflict.value_b} {srcB.unit || conflict.unit_b || ''})
              </button>
            </div>

          </div>

          {/* Recommended Action */}
          <div style={{ background: '#0F172A', padding: '12px 16px', borderRadius: '6px', border: '1px solid #1E293B', fontSize: '13px', color: '#94A3B8' }}>
            <strong style={{ color: '#F8FAFC' }}>Recommended Action:</strong> {conflict.recommended_action || 'Verify against primary technical specification.'}
          </div>

          {/* Custom Correction Form Toggle */}
          {mode === 'custom' ? (
            <div style={{ background: '#0F172A', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC', marginBottom: '10px' }}>
                Enter Correct Engineering Value
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '10px', marginBottom: '10px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Value</label>
                  <input
                    type="text"
                    value={customValue}
                    onChange={(e) => setCustomValue(e.target.value)}
                    style={{ width: '100%', background: '#1E293B', border: '1px solid #334155', color: '#F8FAFC', padding: '8px', borderRadius: '4px', fontSize: '13px' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Unit</label>
                  <input
                    type="text"
                    value={customUnit}
                    onChange={(e) => setCustomUnit(e.target.value)}
                    style={{ width: '100%', background: '#1E293B', border: '1px solid #334155', color: '#F8FAFC', padding: '8px', borderRadius: '4px', fontSize: '13px' }}
                  />
                </div>
              </div>
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>Reason for Override</label>
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  style={{ width: '100%', background: '#1E293B', border: '1px solid #334155', color: '#F8FAFC', padding: '8px', borderRadius: '4px', fontSize: '13px' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => handleAction('ENTER_CORRECT_VALUE', customValue, customUnit)}
                  disabled={submitting || !customValue.trim()}
                  style={{ background: '#059669', color: '#FFF', border: 'none', padding: '8px 16px', borderRadius: '6px', fontWeight: '700', fontSize: '13px', cursor: 'pointer' }}
                >
                  Save & Mark Human Verified (100%)
                </button>
                <button
                  onClick={() => setMode('select')}
                  style={{ background: 'transparent', color: '#94A3B8', border: '1px solid #334155', padding: '8px 14px', borderRadius: '6px', fontSize: '13px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
              <button
                onClick={() => setMode('custom')}
                style={{ background: '#1E293B', color: '#38BDF8', border: '1px solid #334155', padding: '8px 14px', borderRadius: '6px', fontWeight: '600', fontSize: '13px', cursor: 'pointer' }}
              >
                Enter Correct Value
              </button>
              <button
                onClick={() => handleAction('DISMISS_CONFLICT')}
                disabled={submitting}
                style={{ background: 'transparent', color: '#94A3B8', border: '1px solid #334155', padding: '8px 14px', borderRadius: '6px', fontSize: '13px', cursor: 'pointer' }}
              >
                Dismiss Conflict
              </button>
              <button
                onClick={onClose}
                style={{ background: 'transparent', color: '#94A3B8', border: '1px solid #334155', padding: '8px 14px', borderRadius: '6px', fontSize: '13px', cursor: 'pointer' }}
              >
                Leave Unresolved
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
