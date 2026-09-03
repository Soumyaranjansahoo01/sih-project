"""
Task Priority Engine for SIH26027
Calculates transparent, explainable priority scores (0-100) for railway maintenance tasks.

Evaluates 5 operational factors:
1. Criticality (1-5 scale)
2. Operational Urgency (Immediate, High, Normal, Low)
3. Overdue Duration (days overdue)
4. Asset Health Condition Score (0-100 scale, inverse degradation)
5. Safety / Possession Requirement (Power Block, Traffic Block, Both)
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.config import settings
from backend.models.task import MaintenanceTask
from backend.models.asset import Asset


class TaskPriorityEngine:
    """
    Transparent mathematical priority scoring engine with explainable AI outputs.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Allow configurable weights, defaulting to application settings
        self.weights = {
            "criticality": settings.WEIGHT_CRITICALITY,
            "urgency": settings.WEIGHT_URGENCY,
            "overdue": settings.WEIGHT_OVERDUE,
            "asset_condition": settings.WEIGHT_ASSET_CONDITION,
            "safety": settings.WEIGHT_SAFETY
        }
        if weights:
            # Normalize provided weights to sum to 1.0
            total = sum(weights.values())
            if total > 0:
                self.weights = {k: v / total for k, v in weights.items()}

    def normalize_criticality(self, criticality: int) -> float:
        """Maps 1-5 criticality to 0-100 scale."""
        crit_map = {1: 20.0, 2: 40.0, 3: 60.0, 4: 80.0, 5: 100.0}
        return crit_map.get(criticality, 50.0)

    def normalize_urgency(self, urgency: str) -> float:
        """Maps urgency category to 0-100 scale."""
        urg_map = {
            "Immediate": 100.0,
            "High": 75.0,
            "Normal": 45.0,
            "Low": 20.0
        }
        return urg_map.get(urgency, 45.0)

    def normalize_overdue(self, overdue_days: int) -> float:
        """Maps overdue days to 0-100 scale (capped at 25 days overdue = 100)."""
        if overdue_days <= 0:
            return 0.0
        return min(100.0, round(overdue_days * 4.0, 1))

    def normalize_asset_condition(self, condition_score: float) -> float:
        """Inverts condition score: degraded asset (low score) yields high maintenance priority."""
        cond = max(0.0, min(100.0, condition_score))
        return round(100.0 - cond, 1)

    def normalize_safety(self, safety_required: str) -> float:
        """Maps safety isolation requirements to operational priority."""
        safety = (safety_required or "").lower()
        if "power" in safety and "traffic" in safety:
            return 100.0
        elif "power" in safety:
            return 85.0
        elif "traffic" in safety:
            return 80.0
        elif "caution" in safety:
            return 40.0
        return 15.0

    def classify_priority(self, score: float) -> str:
        """
        Classifies score into operational urgency tier:
        0-30: Low
        31-60: Medium
        61-80: High
        81-100: Critical
        """
        if score >= 81.0:
            return "Critical"
        elif score >= 61.0:
            return "High"
        elif score >= 31.0:
            return "Medium"
        return "Low"

    def evaluate_task(self, task: MaintenanceTask, asset: Optional[Asset] = None) -> Dict[str, Any]:
        """
        Calculates score and transparent breakdown for a single task.
        """
        crit_raw = task.criticality
        urg_raw = task.urgency
        overdue_raw = task.overdue_days
        cond_raw = asset.condition_score if asset else (task.asset.condition_score if task.asset else 75.0)
        safety_raw = task.safety_required or "None"

        # Normalized 0-100 values
        f_crit = self.normalize_criticality(crit_raw)
        f_urg = self.normalize_urgency(urg_raw)
        f_overdue = self.normalize_overdue(overdue_raw)
        f_cond = self.normalize_asset_condition(cond_raw)
        f_safety = self.normalize_safety(safety_raw)

        # Weighted points contribution
        p_crit = round(f_crit * self.weights["criticality"], 1)
        p_urg = round(f_urg * self.weights["urgency"], 1)
        p_overdue = round(f_overdue * self.weights["overdue"], 1)
        p_cond = round(f_cond * self.weights["asset_condition"], 1)
        p_safety = round(f_safety * self.weights["safety"], 1)

        total_score = round(p_crit + p_urg + p_overdue + p_cond + p_safety, 1)
        total_score = max(0.0, min(100.0, total_score))
        p_class = self.classify_priority(total_score)

        # Transparent human-readable reasons
        key_reasons = []
        if crit_raw >= 4:
            key_reasons.append(f"High asset/task criticality (Level {crit_raw}/5)")
        if urg_raw in ["Immediate", "High"]:
            key_reasons.append(f"{urg_raw} operational urgency")
        if overdue_raw > 0:
            key_reasons.append(f"{overdue_raw} days overdue (maintenance backlog)")
        if cond_raw < 50.0:
            key_reasons.append(f"Severely degraded asset health ({cond_raw:.1f}% remaining)")
        elif cond_raw < 70.0:
            key_reasons.append(f"Moderate asset wear ({cond_raw:.1f}% health)")
        if "block" in safety_raw.lower():
            key_reasons.append(f"Mandatory safety isolation: {safety_raw}")

        if not key_reasons:
            key_reasons.append("Routine scheduled preventive maintenance")

        explanation_summary = (
            f"Priority Score: {total_score}/100 ({p_class}). "
            f"Key factors: {'; '.join(key_reasons)}."
        )

        factor_breakdown = [
            {
                "factor_name": "Criticality",
                "raw_value": f"Level {crit_raw}/5",
                "normalized_score": f_crit,
                "weight": self.weights["criticality"],
                "contribution_points": p_crit,
                "description": f"Criticality score {f_crit:.0f}/100 based on asset hierarchy"
            },
            {
                "factor_name": "Urgency",
                "raw_value": urg_raw,
                "normalized_score": f_urg,
                "weight": self.weights["urgency"],
                "contribution_points": p_urg,
                "description": f"{urg_raw} urgency tier contributing {p_urg:.1f} points"
            },
            {
                "factor_name": "Overdue Days",
                "raw_value": f"{overdue_raw} days",
                "normalized_score": f_overdue,
                "weight": self.weights["overdue"],
                "contribution_points": p_overdue,
                "description": f"{overdue_raw} days past maintenance due date"
            },
            {
                "factor_name": "Asset Condition",
                "raw_value": f"{cond_raw:.1f}% health",
                "normalized_score": f_cond,
                "weight": self.weights["asset_condition"],
                "contribution_points": p_cond,
                "description": f"Degradation score ({f_cond:.1f}/100) based on physical wear"
            },
            {
                "factor_name": "Safety Isolation",
                "raw_value": safety_raw,
                "normalized_score": f_safety,
                "weight": self.weights["safety"],
                "contribution_points": p_safety,
                "description": f"Protection protocol requiring {safety_raw}"
            }
        ]

        return {
            "total_score": total_score,
            "priority_class": p_class,
            "key_reasons": key_reasons,
            "explanation_summary": explanation_summary,
            "factor_breakdown": factor_breakdown
        }

    def recalculate_database_tasks(self, db: Session) -> Dict[str, Any]:
        """
        Recalculates and updates priority scores and reasons for all tasks in database.
        """
        tasks = db.query(MaintenanceTask).all()
        updated_count = 0
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for task in tasks:
            result = self.evaluate_task(task, task.asset)
            task.priority_score = result["total_score"]
            task.priority_class = result["priority_class"]
            task.priority_reason = result["explanation_summary"]
            distribution[result["priority_class"]] += 1
            updated_count += 1

        db.commit()

        return {
            "tasks_updated": updated_count,
            "weights_used": self.weights,
            "distribution": distribution
        }

    def get_task_explanation(self, task_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed explainable AI breakdown for a specific task.
        """
        task = db.query(MaintenanceTask).filter(MaintenanceTask.task_id == task_id).first()
        if not task:
            return None

        result = self.evaluate_task(task, task.asset)

        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "department": task.department.code,
            "department_name": task.department.name,
            "section_code": task.section.section_code,
            "section_name": task.section.name,
            "asset_id": task.asset.asset_id,
            "asset_name": task.asset.name,
            "asset_type": task.asset.asset_type,
            "total_priority_score": result["total_score"],
            "priority_class": result["priority_class"],
            "explanation_summary": result["explanation_summary"],
            "key_reasons": result["key_reasons"],
            "factor_breakdown": result["factor_breakdown"]
        }
