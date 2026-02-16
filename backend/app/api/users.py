from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ..models.base import get_db
from ..models.user import User
from .auth import get_current_user

router = APIRouter()

class UserProfile(BaseModel):
    id: UUID
    email: str
    name: str
    plan: str
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    name: str = None
    email: str = None

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "plan": current_user.plan,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    if user_update.name:
        current_user.name = user_update.name
    if user_update.email:
        # Check if email is already in use
        existing = db.query(User).filter(User.email == user_update.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "plan": current_user.plan,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
