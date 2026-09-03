from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from backend.database import get_db
from backend.models.station import Station
from backend.models.section import Section
from backend.models.asset import Asset
from backend.models.train import Train
from backend.models.block import OptimizedBlock
from backend.models.optimization_run import OptimizationRun

router = APIRouter(tags=["Railway Network & Assets"])


@router.get("/network")
def get_network_topology(db: Session = Depends(get_db)):
    """
    Returns the synthetic railway corridor network topology for Leaflet visualization:
    - Stations with geographic coordinates (lat/lng)
    - Connected track sections with distance and permissible speed
    - Currently active maintenance blocks
    - Section health and corridor availability
    """
    stations = db.query(Station).all()
    sections = db.query(Section).all()

    # Get active blocks from latest run
    latest_run = db.query(OptimizationRun).order_by(OptimizationRun.timestamp.desc()).first()
    active_blocks_by_section: Dict[int, List[Dict[str, Any]]] = {}

    if latest_run:
        blocks = db.query(OptimizedBlock).filter(OptimizedBlock.run_id == latest_run.id).all()
        for b in blocks:
            active_blocks_by_section.setdefault(b.section_id, []).append({
                "block_id": b.block_id,
                "start_time": b.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": b.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": b.duration_minutes,
                "is_combined": b.is_combined,
                "departments": [a.task.department.code for a in b.task_assignments]
            })

    station_data = [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "zone": s.zone,
            "division": s.division,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "lines_count": s.lines_count
        }
        for s in stations
    ]

    section_data = []
    for sec in sections:
        sec_blocks = active_blocks_by_section.get(sec.id, [])
        # Average asset health on this section
        assets = sec.assets
        avg_health = round(sum(a.condition_score for a in assets) / len(assets), 1) if assets else 85.0

        section_data.append({
            "id": sec.id,
            "section_code": sec.section_code,
            "name": sec.name,
            "station_from": {
                "id": sec.station_from.id,
                "code": sec.station_from.code,
                "name": sec.station_from.name,
                "lat": sec.station_from.latitude,
                "lng": sec.station_from.longitude
            },
            "station_to": {
                "id": sec.station_to.id,
                "code": sec.station_to.code,
                "name": sec.station_to.name,
                "lat": sec.station_to.latitude,
                "lng": sec.station_to.longitude
            },
            "distance_km": sec.distance_km,
            "max_speed_kmh": sec.max_speed_kmh,
            "tracks_count": sec.tracks_count,
            "electrified": sec.electrified,
            "line_capacity_trains_per_day": sec.line_capacity_trains_per_day,
            "average_asset_condition": avg_health,
            "active_blocks_count": len(sec_blocks),
            "is_blocked": len(sec_blocks) > 0,
            "active_blocks": sec_blocks
        })

    return {
        "status": "success",
        "disclaimer": "Prototype / Synthetic Railway Network for decision-support algorithm testing.",
        "corridor_name": "New Delhi - Kanpur - Prayagraj - Pt. Deen Dayal Upadhyaya Jn Trunk Route",
        "total_stations": len(station_data),
        "total_sections": len(section_data),
        "stations": station_data,
        "sections": section_data
    }


@router.get("/sections")
def list_sections(
    station_code: Optional[str] = Query(None, description="Filter sections passing through station code"),
    electrified: Optional[bool] = Query(None, description="Filter by electrification status"),
    db: Session = Depends(get_db)
):
    """
    Returns list of railway sections with connected stations and operational parameters.
    """
    query = db.query(Section)
    if electrified is not None:
        query = query.filter(Section.electrified == electrified)

    sections = query.all()
    results = []
    for s in sections:
        if station_code and (s.station_from.code != station_code and s.station_to.code != station_code):
            continue
        results.append({
            "id": s.id,
            "section_code": s.section_code,
            "name": s.name,
            "station_from": s.station_from.code,
            "station_to": s.station_to.code,
            "distance_km": s.distance_km,
            "max_speed_kmh": s.max_speed_kmh,
            "tracks_count": s.tracks_count,
            "electrified": s.electrified,
            "line_capacity": s.line_capacity_trains_per_day,
            "total_assets": len(s.assets),
            "pending_tasks": len([t for t in s.tasks if t.status == "Pending"])
        })
    return {"total_count": len(results), "sections": results}


@router.get("/trains")
def list_trains(
    train_type: Optional[str] = Query(None, description="Filter by train category"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by train operational priority"),
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns list of trains with origin, destination, movements count, and priority.
    """
    query = db.query(Train)
    if train_type:
        query = query.filter(Train.train_type.ilike(f"%{train_type}%"))
    if priority is not None:
        query = query.filter(Train.priority == priority)

    total_count = query.count()
    trains = query.order_by(Train.priority.desc(), Train.train_number).offset(offset).limit(limit).all()

    items = []
    for t in trains:
        items.append({
            "id": t.id,
            "train_id": t.train_id,
            "train_number": t.train_number,
            "train_name": t.train_name,
            "train_type": t.train_type,
            "origin": t.origin_station.code,
            "origin_name": t.origin_station.name,
            "destination": t.destination_station.code,
            "destination_name": t.destination_station.name,
            "priority": t.priority,
            "total_movements": len(t.movements)
        })

    return {
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "trains": items
    }


@router.get("/assets")
def list_assets(
    department: Optional[str] = Query(None, description="Filter by department (ENG, OHE, S&T)"),
    criticality: Optional[int] = Query(None, ge=1, le=5),
    max_condition: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter for degraded assets below score"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns list of railway infrastructure assets with health condition and maintenance dates.
    """
    query = db.query(Asset)
    if department:
        query = query.filter(Asset.department.has(code=department.upper()))
    if criticality:
        query = query.filter(Asset.criticality == criticality)
    if max_condition is not None:
        query = query.filter(Asset.condition_score <= max_condition)

    total_count = query.count()
    assets = query.order_by(Asset.condition_score.asc()).offset(offset).limit(limit).all()

    items = []
    for a in assets:
        items.append({
            "id": a.id,
            "asset_id": a.asset_id,
            "name": a.name,
            "asset_type": a.asset_type,
            "department": a.department.code,
            "section_code": a.section.section_code,
            "condition_score": a.condition_score,
            "last_maintenance_date": a.last_maintenance_date.strftime("%Y-%m-%d") if a.last_maintenance_date else None,
            "next_due_date": a.next_due_date.strftime("%Y-%m-%d") if a.next_due_date else None,
            "criticality": a.criticality
        })

    return {
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "assets": items
    }
