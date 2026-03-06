import ast
import os
from typing import List, Dict, Any

class CodeAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_python_files(self) -> List[str]:
        python_files = []
        for root, _, files in os.walk(self.repo_path):
            if "venv" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def parse_functions(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return []
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
        return functions

    def match_bug_to_code(self, bug_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        suspicious_files = []
        py_files = self.get_python_files()
        
        for file_path in py_files:
            file_name = os.path.basename(file_path)
            score = 0
            if file_name in bug_analysis.get("files", []):
                score += 10
            
            funcs = self.parse_functions(file_path)
            matching_funcs = [f for f in funcs if f["name"] in bug_analysis.get("functions", [])]
            
            if matching_funcs or score > 0:
                suspicious_files.append({
                    "file": file_path,
                    "score": score + (len(matching_funcs) * 5),
                    "matched_functions": matching_funcs
                })
        
        return sorted(suspicious_files, key=lambda x: x["score"], reverse=True)
