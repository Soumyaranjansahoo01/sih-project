import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_network_endpoint():
    response = client.get("/network")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_stations"] >= 100
    assert data["total_sections"] >= 50
    assert len(data["stations"]) >= 100
    assert len(data["sections"]) >= 50

    # Verify coordinates format for Leaflet
    first_station = data["stations"][0]
    assert "latitude" in first_station and "longitude" in first_station
    assert float(first_station["latitude"]) > 0


def test_sections_and_trains_endpoints():
    # Sections
    res_sec = client.get("/sections")
    assert res_sec.status_code == 200
    sec_data = res_sec.json()
    assert sec_data["total_count"] >= 50

    # Trains
    res_trn = client.get("/trains?limit=10")
    assert res_trn.status_code == 200
    trn_data = res_trn.json()
    assert trn_data["total_count"] >= 200
    assert len(trn_data["trains"]) == 10
    # Top priority trains (Vande Bharat / Rajdhani = 5) should appear first
    assert trn_data["trains"][0]["priority"] == 5


def test_assets_endpoint():
    response = client.get("/assets?department=ENG&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert len(data["assets"]) > 0
    for a in data["assets"]:
        assert a["department"] == "ENG"


def test_emergency_task_creation():
    # Submit an emergency rail defect
    payload = {
        "department": "ENG",
        "section_id": 1,
        "task_type": "Emergency Rail Fracture Defect",
        "description": "Ultrasonic flaw detection flagged 35mm transverse rail fracture",
        "criticality": 5,
        "urgency": "Immediate",
        "overdue_days": 10,
        "duration_minutes": 120,
        "crew_required": 8,
        "safety_required": "Traffic Block",
        "is_emergency": True
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_emergency"] is True
    assert data["priority_score"] >= 95.0
    assert data["priority_class"] == "Critical"
    assert "emergency_assessment" in data
    assert "recommended_safe_window" in data["emergency_assessment"]


def test_analytics_endpoint():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "kpis" in data
    assert "department_workload" in data
    assert "criticality_distribution" in data
    assert "comparison_chart" in data
    assert "weekly_workload_trend" in data
    assert len(data["department_workload"]) == 3  # ENG, OHE, S&T


def test_simulation_endpoint():
    payload = {
        "scenario_name": "Festival Traffic Spike (+20% Trains)",
        "train_traffic_multiplier": 1.2,
        "emergency_tasks_count": 1,
        "weather_disruption": False,
        "horizon_days": 7
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "adaptation_summary" in data
    assert data["adaptation_summary"]["critical_train_conflicts"] == 0
    assert len(data["injected_emergencies"]) == 1
