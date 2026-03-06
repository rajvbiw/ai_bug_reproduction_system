from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.api import deps
from backend.schemas.bug_report import BugReportCreate, BugReportResponse
from database.models import BugReport
from backend.services.tasks import process_bug_report

router = APIRouter()

@router.post("/", response_model=BugReportResponse)
def create_bug_report(
    bug_in: BugReportCreate,
    db: Session = Depends(deps.get_db)
):
    bug = BugReport(**bug_in.model_dump())
    db.add(bug)
    db.commit()
    db.refresh(bug)
    
    # Trigger AI analysis and reproduction asynchronously
    process_bug_report.delay(bug.id)
    
    return bug

@router.get("/", response_model=List[BugReportResponse])
def get_bugs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    bugs = db.query(BugReport).offset(skip).limit(limit).all()
    return bugs
