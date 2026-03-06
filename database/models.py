from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from database.database import Base

class BugStatus(str, enum.Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    REPRODUCED = "REPRODUCED"
    FAILED = "FAILED"

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    environment_details = Column(Text, nullable=True)
    repository_url = Column(String(255), nullable=True)
    
    status = Column(Enum(BugStatus), default=BugStatus.PENDING)
    structured_nlp_data = Column(Text, nullable=True) # Storing JSON as string for simplicity
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    test_cases = relationship("TestCase", back_populates="bug_report")


class TestCaseStatus(str, enum.Enum):
    GENERATED = "GENERATED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"    # Wait, passing means not reproduced
    FAILED = "FAILED"    # Failing test = Bug REPRODUCED
    ERROR = "ERROR"

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"))
    
    code = Column(Text, nullable=False)
    strategy = Column(String(100), nullable=True) # "unit", "boundary", "fuzz"
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.GENERATED)
    
    execution_logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    bug_report = relationship("BugReport", back_populates="test_cases")
