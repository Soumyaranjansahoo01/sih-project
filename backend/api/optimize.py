from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from backend.database import get_db
from backend.models.optimization_run import OptimizationRun, Conflict
from backend.models.block import OptimizedBlock
from backend.schemas.optimization import OptimizationRequest, OptimizationResponse
from backend.services.optimization_service import OptimizationService

router = APIRouter(tags=["Optimization & Scheduling"])


@router.post("/optimize", response_model=OptimizationResponse)
def execute_optimization(
    request: OptimizationRequest = OptimizationRequest(),
    db: Session = Depends(get_db)
):
    """
    Executes the Mathematical Block Scheduling Optimizer (MILP).
    Consolidates compatible multi-department tasks (ENG + OHE + S&T),
    avoids train conflicts, and computes dynamic improvement over baseline.
    """
    service = OptimizationService(db=db)
    result = service.run_optimization(
        horizon_days=request.horizon_days,
        time_limit_seconds=request.time_limit_seconds,
        prioritize_coordination=request.prioritize_coordination
    )
    return result


@router.get("/schedule")
def get_current_schedule(
    is_combined: Optional[bool] = Query(None, description="Filter for multi-department combined blocks only"),
    section_id: Optional[int] = Query(None, description="Filter by section ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns the latest scheduled maintenance blocks.
    """
    latest_run = db.query(OptimizationRun).order_by(OptimizationRun.timestamp.desc()).first()
    if not latest_run:
        # Run optimization if none has been executed yet
        service = OptimizationService(db=db)
        run_res = service.run_optimization(horizon_days=7)
        return {
            "run_id": run_res["run_id"],
            "total_blocks": len(run_res["blocks"]),
            "blocks": run_res["blocks"][:limit]
        }

    query = db.query(OptimizedBlock).filter(OptimizedBlock.run_id == latest_run.id)
    if is_combined is not None:
        query = query.filter(OptimizedBlock.is_combined == is_combined)
    if section_id:
        query = query.filter(OptimizedBlock.section_id == section_id)

    total_count = query.count()
    blocks = query.order_by(OptimizedBlock.start_time).offset(offset).limit(limit).all()

    blocks_data = []
    for b in blocks:
        task_list = []
        for assign in b.task_assignments:
            task_list.append({
                "task_id": assign.task.task_id,
                "department": assign.task.department.code,
                "task_type": assign.task.task_type,
                "priority_score": assign.task.priority_score,
                "duration_minutes": assign.allocated_duration_minutes
            })

        depts = list({t["department"] for t in task_list})
        blocks_data.append({
            "block_id": b.block_id,
            "section_id": b.section_id,
            "section_code": b.section.section_code,
            "start_time": b.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": b.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": b.duration_minutes,
            "duration_hours": round(b.duration_minutes / 60.0, 2),
            "is_combined": b.is_combined,
            "department_count": b.department_count,
            "departments": depts,
            "tasks_count": len(task_list),
            "tasks": task_list,
            "reason": b.reason,
            "train_impact_score": b.train_impact_score
        })

    return {
        "run_id": latest_run.run_id,
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "blocks": blocks_data
    }


@router.get("/schedule/weekly")
def get_weekly_schedule(db: Session = Depends(get_db)):
    """
    Returns the 7-day hourly detailed block schedule.
    """
    service = OptimizationService(db=db)
    return service.run_optimization(horizon_days=7)


@router.get("/schedule/monthly")
def get_monthly_schedule(db: Session = Depends(get_db)):
    """
    Returns the 30-day aggregated block schedule.
    """
    service = OptimizationService(db=db)
    return service.run_optimization(horizon_days=30, time_limit_seconds=60)


@router.get("/comparison")
def get_baseline_vs_optimized_comparison(
    run_id: Optional[str] = Query(None, description="Optional specific run ID"),
    db: Session = Depends(get_db)
):
    """
    Returns dynamic before-and-after comparison metrics:
    downtime reduction, blocks saved, conflict reduction, and asset availability improvement.
    """
    service = OptimizationService(db=db)
    return service.get_comparison(run_id=run_id)


@router.get("/conflicts")
def list_conflicts(
    severity: Optional[str] = Query(None, description="Filter by severity (Critical, Major, Minor)"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db)
):
    """
    Returns operational train conflicts identified and resolved during optimization.
    """
    query = db.query(Conflict)
    if severity:
        query = query.filter(Conflict.severity == severity.capitalize())
    if resolved is not None:
        query = query.filter(Conflict.resolved == resolved)

    conflicts = query.limit(100).all()
    return {
        "total_count": len(conflicts),
        "conflicts": [
            {
                "conflict_id": c.conflict_id,
                "conflict_type": c.conflict_type,
                "section_code": c.section.section_code,
                "start_time": c.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": c.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "severity": c.severity,
                "description": c.description,
                "resolved": c.resolved,
                "resolution_strategy": c.resolution_strategy
            }
            for c in conflicts
        ]
    }
