from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PriorityWeightConfig(BaseModel):
    weight_criticality: float = Field(0.30, ge=0.0, le=1.0, description="Weight for asset/task criticality (1-5)")
    weight_urgency: float = Field(0.25, ge=0.0, le=1.0, description="Weight for task operational urgency")
    weight_overdue: float = Field(0.20, ge=0.0, le=1.0, description="Weight for overdue maintenance days")
    weight_asset_condition: float = Field(0.15, ge=0.0, le=1.0, description="Weight for asset degradation")
    weight_safety: float = Field(0.10, ge=0.0, le=1.0, description="Weight for safety block requirements")


class PriorityFactorDetail(BaseModel):
    factor_name: str
    raw_value: Any
    normalized_score: float  # 0 to 100
    weight: float
    contribution_points: float
    description: str


class TaskPriorityExplanation(BaseModel):
    task_id: str
    task_type: str
    department: str
    section_code: str
    asset_id: str
    asset_name: str
    asset_type: str
    total_priority_score: float  # 0 to 100
    priority_class: str  # Critical, High, Medium, Low
    explanation_summary: str
    key_reasons: List[str]
    factor_breakdown: List[PriorityFactorDetail]


class TaskResponse(BaseModel):
    id: int
    task_id: str
    department_code: str
    department_name: str
    asset_id: str
    asset_type: str
    section_id: int
    section_code: str
    task_type: str
    description: Optional[str] = None
    criticality: int
    urgency: str
    overdue_days: int
    duration_minutes: int
    crew_required: int
    equipment_required: Optional[str] = None
    safety_required: str
    priority_score: float
    priority_class: str
    priority_reason: Optional[str] = None
    status: str
    preferred_start: Optional[datetime] = None
    preferred_end: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreateRequest(BaseModel):
    department: str = Field(..., description="ENG, OHE, or S&T")
    section_id: int = Field(..., description="Target section ID")
    asset_id: Optional[str] = Field(None, description="Target asset ID (auto-assigned if omitted)")
    task_type: str = Field(..., description="Name/type of maintenance required")
    description: Optional[str] = Field(None, description="Description of the defect or activity")
    criticality: int = Field(3, ge=1, le=5, description="1 (Low) to 5 (Critical safety impact)")
    urgency: str = Field("Normal", description="Immediate, High, Normal, Low")
    overdue_days: int = Field(0, ge=0)
    duration_minutes: int = Field(90, ge=30, le=360)
    crew_required: int = Field(4, ge=1, le=25)
    equipment_required: Optional[str] = Field("General Tool Kit")
    safety_required: str = Field("Traffic Block", description="Traffic Block, Power Block, Both, Caution Order")
    is_emergency: bool = Field(False, description="Flag as immediate emergency maintenance")


class EmergencyTaskResponse(BaseModel):
    status: str
    task_id: str
    priority_score: float
    priority_class: str
    is_emergency: bool
    recommended_window: Dict[str, Any]
    affected_trains_count: int
    operational_impact: str
    notice: str

