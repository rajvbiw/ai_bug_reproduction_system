import docker
import os
import tempfile
import json
from pathlib import Path

from backend.core.config import settings

class SandboxExecutionEngine:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            print(f"Warning: Docker is not available. Engine will fail. {e}")
            self.client = None

    def execute_test(self, test_code: str, requirements: str = "pytest\n") -> dict:
        """
        Creates a temporary directory with the test code and requirements,
        mounts it into a Docker container, runs pytest, and captures the results.
        """
        if not self.client:
            return {"status": "error", "logs": "Docker is not running or accessible.", "passed": False}
        
        # Create temporary directory for sandbox
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write test file
            test_file = temp_path / "test_bug.py"
            test_file.write_text(test_code, encoding="utf-8")
            
            # Write requirements
            req_file = temp_path / "requirements.txt"
            req_file.write_text(requirements, encoding="utf-8")
            
            volumes = {
                temp_dir: {'bind': '/app/sandbox', 'mode': 'rw'}
            }
            
            # Docker run command
            command = "sh -c 'pip install -r /app/sandbox/requirements.txt -q && cd /app/sandbox && pytest test_bug.py --json-report --json-report-file=/app/sandbox/report.json'"
            
            try:
                container = self.client.containers.run(
                    image=settings.SANDBOX_IMAGE,
                    command=command,
                    volumes=volumes,
                    working_dir="/app/sandbox",
                    detach=False,
                    auto_remove=True,
                    network_disabled=True, # Prevent net access for safety
                    mem_limit="256m",       # Memory limits
                    cpu_quota=50000         # CPU limits
                )
                logs = container.decode("utf-8") if isinstance(container, bytes) else "Executed"
            except docker.errors.ContainerError as e:
                logs = e.stderr.decode('utf-8') if e.stderr else e.stdout.decode('utf-8')
            except Exception as e:
                logs = str(e)
            
            # Check for pytest json report
            report_file = temp_path / "report.json"
            if report_file.exists():
                with open(report_file, "r") as f:
                    try:
                        report_data = json.load(f)
                        summary = report_data.get("summary", {})
                        passed = summary.get("failed", 0) == 0 and summary.get("passed", 0) > 0
                        return {"status": "success", "logs": logs, "passed": passed, "report": report_data}
                    except json.JSONDecodeError:
                        pass
                        
            # If report fallback to logs
            passed = "failed" not in logs.lower() and "passed" in logs.lower()
            return {"status": "success", "logs": logs, "passed": passed}
