import React, { useState } from 'react';
import { ChevronRight, CheckCircle2, XCircle, FileText, Check, Shield } from 'lucide-react';

export default function BenchmarkResults({ products = [] }) {
  const [selectedProduct, setSelectedProduct] = useState(null);

  if (!products || products.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-900/50 rounded-xl border border-slate-800">
        No product results found for this evaluation run.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200">
            Per-Product Benchmark Accuracy ({products.length} Products)
          </h3>
          <span className="text-xs text-slate-400">Click any product to inspect attribute breakdown</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/60 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Product ID</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-center">Extraction F1</th>
                <th className="py-3 px-4 text-center">Value Acc</th>
                <th className="py-3 px-4 text-center">Unit Acc</th>
                <th className="py-3 px-4 text-center">Evidence</th>
                <th className="py-3 px-4 text-center">Commerce Readiness</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {products.map((p) => {
                const isSelected = selectedProduct?.product_id === p.product_id;
                return (
                  <tr
                    key={p.product_id}
                    onClick={() => setSelectedProduct(isSelected ? null : p)}
                    className={`hover:bg-slate-800/40 transition-colors cursor-pointer ${
                      isSelected ? 'bg-cyan-950/20 border-l-2 border-cyan-400' : ''
                    }`}
                  >
                    <td className="py-3 px-4 font-mono text-cyan-400 font-medium">{p.product_id}</td>
                    <td className="py-3 px-4 font-medium text-slate-200">{p.product_name}</td>
                    <td className="py-3 px-4 text-slate-400">{p.category}</td>
                    <td className="py-3 px-4 text-center font-mono">{p.extraction_f1}%</td>
                    <td className="py-3 px-4 text-center font-mono">{p.value_accuracy}%</td>
                    <td className="py-3 px-4 text-center font-mono">{p.unit_accuracy}%</td>
                    <td className="py-3 px-4 text-center font-mono text-emerald-400">{p.evidence_coverage}%</td>
                    <td className="py-3 px-4 text-center">
                      {p.commerce_readiness_correct ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <Check className="w-3 h-3 mr-1" /> {p.actual_readiness}
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <XCircle className="w-3 h-3 mr-1" /> {p.actual_readiness}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <ChevronRight className={`w-4 h-4 inline-block text-slate-400 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Product Detail Panel */}
      {selectedProduct && (
        <div className="p-6 rounded-xl bg-slate-900/80 border border-cyan-500/30 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span className="text-xs font-mono text-cyan-400">{selectedProduct.product_id}</span>
              <h4 className="text-base font-bold text-slate-100 mt-0.5">{selectedProduct.product_name}</h4>
            </div>
            <button
              onClick={() => setSelectedProduct(null)}
              className="text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">TP / FP / FN</span>
              <div className="font-mono text-base font-bold text-slate-200 mt-1">
                {selectedProduct.tp_count} / {selectedProduct.fp_count} / {selectedProduct.fn_count}
              </div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Extraction F1</span>
              <div className="font-mono text-base font-bold text-cyan-400 mt-1">
                {selectedProduct.extraction_f1}%
              </div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Value Accuracy</span>
              <div className="font-mono text-base font-bold text-emerald-400 mt-1">
                {selectedProduct.value_accuracy}%
              </div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Hallucination Rate</span>
              <div className="font-mono text-base font-bold text-slate-200 mt-1">
                {selectedProduct.hallucination_rate}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
