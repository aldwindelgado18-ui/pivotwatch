from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl

from ..models.base import get_db
from ..models.company import Company
from ..models.user import User
from .auth import oauth2_scheme, get_current_user
from ..tasks.scrape_tasks import scrape_company

router = APIRouter()

class CompanyCreate(BaseModel):
    name: str
    url: HttpUrl
    industry: Optional[str] = None
    notes: Optional[str] = None
    scan_frequency: str = "daily"
    alert_threshold: int = 50

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    url: str
    industry: Optional[str]
    notes: Optional[str]
    status: str
    last_scanned: Optional[datetime]
    next_scan: Optional[datetime]
    created_at: datetime

class CompanyDetailResponse(CompanyResponse):
    total_changes: int = 0
    last_change: Optional[datetime]

@router.post("", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new company to track"""
    
    # Check if already tracking
    existing = db.query(Company).filter(
        Company.user_id == current_user.id,
        Company.url == str(company_data.url)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already tracking this company")
    
    # Create company
    company = Company(
        user_id=current_user.id,
        name=company_data.name,
        url=str(company_data.url),
        industry=company_data.industry,
        notes=company_data.notes,
        scan_frequency=company_data.scan_frequency,
        alert_threshold=company_data.alert_threshold,
        next_scan=datetime.utcnow()  # Scan immediately
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    # Trigger initial scrape in background
    background_tasks.add_task(
        scrape_company.delay,
        str(company.id),
        str(company_data.url)
    )
    
    return company

@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tracked companies"""
    companies = db.query(Company).filter(
        Company.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return companies

@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed company information"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get change count
    change_count = len(company.changes) if company.changes else 0
    
    # Get last change
    last_change = None
    if company.changes:
        last_change = max(c.detected_at for c in company.changes)
    
    # Convert to response
    response = CompanyDetailResponse(
        id=company.id,
        name=company.name,
        url=company.url,
        industry=company.industry,
        notes=company.notes,
        status=company.status,
        last_scanned=company.last_scanned,
        next_scan=company.next_scan,
        created_at=company.created_at,
        total_changes=change_count,
        last_change=last_change
    )
    
    return response

@router.delete("/{company_id}")
async def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop tracking a company"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    
    return {"message": "Company deleted successfully"}

@router.post("/{company_id}/scan")
async def trigger_scan(
    company_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger a scan"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    background_tasks.add_task(
        scrape_company.delay,
        str(company.id),
        company.url
    )
    
    return {"message": "Scan triggered successfully"}