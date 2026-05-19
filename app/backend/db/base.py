# Import all models here for Alembic
from backend.db.base_class import Base
from database.models.bug_report import BugReport
from database.models.test_case import TestCase
from database.models.execution_log import ExecutionLog
from database.models.chat_message import ChatMessage
from database.models.bug_analysis import BugAnalysis
from database.models.github_issue import GithubIssue

