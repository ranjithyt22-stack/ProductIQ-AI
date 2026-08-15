/**
 * Centralized REST API Service for ProductIQ AI Frontend.
 * Connects React frontend components to FastAPI backend endpoints.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, options);
  
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errData = await response.json();
      errorDetail = errData.detail || JSON.stringify(errData);
    } catch (e) {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }
  
  return await response.json();
}

export const apiService = {
  // System Health
  async healthCheck() {
    return request('/health');
  },

  // State Management
  async getState() {
    return request('/state');
  },

  async resetState() {
    return request('/state/reset', { method: 'POST' });
  },

  async getConflicts() {
    return request('/conflicts');
  },

  // Product Analysis Endpoints
  async analyzeProduct({ manufacturer, productName, productCode, description, productUrl, file }) {
    const formData = new FormData();
    if (manufacturer) formData.append('manufacturer', manufacturer);
    if (productName) formData.append('product_name', productName);
    if (productCode) formData.append('product_code', productCode);
    if (description) formData.append('description', description);
    if (productUrl) formData.append('product_url', productUrl);
    if (file) formData.append('file', file);

    return request('/analyze', {
      method: 'POST',
      body: formData,
    });
  },

  async analyzeUrl({ url, manufacturer, productName, productCode }) {
    return request('/analyze/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        manufacturer,
        product_name: productName,
        product_code: productCode,
      }),
    });
  },

  async analyzeFile({ file, manufacturer, productName, productCode }) {
    const formData = new FormData();
    formData.append('file', file);
    if (manufacturer) formData.append('manufacturer', manufacturer);
    if (productName) formData.append('product_name', productName);
    if (productCode) formData.append('product_code', productCode);

    return request('/analyze/file', {
      method: 'POST',
      body: formData,
    });
  },

  async analyzeText({ text, manufacturer, productName, productCode }) {
    return request('/analyze/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        manufacturer,
        product_name: productName,
        product_code: productCode,
      }),
    });
  },

  async analyzeMultiSource({ files, urls, text, manufacturer, productName, productCode }) {
    const formData = new FormData();
    if (files && files.length > 0) {
      files.forEach((f) => formData.append('files', f));
    }
    if (urls && urls.length > 0) {
      formData.append('urls', urls.join(','));
    }
    if (text) formData.append('text', text);
    if (manufacturer) formData.append('manufacturer', manufacturer);
    if (productName) formData.append('product_name', productName);
    if (productCode) formData.append('product_code', productCode);

    return request('/analyze/multi-source', {
      method: 'POST',
      body: formData,
    });
  },

  // Standalone Validation & Enrichment
  async validateProduct(product, specifications, userMetadata) {
    return request('/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product,
        specifications,
        user_metadata: userMetadata,
      }),
    });
  },

  async enrichProduct(product, specifications) {
    return request('/enrich', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product, specifications }),
    });
  },

  // Single Product & Catalog Retrieval
  async getProduct(productId) {
    return request(`/product/${productId}`);
  },

  async reviewProduct(productId, attributeName, reviewedValue, reviewedUnit) {
    return request(`/product/${productId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        attribute_name: attributeName,
        reviewed_value: reviewedValue,
        reviewed_unit: reviewedUnit,
      }),
    });
  },

  // Catalog Engine Endpoints
  async analyzeCatalog(csvFile) {
    const formData = new FormData();
    formData.append('file', csvFile);

    return request('/catalog/analyze', {
      method: 'POST',
      body: formData,
    });
  },

  async getCatalog(catalogId) {
    return request(`/catalog/${catalogId}`);
  },

  // Conflict Detection & Human Review Endpoints
  async getProductConflicts(productId, { status, severity } = {}) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request(`/api/v1/products/${productId}/conflicts${qs}`);
  },

  async getProductConflictDetail(productId, conflictId) {
    return request(`/api/v1/products/${productId}/conflicts/${conflictId}`);
  },

  async resolveProductConflict(productId, conflictId, { action, resolution_value, resolution_unit, reason, notes, reviewer }) {
    return request(`/api/v1/products/${productId}/conflicts/${conflictId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action,
        resolution_value,
        resolution_unit,
        reason,
        notes,
        reviewer: reviewer || 'Reviewer 1',
      }),
    });
  },

  async listReviews({ status, severity, productId, limit = 50, offset = 0 } = {}) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    if (productId) params.append('product_id', productId);
    params.append('limit', limit);
    params.append('offset', offset);
    return request(`/api/v1/reviews?${params.toString()}`);
  },

  async getReviewDetail(reviewId) {
    return request(`/api/v1/reviews/${reviewId}`);
  },

  async resolveReview(reviewId, { reviewed_value, reviewed_unit, verification_note, reviewer_id }) {
    return request(`/api/v1/reviews/${reviewId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reviewed_value,
        reviewed_unit,
        verification_note,
        reviewer_id: reviewer_id || 'Reviewer 1',
      }),
    });
  },

  async getReviewAudits(productId = null) {
    const qs = productId ? `?product_id=${productId}` : '';
    return request(`/api/v1/reviews/audits/history${qs}`);
  },

  // ============================================================
  // PHASE 4: EVALUATION & BENCHMARKING ENDPOINTS
  // ============================================================
  async runEvaluation({ datasetName, modelName, modelProvider, thresholds } = {}) {
    return request('/api/v1/evaluations/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_name: datasetName || 'Industrial Benchmark v1',
        model_name: modelName || 'llama3.2:3b',
        model_provider: modelProvider || 'Ollama',
        thresholds: thresholds || null,
      }),
    });
  },

  async listEvaluations(limit = 50, offset = 0) {
    return request(`/api/v1/evaluations?limit=${limit}&offset=${offset}`);
  },

  async getEvaluation(evaluationId) {
    return request(`/api/v1/evaluations/${evaluationId}`);
  },

  async getEvaluationMetrics(evaluationId) {
    return request(`/api/v1/evaluations/${evaluationId}/metrics`);
  },

  async getEvaluationProducts(evaluationId) {
    return request(`/api/v1/evaluations/${evaluationId}/products`);
  },

  async getEvaluationReport(evaluationId) {
    return request(`/api/v1/evaluations/${evaluationId}/report`);
  },

  async getEvaluationConfusionMatrix(evaluationId) {
    return request(`/api/v1/evaluations/${evaluationId}/confusion-matrix`);
  },

  async getBaselineComparison(evaluationId = null) {
    const qs = evaluationId ? `?evaluation_id=${evaluationId}` : '';
    return request(`/api/v1/evaluations/baseline/compare${qs}`);
  },

  // Export URLs & Helpers
  getExportJsonUrl(productId) {
    return `${API_BASE_URL}/product/${productId}/export/json`;
  },

  getExportCsvUrl(productId) {
    return `${API_BASE_URL}/product/${productId}/export/csv`;
  },

  getCatalogExportJsonUrl(catalogId) {
    return `${API_BASE_URL}/catalog/${catalogId}/export/json`;
  },

  getCatalogExportCsvUrl(catalogId) {
    return `${API_BASE_URL}/catalog/${catalogId}/export/csv`;
  },
};

export const api = apiService;
export default apiService;



