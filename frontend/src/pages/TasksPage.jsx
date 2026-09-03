import React, { useState, useEffect } from 'react';
import { ChevronRight, Search, Filter, Sparkles } from 'lucide-react';
import api from '../services/api';
import ExplainableModal from '../components/ExplainableModal';

const TIER_COLORS = {
  Critical: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
  High: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  Medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
};

const DEPT_STYLES = {
  ENG: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  OHE: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  'S&T': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
};

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [explainTask, setExplainTask] = useState(null);
  const [page, setPage] = useState(0);

  const limit = 15;

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = {
        limit,
        offset: page * limit,
        ...(departmentFilter && { department: departmentFilter }),
        ...(priorityFilter && { priority_class: priorityFilter }),
      };
      const res = await api.getTasks(params);
      let items = res.data.tasks || [];
      if (search) {
        const q = search.toLowerCase();
        items = items.filter(t =>
          t.task_type.toLowerCase().includes(q) ||
          t.section_code.toLowerCase().includes(q) ||
          t.task_id.toLowerCase().includes(q)
        );
      }
      setTasks(items);
      setTotalCount(res.data.total_count || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTasks(); }, [departmentFilter, priorityFilter, page]);

  const handleExplain = async (taskId) => {
    try {
      const res = await api.getTaskDetails(taskId);
      setExplainTask(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white">Maintenance Tasks</h2>
          <p className="text-xs text-slate-400">{totalCount} tasks · Scoring: Criticality (30%) + Urgency (25%) + Overdue Days (20%) + Asset Condition (15%) + Safety (10%)</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-800 pl-9 pr-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
            placeholder="Search task type, section..."
            value={search}
            onChange={e => { setSearch(e.target.value); fetchTasks(); }}
          />
        </div>
        <select
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
          value={departmentFilter}
          onChange={e => { setDepartmentFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Departments</option>
          <option value="ENG">Civil Engineering (ENG)</option>
          <option value="OHE">Traction Distribution (OHE)</option>
          <option value="S&T">Signal & Telecom (S&T)</option>
        </select>
        <select
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
          value={priorityFilter}
          onChange={e => { setPriorityFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Priority Tiers</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900">
        <table className="w-full text-xs sm:text-sm">
          <thead className="border-b border-slate-800 bg-slate-950/60">
            <tr>
              {['Task ID', 'Type', 'Department', 'Section', 'Priority Score', 'Tier', 'Duration', 'Status', 'AI Explain'].map(h => (
                <th key={h} className="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              <tr><td colSpan={9} className="text-center py-10 text-slate-400">Loading tasks...</td></tr>
            ) : tasks.length === 0 ? (
              <tr><td colSpan={9} className="text-center py-10 text-slate-500">No tasks found</td></tr>
            ) : tasks.map(t => (
              <tr key={t.id} className="hover:bg-slate-800/40 transition">
                <td className="px-3 py-3 font-mono text-blue-400 text-xs">{t.task_id}</td>
                <td className="px-3 py-3 text-slate-200 max-w-[160px] truncate">{t.task_type}</td>
                <td className="px-3 py-3">
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold border ${DEPT_STYLES[t.department] || ''}`}>
                    {t.department}
                  </span>
                </td>
                <td className="px-3 py-3 text-slate-300 font-mono text-xs">{t.section_code}</td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 rounded-full bg-slate-800 max-w-[60px]">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-blue-500 to-sky-400"
                        style={{ width: `${t.priority_score}%` }}
                      />
                    </div>
                    <span className="text-slate-200 font-bold w-7">{Math.round(t.priority_score)}</span>
                  </div>
                </td>
                <td className="px-3 py-3">
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold border ${TIER_COLORS[t.priority_class] || ''}`}>
                    {t.priority_class}
                  </span>
                </td>
                <td className="px-3 py-3 text-slate-400">{t.duration_minutes} min</td>
                <td className="px-3 py-3 text-slate-400">{t.status}</td>
                <td className="px-3 py-3">
                  <button
                    onClick={() => handleExplain(t.task_id)}
                    className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-medium"
                  >
                    <Sparkles className="h-3.5 w-3.5" /> Why?
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Showing {page * limit + 1}–{Math.min((page + 1) * limit, totalCount)} of {totalCount}</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
            className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 disabled:opacity-40 hover:bg-slate-700">
            ← Prev
          </button>
          <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * limit >= totalCount}
            className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 disabled:opacity-40 hover:bg-slate-700">
            Next →
          </button>
        </div>
      </div>

      {/* Explain Modal */}
      <ExplainableModal
        isOpen={!!explainTask}
        onClose={() => setExplainTask(null)}
        data={explainTask}
      />
    </div>
  );
}
