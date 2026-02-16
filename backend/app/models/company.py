from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    industry = Column(String(100))
    notes = Column(Text)
    scan_frequency = Column(String(50), default="daily")
    alert_threshold = Column(Integer, default=50)
    status = Column(String(50), default="active")
    last_scanned = Column(DateTime)
    next_scan = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = relationship("Snapshot", back_populates="company", cascade="all, delete-orphan")
    changes = relationship("Change", back_populates="company", cascade="all, delete-orphan")