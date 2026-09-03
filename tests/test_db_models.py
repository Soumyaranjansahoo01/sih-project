import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.department import Department
from backend.models.station import Station
from backend.models.section import Section
from backend.models.asset import Asset
from backend.models.task import MaintenanceTask
from backend.models.train import Train, TrainMovement
from backend.models.block import BlockRequest, OptimizedBlock, BlockTaskAssignment
from backend.models.optimization_run import OptimizationRun, Conflict
from backend.config import settings


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_counts(test_db):
    dept_count = test_db.query(Department).count()
    assert dept_count == 3, f"Expected 3 departments, got {dept_count}"

    station_count = test_db.query(Station).count()
    assert station_count >= 100, f"Expected >= 100 stations, got {station_count}"

    section_count = test_db.query(Section).count()
    assert section_count >= 50, f"Expected >= 50 sections, got {section_count}"

    asset_count = test_db.query(Asset).count()
    assert asset_count >= 300, f"Expected >= 300 assets, got {asset_count}"

    task_count = test_db.query(MaintenanceTask).count()
    assert task_count >= 500, f"Expected >= 500 tasks, got {task_count}"

    train_count = test_db.query(Train).count()
    assert train_count >= 200, f"Expected >= 200 trains, got {train_count}"

    movement_count = test_db.query(TrainMovement).count()
    assert movement_count >= 1000, f"Expected >= 1000 movements, got {movement_count}"


def test_department_relationship(test_db):
    eng = test_db.query(Department).filter_by(code="ENG").first()
    assert eng is not None
    assert len(eng.assets) > 0
    assert len(eng.tasks) > 0


def test_section_relationship(test_db):
    first_section = test_db.query(Section).first()
    assert first_section is not None
    assert first_section.station_from is not None
    assert first_section.station_to is not None
    assert len(first_section.assets) > 0


def test_task_relationship(test_db):
    sample_task = test_db.query(MaintenanceTask).first()
    assert sample_task is not None
    assert sample_task.department is not None
    assert sample_task.asset is not None
    assert sample_task.section is not None
    assert sample_task.priority_score >= 0.0


def test_train_movements_relationship(test_db):
    movement = test_db.query(TrainMovement).first()
    assert movement is not None
    assert movement.train is not None
    assert movement.section is not None
    assert movement.scheduled_entry < movement.scheduled_exit
