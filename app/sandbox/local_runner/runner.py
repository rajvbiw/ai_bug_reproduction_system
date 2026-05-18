import subprocess
import os

class LocalRunner:
    def run_test(self, test_file: str, repo_path: str) -> dict:
        try:
            # Set PYTHONPATH to include repo_path's parent directory
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.dirname(repo_path)
            
            result = subprocess.run(
                ["pytest", test_file],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            logs = result.stdout + "\n" + result.stderr
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            return {"status": status, "logs": logs, "exit_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"status": "FAILED", "logs": "Timeout expired", "exit_code": -1}
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "logs": str(e), "exit_code": -1}
