import React, { useState, useEffect } from 'react';
import { Search, Filter, Layers, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function ProductSearch({ initialQuery = '', onSelectProduct = null }) {
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState('');
  const [readiness, setReadiness] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [totalCount, setTotalCount] = useState(0);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query.trim()) params.append('q', query.trim());
      if (category) params.append('category', category);
      if (readiness) params.append('commerce_status', readiness);

      const endpoint = `/api/v1/search?${params.toString()}`;
      const res = await (api.request ? api.request(endpoint) : null);
      if (res) {
        setResults(res.products || []);
        setTotalCount(res.total_count || 0);
      }
    } catch (err) {
      console.error('Search query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', margin: 0 }}>
          Global Product & Specification Search
        </h1>
        <p style={{ fontSize: '13px', color: '#94A3B8', margin: '4px 0 0 0' }}>
          Multi-attribute filtering across stored products, part numbers, manufacturers, and technical specifications.
        </p>
      </div>

      {/* Filter Form */}
      <form onSubmit={handleSearch} style={{
        backgroundColor: '#1E293B',
        border: '1px solid #334155',
        borderRadius: '8px',
        padding: '16px',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        alignItems: 'center'
      }}>
        <div style={{ flex: '1 1 240px', position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '10px', color: '#64748B' }} />
          <input
            type="text"
            placeholder="Search attribute name, value, part code, or manufacturer..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              width: '100%',
              backgroundColor: '#0F172A',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '8px 12px 8px 36px',
              fontSize: '13px',
              color: '#F8FAFC',
              outline: 'none'
            }}
          />
        </div>

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{
            backgroundColor: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '8px 12px',
            fontSize: '13px',
            color: '#F8FAFC',
            outline: 'none'
          }}
        >
          <option value="">All Categories</option>
          <option value="Pneumatic Cylinder">Pneumatic Cylinder</option>
          <option value="Solenoid Valve">Solenoid Valve</option>
          <option value="Temperature Sensor">Temperature Sensor</option>
          <option value="Industrial Bearing">Industrial Bearing</option>
          <option value="Electric Motor">Electric Motor</option>
          <option value="Hydraulic Pump">Hydraulic Pump</option>
        </select>

        <select
          value={readiness}
          onChange={(e) => setReadiness(e.target.value)}
          style={{
            backgroundColor: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '8px 12px',
            fontSize: '13px',
            color: '#F8FAFC',
            outline: 'none'
          }}
        >
          <option value="">All Commerce Statuses</option>
          <option value="READY_FOR_COMMERCE">Ready for Commerce</option>
          <option value="REVIEW_REQUIRED">Review Required</option>
          <option value="NOT_READY">Not Ready</option>
        </select>

        <button
          type="submit"
          disabled={loading}
          style={{
            backgroundColor: '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Search size={14} /> Search
        </button>
      </form>

      {/* Results Table */}
      <div style={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #334155', fontSize: '12px', color: '#94A3B8' }}>
          Found {totalCount} matching catalog products
        </div>

        {results.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead style={{ backgroundColor: '#0F172A', color: '#94A3B8', fontSize: '11px', textTransform: 'uppercase' }}>
              <tr>
                <th style={{ padding: '10px 16px' }}>Part Code / ID</th>
                <th style={{ padding: '10px 16px' }}>Product Name</th>
                <th style={{ padding: '10px 16px' }}>Manufacturer</th>
                <th style={{ padding: '10px 16px' }}>Category</th>
                <th style={{ padding: '10px 16px', textAlign: 'center' }}>Quality Score</th>
                <th style={{ padding: '10px 16px', textAlign: 'center' }}>Commerce Status</th>
              </tr>
            </thead>
            <tbody style={{ color: '#F8FAFC' }}>
              {results.map((p) => (
                <tr key={p.product_id} style={{ borderBottom: '1px solid #334155' }}>
                  <td style={{ padding: '12px 16px', fontFamily: 'monospace', color: '#06B6D4' }}>
                    {p.product_code || p.product_id}
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: '600' }}>{p.product_name}</td>
                  <td style={{ padding: '12px 16px', color: '#94A3B8' }}>{p.manufacturer}</td>
                  <td style={{ padding: '12px 16px', color: '#94A3B8' }}>{p.category}</td>
                  <td style={{ padding: '12px 16px', textAlign: 'center', fontFamily: 'monospace', fontWeight: '700' }}>
                    {p.quality_score}%
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: '700',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontFamily: 'monospace',
                      backgroundColor: p.commerce_readiness === 'READY_FOR_COMMERCE' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: p.commerce_readiness === 'READY_FOR_COMMERCE' ? '#10B981' : '#F59E0B',
                      border: `1px solid ${p.commerce_readiness === 'READY_FOR_COMMERCE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
                    }}>
                      {p.commerce_readiness}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 16px', color: '#64748B', fontSize: '13px' }}>
            No products matching the search query. Try broadening your keyword criteria.
          </div>
        )}
      </div>
    </div>
  );
}
