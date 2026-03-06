from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.db.base_class import Base

class BugStatus(str, enum.Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    REPRODUCING = "reproducing"
    REPRODUCED = "reproduced"
    NOT_REPRODUCED = "not_reproduced"
    DIAGNOSING = "diagnosing"
    COMPLETED = "completed"
    ERROR = "error"

class BugReport(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    environment_details = Column(JSON, nullable=True)
    repository_url = Column(String, nullable=True)
    status = Column(Enum(BugStatus), default=BugStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis_results = relationship("AnalysisResult", back_populates="bug_report", uselist=False)
    test_cases = relationship("TestCase", back_populates="bug_report")

class AnalysisResult(Base):
    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bugreport.id"))
    affected_module = Column(String, nullable=True)
    functions_mentioned = Column(JSON, nullable=True)
    error_messages = Column(JSON, nullable=True)
    stack_traces = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    probable_failure_points = Column(JSON, nullable=True)
    
    bug_report = relationship("BugReport", back_populates="analysis_results")

class TestCase(Base):
    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bugreport.id"))
    code = Column(Text)
    status = Column(String) # generated, executing, passed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bug_report = relationship("BugReport", back_populates="test_cases")
    executions = relationship("ExecutionLog", back_populates="test_case")

class ExecutionLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("testcase.id"))
    status = Column(String) # running, success, failed, error
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    errors = Column(JSON, nullable=True)
    stack_traces = Column(JSON, nullable=True)
    failed_assertions = Column(JSON, nullable=True)
    runtime_exceptions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_case = relationship("TestCase", back_populates="executions")
