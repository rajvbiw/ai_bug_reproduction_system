from backend.services.celery_app import celery_app
from backend.nlp_engine.analysis import nlp_engine
from backend.code_analyzer.parser import CodeAnalyzer
from backend.test_generator.generator import TestGenerator
from backend.execution_engine.sandbox import SandboxExecutionEngine
from backend.bug_detector.detector import BugReproductionDetector
from backend.db.session import SessionLocal
from database.models import BugReport, BugStatus, TestCase, TestExecutionStatus

@celery_app.task
def process_bug_report(bug_id: int):
    db = SessionLocal()
    try:
        bug = db.query(BugReport).get(bug_id)
        if not bug:
            return
        
        bug.status = BugStatus.ANALYZING
        db.commit()
        
        # 1. NLP Analysis
        analysis = nlp_engine.analyze_bug(bug.description)
        
        # 2. Codebase Analysis
        repo_path = "/app" # Use the app path inside container
        analyzer = CodeAnalyzer(repo_path)
        suspicious_code = analyzer.match_bug_to_code(analysis)
        
        # 3. Test Generation
        bug.status = BugStatus.REPRODUCING
        db.commit()
        
        generator = TestGenerator()
        test_file = generator.generate_pytest(bug.id, suspicious_code, analysis)
        
        # Create TestCase record
        try:
            with open(test_file, "r") as f:
                code_content = f.read()
        except Exception:
            code_content = "# Error reading generated test file"
            
        test_case = TestCase(
            bug_report_id=bug.id,
            name=f"test_bug_{bug.id}.py",
            code_content=code_content,
            execution_status=TestExecutionStatus.RUNNING
        )
        db.add(test_case)
        db.commit()
        
        # 4. Sandbox Execution
        runner = SandboxExecutionEngine()
        exec_result = runner.execute_test(code_content)
        
        # 5. Detection
        detector = BugReproductionDetector()
        detection = detector.determine_reproduction(analysis, exec_result)
        
        # Update records
        test_case.execution_status = TestExecutionStatus.FAILED if detection["reproduced"] else TestExecutionStatus.PASSED
        # test_case.execution_logs = exec_result.get("logs") # This might need a separate ExecutionLog entry based on model
        
        bug.status = BugStatus.REPRODUCED if detection["reproduced"] else BugStatus.NOT_REPRODUCED
        db.commit()
        
    finally:
        db.close()
