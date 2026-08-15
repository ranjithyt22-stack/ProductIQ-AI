import React, { useState } from 'react';
import { apiService } from '../services/api';
import { CatalogDashboard } from '../components/CatalogDashboard';
import { ErrorState } from '../components/ErrorState';

export function CatalogEngine() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [catalogResult, setCatalogResult] = useState(null);

  const handleAnalyzeCatalog = async (csvFile) => {
    if (!csvFile) return;

    setLoading(true);
    setError(null);

    try {
      const result = await apiService.analyzeCatalog(csvFile);
      setCatalogResult(result);
    } catch (err) {
      setError(err.message || 'Failed to process catalog batch.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <ErrorState title="Catalog Processing Error" message={error} />}

      <CatalogDashboard
        catalogResult={catalogResult}
        onAnalyzeCatalog={handleAnalyzeCatalog}
        loading={loading}
      />
    </div>
  );
}
