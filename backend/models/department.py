from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    system_source = Column(String(50), nullable=False)  # TMS, SMMS, TDMS
    color_code = Column(String(20), default="#2563eb")
    description = Column(Text, nullable=True)

    # Relationships
    assets = relationship("Asset", back_populates="department")
    tasks = relationship("MaintenanceTask", back_populates="department")
    block_requests = relationship("BlockRequest", back_populates="department")
