import React, { useState, useEffect } from 'react';
import { Play, Sparkles, AlertOctagon, Menu, X, Clock, ShieldCheck } from 'lucide-react';

export default function Navbar({
  onRunOptimization,
  onRunBaseline,
  onOpenEmergencyModal,
  isOptimizing,
  onToggleMobileMenu
}) {
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-4 sm:px-6 py-3">
      <div className="flex items-center justify-between gap-4">
        {/* Left Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-blue-600 flex items-center justify-center font-bold text-white text-base shadow-lg shadow-blue-500/20">
              IR
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm sm:text-base font-bold text-white tracking-tight">
                  SIH26027 • Automatic Block Planning
                </h1>
                <span className="hidden sm:inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  MoR Prototype
                </span>
              </div>
              <p className="hidden sm:block text-xs text-slate-400">
                Decision-Support System to Maximize Asset Availability
              </p>
            </div>
          </div>
        </div>

        {/* Right Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Live Clock */}
          <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 font-mono">
            <Clock className="h-3.5 w-3.5 text-blue-400" />
            <span>{currentTime}</span>
          </div>

          {/* Emergency Defect Button */}
          <button
            onClick={onOpenEmergencyModal}
            className="flex items-center gap-1.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-lg bg-rose-600/20 text-rose-300 border border-rose-500/40 hover:bg-rose-600/30 font-semibold text-xs sm:text-sm transition"
            title="Declare Emergency Defect"
          >
            <AlertOctagon className="h-4 w-4 text-rose-400" />
            <span className="hidden sm:inline">Emergency Defect</span>
          </button>

          {/* Baseline Button */}
          <button
            onClick={onRunBaseline}
            disabled={isOptimizing}
            className="flex items-center gap-1.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs sm:text-sm transition disabled:opacity-50"
            title="Generate Baseline Uncoordinated Plan"
          >
            <Play className="h-3.5 w-3.5 text-slate-400" />
            <span className="hidden md:inline">Generate Baseline</span>
          </button>

          {/* Run Optimization Button */}
          <button
            onClick={onRunOptimization}
            disabled={isOptimizing}
            className="flex items-center gap-1.5 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-lg bg-gradient-to-r from-blue-600 to-sky-500 hover:from-blue-500 hover:to-sky-400 text-white font-semibold text-xs sm:text-sm shadow-md shadow-blue-500/20 transition disabled:opacity-50"
          >
            <Sparkles className={`h-4 w-4 ${isOptimizing ? 'animate-spin' : ''}`} />
            <span>{isOptimizing ? 'Optimizing...' : 'Run AI Optimizer'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
