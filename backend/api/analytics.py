from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session # type: ignore
from backend.database import get_db
from backend.services.analytics import AnalyticsService

router = APIRouter(tags=["Analytics & Reporting"])


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)): # type: ignore
    """
    Returns comprehensive metrics for controller dashboard charts:
    - Department-wise workload (hours and task counts)
    - Criticality and urgency tier distributions
    - Asset condition degradation profiles
    - Baseline vs. Optimized blocks and downtime comparisons
    - 7-day operational workload trends
    """
    service = AnalyticsService(db=db) # type: ignore
    return service.get_dashboard_analytics()
