import React, { useRef, useEffect, useState, useMemo } from 'react';
import { CalendarDays, Layers, Info, Train } from 'lucide-react';

const DEPT_COLORS = {
  ENG: { bg: '#1d4ed8', combined: '#0ea5e9', label: '#93c5fd' },
  OHE: { bg: '#d97706', combined: '#f59e0b', label: '#fcd34d' },
  'S&T': { bg: '#047857', combined: '#10b981', label: '#6ee7b7' },
  COMBINED: { bg: '#7c3aed', combined: '#8b5cf6', label: '#c4b5fd' },
};

function parseTime(str) {
  const d = new Date(str);
  if (isNaN(d)) return null;
  return d;
}

// Get day label "Day 1 (Mon)" from date string
function dayLabel(dt) {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return `${days[dt.getDay()]} ${dt.getDate()}`;
}

export default function GanttPage({ scheduleData }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [hoveredBlock, setHoveredBlock] = useState(null);
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, data: null });

  const blocks = useMemo(() => {
    if (!scheduleData?.blocks) return [];
    return scheduleData.blocks.filter(b => {
      const s = parseTime(b.start_time);
      const e = parseTime(b.end_time);
      return s && e;
    });
  }, [scheduleData]);

  // Compute timeline bounds
  const { minTime, maxTime, sections, sectionRows } = useMemo(() => {
    if (!blocks.length) return { minTime: new Date(), maxTime: new Date(), sections: [], sectionRows: {} };

    let minT = Infinity, maxT = -Infinity;
    const secSet = new Set();
    blocks.forEach(b => {
      const s = parseTime(b.start_time).getTime();
      const e = parseTime(b.end_time).getTime();
      if (s < minT) minT = s;
      if (e > maxT) maxT = e;
      secSet.add(b.section_code);
    });

    const secList = [...secSet].sort();
    const rowMap = {};
    secList.forEach((s, i) => { rowMap[s] = i; });

    return { minTime: new Date(minT), maxTime: new Date(maxT), sections: secList, sectionRows: rowMap };
  }, [blocks]);

  const LABEL_WIDTH = 110;
  const ROW_HEIGHT = 36;
  const HEADER_HEIGHT = 40;
  const BLOCK_MARGIN = 4;

  const totalDuration = maxTime.getTime() - minTime.getTime();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !blocks.length) return;

    const width = containerRef.current?.offsetWidth || 900;
    const chartWidth = Math.max(800, width - LABEL_WIDTH);
    canvas.width = LABEL_WIDTH + chartWidth;
    canvas.height = HEADER_HEIGHT + sections.length * ROW_HEIGHT;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw day markers
    const msInDay = 86400000;
    const dayStart = new Date(minTime);
    dayStart.setHours(0, 0, 0, 0);
    let dayIter = dayStart.getTime();
    const dayColors = ['#1e293b', '#0f172a'];
    let dayIdx = 0;
    while (dayIter < maxTime.getTime()) {
      const x = LABEL_WIDTH + ((dayIter - minTime.getTime()) / totalDuration) * chartWidth;
      const nextDay = dayIter + msInDay;
      const w = Math.min(chartWidth, ((Math.min(nextDay, maxTime.getTime()) - dayIter) / totalDuration) * chartWidth);

      ctx.fillStyle = dayColors[dayIdx % 2];
      ctx.fillRect(x, HEADER_HEIGHT, w, canvas.height - HEADER_HEIGHT);

      // Day label
      const label = dayLabel(new Date(dayIter));
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.fillStyle = '#64748b';
      ctx.fillText(label, Math.max(x + 4, LABEL_WIDTH + 2), HEADER_HEIGHT - 12);

      // Day separator
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, HEADER_HEIGHT);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();

      dayIdx++;
      dayIter = nextDay;
    }

    // Header line
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, HEADER_HEIGHT);
    ctx.lineTo(canvas.width, HEADER_HEIGHT);
    ctx.stroke();

    // Row separators and labels
    sections.forEach((sec, idx) => {
      const y = HEADER_HEIGHT + idx * ROW_HEIGHT;

      // Label background
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, y, LABEL_WIDTH, ROW_HEIGHT);

      // Row separator
      ctx.strokeStyle = '#1e293b';
      ctx.beginPath();
      ctx.moveTo(0, y + ROW_HEIGHT);
      ctx.lineTo(canvas.width, y + ROW_HEIGHT);
      ctx.stroke();

      // Section label
      ctx.font = '10px "Courier New", monospace';
      ctx.fillStyle = '#94a3b8';
      const labelText = sec.length > 14 ? sec.slice(0, 13) + '…' : sec;
      ctx.fillText(labelText, 4, y + ROW_HEIGHT / 2 + 4);
    });

    // Label/Chart separator
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(LABEL_WIDTH, 0);
    ctx.lineTo(LABEL_WIDTH, canvas.height);
    ctx.stroke();

    // Draw blocks
    blocks.forEach(b => {
      const row = sectionRows[b.section_code];
      if (row === undefined) return;

      const s = parseTime(b.start_time).getTime();
      const e = parseTime(b.end_time).getTime();
      const x = LABEL_WIDTH + ((s - minTime.getTime()) / totalDuration) * chartWidth;
      const w = Math.max(3, ((e - s) / totalDuration) * chartWidth);
      const y = HEADER_HEIGHT + row * ROW_HEIGHT + BLOCK_MARGIN;
      const h = ROW_HEIGHT - BLOCK_MARGIN * 2;

      let color;
      if (b.is_combined) {
        color = DEPT_COLORS.COMBINED.bg;
      } else {
        const dept = b.departments?.[0] || 'ENG';
        color = DEPT_COLORS[dept]?.bg || '#334155';
      }

      // Block rectangle
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 3);
      ctx.fill();

      // Block border
      ctx.strokeStyle = b.is_combined ? '#a78bfa' : 'rgba(255,255,255,0.15)';
      ctx.lineWidth = b.is_combined ? 1.5 : 0.5;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 3);
      ctx.stroke();

      // Block label text
      if (w > 30) {
        ctx.font = `${b.is_combined ? 'bold ' : ''}9px Inter, sans-serif`;
        ctx.fillStyle = 'rgba(255,255,255,0.9)';
        ctx.fillText(b.departments?.join('+') || 'ENG', x + 3, y + h / 2 + 3);
      }
    });
  }, [blocks, sections, sectionRows, minTime, maxTime, totalDuration]);

  // Mouse hover for tooltip
  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const chartWidth = canvas.width - LABEL_WIDTH;

    if (mx < LABEL_WIDTH) {
      setTooltip(t => ({ ...t, visible: false }));
      return;
    }

    const rowIdx = Math.floor((my - HEADER_HEIGHT) / ROW_HEIGHT);
    const hoveredSec = sections[rowIdx];
    if (!hoveredSec) { setTooltip(t => ({ ...t, visible: false })); return; }

    const hoverMs = minTime.getTime() + ((mx - LABEL_WIDTH) / chartWidth) * totalDuration;

    const hit = blocks.find(b => {
      if (b.section_code !== hoveredSec) return false;
      const s = parseTime(b.start_time).getTime();
      const e = parseTime(b.end_time).getTime();
      return hoverMs >= s && hoverMs <= e;
    });

    if (hit) {
      setTooltip({ visible: true, x: e.clientX, y: e.clientY, data: hit });
    } else {
      setTooltip(t => ({ ...t, visible: false }));
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <CalendarDays className="h-5 w-5 text-blue-400" /> Multi-Track Interactive Gantt Chart
          </h2>
          <p className="text-xs text-slate-400">Run AI Optimizer first to populate the Gantt with coordinated blocks</p>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs">
        {[
          { label: 'Civil Engineering (ENG)', color: '#1d4ed8' },
          { label: 'Traction Distribution (OHE)', color: '#d97706' },
          { label: 'Signalling & Telecom (S&T)', color: '#047857' },
          { label: 'Combined Multi-Dept Block ★', color: '#7c3aed' },
        ].map(l => (
          <div key={l.label} className="flex items-center gap-1.5">
            <div className="h-3 w-6 rounded" style={{ background: l.color }} />
            <span className="text-slate-300">{l.label}</span>
          </div>
        ))}
      </div>

      {/* Stats Row */}
      {scheduleData && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Total Blocks', value: scheduleData.total_blocks || blocks.length },
            { label: 'Sections Covered', value: sections.length },
            { label: 'Combined Blocks', value: blocks.filter(b => b.is_combined).length, color: 'text-purple-400' },
            { label: 'Horizon', value: '7 days' },
          ].map(s => (
            <div key={s.label} className="rounded-xl border border-slate-800 bg-slate-900 p-3 text-xs">
              <div className="text-slate-400">{s.label}</div>
              <div className={`text-xl font-bold text-white mt-0.5 ${s.color || ''}`}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Gantt Canvas */}
      <div ref={containerRef} className="rounded-2xl border border-slate-800 bg-slate-950 overflow-auto relative"
        style={{ maxHeight: 'calc(100vh - 360px)' }}>
        {blocks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Layers className="h-12 w-12 mb-3 opacity-30" />
            <p className="font-medium">No schedule data yet</p>
            <p className="text-xs mt-1">Run the AI Optimizer using the button in the top navigation</p>
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setTooltip(t => ({ ...t, visible: false }))}
            className="cursor-crosshair block"
          />
        )}
      </div>

      {/* Tooltip */}
      {tooltip.visible && tooltip.data && (
        <div
          className="fixed z-50 rounded-xl border border-slate-700 bg-slate-950 p-3 shadow-2xl text-xs pointer-events-none"
          style={{ left: tooltip.x + 14, top: tooltip.y - 14 }}
        >
          <div className={`font-bold text-sm mb-1 ${tooltip.data.is_combined ? 'text-purple-300' : 'text-blue-300'}`}>
            {tooltip.data.is_combined ? '★ Combined Block' : 'Maintenance Block'}
          </div>
          <div className="text-slate-300">{tooltip.data.block_id}</div>
          <div className="text-slate-400 mt-1">Section: <strong className="text-slate-200">{tooltip.data.section_code}</strong></div>
          <div className="text-slate-400">Depts: <strong className="text-slate-200">{tooltip.data.departments?.join(' + ')}</strong></div>
          <div className="text-slate-400">Start: {tooltip.data.start_time}</div>
          <div className="text-slate-400">Duration: <strong className="text-slate-200">{tooltip.data.duration_minutes} min</strong></div>
          <div className="text-slate-400">Tasks: {tooltip.data.tasks_count}</div>
        </div>
      )}
    </div>
  );
}
