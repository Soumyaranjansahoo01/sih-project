from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., MT_0001
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)

    task_type = Column(String(100), nullable=False)  # Tamping, Catenary Renewal, Point Overhaul, etc.
    description = Column(Text, nullable=True)

    criticality = Column(Integer, default=3)  # 1 to 5
    urgency = Column(String(20), default="Normal")  # Immediate, High, Normal, Low
    overdue_days = Column(Integer, default=0)
    duration_minutes = Column(Integer, nullable=False)  # 60, 90, 120, 180, etc.

    crew_required = Column(Integer, default=4)
    equipment_required = Column(String(100), nullable=True)  # BCM, Tower Wagon, Testing Kit
    preferred_start = Column(DateTime, nullable=True)
    preferred_end = Column(DateTime, nullable=True)
    safety_required = Column(String(100), default="Traffic Block")  # Power Block, Traffic Block, Both

    # Priority Calculation Fields
    priority_score = Column(Float, default=50.0)  # 0 to 100
    priority_reason = Column(Text, nullable=True)  # Explanatory breakdown
    priority_class = Column(String(20), default="Medium")  # Low, Medium, High, Critical

    status = Column(String(30), default="Pending")  # Pending, Scheduled, In_Progress, Completed

    # Relationships
    department = relationship("Department", back_populates="tasks")
    asset = relationship("Asset", back_populates="tasks")
    section = relationship("Section", back_populates="tasks")
    block_assignments = relationship("BlockTaskAssignment", back_populates="task")
