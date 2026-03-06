import re
from typing import Dict, Any, List

class AIDiagnostician:
    def __init__(self):
        pass

    def extract_pytest_error(self, logs: str) -> str:
        """Extracts the main error message from pytest logs."""
        match = re.search(r"E\s+(.+?)(?=\n)", logs)
        if match:
            return match.group(1).strip()
        return "Unknown Error"

    def extract_pytest_stacktrace(self, logs: str) -> str:
        """Extracts the stack trace block from pytest logs."""
        # A simple extraction, look for the block between '_____' lines or similar
        return logs[-1000:] # Naive implementation: return the last 1000 chars

    def diagnose_root_cause(self, bug: Any, test_case: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes NLP context, repository AST, and failing test logs
        to suggest the root cause of the bug.
        """
        error_msg = test_case.error_message
        stack_trace = test_case.stack_trace
        nlp_context = context.get("nlp", {})
        
        suspected_functions = nlp_context.get("suspected_functions", [])
        
        # Simulated intelligent ranking
        ranked_candidates = []
        for func in suspected_functions:
            confidence = 80 if func in (str(stack_trace) or "") else 40
            ranked_candidates.append({
                "function": func,
                "confidence_score": confidence,
                "reason": f"Function '{func}' appeared in stack trace." if confidence > 50 else f"Function '{func}' was extracted from bug report NLP."
            })
            
        # Sort by confidence
        ranked_candidates = sorted(ranked_candidates, key=lambda x: x["confidence_score"], reverse=True)

        return {
            "root_cause_summary": f"The test failed with '{error_msg}'. AI analysis points to {ranked_candidates[0]['function'] if ranked_candidates else 'unknown function'} as the most probable root cause.",
            "candidates": ranked_candidates,
            "suggested_fix": "Investigate the edge-case branch logic in the top-ranked candidate function."
        }
