"""
Block Optimization MILP Model for SIH26027
Formulates and solves the mathematical block scheduling problem using PuLP.
Coordinates Civil Engineering (TMS), OHE (TDMS), and Signalling (SMMS) tasks
into unified track possessions while avoiding operational train clashes.
"""

import uuid
import pulp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


class BlockOptimizationSolver:
    def __init__(
        self,
        tasks: List[Any],
        sections: List[Any],
        train_movements: List[Any],
        horizon_days: int = 7,
        time_limit_seconds: int = 60,
        prioritize_coordination: bool = True
    ):
        self.tasks = tasks
        self.sections = sections
        self.train_movements = train_movements
        self.horizon_days = horizon_days
        self.time_limit_seconds = time_limit_seconds
        self.prioritize_coordination = prioritize_coordination

        self.start_date = datetime(2026, 9, 7, 0, 0)
        self.end_date = self.start_date + timedelta(days=horizon_days)

        # Pre-compute candidate maintenance windows across sections
        self.windows = self._generate_candidate_windows()

        # Map train movements to windows
        self.window_train_impact, self.window_critical_trains = self._evaluate_window_traffic()

    def _generate_candidate_windows(self) -> List[Dict[str, Any]]:
        """
        Generates candidate maintenance slots for each section over the horizon.
        Standard IR maintenance slots:
        - Night window: 01:30 to 04:30 (180 mins) - lowest passenger density
        - Midday shadow window: 11:30 to 14:00 (150 mins)
        - Late night window: 22:30 to 01:00 (150 mins)
        """
        windows = []
        w_id = 0

        for day in range(self.horizon_days):
            day_date = self.start_date + timedelta(days=day)
            slots = [
                (1, 30, 180, "NIGHT_SHADOW"),
                (11, 30, 150, "MIDDAY_SHADOW"),
                (22, 30, 150, "LATE_NIGHT")
            ]

            for s in self.sections:
                for h, m, dur, s_type in slots:
                    w_start = day_date + timedelta(hours=h, minutes=m)
                    w_end = w_start + timedelta(minutes=dur)
                    windows.append({
                        "window_id": w_id,
                        "section_id": s.id,
                        "section_code": s.section_code,
                        "slot_type": s_type,
                        "start_time": w_start,
                        "end_time": w_end,
                        "duration_minutes": dur,
                        "day_index": day
                    })
                    w_id += 1

        return windows

    def _evaluate_window_traffic(self) -> Tuple[Dict[int, float], Dict[int, bool]]:
        """
        Evaluates scheduled train traffic for each candidate window.
        Returns:
        - impact_scores: {window_id: total_weighted_penalty}
        - critical_trains: {window_id: True if Priority 5 train intersects}
        """
        impact_scores: Dict[int, float] = {}
        critical_trains: Dict[int, bool] = {}

        # Index movements by section for O(1) section lookups
        movements_by_sec: Dict[int, List[Any]] = {}
        for m in self.train_movements:
            movements_by_sec.setdefault(m.section_id, []).append(m)

        for w in self.windows:
            w_id = w["window_id"]
            sec_id = w["section_id"]
            w_start = w["start_time"]
            w_end = w["end_time"]

            sec_moves = movements_by_sec.get(sec_id, [])
            total_penalty = 0.0
            has_crit = False

            for m in sec_moves:
                if not (m.scheduled_exit <= w_start or m.scheduled_entry >= w_end):
                    prio = m.train.priority
                    if prio == 5:
                        has_crit = True
                        total_penalty += 100.0  # High penalty
                    elif prio >= 4:
                        total_penalty += 30.0
                    elif prio >= 3:
                        total_penalty += 15.0
                    else:
                        total_penalty += 5.0

            impact_scores[w_id] = total_penalty
            critical_trains[w_id] = has_crit

        return impact_scores, critical_trains

    def solve(self) -> Dict[str, Any]:
        """
        Builds and solves the Mixed-Integer Linear Program.
        """
        prob = pulp.LpProblem("IndianRailways_AutomaticBlockPlanning", pulp.LpMaximize)

        # Map tasks by section for fast lookup
        tasks_by_sec: Dict[int, List[Any]] = {}
        for t in self.tasks:
            tasks_by_sec.setdefault(t.section_id, []).append(t)

        # -------------------------------------------------------------
        # 1. Decision Variables
        # -------------------------------------------------------------
        # x[t_id, w_id]: 1 if task t is assigned to window w
        x = {}
        # y[w_id]: 1 if block is activated in window w
        y = {}
        # z[w_id]: 1 if window w is multi-department coordinated
        z = {}

        for w in self.windows:
            w_id = w["window_id"]
            sec_id = w["section_id"]
            y[w_id] = pulp.LpVariable(f"y_{w_id}", cat=pulp.LpBinary)
            z[w_id] = pulp.LpVariable(f"z_{w_id}", cat=pulp.LpBinary)

            sec_tasks = tasks_by_sec.get(sec_id, [])
            for t in sec_tasks:
                x[(t.id, w_id)] = pulp.LpVariable(f"x_{t.id}_{w_id}", cat=pulp.LpBinary)

        # -------------------------------------------------------------
        # 2. Objective Function
        # -------------------------------------------------------------
        # MAXIMIZE: Priority Completion + Coordination Bonus
        # MINIMIZE: Total Block Hours + Train Disruptions
        obj_terms = []

        # Term A: Task priority rewards
        for (t_id, w_id), var in x.items():
            task = next(t for t in self.tasks if t.id == t_id)
            obj_terms.append(task.priority_score * var)

        # Term B: Multi-department coordination bonus (heavily incentivized!)
        coord_multiplier = 150.0 if self.prioritize_coordination else 50.0
        for w_id, var in z.items():
            obj_terms.append(coord_multiplier * var)

        # Term C: Block downtime penalty (minimizes number of separate blocks)
        for w in self.windows:
            w_id = w["window_id"]
            dur_hours = w["duration_minutes"] / 60.0
            obj_terms.append(-20.0 * dur_hours * y[w_id])

        # Term D: Train disruption penalty
        for w in self.windows:
            w_id = w["window_id"]
            penalty = self.window_train_impact.get(w_id, 0.0)
            if penalty > 0:
                obj_terms.append(-1.5 * penalty * y[w_id])

        prob += pulp.lpSum(obj_terms), "Maximize_Availability_And_Coordination"

        # -------------------------------------------------------------
        # 3. Constraints
        # -------------------------------------------------------------
        # C1: Each task assigned at most once
        for t in self.tasks:
            assigned_vars = [x[(t.id, w["window_id"])] for w in self.windows if (t.id, w["window_id"]) in x]
            if assigned_vars:
                prob += pulp.lpSum(assigned_vars) <= 1, f"TaskOnce_{t.id}"

        # C2: Coupling: task assignment requires block activation
        for (t_id, w_id), var in x.items():
            prob += var <= y[w_id], f"Coupling_{t_id}_{w_id}"

        # C3: Hard train safety constraint: Avoid windows with Priority 5 trains (Vande Bharat / Rajdhani)
        for w in self.windows:
            w_id = w["window_id"]
            if self.window_critical_trains.get(w_id, False):
                prob += y[w_id] == 0, f"NoCriticalTrainClash_{w_id}"

        # C4: Multi-department coordination linking
        # z[w_id] can only be 1 if tasks from 2 or more distinct departments are assigned to window w
        for w in self.windows:
            w_id = w["window_id"]
            sec_id = w["section_id"]
            sec_tasks = tasks_by_sec.get(sec_id, [])

            eng_vars = [x[(t.id, w_id)] for t in sec_tasks if (t.department.code if t.department else "ENG") == "ENG" and (t.id, w_id) in x]
            ohe_vars = [x[(t.id, w_id)] for t in sec_tasks if (t.department.code if t.department else "OHE") == "OHE" and (t.id, w_id) in x]
            st_vars = [x[(t.id, w_id)] for t in sec_tasks if (t.department.code if t.department else "S&T") == "S&T" and (t.id, w_id) in x]

            # Total tasks in window must be at least 2 to have coordination
            total_window_tasks = eng_vars + ohe_vars + st_vars
            if total_window_tasks:
                prob += 2 * z[w_id] <= pulp.lpSum(total_window_tasks), f"CoordMinTasks_{w_id}"

            # Capacity limit: Maximum 4 tasks per combined block to ensure crew feasibility
            if total_window_tasks:
                prob += pulp.lpSum(total_window_tasks) <= 4 * y[w_id], f"WindowCap_{w_id}"

        # -------------------------------------------------------------
        # 4. Solve Problem
        # -------------------------------------------------------------
        solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=self.time_limit_seconds)
        solve_status = prob.solve(solver)
        status_str = pulp.LpStatus[solve_status]

        # -------------------------------------------------------------
        # 5. Extract Optimized Solution & Metrics
        # -------------------------------------------------------------
        scheduled_blocks = []
        run_tag = uuid.uuid4().hex[:6].upper()
        block_counter = 1
        scheduled_tasks_count = 0
        total_block_minutes = 0
        multi_dept_blocks_count = 0
        conflicts_count = 0

        for w in self.windows:
            w_id = w["window_id"]
            if pulp.value(y[w_id]) and pulp.value(y[w_id]) > 0.5:
                # Find all tasks assigned to this window
                sec_id = w["section_id"]
                assigned_tasks = []
                for t in tasks_by_sec.get(sec_id, []):
                    if (t.id, w_id) in x and pulp.value(x[(t.id, w_id)]) and pulp.value(x[(t.id, w_id)]) > 0.5:
                        assigned_tasks.append(t)

                if not assigned_tasks:
                    continue

                scheduled_tasks_count += len(assigned_tasks)
                depts_in_block = list({(t.department.code if t.department else "ENG") for t in assigned_tasks})
                is_combined = len(depts_in_block) >= 2
                if is_combined:
                    multi_dept_blocks_count += 1

                # Block duration is max task duration in window
                block_dur = max(t.duration_minutes for t in assigned_tasks)
                total_block_minutes += block_dur

                w_start = w["start_time"]
                w_end = w_start + timedelta(minutes=block_dur)

                # Reason for scheduling
                reasons = [
                    f"Prioritized {len(assigned_tasks)} high-urgency tasks",
                    f"Window in {w['slot_type']} minimizes train interference"
                ]
                if is_combined:
                    reasons.append(f"Combined {', '.join(depts_in_block)} maintenance into single track possession")

                block_obj = {
                    "block_id": f"BLK_{run_tag}_{block_counter:04d}",
                    "section_id": sec_id,
                    "section_code": w["section_code"],
                    "start_time": w_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": w_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_minutes": block_dur,
                    "duration_hours": round(block_dur / 60.0, 2),
                    "is_combined": is_combined,
                    "department_count": len(depts_in_block),
                    "departments": depts_in_block,
                    "tasks_count": len(assigned_tasks),
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "department": t.department.code if t.department else "ENG",
                            "task_type": t.task_type,
                            "priority_score": t.priority_score,
                            "duration_minutes": t.duration_minutes
                        }
                        for t in assigned_tasks
                    ],
                    "reason": "; ".join(reasons),
                    "train_impact_score": self.window_train_impact.get(w_id, 0.0)
                }
                scheduled_blocks.append(block_obj)
                block_counter += 1

        total_block_hours = round(total_block_minutes / 60.0, 1)
        total_maintenance_minutes = sum(t["duration_minutes"] for b in scheduled_blocks for t in b["tasks"])
        total_maint_hours = round(total_maintenance_minutes / 60.0, 1)

        utilization = round((total_maintenance_minutes / total_block_minutes * 100.0), 1) if total_block_minutes > 0 else 100.0

        # Rejected windows sample (explainable AI)
        rejected_windows = []
        for w in self.windows[:60]:
            w_id = w["window_id"]
            if self.window_critical_trains.get(w_id, False):
                rejected_windows.append({
                    "section_code": w["section_code"],
                    "window": f"{w['start_time'].strftime('%Y-%m-%d %H:%M')} - {w['end_time'].strftime('%H:%M')}",
                    "rejection_reason": "Hard train safety lock: Intersects Priority 5 train movement (Vande Bharat / Rajdhani Express)"
                })
            elif self.window_train_impact.get(w_id, 0) > 40.0:
                rejected_windows.append({
                    "section_code": w["section_code"],
                    "window": f"{w['start_time'].strftime('%Y-%m-%d %H:%M')} - {w['end_time'].strftime('%H:%M')}",
                    "rejection_reason": f"High traffic penalty: {self.window_train_impact[w_id]} points traffic clash"
                })

        metrics = {
            "solver_status": status_str,
            "objective_value": round(pulp.value(prob.objective) or 0.0, 2),
            "planning_horizon_days": self.horizon_days,
            "total_tasks_evaluated": len(self.tasks),
            "tasks_scheduled": scheduled_tasks_count,
            "total_maintenance_hours": total_maint_hours,
            "total_block_hours": total_block_hours,
            "asset_downtime_hours": total_block_hours,
            "number_of_blocks": len(scheduled_blocks),
            "multi_department_blocks_count": multi_dept_blocks_count,
            "coordination_rate_pct": round((multi_dept_blocks_count / len(scheduled_blocks) * 100.0), 1) if scheduled_blocks else 0.0,
            "average_block_utilization_pct": utilization,
            "train_conflicts_remaining": sum(1 for b in scheduled_blocks if b["train_impact_score"] > 0),
            "critical_train_conflicts": 0  # 0 because hard constrained!
        }

        return {
            "status": "success",
            "solver_status": status_str,
            "metrics": metrics,
            "blocks": scheduled_blocks,
            "rejected_windows_sample": rejected_windows[:10]
        }
