import pytest
from unittest.mock import patch, MagicMock
from backend.services.ai_service import ai_service
from backend.services.ocr_service import ocr_service
from backend.services.slack_service import slack_service
from database.models.chat_message import ChatMessage
from database.models.bug_analysis import BugAnalysis
from database.models.github_issue import GithubIssue

# 1. Test AI Service Integration & Fallbacks
def test_ai_service_fallback():
    # If Ollama is offline/non-responsive, it should return a fallback demo response
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Connection refused")
        
        response = ai_service.generate_response([{"role": "user", "content": "Hello"}])
        assert "[DEMO MODE - Ollama is offline]" in response
        assert "Ollama is running" in response

def test_ai_service_generate_reproduction_plan():
    # Test plan generation returns structured keys even on failure or mock
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Ollama offline")
        
        plan = ai_service.generate_reproduction_plan("Login fails", "Details")
        assert "reproduction_steps" in plan
        assert "debugging_workflow" in plan
        assert "expected_behavior" in plan
        assert "actual_behavior" in plan

def test_ai_service_analyze_logs():
    # Test logs analysis returns structured root causes
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Ollama offline")
        
        analysis = ai_service.analyze_logs("ZeroDivisionError: division by zero")
        assert "root_cause" in analysis
        assert "severity" in analysis
        assert "suggested_fix" in analysis
        assert "patch_example" in analysis
        assert "summary" in analysis

# 2. Test OCR Screenshot Processing
def test_ocr_service_fallback():
    # If an image has mock bytes, it should return mock traceback text
    extracted_text = ocr_service.extract_text_from_image(b"fake-image-bytes")
    assert "Traceback (most recent call last):" in extracted_text
    assert "sqlalchemy.exc.OperationalError" in extracted_text

# 3. Test Slack Alerts
def test_slack_webhook_mock():
    # Send a mock alert and verify it runs successfully (returns True)
    success = slack_service.send_webhook_alert(
        title="Test Alert",
        text="A test bug has been verified.",
        status="success"
    )
    assert success is True

# 4. Test Model Schema Definitions
def test_db_model_properties():
    chat_msg = ChatMessage(conversation_id="test_conv", role="user", content="Hi")
    assert chat_msg.conversation_id == "test_conv"
    assert chat_msg.role == "user"
    assert chat_msg.content == "Hi"

    analysis = BugAnalysis(bug_report_id=1, severity="High", root_cause="Null pointer exception")
    assert analysis.bug_report_id == 1
    assert analysis.severity == "High"
    assert analysis.root_cause == "Null pointer exception"

    issue = GithubIssue(bug_report_id=1, issue_number=42, repo_owner="facebook", repo_name="react", github_url="https://github.com/facebook/react/issues/42")
    assert issue.issue_number == 42
    assert issue.repo_owner == "facebook"
    assert issue.repo_name == "react"
