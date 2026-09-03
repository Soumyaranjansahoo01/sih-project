from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # e.g., NDLS, CNB
    name = Column(String(100), nullable=False)
    zone = Column(String(10), nullable=False)  # NR, NCR, etc.
    division = Column(String(20), nullable=False)  # DLI, PRYJ, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    lines_count = Column(Integer, default=4)

    # Relationships
    origin_trains = relationship("Train", foreign_keys="Train.origin_id", back_populates="origin_station")
    dest_trains = relationship("Train", foreign_keys="Train.destination_id", back_populates="destination_station")
