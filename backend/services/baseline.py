"""
Baseline Planner Service for SIH26027
Simulates current Indian Railways uncoordinated manual scheduling practice.

Each department (ENG, OHE, S&T) plans and requests track possessions independently
using simple first-available-slot heuristics without cross-department consolidation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.models.task import MaintenanceTask
from backend.models.section import Section
from backend.models.train import TrainMovement
from backend.models.block import BlockRequest


class BaselineScheduler:
    def __init__(self, db: Session, horizon_days: int = 7):
        self.db = db
        self.horizon_days = horizon_days
        self.planning_start = datetime(2026, 9, 7, 0, 0)
        self.planning_end = self.planning_start + timedelta(days=horizon_days)

    def run(self) -> Dict[str, Any]:
        """
        Executes baseline independent scheduling for all departments.
        Returns detailed scheduled blocks and dynamic baseline metrics.
        """
        # Fetch all pending maintenance tasks
        tasks = self.db.query(MaintenanceTask).order_by(
            MaintenanceTask.section_id,
            MaintenanceTask.department_id,
            MaintenanceTask.preferred_start
        ).all()

        # Fetch train movements within the planning horizon
        movements = self.db.query(TrainMovement).filter(
            TrainMovement.scheduled_entry >= self.planning_start,
            TrainMovement.scheduled_entry <= self.planning_end
        ).all()

        # Map movements by section for rapid conflict checking
        movements_by_section: Dict[int, List[TrainMovement]] = {}
        for m in movements:
            movements_by_section.setdefault(m.section_id, []).append(m)

        scheduled_blocks: List[Dict[str, Any]] = []
        train_conflicts: List[Dict[str, Any]] = []

        total_maintenance_minutes = 0
        total_block_minutes = 0
        scheduled_task_ids = set()

        # In baseline planning, each department submits blocks independently.
        # Track section timeline separately per department
        dept_section_timeline: Dict[str, Dict[int, List[tuple]]] = {
            "ENG": {},
            "OHE": {},
            "S&T": {}
        }

        block_counter = 1

        for task in tasks:
            dept_code = task.department.code
            sec_id = task.section_id
            duration = task.duration_minutes
            total_maintenance_minutes += duration

            # Determine preferred start or default to next morning
            p_start = task.preferred_start if task.preferred_start else (self.planning_start + timedelta(hours=2))
            p_end = p_start + timedelta(minutes=duration)

            # Check if department already has a block on this section at that time
            existing_dept_slots = dept_section_timeline[dept_code].setdefault(sec_id, [])
            conflict_found = False
            for s_start, s_end in existing_dept_slots:
                if not (p_end <= s_start or p_start >= s_end):
                    conflict_found = True
                    break

            # If overlapping with same department, shift forward by duration
            if conflict_found and existing_dept_slots:
                last_end = max(s_end for _, s_end in existing_dept_slots)
                p_start = last_end + timedelta(minutes=30)
                p_end = p_start + timedelta(minutes=duration)

            existing_dept_slots.append((p_start, p_end))
            scheduled_task_ids.add(task.task_id)

            # Each task becomes its own independent block in baseline!
            block_id = f"BLK_BASE_{block_counter:04d}"
            block_counter += 1
            total_block_minutes += duration

            # Check for train conflicts in this window on this section
            sec_trains = movements_by_section.get(sec_id, [])
            conflicting_trains = []
            for trn in sec_trains:
                # Overlap check
                if not (trn.scheduled_exit <= p_start or trn.scheduled_entry >= p_end):
                    conflicting_trains.append(trn)
                    train_conflicts.append({
                        "conflict_id": f"CONF_BASE_{len(train_conflicts) + 1:04d}",
                        "block_id": block_id,
                        "task_id": task.task_id,
                        "section_id": sec_id,
                        "section_code": task.section.section_code,
                        "train_number": trn.train.train_number,
                        "train_name": trn.train.train_name,
                        "train_priority": trn.train.priority,
                        "start_time": max(p_start, trn.scheduled_entry).strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": min(p_end, trn.scheduled_exit).strftime("%Y-%m-%d %H:%M:%S"),
                        "severity": "Critical" if trn.train.priority == 5 else ("Major" if trn.train.priority >= 3 else "Minor"),
                        "description": f"Train {trn.train.train_number} ({trn.train.train_name}, Priority {trn.train.priority}) intersects independent {dept_code} block on {task.section.section_code}."
                    })

            scheduled_blocks.append({
                "block_id": block_id,
                "planning_mode": "Baseline (Independent)",
                "department": dept_code,
                "department_name": task.department.name,
                "section_id": sec_id,
                "section_code": task.section.section_code,
                "station_from": task.section.station_from.code,
                "station_to": task.section.station_to.code,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "priority_score": task.priority_score,
                "start_time": p_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": p_end.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": duration,
                "duration_hours": round(duration / 60.0, 2),
                "is_combined": False,
                "department_count": 1,
                "train_conflicts_count": len(conflicting_trains),
                "train_impact_score": sum(t.train.priority for t in conflicting_trains)
            })

        # Dynamic metrics calculation from dataset
        total_maintenance_hours = round(total_maintenance_minutes / 60.0, 1)
        total_block_hours = round(total_block_minutes / 60.0, 1)
        block_count = len(scheduled_blocks)
        avg_utilization = round((total_maintenance_minutes / total_block_minutes * 100.0), 1) if total_block_minutes > 0 else 0.0

        critical_conflicts = sum(1 for c in train_conflicts if c["severity"] == "Critical")
        major_conflicts = sum(1 for c in train_conflicts if c["severity"] == "Major")
        minor_conflicts = sum(1 for c in train_conflicts if c["severity"] == "Minor")

        overdue_tasks_count = self.db.query(MaintenanceTask).filter(MaintenanceTask.overdue_days > 0).count()

        metrics = {
            "planning_mode": "Baseline (Independent)",
            "horizon_days": self.horizon_days,
            "total_tasks": len(tasks),
            "tasks_scheduled": len(scheduled_task_ids),
            "tasks_pending": len(tasks) - len(scheduled_task_ids),
            "total_maintenance_hours": total_maintenance_hours,
            "total_block_hours": total_block_hours,
            "asset_downtime_hours": total_block_hours,
            "number_of_blocks": block_count,
            "multi_department_blocks_count": 0,  # 0 because independent
            "coordination_rate_pct": 0.0,
            "average_block_utilization_pct": avg_utilization,
            "total_train_conflicts": len(train_conflicts),
            "critical_train_conflicts": critical_conflicts,
            "major_train_conflicts": major_conflicts,
            "minor_train_conflicts": minor_conflicts,
            "overdue_tasks_remaining": overdue_tasks_count,
            "coordination_savings_hours": 0.0,
            "downtime_reduction_pct": 0.0,
            "blocks_saved": 0
        }

        return {
            "metrics": metrics,
            "blocks": scheduled_blocks,
            "conflicts": train_conflicts
        }
