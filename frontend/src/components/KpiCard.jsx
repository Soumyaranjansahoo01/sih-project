import React from 'react';

export default function KpiCard({ title, value, subtitle, icon: Icon, color = 'blue', trend, alert = false }) {
  const colorStyles = {
    blue: 'border-blue-500/30 bg-blue-950/20 text-blue-400',
    emerald: 'border-emerald-500/30 bg-emerald-950/20 text-emerald-400',
    amber: 'border-amber-500/30 bg-amber-950/20 text-amber-400',
    rose: 'border-rose-500/30 bg-rose-950/20 text-rose-400',
    purple: 'border-purple-500/30 bg-purple-950/20 text-purple-400',
    indigo: 'border-indigo-500/30 bg-indigo-950/20 text-indigo-400'
  };

  return (
    <div className={`relative overflow-hidden rounded-xl border p-4 sm:p-5 transition-all duration-200 hover:shadow-lg hover:border-slate-600 bg-slate-900/80 backdrop-blur-sm ${
      alert ? 'border-rose-500/50 ring-1 ring-rose-500/30' : 'border-slate-800'
    }`}>
      <div className="flex items-center justify-between">
        <span className="text-xs sm:text-sm font-medium text-slate-400 truncate">{title}</span>
        {Icon && (
          <div className={`rounded-lg p-2 ${colorStyles[color] || colorStyles.blue}`}>
            <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
          </div>
        )}
      </div>

      <div className="mt-2 sm:mt-3 flex items-baseline gap-2">
        <span className="text-2xl sm:text-3xl font-bold tracking-tight text-white">{value}</span>
        {trend && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            trend.startsWith('+') ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
          }`}>
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-400 truncate">{subtitle}</p>
      )}
    </div>
  );
}
