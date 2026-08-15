import React, { useState } from 'react';
import { GitCommit, ArrowRight, ShieldCheck, Scale, FileText, CheckCircle2, UserCheck, Sparkles, Layers } from 'lucide-react';

export function DataLineage({ specifications = [], sources = [], product = {} }) {
  const [selectedAttr, setSelectedAttr] = useState(
    specifications.length > 0 ? specifications[0].name : ''
  );

  if (!specifications || specifications.length === 0) {
    return null;
  }

  const currentSpec = specifications.find(
    (s) => s.name.toLowerCase() === selectedAttr.toLowerCase()
  ) || specifications[0];

  const sourceName = currentSpec.source_name || (sources.length > 0 ? (sources[0].filename || sources[0].source_name) : 'Datasheet.pdf');

  const lineageStages = [
    {
      step: 1,
      title: '1. Ingested Source',
      icon: FileText,
      color: '#38BDF8',
      details: sourceName,
      subtext: currentSpec.page ? `Page ${currentSpec.page}` : 'Document Content'
    },
    {
      step: 2,
      title: '2. Raw Extraction',
      icon: Sparkles,
      color: '#818CF8',
      details: currentSpec.raw_value || currentSpec.original_value || currentSpec.value || 'Extracted',
      subtext: 'LLM Structured Parser'
    },
    {
      step: 3,
      title: '3. Evidence Matching',
      icon: ShieldCheck,
      color: currentSpec.match_status === 'VERIFIED' ? '#34D399' : '#FBBF24',
      details: currentSpec.match_status || 'VERIFIED',
      subtext: currentSpec.evidence ? `Quote: "${currentSpec.evidence.substring(0, 45)}..."` : 'No exact citation'
    },
    {
      step: 4,
      title: '4. Normalization',
      icon: Scale,
      color: '#A78BFA',
      details: `${currentSpec.value} ${currentSpec.unit || ''}`,
      subtext: currentSpec.normalization_rule || (currentSpec.normalization_applied ? 'Unit Standardized' : 'Exact Format')
    },
    {
      step: 5,
      title: '5. Deterministic Validation',
      icon: CheckCircle2,
      color: currentSpec.status === 'PASS' ? '#34D399' : '#F87171',
      details: currentSpec.status || 'PASS',
      subtext: 'Engineering Rules Engine'
    },
    {
      step: 6,
      title: '6. Attribute Confidence',
      icon: Layers,
      color: currentSpec.confidence >= 80 ? '#34D399' : (currentSpec.confidence >= 50 ? '#FBBF24' : '#F87171'),
      details: `${Math.round(currentSpec.confidence || 0)}% (${currentSpec.confidence_level || 'HIGH'})`,
      subtext: 'Multi-Factor Reliability Score'
    },
    {
      step: 7,
      title: '7. Human Review',
      icon: UserCheck,
      color: currentSpec.review_status === 'human_verified' ? '#34D399' : (currentSpec.review_required ? '#F87171' : '#94A3B8'),
      details: currentSpec.review_status === 'human_verified' ? 'Verified (100%)' : (currentSpec.review_required ? 'Review Required' : 'Auto Approved'),
      subtext: currentSpec.review_reason || 'Audit Trail'
    },
    {
      step: 8,
      title: '8. Commerce Value',
      icon: CheckCircle2,
      color: '#34D399',
      details: `${currentSpec.value} ${currentSpec.unit || ''}`,
      subtext: 'Syndication Ready'
    }
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
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitCommit size={20} color="#38BDF8" />
            End-to-End Data Lineage Graph
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
            Complete audit trail from original source bytes to final commerce specification.
          </p>
        </div>

        {/* Attribute Selector */}
        <select
          value={selectedAttr}
          onChange={(e) => setSelectedAttr(e.target.value)}
          style={{
            background: '#1E293B',
            border: '1px solid #334155',
            color: '#F8FAFC',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '600'
          }}
        >
          {specifications.map((s, i) => (
            <option key={i} value={s.name}>
              {s.name} ({s.value} {s.unit || ''})
            </option>
          ))}
        </select>
      </div>

      {/* Horizontal Lineage Nodes Flow */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '12px',
        overflowX: 'auto',
        paddingBottom: '8px'
      }}>
        {lineageStages.map((stage) => {
          const Icon = stage.icon;
          return (
            <div
              key={stage.step}
              style={{
                background: '#1E293B',
                border: '1px solid #334155',
                borderRadius: '8px',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '6px',
                    background: `${stage.color}22`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Icon size={16} color={stage.color} />
                  </div>
                  <span style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8' }}>
                    {stage.title}
                  </span>
                </div>

                <div style={{
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#F8FAFC',
                  wordBreak: 'break-word',
                  marginBottom: '4px'
                }}>
                  {stage.details}
                </div>
              </div>

              <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '6px', lineHeight: '1.3' }}>
                {stage.subtext}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
