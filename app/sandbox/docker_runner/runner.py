import docker
import os

class DockerRunner:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception:
            self.client = None

    def run_test(self, test_file: str, repo_path: str) -> dict:
        if not self.client:
            return {"status": "ERROR", "error": "Docker not available", "logs": "", "exit_code": -1}
            
        try:
            # Read test code
            with open(test_file, 'r', encoding='utf-8') as f:
                test_code = f.read()
                
            # Execute within python:3.11-slim container.
            # Passing code via TEST_CODE env variable avoids escaping and volume mount issues.
            container = self.client.containers.run(
                image="python:3.11-slim",
                command='sh -c "pip install pytest -q && echo \\"$TEST_CODE\\" > test_bug.py && PYTHONPATH=. pytest test_bug.py"',
                environment={"TEST_CODE": test_code},
                network_disabled=True,
                mem_limit="256m",
                cpu_quota=50000,
                detach=False
            )
            logs = container.decode('utf-8') if isinstance(container, bytes) else "Executed"
            status = "SUCCESS" if "failed" not in logs.lower() and "passed" in logs.lower() else "FAILED"
            return {"status": status, "logs": logs, "exit_code": 0}
        except docker.errors.ContainerError as e:
            logs = e.stderr.decode('utf-8') if e.stderr else e.stdout.decode('utf-8')
            return {"status": "FAILED", "logs": logs, "exit_code": e.exit_status}
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "logs": str(e), "exit_code": -1}
