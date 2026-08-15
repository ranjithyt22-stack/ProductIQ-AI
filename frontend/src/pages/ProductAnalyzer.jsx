import React, { useState, useRef } from 'react';
import { apiService } from '../services/api';
import { FileUploader } from '../components/FileUploader';
import { UrlInput } from '../components/UrlInput';
import { TextInput } from '../components/TextInput';
import { SourceList } from '../components/SourceList';
import { ProcessingPipeline } from '../components/ProcessingPipeline';
import { ProductOverview } from '../components/ProductOverview';
import { QualityScore } from '../components/QualityScore';
import { Specifications } from '../components/Specifications';
import { AttributeIntelligence } from '../components/AttributeIntelligence';
import { DataLineage } from '../components/DataLineage';
import { EvidencePanel } from '../components/EvidencePanel';
import { SourceComparison } from '../components/SourceComparison';
import { ValidationPanel } from '../components/ValidationPanel';
import { CompletenessPanel } from '../components/CompletenessPanel';
import { EnrichmentPanel } from '../components/EnrichmentPanel';
import { CommerceReadyPanel } from '../components/CommerceReadyPanel';
import { HumanReview } from '../components/HumanReview';
import { ExportPanel } from '../components/ExportPanel';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { Play, RotateCcw, Sparkles, AlertCircle, Info, ShieldAlert } from 'lucide-react';

const EMPTY_ANALYSIS = { loading: false, error: null, record: null };

