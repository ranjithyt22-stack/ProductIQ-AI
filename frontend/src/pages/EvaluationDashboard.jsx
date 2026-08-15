import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, Activity, ShieldCheck, Target, Layers, History, Award, AlertTriangle, FileText } from 'lucide-react';
import { api } from '../services/api';
import EvaluationOverview from '../components/EvaluationOverview';
import MetricBreakdown from '../components/MetricBreakdown';
import BenchmarkResults from '../components/BenchmarkResults';
import ConfidenceCalibration from '../components/ConfidenceCalibration';
import HallucinationReport from '../components/HallucinationReport';
import ConfusionMatrix from '../components/ConfusionMatrix';
import EvaluationRunHistory from '../components/EvaluationRunHistory';

export default function EvaluationDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [runningEval, setRunningEval] = useState(false);
  const [error, setError] = useState(null);

  const [currentRun, setCurrentRun] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [products, setProducts] = useState([]);
  const [confusionData, setConfusionData] = useState(null);
  const [runsList, setRunsList] = useState([]);
  const [baselineComparison, setBaselineComparison] = useState(null);

  const loadLatestOrSelectedRun = async (evalId = null) => {
    setLoading(true);
    setError(null);
    try {
      // List runs
      const runsRes = await api.listEvaluations(20, 0);
      const runs = runsRes.evaluations || [];
      setRunsList(runs);

      const targetId = evalId || (runs.length > 0 ? runs[0].evaluation_id : null);
      if (targetId) {
        const [runData, metricsData, productsData, confData, baseComp] = await Promise.all([
          api.getEvaluation(targetId),
          api.getEvaluationMetrics(targetId),
          api.getEvaluationProducts(targetId),
          api.getEvaluationConfusionMatrix(targetId),
          api.getBaselineComparison(targetId),
        ]);

        setCurrentRun(runData);
        setMetrics(metricsData.metrics || []);
        setProducts(productsData.products || []);
        setConfusionData(confData);
        setBaselineComparison(baseComp);
      } else {
        // If no runs exist, trigger auto first run
        await handleRunEvaluation();
      }
    } catch (err) {
      console.error('Failed to load evaluation data:', err);
      setError(err.message || 'Failed to load evaluation benchmark data.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    setRunningEval(true);
    setError(null);
    try {
      const res = await api.runEvaluation({
        datasetName: 'Industrial Benchmark v1',
        modelName: 'llama3.2:3b',
        modelProvider: 'Ollama',
      });
      await loadLatestOrSelectedRun(res.evaluation_id);
    } catch (err) {
      console.error('Evaluation run failed:', err);
      setError(err.message || 'Evaluation run failed. Please ensure backend is reachable.');
    } finally {
      setRunningEval(false);
    }
  };

  useEffect(() => {
    loadLatestOrSelectedRun();
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview & Summary', icon: Award },
    { id: 'breakdown', label: 'Metric Breakdown', icon: Activity },
    { id: 'products', label: 'Product Results', icon: FileText },
    { id: 'hallucination', label: 'Anti-Hallucination', icon: ShieldCheck },
    { id: 'calibration', label: 'Confidence Calibration', icon: Target },
    { id: 'confusion', label: 'Confusion Matrix', icon: Layers },
    { id: 'history', label: 'Run History', icon: History },
  ];

  return (
    <div className="space-y-8 pb-16">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2.5">
            AI Evaluation & Benchmark Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Empirical quality analytics, precision-recall metrics, and anti-hallucination verification across gold-standard industrial datasets.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadLatestOrSelectedRun(currentRun?.evaluation_id)}
            disabled={loading || runningEval}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={handleRunEvaluation}
            disabled={runningEval || loading}
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${runningEval ? 'animate-pulse' : ''}`} />
            {runningEval ? 'Evaluating Benchmark...' : 'Run Benchmark Evaluation'}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Content */}
      {loading && !currentRun ? (
        <div className="p-16 text-center text-slate-400 space-y-3 bg-slate-900/40 rounded-2xl border border-slate-800">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-medium">Loading benchmark evaluation metrics...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Executive Overview Banner */}
          {currentRun && <EvaluationOverview run={currentRun} />}

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-slate-800">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Panes */}
          <div className="pt-2">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <MetricBreakdown metrics={metrics} />
                <BenchmarkResults products={products} />
              </div>
            )}

            {activeTab === 'breakdown' && <MetricBreakdown metrics={metrics} />}

            {activeTab === 'products' && <BenchmarkResults products={products} />}

            {activeTab === 'hallucination' && (
              <HallucinationReport
                hallucinations={[]}
                hallucinationRate={currentRun?.hallucination_rate || 0.0}
                totalAttributes={currentRun?.total_attributes || 60}
              />
            )}

            {activeTab === 'calibration' && (
              <ConfidenceCalibration
                buckets={confusionData?.calibration_buckets}
                calibrationScore={currentRun?.confidence_calibration_score}
              />
            )}

            {activeTab === 'confusion' && (
              <ConfusionMatrix matrixData={confusionData?.confusion_matrix} />
            )}

            {activeTab === 'history' && (
              <EvaluationRunHistory
                runs={runsList}
                selectedRunId={currentRun?.evaluation_id}
                onSelectRun={(id) => loadLatestOrSelectedRun(id)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
