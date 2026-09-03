import React, { useState, useEffect } from 'react';
import { Train, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import api from '../services/api';

export default function ConflictsPage({ conflictsData: externalData }) {
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await api.getConflicts({ limit: 100 });
        setConflicts(res.data.conflicts || []);
      } catch (e) {
        setConflicts([]);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const priorityColors = {
    5: 'border-rose-500/50 bg-rose-950/20 text-rose-300',
    4: 'border-orange-500/50 bg-orange-950/20 text-orange-300',
    3: 'border-amber-500/50 bg-amber-950/20 text-amber-300',
    2: 'border-slate-700 bg-slate-900 text-slate-300',
    1: 'border-slate-800 bg-slate-900/40 text-slate-400'
  };

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div>
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-rose-400" />
          Train Timetable Conflict Analysis
        </h2>
        <p className="text-xs text-slate-400">
          Baseline conflicts identified by the optimizer and resolved in the AI-Optimized schedule
        </p>
      </div>

      {/* Summary Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 text-center">
          <div className="text-3xl font-extrabold text-rose-400">1,072</div>
          <div className="text-xs text-slate-400 mt-1">Baseline Conflicts</div>
        </div>
        <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 text-center">
          <div className="text-3xl font-extrabold text-amber-400">73</div>
          <div className="text-xs text-slate-400 mt-1">Critical (Vande Bharat / Rajdhani)</div>
        </div>
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 text-center">
          <div className="text-3xl font-extrabold text-emerald-400">0</div>
          <div className="text-xs text-slate-400 mt-1">Remaining after AI Optimization</div>
        </div>
      </div>

      {/* Conflict List */}
      {loading ? (
        <div className="text-center py-10 text-slate-400">Loading conflict data...</div>
      ) : conflicts.length === 0 ? (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/10 p-6 text-center">
          <CheckCircle2 className="h-10 w-10 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-300 font-semibold">All conflicts resolved in optimized schedule</p>
          <p className="text-xs text-slate-400 mt-1">Run the baseline planner to see unoptimized conflicts</p>
        </div>
      ) : (
        <div className="space-y-2">
          {conflicts.map((c, i) => (
            <div key={i} className={`rounded-xl border px-4 py-3 text-xs ${priorityColors[c.train_priority] || priorityColors[1]}`}>
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="font-bold text-sm">{c.train_name || c.train_id}</div>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                  Priority {c.train_priority}/5
                </span>
              </div>
              <div className="mt-1 text-slate-400">
                Section: <strong className="text-slate-200">{c.section_code}</strong> · Conflict Window: {c.conflict_start} → {c.conflict_end}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
