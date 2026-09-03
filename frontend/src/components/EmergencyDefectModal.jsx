import React, { useState } from 'react';
import { X, AlertOctagon, ShieldAlert, CheckCircle2, Clock, Train } from 'lucide-react';
import api from '../services/api';

export default function EmergencyDefectModal({ isOpen, onClose, onTaskCreated, sections = [] }) {
  const [department, setDepartment] = useState('ENG');
  const [sectionId, setSectionId] = useState(sections[0]?.id || 1);
  const [taskType, setTaskType] = useState('Emergency Rail Fracture Detected');
  const [description, setDescription] = useState('Critical 30mm rail head crack detected via acoustic / ultrasonic monitoring.');
  const [durationMinutes, setDurationMinutes] = useState(120);
  const [safetyRequired, setSafetyRequired] = useState('Traffic Block');
  const [loading, setLoading] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAssessmentResult(null);

    try {
      const res = await api.createTask({
        department,
        section_id: Number(sectionId),
        task_type: taskType,
        description,
        criticality: 5,
        urgency: 'Immediate',
        overdue_days: 14,
        duration_minutes: Number(durationMinutes),
        crew_required: 8,
        safety_required: safetyRequired,
        is_emergency: true
      });

      setAssessmentResult(res.data);
      if (onTaskCreated) onTaskCreated(res.data);
    } catch (err) {
      console.error(err);
      alert('Error submitting emergency task: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-rose-500/40 bg-slate-900 p-5 sm:p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-rose-500/20 pb-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-rose-500/20 p-2.5 text-rose-400 border border-rose-500/40 animate-pulse">
              <AlertOctagon className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                Emergency Defect Declaration
                <span className="text-xs px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/40">
                  Priority 95-100
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                System will prioritize immediately, check timetable impact, and propose alternative window
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

        {assessmentResult ? (
          /* Results View */
          <div className="my-5 space-y-4">
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="h-5 w-5" />
                Emergency Task Logged: {assessmentResult.task_id}
              </div>
              <p className="text-xs text-slate-300 mt-1">
                Priority Score: <strong>{assessmentResult.priority_score}/100</strong> ({assessmentResult.priority_class}) on section <strong>{assessmentResult.section_code}</strong>
              </p>
            </div>

            {assessmentResult.emergency_assessment && (
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Operational Assessment</h4>
                <div className="text-xs text-slate-300 space-y-1">
                  <div>• Initial Window Checked: <span className="text-slate-200 font-medium">{assessmentResult.emergency_assessment.immediate_window_checked}</span></div>
                  <div>• Conflicting Train Movements: <span className="text-amber-400 font-bold">{assessmentResult.emergency_assessment.conflicting_trains_count} trains affected</span></div>
                  <div>• Premium Train Clashing: <span className={assessmentResult.emergency_assessment.has_critical_train ? 'text-rose-400 font-bold' : 'text-emerald-400'}>{assessmentResult.emergency_assessment.has_critical_train ? 'YES (Vande Bharat / Rajdhani)' : 'None'}</span></div>
                </div>

                {assessmentResult.emergency_assessment.recommended_safe_window && (
                  <div className="rounded-lg border border-blue-500/30 bg-blue-950/30 p-3 text-xs text-blue-200">
                    <span className="font-bold flex items-center gap-1 text-blue-300">
                      <Clock className="h-4 w-4" /> Recommended Safe Window:
                    </span>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {assessmentResult.emergency_assessment.recommended_safe_window.start_time} to {assessmentResult.emergency_assessment.recommended_safe_window.end_time}
                    </div>
                  </div>
                )}

                <div className="text-[11px] text-slate-400 bg-slate-900/90 p-2.5 rounded border border-slate-800">
                  {assessmentResult.emergency_assessment.operational_impact}
                </div>
              </div>
            )}

            <button
              onClick={() => { setAssessmentResult(null); onClose(); }}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition"
            >
              Done & Return to Dashboard
            </button>
          </div>
        ) : (
          /* Form View */
          <form onSubmit={handleSubmit} className="my-5 space-y-4 text-xs sm:text-sm">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Department</label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
                >
                  <option value="ENG">Civil Engineering (P-Way / Track)</option>
                  <option value="OHE">Traction Distribution (OHE / Catenary)</option>
                  <option value="S&T">Signal & Telecommunication</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Affected Section</label>
                <select
                  value={sectionId}
                  onChange={(e) => setSectionId(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
                >
                  {sections.slice(0, 30).map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.section_code}: {s.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Defect Name / Task Type</label>
              <input
                type="text"
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Defect Details & Location Description</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Estimated Duration (Min)</label>
                <input
                  type="number"
                  min={30}
                  max={360}
                  step={15}
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Required Protection</label>
                <select
                  value={safetyRequired}
                  onChange={(e) => setSafetyRequired(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-rose-500 focus:outline-none"
                >
                  <option value="Traffic Block">Traffic Block</option>
                  <option value="Power Block">Power Block</option>
                  <option value="Traffic & Power Block">Traffic & Power Block</option>
                  <option value="Caution Order">Caution Order (Speed Restriction)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-800">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                {loading ? 'Evaluating Corridor...' : 'Submit Emergency Defect'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
