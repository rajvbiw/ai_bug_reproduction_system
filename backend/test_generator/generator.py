import os
from typing import List, Dict, Any

class TestGenerator:
    def __init__(self, output_dir: str = "generated_tests"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_pytest(self, bug_id: int, suspicious_code: List[Dict[str, Any]], bug_analysis: Dict[str, Any]) -> str:
        test_content = [
            "import pytest",
            "# Automatically generated test case for reproduction",
            ""
        ]
        
        # Add imports for matched files
        for item in suspicious_code:
            file_path = item["file"]
            mod_name = os.path.basename(file_path).replace(".py", "")
            test_content.append(f"# From file: {file_path}")
            # In a real scenario, we'd handle absolute/relative imports properly
            # For this demo, we assume the environment is set up
        
        test_func_name = f"test_reproduce_bug_{bug_id}"
        test_content.append(f"def {test_func_name}():")
        
        # Skeleton reproduction based on matched functions
        if suspicious_code:
            for item in suspicious_code:
                for func in item.get("matched_functions", []):
                    test_content.append(f"    # Attempting to call {func['name']}")
                    args = ", ".join(["None"] * len(func['args']))
                    test_content.append(f"    # result = {func['name']}({args})")
        
        # Add assertions based on error messages
        errors = bug_analysis.get("errors", [])
        if errors:
            test_content.append("    # Expected error message matching:")
            for err in errors:
                test_content.append(f"    # assert '{err}' in str(excinfo.value)")
        else:
            test_content.append("    assert True # Placeholder")
            
        file_name = f"test_bug_{bug_id}.py"
        full_path = os.path.join(self.output_dir, file_name)
        
        with open(full_path, "w") as f:
            f.write("\n".join(test_content))
            
        return full_path
