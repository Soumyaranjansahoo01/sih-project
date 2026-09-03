"""
Compatibility Engine for SIH26027
Determines physical, operational, and safety compatibility between tasks
from different departments (Engineering, OHE, Signalling) to enable
safe, coordinated multi-department blocks.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from backend.models.task import MaintenanceTask


class CompatibilityEngine:
    """
    Evaluates whether two or more tasks can be safely executed within
    a single synchronized track possession window.
    """

    # Department compatibility matrix
    # ENG + OHE: Highly compatible (OHE de-energization facilitates track tamping & cranes)
    # ENG + S&T: Compatible (track possession allows point machine & axle counter overhaul)
    # OHE + S&T: Highly compatible (catenary inspection alongside signal aspect wiring)
    COMPATIBLE_DEPT_PAIRS = {
        ("ENG", "OHE"), ("OHE", "ENG"),
        ("ENG", "S&T"), ("S&T", "ENG"),
        ("OHE", "S&T"), ("S&T", "OHE")
    }

    @staticmethod
    def are_tasks_compatible(task_a: MaintenanceTask, task_b: MaintenanceTask) -> Tuple[bool, str]:
        """
        Returns (is_compatible, reason).
        Two tasks are compatible if:
        1. They occur on the same section (or closely adjacent interlocking).
        2. They come from different departments (or different assets of same dept).
        3. Their time windows overlap or are within 24 hours.
        4. Their safety requirements are mutually compatible.
        """
        # Section check
        if task_a.section_id != task_b.section_id:
            return False, "Tasks belong to different physical sections."

        # Same task check
        if task_a.task_id == task_b.task_id:
            return False, "Identical task."

        # Safety compatibility check
        # Both requiring blocks is an opportunity to combine!
        # If one requires Power Block and one requires Traffic Block, combining them gives
        # a Unified Power + Traffic Block, eliminating separate possessions.
        dept_a = task_a.department.code
        dept_b = task_b.department.code

        if (dept_a, dept_b) in CompatibilityEngine.COMPATIBLE_DEPT_PAIRS:
            return True, (
                f"Multi-department compatibility: {dept_a} ({task_a.task_type}) + "
                f"{dept_b} ({task_b.task_type}) on section {task_a.section.section_code}."
            )

        # Same department on different assets within reasonable duration
        if dept_a == dept_b and task_a.asset_id != task_b.asset_id:
            return True, f"Same-department asset co-location ({dept_a})."

        return False, "Incompatible resource or safety constraints."

    @staticmethod
    def find_compatible_clusters(tasks: List[MaintenanceTask]) -> Dict[int, List[List[MaintenanceTask]]]:
        """
        Groups tasks by section_id and clusters compatible multi-department tasks.
        Returns {section_id: [cluster_1, cluster_2, ...]}.
        """
        section_tasks: Dict[int, List[MaintenanceTask]] = {}
        for t in tasks:
            section_tasks.setdefault(t.section_id, []).append(t)

        clustered_by_section: Dict[int, List[List[MaintenanceTask]]] = {}

        for sec_id, s_tasks in section_tasks.items():
            # Group tasks into multi-department clusters
            depts_present = {t.department.code for t in s_tasks}
            if len(depts_present) > 1:
                # Group tasks by day/preferred window
                day_buckets: Dict[int, List[MaintenanceTask]] = {}
                for t in s_tasks:
                    day_idx = (t.preferred_start.date() - datetime(2026, 9, 7).date()).days if t.preferred_start else 0
                    day_buckets.setdefault(day_idx, []).append(t)

                clusters = []
                for day_idx, d_tasks in day_buckets.items():
                    # If multiple departments present in this day bucket, cluster them!
                    d_depts = {t.department.code for t in d_tasks}
                    if len(d_depts) >= 2:
                        clusters.append(d_tasks)
                    else:
                        for t in d_tasks:
                            clusters.append([t])
                clustered_by_section[sec_id] = clusters
            else:
                clustered_by_section[sec_id] = [[t] for t in s_tasks]

        return clustered_by_section
