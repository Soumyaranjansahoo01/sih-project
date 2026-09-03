from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(50), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    planning_horizon = Column(String(20), default="Weekly")  # Weekly or Monthly
    horizon_start = Column(DateTime, nullable=False)
    horizon_end = Column(DateTime, nullable=False)
    objective_value = Column(Float, default=0.0)

    # JSON formatted metrics payloads
    baseline_metrics = Column(Text, nullable=True)
    optimized_metrics = Column(Text, nullable=True)
    improvement_metrics = Column(Text, nullable=True)

    solver_status = Column(String(30), default="Optimal")
    execution_time_seconds = Column(Float, default=0.0)

    # Relationships
    optimized_blocks = relationship("OptimizedBlock", back_populates="run", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="run", cascade="all, delete-orphan")


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, index=True)
    conflict_id = Column(String(50), unique=True, nullable=False, index=True)
    run_id = Column(Integer, ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=True)
    conflict_type = Column(String(50), nullable=False)  # Train_Block, Section_Overlap, Resource_Conflict
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("maintenance_tasks.id", ondelete="SET NULL"), nullable=True)
    train_id = Column(Integer, ForeignKey("trains.id", ondelete="SET NULL"), nullable=True)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    severity = Column(String(20), default="Major")  # Minor, Major, Critical
    description = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    resolution_strategy = Column(Text, nullable=True)

    # Relationships
    run = relationship("OptimizationRun", back_populates="conflicts")
    section = relationship("Section", back_populates="conflicts")
    task = relationship("MaintenanceTask")
    train = relationship("Train")
