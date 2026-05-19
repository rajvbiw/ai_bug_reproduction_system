from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from backend.db.base_class import Base

class BugAnalysis(Base):
    __tablename__ = "bug_analyses"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=False)
    reproduction_plan = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    severity = Column(String(50), nullable=True)  # 'low', 'medium', 'high', 'critical'
    debugging_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
