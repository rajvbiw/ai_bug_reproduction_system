import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from backend.db.base_class import Base

class TestExecutionStatus(str, enum.Enum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"))
    name = Column(String(255))
    code_content = Column(Text)
    execution_status = Column(String(50), default=TestExecutionStatus.RUNNING)
    created_at = Column(DateTime, default=datetime.utcnow)
