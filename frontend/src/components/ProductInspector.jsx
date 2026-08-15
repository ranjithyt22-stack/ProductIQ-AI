import React, { useState } from 'react';
import { ProductOverview } from './ProductOverview';
import { Specifications } from './Specifications';
import { ValidationPanel } from './ValidationPanel';
import { EvidencePanel } from './EvidencePanel';
import { EnrichmentPanel } from './EnrichmentPanel';
import { CompletenessPanel } from './CompletenessPanel';
import { CommerceReadyPanel } from './CommerceReadyPanel';
import { HumanReview } from './HumanReview';
import { ExportPanel } from './ExportPanel';
import { QualityScore } from './QualityScore';
import { X, Layers, ShieldCheck, Tag, ShoppingBag, FileText, Search } from 'lucide-react';

export function ProductInspector({ productItem, onClose, onApplyReview }) {
  const [activeSubTab, setActiveSubTab] = useState('overview');

  if (!productItem || !productItem.record) return null;

  const record = productItem.record;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'specs', label: 'Specifications', icon: Layers },
    { id: 'validation', label: 'Validation', icon: ShieldCheck },
    { id: 'evidence', label: 'Evidence', icon: Search },
    { id: 'enrichment', label: 'AI Enrichment', icon: Tag },
    { id: 'commerce', label: 'Commerce Ready', icon: ShoppingBag },
    { id: 'export', label: 'Export', icon: FileText },
  ];

  return (
    <div style={{
      background: '#0F172A',
      border: '1px solid #334155',
      borderRadius: '8px',
      padding: '24px',
      marginTop: '20px',
      position: 'relative'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #1E293B' }}>
        <div>
          <span style={{ fontSize: '11px', fontWeight: '800', color: '#38BDF8', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Catalog Product Inspector
          </span>
          <h3 style={{ margin: '4px 0 0 0', fontSize: '20px', fontWeight: '800', color: '#F8FAFC' }}>
            {productItem.product_name} ({productItem.product_id})
          </h3>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#94A3B8',
              borderRadius: '6px',
              padding: '6px 12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '13px'
            }}
          >
            <X size={16} /> Close Inspector
          </button>
        )}
      </div>

      {/* Quality Badge */}
      <QualityScore scoreObj={record.quality_score} />

      {/* Sub Tab Navigation */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #1E293B', paddingBottom: '12px' }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              style={{
                background: isActive ? '#2563EB' : '#1E293B',
                color: isActive ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 14px',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Sub Tab Views */}
      <div>
        {activeSubTab === 'overview' && (
          <div>
            <ProductOverview product={record.product} />
            <CompletenessPanel
              product={record.product}
              specifications={record.specifications}
              qualityScore={record.quality_score}
            />
          </div>
        )}

        {activeSubTab === 'specs' && (
          <div>
            <Specifications specifications={record.specifications} />
            {onApplyReview && (
              <HumanReview record={record} onApplyReview={onApplyReview} />
            )}
          </div>
        )}

        {activeSubTab === 'validation' && (
          <ValidationPanel validationResults={record.validation} />
        )}

        {activeSubTab === 'evidence' && (
          <EvidencePanel specifications={record.specifications} sources={record.raw_sources} />
        )}

        {activeSubTab === 'enrichment' && (
          <EnrichmentPanel enrichment={record.enrichment} />
        )}

        {activeSubTab === 'commerce' && (
          <CommerceReadyPanel record={record} />
        )}

        {activeSubTab === 'export' && (
          <ExportPanel productId={record.product_id || productItem.product_id} record={record} />
        )}
      </div>
    </div>
  );
}