export function ProductAnalyzer({ onNavigateToReview }) {
  // --- Source State ---
  const [files, setFiles] = useState([]);
  const [urls, setUrls] = useState([]);
  const [text, setText] = useState('');

  // --- Optional user metadata hints ---
  const [manufacturer, setManufacturer] = useState('');
  const [productName, setProductName] = useState('');
  const [productCode, setProductCode] = useState('');

  // --- Analysis State ---
  const [analysis, setAnalysis] = useState(EMPTY_ANALYSIS);
  const [selectedAttribute, setSelectedAttribute] = useState(null);

  // Prevent duplicate execution
  const analyzingRef = useRef(false);

  // Reset analysis when source files/urls change
  const clearAnalysisResult = () => {
    setAnalysis(EMPTY_ANALYSIS);
    setSelectedAttribute(null);
  };

  // --- Source Handlers ---
  const handleFilesSelected = (newFiles) => {
    setFiles(newFiles);
    clearAnalysisResult();
  };

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    clearAnalysisResult();
  };

  const handleAddUrl = (newUrl) => {
    setUrls((prev) => [...prev, newUrl]);
    clearAnalysisResult();
  };

  const handleRemoveUrl = (index) => {
    setUrls((prev) => prev.filter((_, i) => i !== index));
    clearAnalysisResult();
  };

  const handleTextChange = (newText) => {
    setText(newText);
  };

  const handleClearText = () => {
    setText('');
    clearAnalysisResult();
  };

  // --- Explicit Demo Sample Loader ---
  const handleLoadSample = () => {
    const sampleText = `ACME INDUSTRIAL SYSTEMS PVT. LTD.
Product Name: Pneumatic Cylinder PC-50-100
Manufacturer: Acme Industrial Systems Pvt. Ltd.
Product Code: PC-50-100
Category: Pneumatic Cylinder
Description: Heavy-duty double acting pneumatic cylinder designed for precise industrial automation.

TECHNICAL SPECIFICATIONS:
- Bore Diameter: 50 mm
- Stroke Length: 100 mm
- Operating Pressure: 1 to 10 bar
- Operating Temperature: -20 to 80 degC
- Port Size: G 1/4 inch
- Cushioning: Adjustable pneumatic cushioning on both ends
- Fluid Type: Filtered lubricated or non-lubricated compressed air
- Mounting Type: Foot mount / Flange mount

RECOMMENDED INDUSTRIAL APPLICATIONS:
- Packaging machinery
- Assembly automation lines
- Material handling systems
- Pick and place industrial robotics

COMPLIANCE & CERTIFICATIONS:
- ISO 15552 standard compliant
- CE Certified`;

    setText(sampleText);
    setManufacturer('Acme Industrial Systems Pvt. Ltd.');
    setProductName('Pneumatic Cylinder PC-50-100');
    setProductCode('PC-50-100');
    setFiles([]);
    setUrls([]);
    clearAnalysisResult();
  };

  // --- Clear / Reset All ---
  const handleNewAnalysis = () => {
    setFiles([]);
    setUrls([]);
    setText('');
    setManufacturer('');
    setProductName('');
    setProductCode('');
    setAnalysis(EMPTY_ANALYSIS);
    setSelectedAttribute(null);
    analyzingRef.current = false;
    const fileInput = document.getElementById('file-upload-input');
    if (fileInput) fileInput.value = '';
  };

  // --- Analyze Trigger ---
  const handleAnalyze = async () => {
    if (files.length === 0 && urls.length === 0 && !text.trim()) {
      setAnalysis({
        loading: false,
        error: 'Please provide at least one source document (File, Webpage URL, or Text Description).',
        record: null,
      });
      return;
    }

    if (analyzingRef.current) return;
    analyzingRef.current = true;

    setAnalysis({ loading: true, error: null, record: null });
    setSelectedAttribute(null);

    try {
      let result = null;

      const hasMultipleSources =
        files.length > 1 ||
        (files.length > 0 && (urls.length > 0 || text.trim())) ||
        urls.length > 1 ||
        (urls.length > 0 && text.trim());

      if (hasMultipleSources) {
        result = await apiService.analyzeMultiSource({
          files,
          urls,
          text: text.trim(),
          manufacturer: manufacturer.trim() || undefined,
          productName: productName.trim() || undefined,
          productCode: productCode.trim() || undefined,
        });
      } else if (files.length === 1) {
        result = await apiService.analyzeFile({
          file: files[0],
          manufacturer: manufacturer.trim() || undefined,
          productName: productName.trim() || undefined,
          productCode: productCode.trim() || undefined,
        });
      } else if (urls.length === 1) {
        result = await apiService.analyzeUrl({
          url: urls[0],
          manufacturer: manufacturer.trim() || undefined,
          productName: productName.trim() || undefined,
          productCode: productCode.trim() || undefined,
        });
      } else if (text.trim()) {
        result = await apiService.analyzeText({
          text: text.trim(),
          manufacturer: manufacturer.trim() || undefined,
          productName: productName.trim() || undefined,
          productCode: productCode.trim() || undefined,
        });
      }

      setAnalysis({ loading: false, error: null, record: result });
    } catch (err) {
      setAnalysis({
        loading: false,
        error: err.message || 'Failed to execute product analysis. Please verify your source inputs.',
        record: null,
      });
    } finally {
      analyzingRef.current = false;
    }
  };

  // --- Human Review Override ---
  const handleApplyReview = async (reviewData) => {
    if (!analysis.record || !analysis.record.product_id) return;
    const attrName = reviewData.attribute_name;
    const reviewedValue = reviewData.reviewed_value;
    const reviewedUnit = reviewData.reviewed_unit;

    try {
      const updatedRecord = await apiService.reviewProduct(
        analysis.record.product_id,
        attrName,
        reviewedValue,
        reviewedUnit
      );
      setAnalysis((prev) => ({ ...prev, record: updatedRecord }));

      // Update active selected attribute in drawer
      if (selectedAttribute && selectedAttribute.name.toLowerCase() === attrName.toLowerCase()) {
        setSelectedAttribute((prev) => ({
          ...prev,
          value: reviewedValue,
          unit: reviewedUnit,
          confidence: 100,
          confidence_level: 'HIGH',
          review_status: 'human_verified',
          review_required: false
        }));
      }
    } catch (err) {
      console.error('Human review error:', err.message);
    }
  };

  const hasSourceSelected = files.length > 0 || urls.length > 0 || text.trim().length > 0;
  const { loading, error, record } = analysis;

  const currentExplainability = (record && record.explainability && selectedAttribute)
    ? record.explainability.find((x) => x.attribute_name.toLowerCase() === selectedAttribute.name.toLowerCase())
    : null;

  return (
    <div>
      {/* Input Section Card */}
      <div style={{
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#F8FAFC' }}>
              Single Product Intelligence Input
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94A3B8' }}>
              Upload technical documents (PDF, DOCX, CSV, Excel, TXT, Image), product URLs, or raw specifications.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleLoadSample}
              title="Load demo industrial specification sample"
              style={{
                background: '#1E293B',
                color: '#38BDF8',
                border: '1px solid #334155',
                borderRadius: '6px',
                padding: '6px 14px',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Sparkles size={14} />
              Load Sample Data
            </button>

            {(hasSourceSelected || record) && (
              <button
                onClick={handleNewAnalysis}
                title="Clear all sources and analysis results"
                style={{
                  background: 'transparent',
                  color: '#94A3B8',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  padding: '6px 14px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <RotateCcw size={14} />
                Clear / New Analysis
              </button>
            )}
          </div>
        </div>

        {/* Optional Metadata Hints */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
              Manufacturer (Optional Hint)
            </label>
            <input
              type="text"
              value={manufacturer}
              onChange={(e) => setManufacturer(e.target.value)}
              placeholder="e.g. Acme Industrial Systems"
              style={{
                width: '100%', background: '#1E293B', border: '1px solid #334155',
                color: '#F8FAFC', padding: '8px 12px', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
              Product Name (Optional Hint)
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g. High Pressure Control Valve"
              style={{
                width: '100%', background: '#1E293B', border: '1px solid #334155',
                color: '#F8FAFC', padding: '8px 12px', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', color: '#94A3B8', fontWeight: '600', marginBottom: '4px' }}>
              Part / SKU Code (Optional Hint)
            </label>
            <input
              type="text"
              value={productCode}
              onChange={(e) => setProductCode(e.target.value)}
              placeholder="e.g. PV-50-100"
              style={{
                width: '100%', background: '#1E293B', border: '1px solid #334155',
                color: '#F8FAFC', padding: '8px 12px', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box'
              }}
            />
          </div>
        </div>

        {/* Input Sources */}
        <FileUploader
          files={files}
          onFilesSelected={handleFilesSelected}
          onRemoveFile={handleRemoveFile}
        />

        <UrlInput
          urls={urls}
          onAddUrl={handleAddUrl}
          onRemoveUrl={handleRemoveUrl}
        />

        <TextInput
          value={text}
          onChange={handleTextChange}
        />

        <SourceList
          files={files}
          urls={urls}
          text={text}
          onRemoveFile={handleRemoveFile}
          onRemoveUrl={handleRemoveUrl}
          onClearText={handleClearText}
        />

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: '100%',
            background: loading ? '#1E3A6E' : '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            padding: '14px 24px',
            fontSize: '16px',
            fontWeight: '700',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
        >
          <Play size={18} />
          {loading ? 'Analyzing Product Intelligence...' : 'Analyze Single Product with AI'}
        </button>
      </div>

      {/* Loading State with Visible Processing Pipeline */}
      {loading && (
        <div>
          <ProcessingPipeline isProcessing={true} isCompleted={false} />
          <LoadingState message="Extracting technical specifications, verifying evidence, and computing quality score..." />
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <ErrorState
          title="Analysis Failed"
          message={error}
          onRetry={handleAnalyze}
        />
      )}

      {/* Empty State */}
      {!record && !loading && !error && (
        <EmptyState onLoadSample={handleLoadSample} />
      )}

      {/* Analysis Results Display */}
      {record && !loading && (
        <div>
          <ProcessingPipeline isProcessing={false} isCompleted={true} />
          <QualityScore scoreObj={record.quality_score} />

          {/* Cross-Source Conflict Alert Banner */}
          {record.conflicts && record.conflicts.length > 0 && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <ShieldAlert size={24} color="#F87171" />
                <div>
                  <div style={{ fontWeight: '800', color: '#F87171', fontSize: '15px' }}>
                    {record.conflicts.length} Cross-Source Conflict{record.conflicts.length > 1 ? 's' : ''} Detected
                  </div>
                  <div style={{ fontSize: '12px', color: '#CBD5E1', marginTop: '2px' }}>
                    Multi-source inputs contain conflicting parameter values requiring human verification before commerce publication.
                  </div>
                </div>
              </div>

              {onNavigateToReview && (
                <button
                  onClick={onNavigateToReview}
                  style={{
                    background: '#DC2626',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: '700',
                    cursor: 'pointer'
                  }}
                >
                  Resolve in Review Center
                </button>
              )}
            </div>
          )}

          <ProductOverview product={record.product} enrichment={record.enrichment} />

          <Specifications
            specifications={record.specifications}
            onSelectAttribute={(spec) => setSelectedAttribute(spec)}
            selectedAttributeName={selectedAttribute?.name}
          />
          <DataLineage
            specifications={record.specifications}
            sources={record.raw_sources}
            product={record.product}
          />
          <EvidencePanel
            specifications={record.specifications}
            sources={record.raw_sources}
            enrichment={record.enrichment}
          />
          <SourceComparison
            rawSources={record.raw_sources}
            validations={record.validation}
            specifications={record.specifications}
          />
          <ValidationPanel validationResults={record.validation} />
          <CompletenessPanel
            product={record.product}
            specifications={record.specifications}
            qualityScore={record.quality_score}
          />
          <EnrichmentPanel enrichment={record.enrichment} />
          <CommerceReadyPanel record={record} />
          <HumanReview record={record} onApplyReview={(attr, val, unit) => handleApplyReview({ attribute_name: attr, reviewed_value: val, reviewed_unit: unit })} />
          <ExportPanel productId={record.product_id} record={record} />
        </div>
      )}

      {/* Interactive Attribute Intelligence Drawer */}
      {selectedAttribute && (
        <AttributeIntelligence
          attribute={selectedAttribute}
          explainability={currentExplainability}
          onClose={() => setSelectedAttribute(null)}
          onSaveReview={handleApplyReview}
        />
      )}
    </div>
  );
}
