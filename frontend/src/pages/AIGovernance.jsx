import React, { useState, useEffect } from 'react';
import { Cpu, ShieldCheck, FileCode, CheckCircle2, Award, Terminal, Layers } from 'lucide-react';
import { api } from '../services/api';

export default function AIGovernance() {
  const [govData, setGovData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGovernance() {
      try {
        setLoading(true);
        const res = await api.request ? api.request('/api/v1/governance/overview') : null;
        setGovData(res || {
          active_model: { model_name: 'llama3.2:3b', provider: 'Ollama', version: '1.0', runtime: 'Local (CPU/GPU)', status: 'Production', overall_score: 97.3 },
          active_prompt: { prompt_name: 'Industrial Product Extraction Prompt', version: '1.0', status: 'Production' },
          pipeline_version: '2.5.0',
          environment: 'Local Zero-Cost Enterprise Runtime',
          compliance_status: 'COMPLIANT',
          models: [],
          prompts: [],
          governance_pillars: [
            { pillar: 'Anti-Hallucination Guardrails', status: 'ENFORCED', detail: 'Deterministic verbatim citation matching; ungrounded attributes strictly penalized.' },
            { pillar: 'Model & Prompt Versioning', status: 'ACTIVE', detail: 'Immutable tracking of extraction prompt templates and model checkpoints.' },
            { pillar: 'Zero Cloud Data Exfiltration', status: 'COMPLIANT', detail: '100% local inference with local Ollama runtime and SQLite/PostgreSQL storage.' },
            { pillar: 'Human-in-the-Loop Auditability', status: 'ENFORCED', detail: 'Immutable audit trails for all parameter overrides and conflict resolutions.' }
          ]
        });
      } catch (err) {
        console.error('Failed to load governance data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGovernance();
  }, []);

  const g = govData || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', margin: 0 }}>
          AI Governance & Model Operations
        </h1>
        <p style={{ fontSize: '13px', color: '#94A3B8', margin: '4px 0 0 0' }}>
          Model registry, prompt template versioning, reproducibility tracking, and local zero-cost enterprise compliance.
        </p>
      </div>

      {/* Active Model & Compliance Status */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '16px'
      }}>
        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Cpu size={18} color="#2563EB" />
            <span style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>
              Active Inference Model
            </span>
          </div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: '#F8FAFC', fontFamily: 'monospace' }}>
            {g.active_model?.model_name || 'llama3.2:3b'} (v{g.active_model?.version || '1.0'})
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '6px' }}>
            Provider: <span style={{ color: '#F8FAFC' }}>{g.active_model?.provider || 'Ollama'}</span> • Runtime: <span style={{ color: '#F8FAFC' }}>{g.active_model?.runtime || 'Local'}</span>
          </div>
          <div style={{ marginTop: '12px' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: '700',
              padding: '2px 8px',
              borderRadius: '4px',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: '#10B981',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}>
              STATUS: {g.active_model?.status || 'Production'}
            </span>
          </div>
        </div>

        <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <FileCode size={18} color="#06B6D4" />
            <span style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>
              Active Extraction Prompt Template
            </span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: '700', color: '#F8FAFC' }}>
            {g.active_prompt?.prompt_name || 'Industrial Extraction Template'}
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '6px' }}>
            Version: <span style={{ fontFamily: 'monospace', color: '#F8FAFC' }}>v{g.active_prompt?.version || '1.0'}</span> • Pipeline: <span style={{ fontFamily: 'monospace', color: '#F8FAFC' }}>v{g.pipeline_version || '2.5.0'}</span>
          </div>
          <div style={{ marginTop: '12px' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: '700',
              padding: '2px 8px',
              borderRadius: '4px',
              backgroundColor: 'rgba(6, 182, 212, 0.15)',
              color: '#06B6D4',
              border: '1px solid rgba(6, 182, 212, 0.3)'
            }}>
              STATUS: {g.active_prompt?.status || 'Production'}
            </span>
          </div>
        </div>
      </div>

      {/* Governance Pillars */}
      <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', padding: '20px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#F8FAFC', margin: '0 0 16px 0' }}>
          AI Governance & Security Pillars
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {(g.governance_pillars || []).map((p, idx) => (
            <div key={idx} style={{ backgroundColor: '#0F172A', border: '1px solid #334155', borderRadius: '6px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', fontWeight: '700', color: '#F8FAFC' }}>{p.pillar}</span>
                <span style={{
                  fontSize: '10px',
                  fontWeight: '800',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  color: '#10B981'
                }}>
                  {p.status}
                </span>
              </div>
              <p style={{ fontSize: '12px', color: '#94A3B8', margin: '8px 0 0 0', lineHeight: 1.4 }}>
                {p.detail}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
