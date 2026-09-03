import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "SIH26027"
    assert data["status"] == "online"
    assert "disclaimer" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_baseline_endpoint():
    response = client.get("/baseline?horizon_days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert data["metrics"]["planning_mode"] == "Baseline (Independent)"
    assert data["metrics"]["total_block_hours"] > 0
    assert data["total_blocks"] > 0
    assert "blocks_sample" in data
    assert "conflicts_sample" in data
