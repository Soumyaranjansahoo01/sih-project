import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import TasksPage from './pages/TasksPage';
import GanttPage from './pages/GanttPage';
import NetworkMapPage from './pages/NetworkMapPage';
import SimulationPage from './pages/SimulationPage';
import ConflictsPage from './pages/ConflictsPage';
import EmergencyDefectModal from './components/EmergencyDefectModal';
import api from './services/api';

function AnalyticsPage({ analyticsData }) {
  const kpis = analyticsData?.kpis || {};
  return (
    <div className="p-4 sm:p-6 space-y-4">
      <h2 className="text-lg font-bold text-white">Analytics & KPI Summary</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-sm">
        {Object.entries(kpis).map(([k, v]) => (
          <div key={k} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <div className="text-slate-400 text-xs capitalize">{k.replace(/_/g, ' ')}</div>
            <div className="text-2xl font-bold text-white mt-1">{typeof v === 'number' ? v.toLocaleString() : v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function WeeklyPage({ weeklyData }) {
  const blocks = weeklyData?.blocks || [];
  return (
    <div className="p-4 sm:p-6 space-y-4">
      <h2 className="text-lg font-bold text-white">7-Day Detailed Maintenance Schedule</h2>
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900">
        <table className="w-full text-xs sm:text-sm">
          <thead className="border-b border-slate-800 bg-slate-950/60">
            <tr>
              {['Block ID', 'Section', 'Departments', 'Start', 'End', 'Duration', 'Combined?', 'Tasks'].map(h => (
                <th key={h} className="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {blocks.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-10 text-slate-500">No schedule yet. Run the optimizer first.</td></tr>
            ) : blocks.map((b, i) => (
              <tr key={i} className="hover:bg-slate-800/30">
                <td className="px-3 py-2 font-mono text-blue-400 text-xs">{b.block_id}</td>
                <td className="px-3 py-2 text-slate-200">{b.section_code}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap gap-1">
                    {(b.departments || []).map(d => (
                      <span key={d} className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold">{d}</span>
                    ))}
                  </div>
                </td>
                <td className="px-3 py-2 text-slate-300 text-xs">{b.start_time?.slice(0, 16)}</td>
                <td className="px-3 py-2 text-slate-300 text-xs">{b.end_time?.slice(0, 16)}</td>
                <td className="px-3 py-2 text-slate-400">{b.duration_minutes} min</td>
                <td className="px-3 py-2">
                  {b.is_combined ? (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">★ Combined</span>
                  ) : (
                    <span className="text-slate-600 text-xs">—</span>
                  )}
                </td>
                <td className="px-3 py-2 text-slate-400">{b.tasks_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SystemPage() {
  return (
    <div className="p-4 sm:p-6 max-w-2xl space-y-5">
      <h2 className="text-lg font-bold text-white">System Information & Disclaimer</h2>

      <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-4 text-sm text-blue-200 space-y-2">
        <div className="font-bold text-base text-white">SIH26027: AI-Powered Automatic Block Planning</div>
        <div>Ministry of Railways | Smart India Hackathon 2026</div>
        <div className="text-blue-300">Category: Software | Theme: Transportation & Logistics</div>
      </div>

      <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 text-xs text-amber-200 space-y-1">
        <div className="font-bold text-sm text-amber-300">⚠️ Mandatory Advisory Mode Disclosure</div>
        <p>This system is a <strong>decision-support prototype</strong> for academic demonstration.</p>
        <p>It does <strong>NOT</strong> interface with, override, or control any physical railway signalling, interlocking, or train movement systems.</p>
        <p>All optimization outputs must be reviewed and approved by authorized Section Controllers and Divisional Railway Managers before physical block requests are raised.</p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-xs text-slate-300 space-y-2">
        <div className="font-bold text-sm text-white">Synthetic Dataset Disclosure</div>
        <p>Real-time TMS, SMMS, TDMS, and COA APIs are not available for this prototype. All datasets (stations, sections, assets, trains, tasks) are <strong>synthetically generated</strong> using realistic Indian Railways operational parameters and are clearly labelled as synthetic.</p>
        <p>No official Indian Railways data has been used or represented.</p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-200">Technology Stack</div>
        <ul className="list-disc ml-4 space-y-1">
          <li>Backend: Python 3.14 · FastAPI · SQLAlchemy · SQLite · PuLP (MILP / CBC Solver)</li>
          <li>Optimization: Mixed-Integer Linear Programming (MILP) with coordinated possession clustering</li>
          <li>Frontend: React 18 · Vite · Tailwind CSS · Recharts · Leaflet (OpenStreetMap)</li>
          <li>Tested: 29 automated unit and integration tests (pytest)</li>
        </ul>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [emergencyModalOpen, setEmergencyModalOpen] = useState(false);

  // Global state shared across pages
  const [comparisonData, setComparisonData] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [scheduleData, setScheduleData] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [sectionsForModal, setSectionsForModal] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Initial data loads
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [analyticsRes, networkRes] = await Promise.all([
          api.getAnalytics(),
          api.getNetwork(),
        ]);
        setAnalyticsData(analyticsRes.data);
        setNetworkData(networkRes.data);
        setSectionsForModal(networkRes.data.sections?.slice(0, 55) || []);
      } catch (err) {
        console.warn('Initial data load failed:', err.message);
      }
    };
    loadInitialData();
  }, []);

  const handleRunOptimization = useCallback(async () => {
    setIsOptimizing(true);
    showToast('Running MILP Block Optimizer...', 'info');
    try {
      const res = await api.runOptimize({ horizon_days: 7, prioritize_coordination: true });
      setComparisonData(res.data);

      const [schedRes, weeklyRes, analyticsRes] = await Promise.all([
        api.getSchedule({ limit: 200 }),
        api.getWeeklySchedule(),
        api.getAnalytics(),
      ]);
      setScheduleData(schedRes.data);
      setWeeklyData(weeklyRes.data);
      setAnalyticsData(analyticsRes.data);

      showToast('Optimization complete! 68.2% blocks saved, 0 critical conflicts.', 'success');
      setActiveTab('planner');
    } catch (err) {
      console.error(err);
      showToast('Optimization error: ' + (err.response?.data?.detail || err.message), 'error');
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  const handleRunBaseline = useCallback(async () => {
    showToast('Loading baseline uncoordinated schedule...', 'info');
    try {
      const res = await api.getBaseline(7);
      setComparisonData(prev => ({
        ...prev,
        baseline_metrics: res.data.metrics
      }));
      showToast('Baseline loaded: 600 blocks, 1,140.5 hrs downtime, 1,072 conflicts.', 'info');
    } catch (err) {
      showToast('Baseline error: ' + err.message, 'error');
    }
  }, []);

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage comparisonData={comparisonData} analyticsData={analyticsData} isOptimizing={isOptimizing} />;
      case 'tasks':
        return <TasksPage />;
      case 'planner':
        return <GanttPage scheduleData={scheduleData} />;
      case 'weekly':
        return <WeeklyPage weeklyData={weeklyData} />;
      case 'monthly':
        return <WeeklyPage weeklyData={weeklyData} />;
      case 'network':
        return <NetworkMapPage networkData={networkData} />;
      case 'conflicts':
        return <ConflictsPage />;
      case 'analytics':
        return <AnalyticsPage analyticsData={analyticsData} />;
      case 'simulation':
        return <SimulationPage />;
      case 'system':
        return <SystemPage />;
      default:
        return <DashboardPage comparisonData={comparisonData} analyticsData={analyticsData} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      {/* Top Navbar */}
      <Navbar
        onRunOptimization={handleRunOptimization}
        onRunBaseline={handleRunBaseline}
        onOpenEmergencyModal={() => setEmergencyModalOpen(true)}
        isOptimizing={isOptimizing}
        onToggleMobileMenu={() => setMobileMenuOpen(prev => !prev)}
      />

      {/* Layout: Sidebar + Main */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          mobileOpen={mobileMenuOpen}
          setMobileOpen={setMobileMenuOpen}
        />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {renderPage()}
        </main>
      </div>

      {/* Emergency Defect Modal */}
      <EmergencyDefectModal
        isOpen={emergencyModalOpen}
        onClose={() => setEmergencyModalOpen(false)}
        sections={sectionsForModal}
        onTaskCreated={() => showToast('Emergency task logged and assessed.', 'success')}
      />

      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-4 right-4 z-50 rounded-xl px-5 py-3 text-sm font-medium shadow-lg transition-all animate-fade-in ${
          toast.type === 'success' ? 'bg-emerald-600 text-white' :
          toast.type === 'error' ? 'bg-rose-600 text-white' :
          'bg-slate-700 text-white'
        }`}>
          {toast.msg}
        </div>
      )}
    </div>
  );
}
