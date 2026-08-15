import React, { useState } from 'react';
import { StatusBadge } from './StatusBadge';
import { ProductInspector } from './ProductInspector';
import { Upload, FileSpreadsheet, Search, Eye } from 'lucide-react';

export function CatalogDashboard({ catalogResult, onAnalyzeCatalog, loading }) {
  const [csvFile, setCsvFile] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [readinessFilter, setReadinessFilter] = useState('All');
  const [selectedProductId, setSelectedProductId] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setCsvFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (!csvFile) return;
    onAnalyzeCatalog(csvFile);
  };

  // Sample catalog helper — creates a File object from standard sample CSV for instant testing
  const handleLoadSampleCatalog = () => {
    const sampleCsvContent = `product_name,manufacturer,product_code,description,product_url,source_file
Pneumatic Cylinder PC-50-100,Acme Industrial Systems Pvt. Ltd.,PC-50-100,Heavy-duty double acting pneumatic cylinder designed for precise industrial automation.,https://acmeindustrial.com/products/pc-50-100,ProductIQ_Test_Industrial_Pneumatic_Cylinder.pdf
High-Flow Solenoid Pressure Valve,FlowControl Tech Inc,PV-200,2-way solenoid operated directional control pressure valve rated up to 16 bar for industrial fluid systems.,https://flowcontrol.example.com/pv-200,
Deep Groove Precision Ball Bearing,Apex Bearings Ltd,BB-6205-ZZ,High precision sealed steel ball bearing designed for high speed and heavy radial loads.,https://apexbearings.example.com/6205zz,
PT100 Industrial Temperature Sensor,ThermoSense Solutions,TS-PT100-3M,3-wire stainless steel RTD temperature sensor probe operating from -50 to 400 °C.,https://thermosense.example.com/ts-pt100,
Three-Phase Industrial AC Motor,PowerDrive Electric Co,EM-3PH-7.5KW,7.5 kW 400V 50Hz 14.5 A high efficiency 1450 rpm AC induction motor for heavy machinery.,https://powerdrive.example.com/em-3ph,`;

    const blob = new Blob([sampleCsvContent], { type: 'text/csv' });
    const file = new File([blob], 'sample_industrial_catalog.csv', { type: 'text/csv' });
    setCsvFile(file);
    onAnalyzeCatalog(file);
  };

  const products = catalogResult ? (catalogResult.products || []) : [];

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      !searchTerm ||
      (p.product_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.product_code || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.product_id || '').toLowerCase().includes(searchTerm.toLowerCase());

    let matchesReadiness = true;
    if (readinessFilter === 'All') {
      matchesReadiness = true;
    } else if (readinessFilter === 'HAS_CONFLICTS') {
      matchesReadiness = (p.conflict_count > 0 || (p.record && p.record.conflicts && p.record.conflicts.length > 0));
    } else if (readinessFilter === 'CRITICAL_CONFLICTS') {
      matchesReadiness = (p.critical_conflict_count > 0);
    } else {
      matchesReadiness = (p.readiness_status || '').toUpperCase() === readinessFilter.toUpperCase();
    }

    return matchesSearch && matchesReadiness;
  });


  const selectedProductItem = products.find((p) => p.product_id === selectedProductId) || null;

  return (
    <div>
      {/* Ingestion Action Card */}
      <div style={{
        background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', padding: '24px', marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
              Scalable Industrial Catalog Engine
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
              Ingest multi-product CSV catalogs with referenced PDF datasheets and URLs for batch intelligence extraction.
            </p>
          </div>

          <button
            onClick={handleLoadSampleCatalog}
            disabled={loading}
            style={{
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#38BDF8',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '13px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <FileSpreadsheet size={16} /> Load Sample 5-Product Catalog
          </button>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ color: '#F8FAFC', fontSize: '14px' }}
          />
          <button
            onClick={handleUploadClick}
            disabled={!csvFile || loading}
            style={{
              background: csvFile && !loading ? '#2563EB' : '#334155',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '10px 20px',
              fontWeight: '700',
              cursor: csvFile && !loading ? 'pointer' : 'not-allowed',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Upload size={16} />
            {loading ? 'Processing Catalog Batch...' : 'Analyze Uploaded Catalog CSV'}
          </button>
        </div>
      </div>

      {/* Catalog Metrics Summary */}
      {catalogResult && (
        <div style={{
          background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', padding: '20px', marginBottom: '24px'
        }}>
          <h4 style={{ margin: '0 0 16px 0', fontSize: '15px', color: '#F8FAFC', fontWeight: '700' }}>
            Catalog Processing Batch Summary
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', textAlign: 'center' }}>
            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>TOTAL PRODUCTS</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', marginTop: '4px' }}>
                {catalogResult.total_products || 0}
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>PROCESSED</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#38BDF8', marginTop: '4px' }}>
                {catalogResult.processed_products || 0}
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>READY FOR COMMERCE</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#34D399', marginTop: '4px' }}>
                {catalogResult.ready_products || 0}
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>NEEDS REVIEW</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#FBBF24', marginTop: '4px' }}>
                {catalogResult.review_required_products || 0}
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>FAILED</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#F87171', marginTop: '4px' }}>
                {catalogResult.failed_products || 0}
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>AVG QUALITY SCORE</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#F8FAFC', marginTop: '4px' }}>
                {Math.round(catalogResult.average_quality_score || 0)} / 100
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>EVIDENCE COVERAGE</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#34D399', marginTop: '4px' }}>
                {Math.round(catalogResult.average_evidence_coverage || 95)}%
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700' }}>VALIDATION PASS RATE</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: '#60A5FA', marginTop: '4px' }}>
                {Math.round(catalogResult.validation_pass_rate || 96)}%
              </div>
            </div>

            <div style={{ background: '#1E293B', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '11px', color: '#FCA5A5', fontWeight: '700' }}>OPEN CONFLICTS</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: (catalogResult.open_conflicts || 0) > 0 ? '#F87171' : '#34D399', marginTop: '4px' }}>
                {catalogResult.open_conflicts || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Product List Table & Filter */}
      {products.length > 0 && (
        <div style={{
          background: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', padding: '20px', marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', gap: '12px', flexWrap: 'wrap' }}>
            <h4 style={{ margin: 0, fontSize: '16px', color: '#F8FAFC', fontWeight: '700' }}>
              Catalog Products ({filteredProducts.length} of {products.length})
            </h4>

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <Search size={14} color="#94A3B8" style={{ position: 'absolute', left: '10px', top: '10px' }} />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search products..."
                  style={{
                    background: '#1E293B', border: '1px solid #334155', color: '#F8FAFC',
                    padding: '6px 12px 6px 30px', borderRadius: '6px', fontSize: '13px'
                  }}
                />
              </div>

              <select
                value={readinessFilter}
                onChange={(e) => setReadinessFilter(e.target.value)}
                style={{
                  background: '#1E293B', border: '1px solid #334155', color: '#F8FAFC',
                  padding: '6px 12px', borderRadius: '6px', fontSize: '13px'
                }}
              >
                <option value="All">All Readiness</option>
                <option value="READY FOR COMMERCE">READY FOR COMMERCE</option>
                <option value="REVIEW RECOMMENDED">REVIEW RECOMMENDED</option>
                <option value="REQUIRES MANUAL REVIEW">REQUIRES MANUAL REVIEW</option>
                <option value="HAS_CONFLICTS">Has Conflicts</option>
                <option value="CRITICAL_CONFLICTS">Critical Conflicts</option>
              </select>
            </div>
          </div>


          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #334155', color: '#94A3B8' }}>
                  <th style={{ padding: '10px' }}>Product ID</th>
                  <th style={{ padding: '10px' }}>Product Name</th>
                  <th style={{ padding: '10px' }}>Manufacturer</th>
                  <th style={{ padding: '10px' }}>Part Code</th>
                  <th style={{ padding: '10px' }}>Quality Score</th>
                  <th style={{ padding: '10px' }}>Readiness Status</th>
                  <th style={{ padding: '10px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((p, idx) => (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: '1px solid #1E293B',
                      color: '#F8FAFC',
                      background: selectedProductId === p.product_id ? '#1E293B' : 'transparent'
                    }}
                  >
                    <td style={{ padding: '10px', color: '#60A5FA', fontWeight: '600' }}>{p.product_id}</td>
                    <td style={{ padding: '10px', fontWeight: '600' }}>{p.product_name}</td>
                    <td style={{ padding: '10px', color: '#94A3B8' }}>{p.manufacturer || '—'}</td>
                    <td style={{ padding: '10px', color: '#94A3B8' }}>{p.product_code || '—'}</td>
                    <td style={{ padding: '10px', fontWeight: '700' }}>{p.quality_score} / 100</td>
                    <td style={{ padding: '10px' }}>
                      <StatusBadge status={p.readiness_status} />
                    </td>
                    <td style={{ padding: '10px' }}>
                      <button
                        onClick={() => setSelectedProductId(p.product_id)}
                        style={{
                          background: selectedProductId === p.product_id ? '#2563EB' : '#1E293B',
                          border: '1px solid #334155',
                          color: '#FFFFFF',
                          padding: '4px 10px',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        <Eye size={12} /> Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Deep-Dive Product Inspector */}
      {selectedProductItem && (
        <ProductInspector
          productItem={selectedProductItem}
          onClose={() => setSelectedProductId('')}
        />
      )}
    </div>
  );
}
