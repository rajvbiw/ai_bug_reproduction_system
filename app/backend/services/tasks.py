import os
import shutil
import tempfile
import json
from backend.services.celery_app import celery_app
from backend.nlp_engine.analysis import nlp_engine
from backend.code_analyzer.parser import CodeAnalyzer
from backend.test_generator.generator import TestGenerator
from sandbox.docker_runner.runner import DockerRunner
from sandbox.local_runner.runner import LocalRunner
from backend.bug_detector.detector import BugReproductionDetector
from backend.db.session import SessionLocal
from database.models.bug_report import BugReport, BugStatus
from database.models.test_case import TestCase, TestExecutionStatus
from database.models.execution_log import ExecutionLog
from database.models.bug_analysis import BugAnalysis
from backend.services.ai_service import ai_service
from backend.services.slack_service import slack_service

@celery_app.task
def process_bug_report(bug_id: int):
    db = SessionLocal()
    try:
        bug = db.query(BugReport).get(bug_id)
        if not bug:
            return
        
        bug.status = BugStatus.ANALYZING
        db.commit()
        
        # 1. AI & NLP Analysis
        # Generate reproduction plan via AI service
        repro_plan = ai_service.generate_reproduction_plan(bug.title, bug.description)
        repro_steps_str = "\n".join(repro_plan.get("reproduction_steps", []))
        if repro_steps_str:
            bug.steps_to_reproduce = repro_steps_str
            db.commit()

        analysis = nlp_engine.analyze_bug(bug.description)
        
        # 2. Codebase Analysis
        # Use the /app directory inside the container as the project root
        project_root = "/app"
        repo_path = os.path.join(project_root, "demo_app") 
        
        if bug.repository_url:
            # Real implementation would clone here to a temp dir
            # For this demo, we use the local demo_app
            pass
        
        analyzer = CodeAnalyzer(repo_path)
        suspicious_code = analyzer.match_bug_to_code(analysis)
        
        # 3. Test Generation
        bug.status = BugStatus.REPRODUCING
        db.commit()
        
        generator = TestGenerator(output_dir=os.path.join(project_root, "generated_tests"))
        test_file = generator.generate_pytest(bug.id, suspicious_code, analysis)
        
        # Create TestCase record
        with open(test_file, "r") as f:
            code_content = f.read()
            
        test_case = TestCase(
            bug_report_id=bug.id,
            name=os.path.basename(test_file),
            code_content=code_content,
            execution_status=TestExecutionStatus.RUNNING
        )
        db.add(test_case)
        db.commit()
        
        # 4. Sandbox Execution
        runner = DockerRunner()
        exec_result = runner.run_test(test_file, repo_path)
        
        # Fallback to local execution if Docker fails
        if exec_result.get("status") == "ERROR" and "Docker not available" in exec_result.get("error", ""):
            runner = LocalRunner()
            exec_result = runner.run_test(test_file, repo_path)
        
        # 5. Detection
        detector = BugReproductionDetector()
        detection = detector.determine_reproduction(analysis, exec_result)
        
        # Update records
        test_case.execution_status = TestExecutionStatus.FAILED if detection["reproduced"] else TestExecutionStatus.PASSED
        
        log = ExecutionLog(
            test_case_id=test_case.id,
            output=exec_result.get("logs"),
            exit_code=exec_result.get("exit_code")
        )
        db.add(log)
        
        bug.status = BugStatus.REPRODUCED if detection["reproduced"] else BugStatus.NOT_REPRODUCED
        db.commit()

        # 6. AI Log Analysis & Fix Suggestion
        log_content = exec_result.get("logs") or bug.description
        ai_analysis = ai_service.analyze_logs(log_content)
        
        bug_analysis = BugAnalysis(
            bug_report_id=bug.id,
            reproduction_plan=json.dumps(repro_plan),
            root_cause=ai_analysis.get("root_cause"),
            suggested_fix=json.dumps(ai_analysis.get("suggested_fix")),
            severity=ai_analysis.get("severity"),
            debugging_summary=ai_analysis.get("summary")
        )
        db.add(bug_analysis)
        db.commit()

        # 7. Slack Alert
        status_str = "success" if detection["reproduced"] else "failed"
        slack_msg = (
            f"*Status*: {bug.status.value.upper()}\n"
            f"*Severity*: {ai_analysis.get('severity')}\n"
            f"*Summary*: {ai_analysis.get('summary')}\n"
            f"*Root Cause*: {ai_analysis.get('root_cause')}\n"
            f"*Suggested Fix*: {', '.join(ai_analysis.get('suggested_fix', [])) if isinstance(ai_analysis.get('suggested_fix'), list) else ai_analysis.get('suggested_fix')}"
        )
        slack_service.send_webhook_alert(
            title=f"Bug '{bug.title}' Reproduction Result",
            text=slack_msg,
            status=status_str
        )
        
    finally:
        db.close()

