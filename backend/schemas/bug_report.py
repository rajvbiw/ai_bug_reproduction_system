from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from database.models.bug_report import BugStatus

class BugReportBase(BaseModel):
    title: str
    description: str
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment_details: Optional[str] = None
    repository_url: Optional[str] = None

class BugReportCreate(BugReportBase):
    pass

class BugReportResponse(BugReportBase):
    id: int
    status: BugStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
