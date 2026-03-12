# Backend API - Smart Voice Interviewer

FastAPI backend server for AI-powered interview system.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```
```bash
cd backend
# Set RELOAD=false, WORKERS=4 (or 2*CPU+1) in .env
python app.py
# or directly:
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```
## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `POST /interview/start` - Start new interview
- `POST /interview/answer` - Submit answer
- `GET /interview/results/{session_id}` - Get results
- `GET /categories` - List categories
- `GET /health` - Health check

## Required Files

Make sure these files exist in the parent directory:
- `../final_knowledge_base.csv`
- `../course_catalog.csv`

Generate them by running cells 4 & 5 in `ai_voice.ipynb`
