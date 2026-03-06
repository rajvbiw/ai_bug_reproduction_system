from fastapi import APIRouter
from backend.api.endpoints import bugs

api_router = APIRouter()
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])
