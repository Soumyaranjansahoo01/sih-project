from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    section_code = Column(String(30), unique=True, nullable=False, index=True)  # e.g., SEC_001
    name = Column(String(100), nullable=False)  # e.g., NDLS - GZB UP Line
    station_from_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    station_to_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    distance_km = Column(Float, nullable=False)
    max_speed_kmh = Column(Integer, default=130)
    tracks_count = Column(Integer, default=2)
    electrified = Column(Boolean, default=True)
    line_capacity_trains_per_day = Column(Integer, default=120)

    # Relationships
    station_from = relationship("Station", foreign_keys=[station_from_id])
    station_to = relationship("Station", foreign_keys=[station_to_id])
    assets = relationship("Asset", back_populates="section")
    tasks = relationship("MaintenanceTask", back_populates="section")
    train_movements = relationship("TrainMovement", back_populates="section")
    block_requests = relationship("BlockRequest", back_populates="section")
    optimized_blocks = relationship("OptimizedBlock", back_populates="section")
    conflicts = relationship("Conflict", back_populates="section")
