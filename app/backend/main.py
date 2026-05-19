from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api import router as api_router
from backend.db.session import engine
from backend.db.base_class import Base
from database.models import bug_report, test_case, execution_log, chat_message, bug_analysis, github_issue # Force model registration

import time
from sqlalchemy.exc import OperationalError

# Create tables with retry loop for database availability
for i in range(15):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except OperationalError as e:
        if i == 14:
            raise e
        print(f"Database not ready yet, retrying in 2 seconds... ({i+1}/15)")
        time.sleep(2)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router.api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to AI Bug Reproduction System API"}
