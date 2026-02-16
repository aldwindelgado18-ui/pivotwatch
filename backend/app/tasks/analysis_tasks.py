import json
from celery import shared_task
from sqlalchemy.orm import Session
from ..models.base import SessionLocal
from ..models.change import Change
from ..models.snapshot import Snapshot
from ..services.analyzer import ChangeAnalyzer
import asyncio

@shared_task(bind=True, max_retries=2)
def analyze_change(self, change_id: str):
    """
    Analyze a detected change for business significance
    """
    db = SessionLocal()
    try:
        # Get change with snapshots
        change = db.query(Change).filter(Change.id == change_id).first()
        if not change:
            return {"error": "Change not found"}
        
        old_snapshot = db.query(Snapshot).filter(Snapshot.id == change.old_snapshot_id).first()
        new_snapshot = db.query(Snapshot).filter(Snapshot.id == change.new_snapshot_id).first()
        
        if not old_snapshot or not new_snapshot:
            return {"error": "Snapshots not found"}
        
        # Get company name
        company_name = change.company.name if change.company else "Unknown Company"
        
        # Run analysis
        analyzer = ChangeAnalyzer()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Extract changes from change_data
        change_data = change.change_data or {}
        detected_changes = change_data.get('changes', [])
        
        analysis = loop.run_until_complete(
            analyzer.analyze_significance(
                company_name=company_name,
                old_content=old_snapshot.text_content or "",
                new_content=new_snapshot.text_content or "",
                detected_changes=detected_changes
            )
        )
        
        # Update change record
        change.significance_score = analysis.get('score', 50)
        change.category = analysis.get('category', 'other')
        change.summary = analysis.get('summary', 'Website changes detected')
        change.analysis = json.dumps({
            'justification': analysis.get('justification', ''),
            'recommended_action': analysis.get('recommended_action', ''),
            'full_analysis': analysis
        })
        
        db.commit()
        
        return {
            "success": True,
            "change_id": change_id,
            "significance": change.significance_score,
            "category": change.category
        }
        
    except Exception as e:
        self.retry(exc=e, countdown=60)
    finally:
        db.close()