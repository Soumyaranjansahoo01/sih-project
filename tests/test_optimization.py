import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.config import settings
from backend.database import Base
from backend.models.optimization_run import OptimizationRun
from backend.models.block import OptimizedBlock
from backend.services.optimization_service import OptimizationService
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


def test_optimization_solver_and_service(test_db):
    service = OptimizationService(db=test_db)
    result = service.run_optimization(horizon_days=7, time_limit_seconds=20)

    assert result["status"] == "success"
    assert result["solver_status"] in ["Optimal", "Feasible"]
    assert "improvement" in result
    assert "blocks" in result

    imp = result["improvement"]
    # Verify measurable real-world improvement over baseline
    assert imp["blocks_saved"] > 0, "Optimization should produce fewer total blocks than baseline"
    assert imp["block_reduction_pct"] > 0.0
    assert imp["downtime_saved_hours"] > 0.0, "Optimization should reduce total corridor closure hours"
    assert imp["downtime_reduction_pct"] > 0.0
    assert imp["conflicts_avoided"] > 0, "Optimization should eliminate train clashes"
    assert imp["conflict_reduction_pct"] > 0.0
    assert imp["multi_department_blocks"] > 0, "Must create multi-department coordinated blocks"

    # Verify blocks data
    blocks = result["blocks"]
    assert len(blocks) > 0
    combined_blocks = [b for b in blocks if b["is_combined"]]
    assert len(combined_blocks) > 0

    # Verify critical train conflicts are 0
    assert result["optimized_metrics"]["critical_train_conflicts"] == 0

    # Verify database persistence
    latest_run = test_db.query(OptimizationRun).filter_by(run_id=result["run_id"]).first()
    assert latest_run is not None
    assert len(latest_run.optimized_blocks) == len(blocks)


def test_optimize_api_endpoints():
    # 1. Test POST /optimize
    res_opt = client.post("/optimize", json={"horizon_days": 7, "time_limit_seconds": 15})
    assert res_opt.status_code == 200
    data_opt = res_opt.json()
    assert data_opt["status"] == "success"
    assert data_opt["improvement"]["blocks_saved"] > 0

    # 2. Test GET /schedule
    res_sched = client.get("/schedule?limit=10")
    assert res_sched.status_code == 200
    data_sched = res_sched.json()
    assert "blocks" in data_sched
    assert len(data_sched["blocks"]) > 0

    # 3. Test GET /comparison
    res_comp = client.get("/comparison")
    assert res_comp.status_code == 200
    data_comp = res_comp.json()
    assert "improvement" in data_comp
    assert data_comp["improvement"]["downtime_saved_hours"] > 0.0
