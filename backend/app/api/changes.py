from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from ..models.base import get_db
from ..models.change import Change
from ..models.user import User
from .auth import get_current_user

router = APIRouter()

class ChangeSummary(BaseModel):
    id: UUID
    company_id: UUID
    company_name: str
    detected_at: datetime
    significance_score: int
    category: str
    summary: str

class ChangeDetail(ChangeSummary):
    analysis: str
    change_data: dict
    old_snapshot_id: UUID
    new_snapshot_id: UUID

@router.get("", response_model=List[ChangeSummary])
async def list_changes(
    company_id: Optional[UUID] = None,
    min_significance: int = Query(0, ge=0, le=100),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List changes with filters"""
    query = db.query(Change).join(Change.company).filter(
        Change.company.has(user_id=current_user.id)
    )
    
    # Apply filters
    if company_id:
        query = query.filter(Change.company_id == company_id)
    
    if min_significance > 0:
        query = query.filter(Change.significance_score >= min_significance)
    
    if from_date:
        query = query.filter(Change.detected_at >= from_date)
    
    if to_date:
        query = query.filter(Change.detected_at <= to_date)
    
    if category:
        query = query.filter(Change.category == category)
    
    # Order and paginate
    changes = query.order_by(Change.detected_at.desc())\
                   .offset(offset)\
                   .limit(limit)\
                   .all()
    
    return [
        ChangeSummary(
            id=c.id,
            company_id=c.company_id,
            company_name=c.company.name,
            detected_at=c.detected_at,
            significance_score=c.significance_score or 0,
            category=c.category or "unknown",
            summary=c.summary or "Changes detected"
        )
        for c in changes
    ]

@router.get("/{change_id}", response_model=ChangeDetail)
async def get_change(
    change_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed change information"""
    change = db.query(Change).filter(Change.id == change_id).first()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    # Verify access
    if change.company.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ChangeDetail(
        id=change.id,
        company_id=change.company_id,
        company_name=change.company.name,
        detected_at=change.detected_at,
        significance_score=change.significance_score or 0,
        category=change.category or "unknown",
        summary=change.summary or "Changes detected",
        analysis=change.analysis or "{}",
        change_data=change.change_data or {},
        old_snapshot_id=change.old_snapshot_id,
        new_snapshot_id=change.new_snapshot_id
    )