import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.config import settings
from backend.database import Base
from backend.models.task import MaintenanceTask
from backend.services.task_priority import TaskPriorityEngine
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_priority_engine_normalization():
    engine = TaskPriorityEngine()

    # Criticality
    assert engine.normalize_criticality(5) == 100.0
    assert engine.normalize_criticality(1) == 20.0

    # Urgency
    assert engine.normalize_urgency("Immediate") == 100.0
    assert engine.normalize_urgency("Low") == 20.0

    # Overdue Days
    assert engine.normalize_overdue(0) == 0.0
    assert engine.normalize_overdue(25) == 100.0
    assert engine.normalize_overdue(50) == 100.0  # Capped at 100

    # Asset Condition (inversion)
    assert engine.normalize_asset_condition(100.0) == 0.0
    assert engine.normalize_asset_condition(0.0) == 100.0
    assert engine.normalize_asset_condition(40.0) == 60.0

    # Safety
    assert engine.normalize_safety("Traffic Block & Power Block") == 100.0
    assert engine.normalize_safety("None") == 15.0


def test_priority_classification():
    engine = TaskPriorityEngine()
    assert engine.classify_priority(85.0) == "Critical"
    assert engine.classify_priority(72.0) == "High"
    assert engine.classify_priority(45.0) == "Medium"
    assert engine.classify_priority(25.0) == "Low"


def test_evaluate_task_and_reasons(test_db):
    engine = TaskPriorityEngine()
    task = test_db.query(MaintenanceTask).first()
    assert task is not None

    evaluation = engine.evaluate_task(task, task.asset)
    assert "total_score" in evaluation
    assert 0.0 <= evaluation["total_score"] <= 100.0
    assert evaluation["priority_class"] in ["Critical", "High", "Medium", "Low"]
    assert len(evaluation["key_reasons"]) > 0
    assert len(evaluation["factor_breakdown"]) == 5


def test_database_batch_recalculation(test_db):
    engine = TaskPriorityEngine()
    summary = engine.recalculate_database_tasks(test_db)
    assert summary["tasks_updated"] >= 500
    assert sum(summary["distribution"].values()) == summary["tasks_updated"]
    # Ensure critical tasks exist
    assert summary["distribution"]["Critical"] > 0


def test_tasks_api_endpoints():
    # 1. List tasks
    response = client.get("/tasks?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 10
    first_task_id = data["tasks"][0]["task_id"]

    # 2. Filter tasks by department
    response_eng = client.get("/tasks?department=ENG&limit=5")
    assert response_eng.status_code == 200
    for t in response_eng.json()["tasks"]:
        assert t["department"] == "ENG"

    # 3. Get single task explanation
    response_task = client.get(f"/tasks/{first_task_id}")
    assert response_task.status_code == 200
    task_data = response_task.json()
    assert task_data["task_id"] == first_task_id
    assert "factor_breakdown" in task_data

    # 4. Explainability endpoint
    response_exp = client.get(f"/optimization/explanation/{first_task_id}")
    assert response_exp.status_code == 200
    exp_data = response_exp.json()
    assert exp_data["status"] == "success"
    assert exp_data["explanation"]["task_id"] == first_task_id
