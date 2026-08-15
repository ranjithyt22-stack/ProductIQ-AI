import React from 'react';
import { AlertOctagon, CheckCircle2, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function HallucinationReport({ hallucinations = [], hallucinationRate = 0.0, totalAttributes = 60 }) {
  const hasViolations = hallucinations && hallucinations.length > 0;

  return (
    <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
            Anti-Hallucination & Negative Control Evaluation
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Measures AI generation of ungrounded or fabricated product attributes across explicit negative test probes.
          </p>
        </div>
        <div className="flex items-center gap-6 text-right">
          <div>
            <span className="text-xs text-slate-400 uppercase font-semibold">Hallucination Rate</span>
            <div className={`text-xl font-bold font-mono mt-0.5 ${hallucinationRate === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {hallucinationRate.toFixed(1)}%
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-semibold">Status</span>
            <div className="mt-0.5">
              {!hasViolations ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" /> ZERO HALLUCINATIONS
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  <AlertOctagon className="w-3.5 h-3.5 mr-1" /> {hallucinations.length} VIOLATIONS
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {!hasViolations ? (
        <div className="p-6 rounded-lg bg-emerald-950/20 border border-emerald-500/30 flex items-start gap-4">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <div className="font-semibold text-emerald-300">All Negative Control Probes Passed Verification</div>
            <div className="text-slate-400">
              The model correctly identified unmentioned negative control attributes (e.g. warranty periods, explosion-proof ratings, and wireless modules) as UNVERIFIED or NOT_FOUND without fabricating factual product specifications.
            </div>
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/60 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Probed Attribute</th>
                <th className="py-3 px-4">Hallucinated Output</th>
                <th className="py-3 px-4">Evidence Status</th>
                <th className="py-3 px-4">Failure Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {hallucinations.map((h, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-mono text-rose-300 font-medium">{h.attribute_name}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">{h.hallucinated_value || '--'}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      NOT FOUND
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{h.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
