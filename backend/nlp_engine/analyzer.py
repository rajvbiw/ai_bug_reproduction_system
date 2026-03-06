import re
import spacy
from typing import Dict, Any, List

# Load the spaCy NLP model (Requires `python -m spacy download en_core_web_sm`)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback to importing or blank if not installed yet
    nlp = spacy.blank("en")

class BugAnalyzer:
    def __init__(self):
        pass

    def extract_stack_trace(self, text: str) -> str | None:
        """
        Extracts python stack trace blocks from the text.
        """
        stack_trace_pattern = re.compile(r'Traceback \(most recent call last\):.*?[\r\n]+(?:\s+File ".*?".*?[\r\n]+)+.*?(?:Error|Exception): .*$', re.MULTILINE | re.DOTALL)
        match = stack_trace_pattern.search(text)
        if match:
            return match.group(0)
        return None

    def extract_functions(self, text: str) -> List[str]:
        """
        Extract potential function names (e.g., camelCase, snake_case + '()')
        """
        # A simple regex for function names ending with parentheses or commonly used python names
        func_pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*\(\)')
        # Alternatively, from stack trace
        return list(set(func_pattern.findall(text)))

    def extract_modules(self, text: str) -> List[str]:
        """
        Extract potential file paths or modules (e.g., .py files)
        """
        file_pattern = re.compile(r'\b([a-zA-Z0-9_\-\./]+\.py)\b')
        return list(set(file_pattern.findall(text)))

    def analyze_bug_report(self, description: str, steps_to_reproduce: str = "") -> Dict[str, Any]:
        full_text = f"{description}\n{steps_to_reproduce}"
        
        doc = nlp(full_text)
        
        # We can extract entities (Noun phrases, etc) for contextual keywords
        keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk.text) > 3]
        
        return {
            "stack_trace": self.extract_stack_trace(full_text),
            "suspected_functions": self.extract_functions(full_text),
            "suspected_modules": self.extract_modules(full_text),
            "keywords": list(set(keywords))[:10], # Top 10 unique keywords
        }

analyzer = BugAnalyzer()
