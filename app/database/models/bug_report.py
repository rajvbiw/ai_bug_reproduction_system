import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from datetime import datetime
from backend.db.base_class import Base

class BugStatus(str, enum.Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    REPRODUCING = "reproducing"
    REPRODUCED = "reproduced"
    NOT_REPRODUCED = "not_reproduced"
    FAILED = "failed"

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    environment_details = Column(Text, nullable=True)
    repository_url = Column(String(512), nullable=True)
    status = Column(Enum(BugStatus), default=BugStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
