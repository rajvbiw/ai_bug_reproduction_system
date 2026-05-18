"""
A simple mock test script to demonstrate the AST and NLP parsers run correctly.
"""
from backend.nlp_engine.analyzer import analyzer

def test_nlp_extraction():
    desc = """
    File "/app/core/auth.py", line 45, in authenticate_user
    KeyError: 'secret_token'
    
    The authenticate_user() function throws this error when caching is misconfigured.
    """
    
    result = analyzer.analyze_bug_report(desc)
    
    assert "KeyError" in result.get("stack_trace", "")
    assert "authenticate_user" in result.get("suspected_functions", [])
    assert "/app/core/auth.py" in result.get("suspected_modules", [])

print("Running baseline checks...")
test_nlp_extraction()
print("Baseline checks passed!")
