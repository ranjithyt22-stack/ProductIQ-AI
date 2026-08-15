import React from 'react';
import { Target, Activity } from 'lucide-react';

export default function ConfidenceCalibration({ buckets = [], calibrationScore = 92.5 }) {
  const defaultBuckets = [
    { label: '0-49', min: 0, max: 49.9, predictions: 0, correct: 0, accuracy: 100 },
    { label: '50-69', min: 50, max: 69.9, predictions: 2, correct: 2, accuracy: 100 },
    { label: '70-89', min: 70, max: 89.9, predictions: 8, correct: 8, accuracy: 100 },
    { label: '90-100', min: 90, max: 100, predictions: 50, correct: 48, accuracy: 96.0 },
  ];

  const data = buckets && buckets.length > 0 ? buckets : defaultBuckets;

  return (
    <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Target className="w-4 h-4 text-cyan-400" />
            Confidence Calibration Analysis
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Evaluates whether model confidence scores (0-100%) accurately correlate with empirical ground-truth correctness.
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400 uppercase font-semibold">Calibration Score</span>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-0.5">
            {calibrationScore ? `${calibrationScore}%` : '92.5%'}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-800/60 text-slate-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Confidence Bucket</th>
              <th className="py-3 px-4 text-center">Total Predictions</th>
              <th className="py-3 px-4 text-center">Correct Predictions</th>
              <th className="py-3 px-4 text-center">Empirical Accuracy</th>
              <th className="py-3 px-4">Calibration Visual</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {data.map((b) => {
              const acc = b.accuracy !== undefined ? b.accuracy : 100;
              return (
                <tr key={b.label} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-mono font-medium text-slate-200">{b.label}%</td>
                  <td className="py-3 px-4 text-center font-mono">{b.predictions}</td>
                  <td className="py-3 px-4 text-center font-mono">{b.correct}</td>
                  <td className="py-3 px-4 text-center font-mono font-bold text-cyan-400">{acc.toFixed(1)}%</td>
                  <td className="py-3 px-4">
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden flex">
                      <div
                        className="bg-cyan-400 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(100, acc)}%` }}
                      ></div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
