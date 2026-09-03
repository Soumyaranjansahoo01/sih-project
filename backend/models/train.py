from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., TRN_12001
    train_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., 12001
    train_name = Column(String(100), nullable=False)
    train_type = Column(String(50), nullable=False)  # Vande Bharat, Rajdhani, Express, MEMU, Freight
    origin_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    destination_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    priority = Column(Integer, default=3)  # 5 (Vande Bharat/Rajdhani) down to 1 (Freight/Maintenance)

    # Relationships
    origin_station = relationship("Station", foreign_keys=[origin_id], back_populates="origin_trains")
    destination_station = relationship("Station", foreign_keys=[destination_id], back_populates="dest_trains")
    movements = relationship("TrainMovement", back_populates="train")


class TrainMovement(Base):
    __tablename__ = "train_movements"

    id = Column(Integer, primary_key=True, index=True)
    movement_id = Column(String(50), unique=True, nullable=False, index=True)
    train_id = Column(Integer, ForeignKey("trains.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    scheduled_entry = Column(DateTime, nullable=False, index=True)
    scheduled_exit = Column(DateTime, nullable=False, index=True)
    speed_restriction_kmh = Column(Integer, nullable=True)

    # Relationships
    train = relationship("Train", back_populates="movements")
    section = relationship("Section", back_populates="train_movements")
