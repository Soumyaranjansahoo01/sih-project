from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., AST_TRK_001
    name = Column(String(100), nullable=False)
    asset_type = Column(String(50), nullable=False)  # Track Segment, Point Machine, OHE Catenary, etc.
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    condition_score = Column(Float, nullable=False, default=100.0)  # 0 to 100 (0=failing, 100=pristine)
    last_maintenance_date = Column(DateTime, nullable=True)
    next_due_date = Column(DateTime, nullable=False)
    criticality = Column(Integer, default=3)  # 1 (Low) to 5 (Safety Critical)

    # Relationships
    department = relationship("Department", back_populates="assets")
    section = relationship("Section", back_populates="assets")
    tasks = relationship("MaintenanceTask", back_populates="asset")
