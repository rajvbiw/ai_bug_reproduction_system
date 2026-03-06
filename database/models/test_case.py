from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from backend.db.base_class import Base

class TestExecutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"

class TestCase(Base):
    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bugreport.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code_content = Column(Text, nullable=False)
    execution_status = Column(Enum(TestExecutionStatus), default=TestExecutionStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bug_report = relationship("BugReport", back_populates="test_cases")
    execution_logs = relationship("ExecutionLog", back_populates="test_case", cascade="all, delete-orphan")
