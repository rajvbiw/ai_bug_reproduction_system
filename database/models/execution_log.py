from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class ExecutionLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("testcase.id"), nullable=False)
    output = Column(Text, nullable=True)
    error_trace = Column(Text, nullable=True)
    exit_code = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_case = relationship("TestCase", back_populates="execution_logs")
