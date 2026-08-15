import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

export default function MetricBreakdown({ metrics = [] }) {
  if (!metrics || metrics.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 bg-slate-900/50 rounded-xl border border-slate-800">
        No metric breakdown data available for this run.
      </div>
    );
  }

  const categories = Array.from(new Set(metrics.map(m => m.metric_category)));

  return (
    <div className="space-y-6">
      {categories.map(cat => {
        const catMetrics = metrics.filter(m => m.metric_category === cat);
        return (
          <div key={cat} className="bg-slate-900/60 rounded-xl border border-slate-800 p-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              {cat} Metrics
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {catMetrics.map(m => {
                const isHalluc = m.metric_name.toLowerCase().includes('hallucination');
                const passed = m.passed_gate;

                return (
                  <div key={m.metric_name} className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/60 flex items-start justify-between">
                    <div>
                      <div className="text-xs text-slate-400 font-medium">{m.metric_name}</div>
                      <div className="text-xl font-bold font-mono text-slate-100 mt-1">
                        {m.metric_value}%
                      </div>
                      {m.threshold_value !== null && (
                        <div className="text-xs text-slate-500 mt-1">
                          Gate: {isHalluc ? '<=' : '>='} {m.threshold_value}%
                        </div>
                      )}
                    </div>
                    <div>
                      {passed ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3 mr-1" /> Pass
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <XCircle className="w-3 h-3 mr-1" /> Fail
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
