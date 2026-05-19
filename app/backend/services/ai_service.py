import json
import logging
import requests
from typing import List, Dict, Any, Generator
from backend.core.config import settings

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.url = f"{settings.OLLAMA_URL.rstrip('/')}/api/chat"
        self.model = settings.OLLAMA_MODEL

    def _get_fallback_response(self, prompt_summary: str) -> str:
        """Fallback mock response when Ollama is offline or unavailable."""
        return (
            f"[DEMO MODE - Ollama is offline]\n\n"
            f"Here is a simulated AI analysis for: '{prompt_summary}'.\n\n"
            f"### Analysis\n"
            f"- **Detected Issue**: Possible connection failure to Ollama API or invalid config. (Make sure Ollama is running at {settings.OLLAMA_URL})\n"
            f"- **Severity**: Medium\n"
            f"- **Root Cause**: The system attempted to communicate with Ollama service, but it timed out or is not active.\n\n"
            f"### Suggested Fix\n"
            f"1. Start Ollama locally with `ollama run {settings.OLLAMA_MODEL}`.\n"
            f"2. Ensure model configuration `OLLAMA_MODEL` and URL `OLLAMA_URL` are set correctly in your environment variables.\n\n"
            f"### Mock Code Patch Example\n"
            f"```python\n"
            f"# To start Ollama in Docker, configure the URL:\n"
            f"OLLAMA_URL = 'http://host.docker.internal:11434'\n"
            f"```"
        )

    def generate_chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: str = None
    ) -> Generator[str, None, None]:
        """Streams responses chunk by chunk from Ollama or fallback if offline."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "stream": True,
            "options": {
                "temperature": 0.7
            }
        }

        try:
            response = requests.post(self.url, json=payload, stream=True, timeout=10)
            if response.status_code != 200:
                raise Exception(f"HTTP Status {response.status_code}")
                
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    data = json.loads(decoded)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
        except Exception as e:
            logger.warning(f"Ollama integration error: {e}. Falling back to simulation.")
            # Yield fallback response in chunks to simulate streaming
            fallback = self._get_fallback_response(messages[-1]["content"] if messages else "General chat query")
            for chunk in [fallback[i:i+15] for i in range(0, len(fallback), 15)]:
                yield chunk

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        """Retrieves a full response non-streaming."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "stream": False,
            "options": {
                "temperature": 0.5
            }
        }

        try:
            response = requests.post(self.url, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                raise Exception(f"HTTP Status {response.status_code}")
        except Exception as e:
            logger.warning(f"Ollama offline: {e}")
            return self._get_fallback_response(messages[-1]["content"] if messages else "API task request")

    def generate_reproduction_plan(self, title: str, description: str) -> Dict[str, Any]:
        """Generates reproduction steps and debugging workflow based on title & description."""
        system_prompt = (
            "You are a Senior QA Automation Engineer. Generate a structured JSON response containing: "
            "1. 'reproduction_steps': A list of steps to reproduce this bug.\n"
            "2. 'debugging_workflow': Detailed steps on how to debug this issue.\n"
            "3. 'expected_behavior': What should happen.\n"
            "4. 'actual_behavior': What is currently happening.\n"
            "Output ONLY valid JSON. Do not include markdown code fence wrappers or extra text."
        )
        prompt = f"Bug Title: {title}\nDescription: {description}"
        response_text = self.generate_response([{"role": "user", "content": prompt}], system_prompt)
        
        try:
            # Strip any markdown backticks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception:
            # Safe parsing fallback
            return {
                "reproduction_steps": ["Verify parameters.", "Trigger the function with empty values.", "Analyze output log."],
                "debugging_workflow": "Check stack trace, review input validation checks.",
                "expected_behavior": "Should execute or handle errors gracefully.",
                "actual_behavior": "Throws unhandled exception."
            }

    def analyze_logs(self, log_content: str) -> Dict[str, Any]:
        """Analyzes log/traceback, identifies root cause, severity and suggested fixes."""
        system_prompt = (
            "You are an expert systems debugging assistant. Analyze the logs provided. "
            "Generate a structured JSON output with the following keys:\n"
            "1. 'root_cause': Detail the technical root cause.\n"
            "2. 'severity': 'Low', 'Medium', 'High', or 'Critical'.\n"
            "3. 'suggested_fix': Bullet points of steps to resolve the issue.\n"
            "4. 'patch_example': Example of python code or config fix.\n"
            "5. 'summary': A brief, human-friendly summary of the error.\n"
            "Output ONLY valid JSON. Do not include markdown code fence wrappers."
        )
        response_text = self.generate_response([{"role": "user", "content": log_content}], system_prompt)
        
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "root_cause": "Traceback analysis fallback: Detected python exception in logs.",
                "severity": "High",
                "suggested_fix": ["Check function inputs.", "Verify database connections are open."],
                "patch_example": "try:\n    perform_action()\nexcept Exception as e:\n    logger.error(f'Failure: {e}')",
                "summary": "Exception raised in log execution stream."
            }

ai_service = OllamaService()
