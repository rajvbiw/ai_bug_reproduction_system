# AI Bug Reproduction System

An AI-powered system that automatically analyzes bug reports, generates test cases, and reproduces bugs in isolated Docker sandboxes.

## Features
- **NLP Bug Analysis**: Extracts functions, errors, and files from bug reports using spaCy.
- **AST Code Analysis**: Maps bug reports to specific functions in the codebase.
- **Auto Test Generation**: Generates `pytest` cases to trigger described bugs.
- **Docker Sandboxing**: Executes generated tests in isolated containers.
- **Async Processing**: Uses Celery + Redis for reliable background execution.

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### 2. Quick Start (Docker)
```bash
docker-compose up --build
```

### 3. Manual Setup (Windows)
1. Create virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Setup Database:
   - Ensure PostgreSQL is running and create `bug_repro_db`.
   - Update `backend/core/config.py` if needed.
4. Run Migrations:
   ```powershell
   alembic upgrade head
   ```
5. Run API:
   ```powershell
   uvicorn backend.main:app --reload
   ```
6. Run Celery Worker:
   ```powershell
   celery -A backend.services.tasks worker --loglevel=info
   ```

## API Documentation
Once running, visit `http://localhost:8085/docs` for the interactive Swagger UI.

## Project Structure
- `backend/`: Fast API and core logic.
  - `nlp_engine/`: Bug report parsing.
  - `code_analyzer/`: AST based codebase scanning.
  - `test_generator/`: Pytest generation.
  - `bug_detector/`: Reproduction verification.
- `database/`: SQLAlchemy models and migrations.
- `sandbox/`: Docker container execution logic.
