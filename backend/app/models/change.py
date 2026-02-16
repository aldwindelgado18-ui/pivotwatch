from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Change(Base):
    __tablename__ = "changes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    old_snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"))
    new_snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"))
    detected_at = Column(DateTime, default=datetime.utcnow)
    significance_score = Column(Integer)
    category = Column(String(50))
    summary = Column(String(500))
    analysis = Column(Text)
    change_data = Column(JSON, default={})
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="changes")
    old_snapshot = relationship("Snapshot", foreign_keys=[old_snapshot_id], back_populates="old_changes")
    new_snapshot = relationship("Snapshot", foreign_keys=[new_snapshot_id], back_populates="new_changes")
    notifications = relationship("Notification", back_populates="change", cascade="all, delete-orphan")