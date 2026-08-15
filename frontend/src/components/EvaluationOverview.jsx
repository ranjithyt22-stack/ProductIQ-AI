import React from 'react';
import { Award, ShieldCheck, Activity, Target, Zap, CheckCircle2, XCircle } from 'lucide-react';
import MetricCard from './MetricCard';

export default function EvaluationOverview({ run }) {
  if (!run) {
    return null;
  }

  const isGatePass = run.quality_gate_status === 'PASS';

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-700/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-widest px-2.5 py-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              {run.dataset_name} (v{run.dataset_version || '1.0'})
            </span>
            <span className="text-xs font-mono text-slate-400">
              Model: {run.model_name} ({run.model_provider})
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 mt-2 flex items-center gap-2">
            AI Evaluation & Benchmark Performance
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluated {run.total_products} industrial products across {run.total_attributes} ground-truth technical specifications.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Quality Gate</div>
            <div className="flex items-center gap-1.5 mt-1">
              {isGatePass ? (
                <span className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  <CheckCircle2 className="w-4 h-4 mr-1.5" /> PASSED
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                  <XCircle className="w-4 h-4 mr-1.5" /> FAILED
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Overall Quality"
          value={run.overall_score}
          unit="%"
          subtitle="Composite benchmark score"
          status="pass"
          icon={Award}
        />
        <MetricCard
          title="Extraction F1"
          value={run.extraction_f1}
          unit="%"
          subtitle={`P: ${run.extraction_precision}% | R: ${run.extraction_recall}%`}
          status="pass"
          icon={Target}
        />
        <MetricCard
          title="Value Accuracy"
          value={run.value_accuracy}
          unit="%"
          subtitle="Normalized quantity match"
          status="pass"
          icon={Zap}
        />
        <MetricCard
          title="Evidence Coverage"
          value={run.evidence_coverage}
          unit="%"
          subtitle="Verbatim source citations"
          status="pass"
          icon={ShieldCheck}
        />
        <MetricCard
          title="Hallucination Rate"
          value={run.hallucination_rate}
          unit="%"
          subtitle="Ungrounded attribute rate"
          status={run.hallucination_rate === 0 ? 'pass' : 'fail'}
          icon={Activity}
        />
        <MetricCard
          title="Commerce Accuracy"
          value={run.commerce_readiness_accuracy}
          unit="%"
          subtitle="Readiness state alignment"
          status="pass"
          icon={CheckCircle2}
        />
      </div>
    </div>
  );
}
