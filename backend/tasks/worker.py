import os
import json
from celery import Celery
from sqlalchemy.orm import Session

from backend.core.config import settings
from database import database, models
from backend.nlp_engine.analyzer import analyzer
from backend.code_analyzer.parser import ProjectAnalyzer
from backend.test_generator.generator import LLMTestGenerator
from backend.execution_engine.sandbox import SandboxExecutionEngine
from backend.bug_detector.diagnostician import AIDiagnostician

celery_app = Celery(
    "ai_bug_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "backend.tasks.worker.process_bug_report": "main-queue",
}

@celery_app.task(name="process_bug_report")
def process_bug_report(bug_id: int):
    """
    Main orchestration task for analyzing and reproducing a bug.
    """
    db: Session = database.SessionLocal()
    try:
        bug = db.query(models.BugReport).filter(models.BugReport.id == bug_id).first()
        if not bug:
            return "Bug not found"
            
        bug.status = models.BugStatus.ANALYZING
        db.commit()

        # 1. NLP Understanding
        extracted_data = analyzer.analyze_bug_report(bug.description, bug.steps_to_reproduce or "")
        bug.structured_nlp_data = json.dumps(extracted_data)
        db.commit()

        # 2. Code Analysis (if repo provided)
        repo_context = {}
        if bug.repository_url:
            code_dir = f"/tmp/repos/{bug_id}"
            os.makedirs(code_dir, exist_ok=True)
            project_analyzer = ProjectAnalyzer(bug.repository_url, code_dir)
            repo_context = project_analyzer.analyze_repository()

        # Combine Context
        full_context = {
            "nlp": extracted_data,
            "repo": repo_context
        }

        # 3. Test Generation
        test_gen = LLMTestGenerator()
        bug_dict = {
            "title": bug.title,
            "description": bug.description
        }
        generated_tests = test_gen.batch_generate(bug_dict, extracted_data)

        sandbox = SandboxExecutionEngine()
        diagnostician = AIDiagnostician()
        
        reproduced = False
        
        # 4. Sandbox Execution
        for strategy, code in generated_tests.items():
            test_case = models.TestCase(
                bug_report_id=bug.id,
                code=code,
                strategy=strategy,
                status=models.TestCaseStatus.RUNNING
            )
            db.add(test_case)
            db.commit()
            
            # Execute
            result = sandbox.execute_test(code)
            
            test_case.execution_logs = result.get("logs", "")
            
            # 5. Reproduction Detection
            if result.get("status") == "success" and not result.get("passed"):
                # Test failed = Bug was reproduced
                test_case.status = models.TestCaseStatus.FAILED
                test_case.error_message = diagnostician.extract_pytest_error(result.get("logs", ""))
                test_case.stack_trace = diagnostician.extract_pytest_stacktrace(result.get("logs", ""))
                reproduced = True
                db.commit()
                break # Stop testing once reproduced
            elif result.get("status") == "success":
                test_case.status = models.TestCaseStatus.PASSED
            else:
                test_case.status = models.TestCaseStatus.ERROR
            db.commit()

        if reproduced:
            bug.status = models.BugStatus.REPRODUCED
            
            # 6. Diagnosis root cause based on the failed test case
            diagnosis = diagnostician.diagnose_root_cause(
                bug=bug, 
                test_case=test_case, 
                context=full_context
            )
            
            # Store diagnosis somewhere (appending to structured data for now)
            current_data = json.loads(bug.structured_nlp_data)
            current_data["ai_diagnosis"] = diagnosis
            bug.structured_nlp_data = json.dumps(current_data)
            
        else:
            bug.status = models.BugStatus.FAILED # Failed to reproduce
            
        db.commit()
        return "Process completed"

    except Exception as e:
        bug.status = models.BugStatus.FAILED
        db.commit()
        raise e
    finally:
        db.close()
