"""
Train Conflict Detector for SIH26027
Analyzes train timetable interactions with proposed maintenance windows.
Computes traffic impact scores, detects collisions, and identifies safe alternative slots.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.train import TrainMovement


class ConflictDetector:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_window_conflicts(
        self,
        section_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Checks whether scheduled train movements intersect the requested section window.
        Returns:
        - is_clear: True if no conflicting trains
        - conflict_count: Total trains affected
        - train_impact_score: Weighted traffic disruption score
        - conflicting_trains: List of train details
        - has_critical_train: True if priority 5 (Vande Bharat / Rajdhani) affected
        """
        conflicting_movements = self.db.query(TrainMovement).filter(
            TrainMovement.section_id == section_id,
            TrainMovement.scheduled_entry < end_time,
            TrainMovement.scheduled_exit > start_time
        ).all()

        impact_score = 0.0
        has_critical = False
        train_details = []

        for m in conflicting_movements:
            train = m.train
            prio = train.priority
            if prio == 5:
                has_critical = True
                impact_score += 50.0  # Heavy penalty for premium trains
            elif prio >= 4:
                impact_score += 25.0
            elif prio >= 3:
                impact_score += 10.0
            else:
                impact_score += 5.0

            train_details.append({
                "train_number": train.train_number,
                "train_name": train.train_name,
                "train_type": train.train_type,
                "priority": prio,
                "entry_time": m.scheduled_entry.strftime("%Y-%m-%d %H:%M:%S"),
                "exit_time": m.scheduled_exit.strftime("%Y-%m-%d %H:%M:%S")
            })

        return {
            "is_clear": len(conflicting_movements) == 0,
            "conflict_count": len(conflicting_movements),
            "train_impact_score": impact_score,
            "has_critical_train": has_critical,
            "conflicting_trains": train_details
        }

    def find_best_alternative_window(
        self,
        section_id: int,
        preferred_date: datetime,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """
        Searches candidate windows around preferred_date to find a window
        with zero or minimal train conflicts.
        """
        # Candidate slots: 01:00-05:00 (Night), 11:30-14:00 (Shadow Midday), 22:30-01:00 (Late Night)
        candidate_hours = [1, 2, 3, 11, 12, 13, 23]
        best_slot = None
        min_impact = float("inf")

        for h in candidate_hours:
            candidate_start = datetime(
                preferred_date.year, preferred_date.month, preferred_date.day, h, 0
            )
            candidate_end = candidate_start + timedelta(minutes=duration_minutes)

            eval_res = self.evaluate_window_conflicts(section_id, candidate_start, candidate_end)
            if eval_res["train_impact_score"] < min_impact:
                min_impact = eval_res["train_impact_score"]
                best_slot = {
                    "start_time": candidate_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": candidate_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "conflict_count": eval_res["conflict_count"],
                    "train_impact_score": eval_res["train_impact_score"],
                    "has_critical_train": eval_res["has_critical_train"]
                }
                if min_impact == 0:
                    break

        return best_slot or {}
