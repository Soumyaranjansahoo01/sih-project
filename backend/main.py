"""
SIH26027: AI-Powered Automatic Block Planning Backend
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from backend.config import settings
from backend.database import get_db
from backend.services.baseline import BaselineScheduler
from backend.services.task_priority import TaskPriorityEngine
from backend.api.tasks import router as tasks_router
from backend.api.optimize import router as optimize_router
from backend.api.network import router as network_router
from backend.api.analytics import router as analytics_router
from backend.api.simulation import router as simulation_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Decision-support API for Indian Railways maintenance block planning. "
        "Coordinates Civil Engineering (TMS), OHE (TDMS), and Signalling (SMMS) tasks "
        "to minimize corridor downtime and avoid train conflicts."
    )
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All API Routers
app.include_router(tasks_router)
app.include_router(optimize_router)
app.include_router(network_router)
app.include_router(analytics_router)
app.include_router(simulation_router)


@app.get("/")
def root():
    return {
        "project": "SIH26027",
        "title": settings.APP_NAME,
        "status": "online",
        "version": "1.0.0",
        "mode": "Decision-Support Advisory System",
        "disclaimer": (
            "This prototype uses synthetic data. It is an advisory decision-support system "
            "and does not control physical railway signalling or train movements."
        )
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": settings.DATABASE_URL.split(":///")[0]
    }


@app.get("/baseline")
def get_baseline_schedule(
    horizon_days: int = Query(7, ge=1, le=30, description="Planning horizon in days"),
    db: Session = Depends(get_db)
):
    """
    Executes the Baseline (Independent Department) Scheduler.
    Models current uncoordinated practice where ENG, OHE, and S&T plan separately.
    Returns dynamic metrics, scheduled blocks, and train conflicts.
    """
    scheduler = BaselineScheduler(db=db, horizon_days=horizon_days)
    results = scheduler.run()
    return {
        "status": "success",
        "horizon_days": horizon_days,
        "metrics": results["metrics"],
        "total_blocks": len(results["blocks"]),
        "blocks_sample": results["blocks"][:50],
        "total_conflicts": len(results["conflicts"]),
        "conflicts_sample": results["conflicts"][:50]
    }


@app.get("/optimization/explanation/{task_id}")
def get_optimization_explanation(task_id: str, db: Session = Depends(get_db)):
    """
    Explainable AI endpoint: Explains why a task received its priority score,
    displaying normalized factors, weights, and natural-language rationale.
    """
    engine = TaskPriorityEngine()
    explanation = engine.get_task_explanation(task_id, db)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {
        "status": "success",
        "explanation": explanation
    }
