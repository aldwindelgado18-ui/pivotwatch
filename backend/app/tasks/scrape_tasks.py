import asyncio
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.base import SessionLocal
from ..models.company import Company
from ..models.snapshot import Snapshot
from ..models.change import Change
from ..services.scraper import WebsiteScraper
from .analysis_tasks import analyze_change

@shared_task(bind=True, max_retries=3)
def scrape_company(self, company_id: str, url: str):
    """
    Scrape a single company website
    """
    db = SessionLocal()
    try:
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}
        
        # Get previous snapshot
        previous_snapshot = db.query(Snapshot)\
            .filter(Snapshot.company_id == company_id)\
            .order_by(Snapshot.timestamp.desc())\
            .first()
        
        # Run scraper
        scraper = WebsiteScraper()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scraper.scrape(url, company_id))
        
        if not result['success']:
            # Update company status
            company.status = "error"
            company.last_scanned = datetime.utcnow()
            db.commit()
            return {"error": result['error']}
        
        # Create new snapshot
        new_snapshot = Snapshot(
            company_id=company_id,
            title=result['title'],
            html_hash=result['html_hash'],
            text_content=result['text_content'],
            html_content=result['html_content'],
            screenshot_path=result['screenshot_path'],
            metadata=result['metadata']
        )
        db.add(new_snapshot)
        db.flush()
        
        # Compare with previous
        if previous_snapshot:
            comparison = scraper.compare_with_previous(result, {
                'html_hash': previous_snapshot.html_hash,
                'text_content': previous_snapshot.text_content
            })
            
            if comparison['has_changes']:
                # Create change record
                change = Change(
                    company_id=company_id,
                    old_snapshot_id=previous_snapshot.id,
                    new_snapshot_id=new_snapshot.id,
                    change_data=comparison,
                    detected_at=datetime.utcnow()
                )
                db.add(change)
                db.flush()
                
                # Trigger analysis asynchronously
                analyze_change.delay(str(change.id))
        
        # Update company
        company.status = "active"
        company.last_scanned = datetime.utcnow()
        company.next_scan = datetime.utcnow() + timedelta(days=1)
        db.commit()
        
        return {
            "success": True,
            "company_id": company_id,
            "snapshot_id": str(new_snapshot.id),
            "has_changes": bool(previous_snapshot and comparison['has_changes'])
        }
        
    except Exception as e:
        self.retry(exc=e, countdown=60 * 5)  # Retry in 5 minutes
    finally:
        db.close()

@shared_task
def scrape_all_companies():
    """
    Queue all active companies for scraping
    """
    db = SessionLocal()
    try:
        companies = db.query(Company).filter(
            Company.status == "active",
            Company.next_scan <= datetime.utcnow()
        ).all()
        
        for company in companies:
            scrape_company.delay(str(company.id), company.url)
        
        return {"queued": len(companies)}
    finally:
        db.close()