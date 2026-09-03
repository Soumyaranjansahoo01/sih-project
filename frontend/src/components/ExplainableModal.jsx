import React from 'react';
import { X, Sparkles, CheckCircle2, AlertTriangle, ShieldCheck, Clock, Gauge } from 'lucide-react';

export default function ExplainableModal({ isOpen, onClose, data }) {
  if (!isOpen || !data) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-700 bg-slate-900 p-5 sm:p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600/20 p-2.5 text-blue-400 border border-blue-500/30">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                Explainable AI Rationale
                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-semibold border border-blue-500/30">
                  {data.task_id || data.block_id}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Transparent decision-support breakdown calculated by mathematical model
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Priority Score Summary */}
        <div className="my-5 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Calculated Priority Score</span>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-blue-400">
                  {data.total_priority_score || data.priority_score || '90'}/100
                </span>
                <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                  (data.priority_class === 'Critical') ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                  (data.priority_class === 'High') ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                  {data.priority_class || 'High Priority'}
                </span>
              </div>
            </div>
            <div className="text-right text-xs text-slate-400">
              <div><span className="text-slate-200 font-medium">Department:</span> {data.department || 'ENG'}</div>
              <div><span className="text-slate-200 font-medium">Section:</span> {data.section_code || 'Main Corridor'}</div>
            </div>
          </div>
          {data.explanation_summary && (
            <p className="mt-3 text-xs sm:text-sm text-slate-300 italic bg-blue-950/20 p-3 rounded-lg border border-blue-900/40">
              "{data.explanation_summary}"
            </p>
          )}
        </div>

        {/* Factor Breakdown */}
        {data.factor_breakdown && data.factor_breakdown.length > 0 && (
          <div className="mb-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Gauge className="h-4 w-4 text-blue-400" /> Multi-Factor Contribution Weights
            </h4>
            <div className="space-y-2.5">
              {data.factor_breakdown.map((f, i) => (
                <div key={i} className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200">{f.factor_name}</span>
                    <span className="text-slate-400">
                      Raw: <strong className="text-slate-200">{f.raw_value}</strong> → +{f.contribution_points} pts ({Math.round(f.weight * 100)}% weight)
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-blue-500 to-sky-400"
                      style={{ width: `${Math.min(100, f.normalized_score)}%` }}
                    />
                  </div>
                  <p className="mt-1.5 text-[11px] text-slate-400">{f.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Key Reasons Bullets */}
        {data.key_reasons && data.key_reasons.length > 0 && (
          <div className="mb-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Primary Operational Drivers
            </h4>
            <ul className="space-y-1.5 text-xs sm:text-sm text-slate-300">
              {data.key_reasons.map((r, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer Disclaimer */}
        <div className="border-t border-slate-800 pt-3 flex items-center justify-between text-[11px] text-slate-500">
          <span>Decision-Support Prototype: No autonomous commands dispatched.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-white hover:bg-slate-700 text-xs font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
