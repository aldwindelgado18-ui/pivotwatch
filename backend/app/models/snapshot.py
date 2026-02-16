from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Snapshot(Base):
    __tablename__ = "snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    title = Column(String(500))
    html_hash = Column(String(64))
    text_content = Column(Text)
    html_content = Column(Text)  # Compressed in production
    screenshot_path = Column(String(500))
    snapshot_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="snapshots")
    old_changes = relationship("Change", foreign_keys="Change.old_snapshot_id", back_populates="old_snapshot")
    new_changes = relationship("Change", foreign_keys="Change.new_snapshot_id", back_populates="new_snapshot")