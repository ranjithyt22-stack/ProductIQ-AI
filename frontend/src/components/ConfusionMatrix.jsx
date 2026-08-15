import React from 'react';
import { Grid, Layers } from 'lucide-react';

export default function ConfusionMatrix({ matrixData = null }) {
  const classes = matrixData?.classes || ['READY_FOR_COMMERCE', 'REVIEW_REQUIRED', 'NOT_READY'];
  const matrix = matrixData?.matrix || {
    READY_FOR_COMMERCE: { READY_FOR_COMMERCE: 10, REVIEW_REQUIRED: 0, NOT_READY: 0 },
    REVIEW_REQUIRED: { READY_FOR_COMMERCE: 0, REVIEW_REQUIRED: 0, NOT_READY: 0 },
    NOT_READY: { READY_FOR_COMMERCE: 0, REVIEW_REQUIRED: 0, NOT_READY: 0 },
  };

  return (
    <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-6 space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          Commerce Readiness Classification Confusion Matrix
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Compares expected commerce qualification states against predicted engine outcomes.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-center text-xs">
          <thead>
            <tr>
              <th className="py-2 px-3 text-left text-slate-400">Expected \ Predicted</th>
              {classes.map((c) => (
                <th key={c} className="py-2 px-3 text-slate-300 font-mono font-semibold">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {classes.map((expClass) => (
              <tr key={expClass} className="hover:bg-slate-800/40">
                <td className="py-3 px-3 text-left font-mono font-medium text-slate-300">
                  {expClass}
                </td>
                {classes.map((predClass) => {
                  const count = matrix[expClass]?.[predClass] || 0;
                  const isDiag = expClass === predClass;
                  return (
                    <td key={predClass} className="py-3 px-3">
                      <span
                        className={`inline-block w-12 py-1.5 rounded font-mono font-bold text-sm ${
                          isDiag
                            ? count > 0
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-slate-800 text-slate-400'
                            : count > 0
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-slate-800/40 text-slate-500'
                        }`}
                      >
                        {count}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
