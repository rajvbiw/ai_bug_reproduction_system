import spacy
from typing import Dict, List, Any
import re

class NLPEngine:
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # Fallback if model not downloaded
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", model])
            self.nlp = spacy.load(model)

    def analyze_bug(self, description: str) -> Dict[str, Any]:
        doc = self.nlp(description)
        
        # Extract potential function names (common patterns)
        functions = re.findall(r'(\w+)\(\)', description)
        
        # Extract error messages (common patterns like "Error: ...")
        errors = re.findall(r'(?:Error|Exception): (.+)', description)
        
        # Extract file paths
        files = re.findall(r'(\b[\w\.\-/]+\.py\b)', description)
        
        # NER for potential modules or libraries
        keywords = [ent.text for ent in doc.ents]
        
        return {
            "functions": list(set(functions)),
            "errors": list(set(errors)),
            "files": list(set(files)),
            "keywords": keywords,
            "entities": [(ent.text, ent.label_) for ent in doc.ents]
        }

nlp_engine = NLPEngine()
