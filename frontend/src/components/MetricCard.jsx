import React from 'react';

export default function MetricCard({ title, value, unit = '%', subtitle, status = 'default', icon: Icon }) {
  const getStatusColor = () => {
    switch (status) {
      case 'pass':
      case 'success':
        return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'fail':
      case 'danger':
        return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
      case 'warning':
        return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
      default:
        return 'text-cyan-400 border-slate-700 bg-slate-800/40';
    }
  };

  return (
    <div className={`p-4 rounded-xl border backdrop-blur-sm transition-all duration-200 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && <Icon className="w-4 h-4 opacity-75" />}
      </div>
      <div className="flex items-baseline space-x-1">
        <span className="text-2xl font-bold font-mono text-slate-100">{value !== undefined && value !== null ? value : '--'}</span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400 truncate">{subtitle}</p>}
    </div>
  );
}
