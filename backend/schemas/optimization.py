from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class OptimizationRequest(BaseModel):
    horizon_days: int = Field(7, ge=1, le=30, description="Planning horizon: 7 for weekly, 30 for monthly")
    time_limit_seconds: int = Field(45, ge=5, le=180, description="Solver CPU time budget in seconds")
    prioritize_coordination: bool = Field(True, description="Enforce strong incentives to combine ENG + OHE + S&T")


class TaskInBlock(BaseModel):
    task_id: str
    department: str
    task_type: str
    priority_score: float
    duration_minutes: int


class BlockDetail(BaseModel):
    block_id: str
    section_id: int
    section_code: str
    start_time: str
    end_time: str
    duration_minutes: int
    duration_hours: float
    is_combined: bool
    department_count: int
    departments: List[str]
    tasks_count: int
    tasks: List[TaskInBlock]
    reason: str
    train_impact_score: float


class ImprovementMetrics(BaseModel):
    blocks_saved: int
    block_reduction_pct: float
    downtime_saved_hours: float
    downtime_reduction_pct: float
    conflicts_avoided: int
    conflict_reduction_pct: float
    coordination_rate_pct: float
    multi_department_blocks: int
    baseline_availability_pct: float
    optimized_availability_pct: float
    availability_gain_pct: float


class OptimizationResponse(BaseModel):
    status: str
    run_id: str
    execution_time_seconds: float
    horizon_days: int
    solver_status: str
    baseline_metrics: Dict[str, Any]
    optimized_metrics: Dict[str, Any]
    improvement: ImprovementMetrics
    total_blocks_scheduled: int
    blocks: List[BlockDetail]
    rejected_windows_sample: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
