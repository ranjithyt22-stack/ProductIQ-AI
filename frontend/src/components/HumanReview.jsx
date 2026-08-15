import React, { useState } from 'react';

export function HumanReview({ record, onApplyReview }) {
  if (!record || !record.specifications) return null;

  const specifications = record.specifications || [];
  const [selectedAttr, setSelectedAttr] = useState(
    specifications.length > 0 ? specifications[0].name : ''
  );
  const [newValue, setNewValue] = useState('');
  const [newUnit, setNewUnit] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleConfirm = async (e) => {
    e.preventDefault();
    if (!selectedAttr || !newValue.trim()) {
      setMessage('Please select an attribute and specify a corrected value.');
      return;
    }

    setSubmitting(true);
    setMessage('');
    try {
      await onApplyReview(selectedAttr, newValue.trim(), newUnit.trim());
      setMessage(`Attribute '${selectedAttr}' updated successfully. Marked as HUMAN VERIFIED.`);
      setNewValue('');
      setNewUnit('');
    } catch (err) {
      setMessage(`Review failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #1E293B',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
        Human Review & Specification Override
      </h3>
      <p style={{ margin: '0 0 16px 0', fontSize: '13px', color: '#94A3B8' }}>
        Review extracted attributes, apply human verification, and override values where required.
      </p>

      <form onSubmit={handleConfirm} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'end' }}>
        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
            Attribute to Edit
          </label>
          <select
            value={selectedAttr}
            onChange={(e) => setSelectedAttr(e.target.value)}
            style={{
              width: '100%',
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#F8FAFC',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          >
            {specifications.map((s, i) => (
              <option key={i} value={s.name}>
                {s.name} (Current: {s.value} {s.unit || ''})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
            Corrected Value
          </label>
          <input
            type="text"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            placeholder="e.g. 12.5"
            style={{
              width: '100%',
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#F8FAFC',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '14px',
              boxSizing: 'border-box'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
            Corrected Unit (Optional)
          </label>
          <input
            type="text"
            value={newUnit}
            onChange={(e) => setNewUnit(e.target.value)}
            placeholder="e.g. bar"
            style={{
              width: '100%',
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#F8FAFC',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '14px',
              boxSizing: 'border-box'
            }}
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={submitting}
            style={{
              width: '100%',
              background: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '10px 16px',
              fontWeight: '700',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            {submitting ? 'Updating...' : 'Confirm & Mark Human Verified'}
          </button>
        </div>
      </form>

      {message && (
        <div style={{
          marginTop: '12px',
          padding: '10px',
          borderRadius: '6px',
          background: message.includes('failed') ? '#450A0A' : '#064E3B',
          color: message.includes('failed') ? '#FECACA' : '#D1FAE5',
          fontSize: '13px'
        }}>
          {message}
        </div>
      )}
    </div>
  );
}
