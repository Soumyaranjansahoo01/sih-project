import React, { useState } from 'react';
import { Sliders, Play, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Train } from 'lucide-react';
import api from '../services/api';

const SCENARIOS = [
  { name: 'Festival Traffic Surge (+25% Trains)', multiplier: 1.25, emergencies: 2, weather: false },
  { name: 'Severe Fog Disruption (+10% Traffic)', multiplier: 1.1, emergencies: 1, weather: true },
  { name: 'Monsoon Emergency (+15% Defects)', multiplier: 1.15, emergencies: 4, weather: true },
  { name: 'Peak Summer Rush (+40% Trains)', multiplier: 1.4, emergencies: 3, weather: false },
  { name: 'Custom Scenario', multiplier: 1.0, emergencies: 0, weather: false },
];

export default function SimulationPage() {
  const [selectedScenario, setSelectedScenario] = useState(0);
  const [custom, setCustom] = useState({ multiplier: 1.2, emergencies: 2, weather: false });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const scenario = selectedScenario === 4 ? custom : SCENARIOS[selectedScenario];

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await api.runSimulation({
        scenario_name: SCENARIOS[selectedScenario]?.name || 'Custom Scenario',
        train_traffic_multiplier: Number(scenario.multiplier),
        emergency_tasks_count: Number(scenario.emergencies),
        weather_disruption: scenario.weather,
        horizon_days: 7
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Simulation error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const summary = result?.adaptation_summary;

  return (
    <div className="p-4 sm:p-6 space-y-5">
      <div>
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Sliders className="h-5 w-5 text-purple-400" />
          What-If Operational Simulation Engine
        </h2>
        <p className="text-xs text-slate-400">
          Stress-test the block optimizer against disruption scenarios. The MILP re-runs and adapts the schedule dynamically.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Scenario Selector */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white">Select Disruption Scenario</h3>

          <div className="space-y-2">
            {SCENARIOS.map((s, i) => (
              <button
                key={i}
                onClick={() => setSelectedScenario(i)}
                className={`w-full text-left rounded-xl border px-4 py-3 text-sm transition ${
                  selectedScenario === i
                    ? 'border-purple-500/60 bg-purple-950/30 text-purple-200'
                    : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:bg-slate-800'
                }`}
              >
                <div className="font-semibold">{s.name}</div>
                {i < 4 && (
                  <div className="text-xs mt-0.5 opacity-70">
                    {Math.round((s.multiplier - 1) * 100)}% extra trains · {s.emergencies} emergency defects {s.weather ? '· Weather active' : ''}
                  </div>
                )}
              </button>
            ))}
          </div>

          {/* Custom Scenario Controls */}
          {selectedScenario === 4 && (
            <div className="space-y-3 border-t border-slate-800 pt-4">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">
                  Train Traffic Multiplier: <strong className="text-white">{custom.multiplier}×</strong> ({Math.round((custom.multiplier - 1) * 100)}% extra)
                </label>
                <input type="range" min="0.5" max="2.0" step="0.05"
                  value={custom.multiplier}
                  onChange={e => setCustom(c => ({ ...c, multiplier: parseFloat(e.target.value) }))}
                  className="w-full accent-purple-500"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">
                  Emergency Defects Injected: <strong className="text-white">{custom.emergencies}</strong>
                </label>
                <input type="range" min="0" max="10" step="1"
                  value={custom.emergencies}
                  onChange={e => setCustom(c => ({ ...c, emergencies: parseInt(e.target.value) }))}
                  className="w-full accent-purple-500"
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input type="checkbox" checked={custom.weather}
                  onChange={e => setCustom(c => ({ ...c, weather: e.target.checked }))}
                  className="accent-purple-500 h-4 w-4 rounded" />
                Enable weather disruption (fog/rain speed restrictions)
              </label>
            </div>
          )}

          {/* Run Button */}
          <button
            onClick={handleRun}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-500 hover:from-purple-500 hover:to-indigo-400 text-white font-bold text-sm shadow-lg shadow-purple-500/20 disabled:opacity-50 transition"
          >
            <Play className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Re-running MILP Optimizer...' : 'Run What-If Simulation'}
          </button>
        </div>

        {/* Results Panel */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white">Adaptation Results</h3>

          {!result && (
            <div className="text-center py-12 text-slate-500">
              <Sliders className="h-12 w-12 mb-3 opacity-30 mx-auto" />
              <p className="text-sm">Select a scenario and run the simulation to see how the optimizer adapts.</p>
            </div>
          )}

          {result && summary && (
            <div className="space-y-4">
              {/* Scenario Header */}
              <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-3">
                <div className="font-bold text-purple-200 text-sm">{summary.scenario}</div>
                <div className="text-xs text-purple-300/70 mt-0.5">
                  {summary.trains_simulated} trains simulated · {summary.emergencies_injected} emergency defects injected
                  {summary.weather_disruption_active ? ' · Weather active' : ''}
                </div>
              </div>

              {/* Metrics Comparison */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  {
                    label: 'Optimized Blocks',
                    standard: summary.standard_optimized_blocks,
                    sim: summary.simulated_optimized_blocks,
                    lower_better: true
                  },
                  {
                    label: 'Corridor Downtime (hrs)',
                    standard: summary.standard_downtime_hours,
                    sim: summary.simulated_downtime_hours,
                    lower_better: true
                  },
                  {
                    label: 'Critical Train Conflicts',
                    standard: 0,
                    sim: summary.critical_train_conflicts,
                    lower_better: true
                  },
                  {
                    label: 'Co-location Rate (%)',
                    standard: 96.9,
                    sim: summary.coordination_rate_pct,
                    lower_better: false
                  },
                ].map(m => {
                  const improved = m.lower_better ? m.sim <= m.standard : m.sim >= m.standard;
                  return (
                    <div key={m.label} className="rounded-xl border border-slate-800 bg-slate-950/50 p-3 text-xs">
                      <div className="text-slate-400">{m.label}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-slate-500">Std: {m.standard}</span>
                        <span className="text-slate-600">→</span>
                        <span className={`text-xl font-bold ${improved ? 'text-emerald-400' : 'text-amber-400'}`}>{m.sim}</span>
                        {improved ? <TrendingDown className="h-4 w-4 text-emerald-400" /> : <TrendingUp className="h-4 w-4 text-amber-400" />}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Critical Train Conflict Result */}
              <div className={`rounded-xl border p-3 ${
                summary.critical_train_conflicts === 0
                  ? 'border-emerald-500/30 bg-emerald-950/20'
                  : 'border-rose-500/30 bg-rose-950/20'
              }`}>
                <div className="flex items-center gap-2">
                  {summary.critical_train_conflicts === 0 ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-rose-400" />
                  )}
                  <span className={`font-bold text-sm ${summary.critical_train_conflicts === 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                    {summary.critical_train_conflicts === 0
                      ? 'Zero critical train conflicts under simulated conditions'
                      : `${summary.critical_train_conflicts} residual critical conflicts detected`}
                  </span>
                </div>
              </div>

              {/* Emergency Tasks Injected */}
              {result.injected_emergencies?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Injected Emergency Tasks</h4>
                  {result.injected_emergencies.map((em, i) => (
                    <div key={i} className="rounded-lg border border-rose-500/20 bg-rose-950/10 px-3 py-2 text-xs text-slate-300">
                      <span className="text-rose-400 font-bold">{em.task_id}</span> · {em.task_type} · Priority: {em.priority_score}
                    </div>
                  ))}
                </div>
              )}

              {/* Controller Takeaway */}
              <div className="rounded-xl border border-blue-500/20 bg-blue-950/20 p-3 text-xs text-blue-200 italic">
                {summary.controller_takeaway}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
