import React from 'react';
import { History, CheckCircle2, XCircle, ChevronRight } from 'lucide-react';

export default function EvaluationRunHistory({ runs = [], selectedRunId, onSelectRun }) {
  if (!runs || runs.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 bg-slate-900/50 rounded-xl border border-slate-800">
        No past evaluation runs recorded yet.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <History className="w-4 h-4 text-cyan-400" />
          Benchmark Run History
        </h3>
        <span className="text-xs text-slate-400">{runs.length} Runs Recorded</span>
      </div>

      <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
        {runs.map((r) => {
          const isSelected = selectedRunId === r.evaluation_id;
          const isPass = r.quality_gate_status === 'PASS';

          return (
            <div
              key={r.evaluation_id}
              onClick={() => onSelectRun(r.evaluation_id)}
              className={`p-3 rounded-lg border transition-all cursor-pointer flex items-center justify-between ${
                isSelected
                  ? 'bg-cyan-950/30 border-cyan-500/50 text-slate-100'
                  : 'bg-slate-800/40 border-slate-700/50 hover:bg-slate-800 text-slate-300'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-cyan-400">{r.evaluation_id}</span>
                  {isPass ? (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400">
                      PASS
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-semibold bg-rose-500/10 text-rose-400">
                      FAIL
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-400">
                  {r.dataset_name} • Score: <span className="font-mono text-slate-200">{r.overall_score}%</span> • F1: <span className="font-mono text-slate-200">{r.extraction_f1}%</span>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500" />
            </div>
          );
        })}
      </div>
    </div>
  );
}
