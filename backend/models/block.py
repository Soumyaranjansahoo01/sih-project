from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class BlockRequest(Base):
    __tablename__ = "block_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., BR_0001
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("maintenance_tasks.id", ondelete="SET NULL"), nullable=True)

    requested_start = Column(DateTime, nullable=False)
    requested_end = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    purpose = Column(Text, nullable=True)
    status = Column(String(30), default="Requested")  # Requested, Approved, Rejected, Coordinated

    # Relationships
    department = relationship("Department", back_populates="block_requests")
    section = relationship("Section", back_populates="block_requests")


class OptimizedBlock(Base):
    __tablename__ = "optimized_blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., BLK_OPT_001
    run_id = Column(Integer, ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)

    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    is_combined = Column(Boolean, default=False)
    department_count = Column(Integer, default=1)
    reason = Column(Text, nullable=True)
    train_impact_score = Column(Float, default=0.0)
    status = Column(String(30), default="Scheduled")

    # Relationships
    run = relationship("OptimizationRun", back_populates="optimized_blocks")
    section = relationship("Section", back_populates="optimized_blocks")
    task_assignments = relationship("BlockTaskAssignment", back_populates="block", cascade="all, delete-orphan")


class BlockTaskAssignment(Base):
    __tablename__ = "block_task_assignments"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("optimized_blocks.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("maintenance_tasks.id", ondelete="CASCADE"), nullable=False)
    sequence_order = Column(Integer, default=1)
    allocated_duration_minutes = Column(Integer, nullable=False)
    coordination_notes = Column(Text, nullable=True)

    # Relationships
    block = relationship("OptimizedBlock", back_populates="task_assignments")
    task = relationship("MaintenanceTask", back_populates="block_assignments")
