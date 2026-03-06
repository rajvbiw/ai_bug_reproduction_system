from typing import Dict, Any
import re

class BugReproductionDetector:
    def determine_reproduction(self, bug_analysis: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
        logs = execution_result.get("logs", "")
        status = execution_result.get("status", "ERROR")
        
        if status == "ERROR":
            return {"reproduced": False, "reason": "Execution error", "confidence": 0}
            
        # Check if the test failed (which usually means we've triggered something)
        # However, we specifically want to see if it triggered the *same* bug
        
        matched_errors = []
        for err in bug_analysis.get("errors", []):
            if err in logs:
                matched_errors.append(err)
        
        reproduced = len(matched_errors) > 0 or (status == "FAILED" and not matched_errors)
        
        confidence = 0
        if matched_errors:
            confidence = 0.9
        elif status == "FAILED":
            confidence = 0.5
            
        return {
            "reproduced": reproduced,
            "matched_errors": matched_errors,
            "confidence": confidence,
            "status": "REPRODUCED" if reproduced else "NOT_REPRODUCED"
        }
