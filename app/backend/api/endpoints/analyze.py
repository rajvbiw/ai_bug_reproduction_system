from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.api import deps
from backend.services.ai_service import ai_service
from backend.services.ocr_service import ocr_service

router = APIRouter()

class LogTextIn(BaseModel):
    logs: str

class CodeFixIn(BaseModel):
    code_context: str
    error_message: str
    stack_trace: Optional[str] = None

@router.post("/log")
def analyze_log(
    log_in: LogTextIn
):
    analysis = ai_service.analyze_logs(log_in.logs)
    return analysis

@router.post("/log-file")
async def analyze_log_file(
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        log_text = content.decode("utf-8", errors="ignore")
        analysis = ai_service.analyze_logs(log_text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read log file: {str(e)}")

@router.post("/screenshot")
async def analyze_screenshot(
    file: UploadFile = File(...)
):
    try:
        image_bytes = await file.read()
        extracted_text = ocr_service.extract_text_from_image(image_bytes)
        
        # Analyze extracted text
        analysis = ai_service.analyze_logs(extracted_text)
        # Append extracted text for user reference
        analysis["extracted_text"] = extracted_text
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process screenshot: {str(e)}")

@router.post("/suggest-fixes")
def suggest_fixes(
    fix_in: CodeFixIn
):
    prompt = (
        f"Analyze this python code context and failure details to suggest bug fixes.\n\n"
        f"### Code Context:\n```python\n{fix_in.code_context}\n```\n\n"
        f"### Error Message:\n{fix_in.error_message}\n\n"
        f"### Stack Trace:\n{fix_in.stack_trace or 'None'}"
    )
    
    system_prompt = (
        "You are an expert software engineer. Provide a detailed markdown response containing:\n"
        "1. Code Fix Suggestions: explanation of modifications.\n"
        "2. Dependency Fixes: if any packages need upgrading.\n"
        "3. Patch Example: code snippet showing the fix.\n"
        "4. Refactoring Suggestions: how to prevent this in the future."
    )
    
    response = ai_service.generate_response([{"role": "user", "content": prompt}], system_prompt=system_prompt)
    return {"suggestions": response}
