from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from backend.database import get_db
from backend.services.simulation import SimulationService

router = APIRouter(tags=["What-If Simulation"])


class SimulationRequest(BaseModel):
    scenario_name: str = Field("Festival Rush Surge (+25% Traffic)", description="Name of the scenario")
    train_traffic_multiplier: float = Field(1.25, ge=0.5, le=2.0, description="Multiplier for train density")
    emergency_tasks_count: int = Field(2, ge=0, le=10, description="Number of emergency defects to inject")
    weather_disruption: bool = Field(False, description="Simulate adverse weather (fog/rain)")
    horizon_days: int = Field(7, ge=1, le=14, description="Simulation horizon in days")


@router.post("/simulate")
def run_simulation(
    request: SimulationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Executes a 'What-If' Simulation scenario:
    Simulates operational stress (traffic surges, emergency track fractures, adverse weather),
    re-runs the optimizer, and provides dynamic schedule adaptation metrics.
    """
    service = SimulationService(db=db)
    return service.run_simulation(
        scenario_name=request.scenario_name,
        train_traffic_multiplier=request.train_traffic_multiplier,
        emergency_tasks_count=request.emergency_tasks_count,
        weather_disruption=request.weather_disruption,
        horizon_days=request.horizon_days
    )
