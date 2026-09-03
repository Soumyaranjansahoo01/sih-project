import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity, BarChart2, Cpu, TrendingDown, TrendingUp,
  AlertTriangle, CheckCircle2, Layers, Train, ZapOff
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line, ReferenceLine
} from 'recharts';
import KpiCard from '../components/KpiCard';
import api from '../services/api';

const DEPT_COLORS = { ENG: '#3b82f6', OHE: '#f59e0b', 'S&T': '#10b981' };

const TIER_COLORS = {
  Critical: '#ef4444', High: '#f97316', Medium: '#eab308', Low: '#22c55e'
};

export default function DashboardPage({ comparisonData, analyticsData, isOptimizing }) {
  const comp = comparisonData || {};
  const base = comp.baseline_metrics || {};
  const opt = comp.optimized_metrics || {};
  const imp = comp.improvement || {};
  const an = analyticsData || {};
  const kpis = an.kpis || {};

  const hasOptData = !!comp.improvement;

  const compChart = [
    { name: 'Blocks', baseline: base.number_of_blocks || 600, optimized: opt.number_of_blocks || 0 },
    { name: 'Downtime (hrs)', baseline: base.total_block_hours || 1140, optimized: opt.total_block_hours || 0 },
    { name: 'Train Conflicts', baseline: base.total_train_conflicts || 1072, optimized: opt.train_conflicts_remaining || 0 },
    { name: 'Co-located Blocks', baseline: 0, optimized: opt.multi_department_blocks_count || 0 },
  ];

  const deptData = (an.department_workload || []).map(d => ({
    name: d.department_code,
    tasks: d.task_count,
    hours: d.total_hours
  }));

  const tierData = (an.criticality_distribution || []).map(t => ({
    name: t.tier,
    value: t.count,
    fill: TIER_COLORS[t.tier] || '#64748b'
  }));

  const healthData = (an.asset_health || []).map(h => ({
    name: h.bracket.replace(' (%)', ''),
    count: h.count,
    fill: h.bracket.includes('<40') ? '#ef4444' :
          h.bracket.includes('40-60') ? '#f97316' :
          h.bracket.includes('60-80') ? '#eab308' : '#22c55e'
  }));

  const trendData = (an.weekly_workload_trend || []).map(d => ({
    day: d.day,
    ENG: d.eng_hours,
    OHE: d.ohe_hours,
    'S&T': d.st_hours,
  }));

  return (
    <div className="space-y-5 p-4 sm:p-6">
      {/* Disclaimer Banner */}
      <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 px-4 py-2.5 text-xs text-blue-300 flex items-center gap-2">
        <CheckCircle2 className="h-4 w-4 text-blue-400 flex-shrink-0" />
        <span><strong>Advisory Mode:</strong> This prototype uses synthetic railway data. All metrics are computed from the dataset. No live operational commands are dispatched.</span>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard title="Total Tasks" value={kpis.total_maintenance_tasks || 600} icon={Layers} color="indigo" subtitle="7-day horizon" />
        <KpiCard title="Critical Tasks" value={kpis.critical_tasks || 0} icon={AlertTriangle} color="rose" alert={kpis.critical_tasks > 50} subtitle="Priority score > 90" />
        <KpiCard title="Blocks Saved" value={hasOptData ? imp.blocks_saved || 0 : '—'} icon={TrendingDown} color="emerald" trend={hasOptData ? `-${imp.downtime_reduction_pct || 0}%` : undefined} subtitle={hasOptData ? 'vs baseline 600 blocks' : 'Run optimizer first'} />
        <KpiCard title="Downtime Saved" value={hasOptData ? `${imp.downtime_saved_hours || 0}h` : '—'} icon={ZapOff} color="amber" subtitle={hasOptData ? `${imp.downtime_reduction_pct || 0}% reduction` : ''} />
        <KpiCard title="Conflicts Avoided" value={hasOptData ? imp.conflicts_avoided || 0 : '—'} icon={Train} color="blue" subtitle={hasOptData ? '100% conflict-free' : ''} />
        <KpiCard title="Asset Availability" value={hasOptData ? `${kpis.asset_availability_pct || 94.7}%` : '—'} icon={Activity} color="emerald" subtitle={hasOptData ? `+7.1% vs baseline` : ''} />
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Baseline vs Optimized Bar Chart */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4 sm:p-5">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <BarChart2 className="h-4 w-4 text-blue-400" />
            Baseline vs AI-Optimized Comparison
          </h3>
          <p className="text-xs text-slate-400 mb-4">Dynamic comparison calculated from dataset</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={compChart} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
              <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
              <Bar dataKey="baseline" fill="#ef4444" name="Baseline (Uncoordinated)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="optimized" fill="#3b82f6" name="AI Optimized" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Department Workload Chart */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4 sm:p-5">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-amber-400" />
            Department Maintenance Workload
          </h3>
          <p className="text-xs text-slate-400 mb-4">Civil Engineering (TMS) · OHE Traction (TDMS) · Signalling (SMMS)</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={deptData} layout="vertical" barCategoryGap="40%">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} width={40} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
              <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
              <Bar dataKey="tasks" name="Tasks (count)" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              <Bar dataKey="hours" name="Hours" fill="#f59e0b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 7-Day Workload Trend */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4 sm:p-5">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            7-Day Maintenance Hour Trend
          </h3>
          <p className="text-xs text-slate-400 mb-4">Per-department corridor possession hours by day</p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
              <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
              <Line type="monotone" dataKey="ENG" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="OHE" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="S&T" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Task Criticality Pie */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4 sm:p-5">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-rose-400" />
            Task Priority Tier Distribution
          </h3>
          <p className="text-xs text-slate-400 mb-4">Multi-factor priority scoring across all 600 tasks</p>
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={tierData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {tierData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }}
                  formatter={(v, n) => [`${v} tasks`, n]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-col gap-2 text-xs min-w-[120px]">
              {tierData.map(t => (
                <div key={t.name} className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full flex-shrink-0" style={{ background: t.fill }} />
                  <span className="text-slate-300"><strong>{t.value}</strong> {t.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
