import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { ReviewFilters } from '../components/ReviewFilters';
import { ReviewQueue } from '../components/ReviewQueue';
import { ConflictDetail } from '../components/ConflictDetail';
import { ReviewHistory } from '../components/ReviewHistory';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { ShieldAlert, AlertTriangle, CheckCircle2, History, RefreshCw } from 'lucide-react';

export function ReviewCenter() {
  const [activeTab, setActiveTab] = useState('queue'); // 'queue' or 'history'
  const [conflicts, setConflicts] = useState([]);
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const [selectedConflict, setSelectedConflict] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = {};
      if (statusFilter !== 'ALL') filters.status = statusFilter;
      if (severityFilter !== 'ALL') filters.severity = severityFilter;

      const [revRes, auditRes] = await Promise.all([
        apiService.listReviews(filters),
        apiService.getReviewAudits()
      ]);

      setConflicts(revRes.reviews || []);
      setAudits(auditRes.audits || []);
    } catch (err) {
      setError(err.message || 'Failed to load review queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter, severityFilter]);

  const handleResolveConflict = async (productId, conflictId, resolutionData) => {
    await apiService.resolveProductConflict(productId, conflictId, resolutionData);
    fetchData();
  };

  const handleResetFilters = () => {
    setSeverityFilter('ALL');
    setStatusFilter('ALL');
    setSearchTerm('');
  };

  // Filtered conflicts
  const filteredConflicts = conflicts.filter((c) => {
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchProd = (c.product_id || '').toLowerCase().includes(q);
      const matchAttr = (c.attribute_name || '').toLowerCase().includes(q);
      const matchReason = (c.reason || '').toLowerCase().includes(q);
      if (!matchProd && !matchAttr && !matchReason) return false;
    }
    return true;
  });

  const totalOpen = conflicts.filter((c) => c.status === 'OPEN').length;
  const criticalCount = conflicts.filter((c) => c.status === 'OPEN' && c.severity === 'CRITICAL').length;
  const highCount = conflicts.filter((c) => c.status === 'OPEN' && c.severity === 'HIGH').length;
  const resolvedCount = conflicts.filter((c) => c.status === 'RESOLVED').length;

  return (
    <div>
      {/* Header & Stats Banner */}
      <div style={{
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '800', color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldAlert size={24} color="#38BDF8" />
              Human Review & Conflict Center
            </h2>
            <p style={{ margin: '6px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
              Deterministic cross-source discrepancy detection, side-by-side evidence inspection, and immutable resolution audit trails.
            </p>
          </div>

          <button
            onClick={fetchData}
            title="Refresh review queue"
            style={{
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#38BDF8',
              padding: '8px 14px',
              borderRadius: '6px',
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <RefreshCw size={14} />
            Refresh Queue
          </button>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '12px', color: '#94A3B8' }}>Open Conflicts</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: totalOpen > 0 ? '#FBBF24' : '#34D399', marginTop: '2px' }}>
              {totalOpen}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
            <div style={{ fontSize: '12px', color: '#FCA5A5' }}>Critical Severity (Blocking)</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: criticalCount > 0 ? '#F87171' : '#34D399', marginTop: '2px' }}>
              {criticalCount}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid rgba(249, 115, 22, 0.3)' }}>
            <div style={{ fontSize: '12px', color: '#FDBA74' }}>High Severity (Blocking)</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: highCount > 0 ? '#FB923C' : '#34D399', marginTop: '2px' }}>
              {highCount}
            </div>
          </div>

          <div style={{ background: '#1E293B', padding: '14px', borderRadius: '6px', border: '1px solid rgba(52, 211, 153, 0.3)' }}>
            <div style={{ fontSize: '12px', color: '#6EE7B7' }}>Resolved & Human Verified</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: '#34D399', marginTop: '2px' }}>
              {resolvedCount}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #1E293B', paddingBottom: '12px', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('queue')}
          style={{
            background: activeTab === 'queue' ? '#2563EB' : '#1E293B',
            color: activeTab === 'queue' ? '#FFFFFF' : '#94A3B8',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <ShieldAlert size={15} />
          Active Review Queue ({filteredConflicts.length})
        </button>

        <button
          onClick={() => setActiveTab('history')}
          style={{
            background: activeTab === 'history' ? '#2563EB' : '#1E293B',
            color: activeTab === 'history' ? '#FFFFFF' : '#94A3B8',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <History size={15} />
          Resolution History & Audit Trail ({audits.length})
        </button>
      </div>

      {/* Tab 1: Active Review Queue */}
      {activeTab === 'queue' && (
        <div>
          <ReviewFilters
            severityFilter={severityFilter}
            setSeverityFilter={setSeverityFilter}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            onReset={handleResetFilters}
          />

          {loading ? (
            <LoadingState message="Fetching open cross-source review items..." />
          ) : error ? (
            <ErrorState title="Error Loading Reviews" message={error} onRetry={fetchData} />
          ) : (
            <ReviewQueue
              conflicts={filteredConflicts}
              onSelectConflict={(c) => setSelectedConflict(c)}
            />
          )}
        </div>
      )}

      {/* Tab 2: Resolution History & Audit Trail */}
      {activeTab === 'history' && (
        <div>
          {loading ? (
            <LoadingState message="Fetching immutable audit trail..." />
          ) : (
            <ReviewHistory audits={audits} />
          )}
        </div>
      )}

      {/* Side-by-Side Conflict Detail Modal */}
      {selectedConflict && (
        <ConflictDetail
          conflict={selectedConflict}
          onClose={() => setSelectedConflict(null)}
          onResolve={handleResolveConflict}
        />
      )}
    </div>
  );
}
