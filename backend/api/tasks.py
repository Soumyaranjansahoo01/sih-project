from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from backend.database import get_db
from backend.models.task import MaintenanceTask
from backend.models.department import Department
from backend.models.section import Section
from backend.models.asset import Asset
from backend.schemas.task import (
    PriorityWeightConfig,
    TaskPriorityExplanation,
    TaskCreateRequest,
    EmergencyTaskResponse
)
from backend.services.task_priority import TaskPriorityEngine
from backend.services.conflict_detector import ConflictDetector

router = APIRouter(prefix="/tasks", tags=["Maintenance Tasks"])


@router.get("")
def list_tasks(
    department: Optional[str] = Query(None, description="Filter by department code (ENG, OHE, S&T)"),
    priority_class: Optional[str] = Query(None, description="Filter by priority tier (Critical, High, Medium, Low)"),
    section_id: Optional[int] = Query(None, description="Filter by section ID"),
    min_priority: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum priority score"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List maintenance tasks with filtering by department, priority class, section, and score.
    """
    query = db.query(MaintenanceTask)

    if department:
        query = query.join(Department).filter(Department.code == department.upper())
    if priority_class:
        query = query.filter(MaintenanceTask.priority_class == priority_class.capitalize())
    if section_id:
        query = query.filter(MaintenanceTask.section_id == section_id)
    if min_priority is not None:
        query = query.filter(MaintenanceTask.priority_score >= min_priority)

    total_count = query.count()
    tasks = query.order_by(MaintenanceTask.priority_score.desc()).offset(offset).limit(limit).all()

    items = []
    for t in tasks:
        items.append({
            "id": t.id,
            "task_id": t.task_id,
            "department": t.department.code,
            "department_name": t.department.name,
            "asset_id": t.asset.asset_id,
            "asset_name": t.asset.name,
            "asset_type": t.asset.asset_type,
            "section_id": t.section_id,
            "section_code": t.section.section_code,
            "station_from": t.section.station_from.code,
            "station_to": t.section.station_to.code,
            "task_type": t.task_type,
            "description": t.description,
            "criticality": t.criticality,
            "urgency": t.urgency,
            "overdue_days": t.overdue_days,
            "duration_minutes": t.duration_minutes,
            "crew_required": t.crew_required,
            "equipment_required": t.equipment_required,
            "safety_required": t.safety_required,
            "priority_score": t.priority_score,
            "priority_class": t.priority_class,
            "priority_reason": t.priority_reason,
            "status": t.status,
            "preferred_start": t.preferred_start.strftime("%Y-%m-%d %H:%M:%S") if t.preferred_start else None,
            "preferred_end": t.preferred_end.strftime("%Y-%m-%d %H:%M:%S") if t.preferred_end else None
        })

    return {
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "tasks": items
    }


@router.post("", response_model=Dict[str, Any])
def create_task(req: TaskCreateRequest, db: Session = Depends(get_db)):
    """
    Creates a new maintenance task or emergency defect.
    If flagged as an emergency:
    1. Assigns top priority (95-100/100).
    2. Searches for the best safe available block slot.
    3. Identifies potentially affected trains.
    4. Proposes an operational mitigation window without overriding signalling.
    """
    dept = db.query(Department).filter(Department.code == req.department.upper()).first()
    if not dept:
        raise HTTPException(status_code=400, detail=f"Invalid department {req.department}")

    sec = db.query(Section).filter(Section.id == req.section_id).first()
    if not sec:
        raise HTTPException(status_code=400, detail=f"Invalid section ID {req.section_id}")

    # Find or pick asset
    asset = None
    if req.asset_id:
        asset = db.query(Asset).filter(Asset.asset_id == req.asset_id).first()
    if not asset:
        asset = db.query(Asset).filter(Asset.section_id == req.section_id, Asset.department_id == dept.id).first()
    if not asset:
        asset = db.query(Asset).filter(Asset.section_id == req.section_id).first()

    # Generate task ID
    task_code = f"MT_{uuid.uuid4().hex[:6].upper()}"

    # Evaluate priority
    engine = TaskPriorityEngine()
    crit = 5 if req.is_emergency else req.criticality
    urg = "Immediate" if req.is_emergency else req.urgency

    # Temporary task object for evaluation
    temp_task = MaintenanceTask(
        task_id=task_code,
        criticality=crit,
        urgency=urg,
        overdue_days=req.overdue_days,
        safety_required=req.safety_required
    )
    eval_res = engine.evaluate_task(temp_task, asset)

    if req.is_emergency:
        # Boost to emergency ceiling
        eval_res["total_score"] = max(95.0, eval_res["total_score"])
        eval_res["priority_class"] = "Critical"
        eval_res["explanation_summary"] = (
            f"EMERGENCY PRIORITY (Score: {eval_res['total_score']}/100): "
            f"Immediate defect on {sec.section_code} requiring urgent possession."
        )

    # Save to database
    start_time = datetime.now() + timedelta(hours=2)
    end_time = start_time + timedelta(minutes=req.duration_minutes)

    new_task = MaintenanceTask(
        task_id=task_code,
        department_id=dept.id,
        asset_id=asset.id,
        section_id=sec.id,
        task_type=req.task_type,
        description=req.description or f"{req.department} task on {sec.section_code}",
        criticality=crit,
        urgency=urg,
        overdue_days=req.overdue_days,
        duration_minutes=req.duration_minutes,
        crew_required=req.crew_required,
        equipment_required=req.equipment_required,
        preferred_start=start_time,
        preferred_end=end_time,
        safety_required=req.safety_required,
        priority_score=eval_res["total_score"],
        priority_reason=eval_res["explanation_summary"],
        priority_class=eval_res["priority_class"],
        status="Pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    response_data: Dict[str, Any] = {
        "status": "success",
        "task_id": task_code,
        "task_type": req.task_type,
        "section_code": sec.section_code,
        "priority_score": eval_res["total_score"],
        "priority_class": eval_res["priority_class"],
        "is_emergency": req.is_emergency
    }

    # If emergency, evaluate train impact and find alternative slot
    if req.is_emergency:
        detector = ConflictDetector(db)
        traffic_eval = detector.evaluate_window_conflicts(sec.id, start_time, end_time)
        recommended_slot = detector.find_best_alternative_window(sec.id, start_time, req.duration_minutes)

        response_data["emergency_assessment"] = {
            "immediate_window_checked": f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}",
            "conflicting_trains_count": traffic_eval["conflict_count"],
            "has_critical_train": traffic_eval["has_critical_train"],
            "conflicting_trains": traffic_eval["conflicting_trains"][:3],
            "recommended_safe_window": recommended_slot,
            "operational_impact": (
                "Traffic block requires dispatching caution orders and holding freight traffic. "
                "No live signalling commands have been issued."
            ),
            "notice": "DECISION-SUPPORT ONLY: Section controller authorization required before physical possession."
        }

    return response_data


@router.get("/{task_id}")
def get_task_details(task_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information and priority evaluation for a single task.
    """
    engine = TaskPriorityEngine()
    explanation = engine.get_task_explanation(task_id, db)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return explanation


@router.post("/recalculate")
def recalculate_priorities(
    weights: Optional[PriorityWeightConfig] = None,
    db: Session = Depends(get_db)
):
    """
    Recalculates transparent priority scores across the entire task database
    using custom or default factor weights.
    """
    weight_dict = None
    if weights:
        weight_dict = {
            "criticality": weights.weight_criticality,
            "urgency": weights.weight_urgency,
            "overdue": weights.weight_overdue,
            "asset_condition": weights.weight_asset_condition,
            "safety": weights.weight_safety
        }

    engine = TaskPriorityEngine(weights=weight_dict)
    summary = engine.recalculate_database_tasks(db)
    return {
        "status": "success",
        "message": f"Successfully recalculated priority scores for {summary['tasks_updated']} tasks.",
        "summary": summary
    }
