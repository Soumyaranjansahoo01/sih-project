import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.services.baseline import BaselineScheduler


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_baseline_scheduler_execution(test_db):
    scheduler = BaselineScheduler(db=test_db, horizon_days=7)
    results = scheduler.run()

    assert "metrics" in results
    assert "blocks" in results
    assert "conflicts" in results

    metrics = results["metrics"]
    blocks = results["blocks"]
    conflicts = results["conflicts"]

    # Verify metrics structure
    assert metrics["planning_mode"] == "Baseline (Independent)"
    assert metrics["total_tasks"] >= 500
    assert metrics["tasks_scheduled"] > 0
    assert metrics["number_of_blocks"] > 0
    assert metrics["total_block_hours"] > 0.0
    assert metrics["asset_downtime_hours"] > 0.0
    assert metrics["multi_department_blocks_count"] == 0  # No coordination in baseline
    assert metrics["coordination_savings_hours"] == 0.0

    # Verify blocks structure
    assert len(blocks) == metrics["number_of_blocks"]
    for b in blocks[:10]:
        assert "block_id" in b
        assert "department" in b
        assert b["department"] in ["ENG", "OHE", "S&T"]
        assert b["is_combined"] is False
        assert b["duration_minutes"] > 0

    # Verify conflicts
    assert len(conflicts) > 0
    for c in conflicts[:10]:
        assert "conflict_id" in c
        assert "severity" in c
        assert c["severity"] in ["Critical", "Major", "Minor"]
