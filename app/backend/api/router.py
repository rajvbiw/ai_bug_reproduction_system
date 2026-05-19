from fastapi import APIRouter
from backend.api.endpoints import bugs, chat, analyze, github, slack

api_router = APIRouter()
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(slack.router, prefix="/slack", tags=["slack"])
