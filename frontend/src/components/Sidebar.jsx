import React from 'react';
import {
  LayoutDashboard,
  ClipboardList,
  Calendar,
  CalendarDays,
  CalendarRange,
  MapPin,
  AlertTriangle,
  BarChart3,
  Sliders,
  Info,
  X
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, mobileOpen, setMobileOpen }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'tasks', label: 'Maintenance Tasks', icon: ClipboardList },
    { id: 'planner', label: 'Block Planner (Gantt)', icon: Calendar },
    { id: 'weekly', label: 'Weekly Plan', icon: CalendarDays },
    { id: 'monthly', label: 'Monthly Plan', icon: CalendarRange },
    { id: 'network', label: 'Railway Network Map', icon: MapPin },
    { id: 'conflicts', label: 'Train Conflicts', icon: AlertTriangle },
    { id: 'analytics', label: 'Analytics & KPIs', icon: BarChart3 },
    { id: 'simulation', label: 'What-If Simulation', icon: Sliders },
    { id: 'system', label: 'System Info & Disclaimer', icon: Info },
  ];

  const handleSelect = (id) => {
    setActiveTab(id);
    if (setMobileOpen) setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden animate-fade-in"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 border-r border-slate-800 bg-slate-950 p-4 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Mobile Close Button */}
        <div className="flex items-center justify-between lg:hidden mb-4 pb-2 border-b border-slate-800">
          <span className="text-sm font-bold text-white">Menu Navigation</span>
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Department Status Pills */}
        <div className="mb-4 rounded-xl border border-slate-800/80 bg-slate-900/60 p-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Integrated Systems</span>
          <div className="mt-2 grid grid-cols-3 gap-1.5 text-center text-[10px] font-bold">
            <div className="rounded bg-blue-500/20 text-blue-400 py-1 border border-blue-500/30">
              TMS (ENG)
            </div>
            <div className="rounded bg-amber-500/20 text-amber-400 py-1 border border-amber-500/30">
              TDMS (OHE)
            </div>
            <div className="rounded bg-emerald-500/20 text-emerald-400 py-1 border border-emerald-500/30">
              SMMS (S&T)
            </div>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelect(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100'
                }`}
              >
                <Icon className={`h-4 w-4 sm:h-5 sm:w-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer Info */}
        <div className="absolute bottom-4 left-4 right-4 rounded-xl border border-slate-800 bg-slate-900/40 p-3 text-[11px] text-slate-500">
          <div className="font-semibold text-slate-400">SIH 2026 Prototype</div>
          <div>Ministry of Railways</div>
          <div className="text-[10px] text-slate-600 mt-1">Decision-Support Mode</div>
        </div>
      </aside>
    </>
  );
}
