from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from backend.db.base_class import Base

class GithubIssue(Base):
    __tablename__ = "github_issues"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=True)
    issue_number = Column(Integer, nullable=False)
    repo_owner = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    issue_title = Column(String(255), nullable=False)
    issue_body = Column(Text, nullable=True)
    github_url = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
