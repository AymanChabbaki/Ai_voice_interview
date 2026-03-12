# Smart Voice Interviewer

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![Vite](https://img.shields.io/badge/vite-5-646cff.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**AI-powered mock interview platform with semantic answer scoring, course recommendations, and progress tracking.**

[Overview](#overview) � [Quick Start](#quick-start) � [Project Structure](#project-structure) � [API Reference](#api-reference) � [Team](#team)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [AI and ML Pipeline](#ai-and-ml-pipeline)
- [Achievements System](#achievements-system)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Team](#team)

---

## Overview

Smart Voice Interviewer is an AI-powered interview preparation platform. Candidates practice mock interviews by answering questions and receiving instant, semantically-aware feedback scored by **Sentence-BERT** (cosine similarity). After each session the system recommends courses targeted at the candidate's weak areas using a TF-IDF retrieval pipeline and pre-trained classifiers.

### Key Highlights

- **Semantic Scoring** � answers are evaluated by meaning, not keyword matching, using `sentence-transformers/all-MiniLM-L6-v2`
- **Course Recommendations** � personalized courses suggested from a catalog based on topic and difficulty gap
- **User Profiles** � registration, JWT auth, bio, experience level, interests
- **Progress Analytics** � per-category scores, interview history, streaks
- **Achievements** � five milestone badges unlocked automatically
- **Production-Ready Backend** — rate limiting, env-based secrets, PostgreSQL with connection pooling, structured logging

---

## Features

| Area | Details |
|------|---------|
| Interview flow | Select a category, answer `NUM_QUESTIONS` questions, receive a score per question |
| Semantic scoring | Cosine similarity between candidate embedding and reference answer embedding; threshold configurable |
| Course recommendations | After results, TF-IDF + category/difficulty classifiers suggest relevant courses |
| Authentication | JWT Bearer tokens (HS256, 7-day default expiry) |
| Rate limiting | `/register` 5 req/min � `/login` 10 req/min � global 200 req/min |
| Profiles | Username, name, bio, experience level (Beginner / Intermediate / Advanced), interests |
| Stats | Total interviews, average pass rate, current streak, best streak |
| History | Per-session record: topic, date, pass rate, average score, question count |
| Achievements | Five automatic badges triggered by interview count, pass rate, and streak |
| Analytics | Per-category performance breakdown across all historical sessions |

---

## Architecture

```
+--------------------------------------+
�         Browser (React 18 + Vite)    �
�  Home � Dashboard � Interview � Auth �
�  port 5173                           �
+--------------------------------------+
                �  REST (JSON)
                ?
+--------------------------------------+
�       FastAPI Backend (Python)       �
�  JWT auth � slowapi rate limiting    �
�  Pydantic v2 validation              �
�  port 8000                           �
�                                      �
�  +------------------------------+    �
�  �   Sentence-BERT inference   �    �
�  �   all-MiniLM-L6-v2          �    �
�  �   cosine_similarity scorer  �    �
�  +------------------------------+    �
�                                      �
�  +------------------------------+    �
�  �   Course recommendation     �    �
�  �   TF-IDF � RF classifiers   �    �
�  +------------------------------+    �
�                                      �
�  +------------------------------+    �
│  │   PostgreSQL                 │    │
│  │   users · user_stats ·       │    │
│  │   interview_history          │    │
�  +------------------------------+    �
+--------------------------------------+
```

---

## Project Structure

```
Jira_Project/
+-- backend/                        # FastAPI Python backend
�   +-- app.py                      # Main application (routes, auth, AI scoring)
�   +-- database.py                 # PostgreSQL layer (psycopg2, connection pool)  
�   +-- requirements.txt            # Python dependencies
�   +-- .env.example                # Environment variable template
�
+-- frontend/                       # React 18 + Vite frontend
�   +-- src/
�   �   +-- App.jsx                 # Single-page application (~1900 lines)
�   �   +-- App.css                 # Global styles
�   �   +-- confetti.js             # Celebration animation
�   �   +-- index.css               # Base CSS reset
�   �   +-- main.jsx                # React entry point
�   +-- package.json
�   +-- vite.config.js
�
+-- models/                         # Pre-trained ML artefacts
�   +-- category_classifier.joblib         # RandomForest: predicts topic category
�   +-- difficulty_classifier.joblib       # RandomForest: predicts difficulty
�   +-- label_encoder_category.joblib      # LabelEncoder for category classes
�   +-- label_encoder_difficulty.joblib    # LabelEncoder for difficulty classes
�   +-- tfidf_vectorizer.joblib            # TF-IDF vectorizer for course retrieval
�   +-- tfidf_matrix.joblib                # Pre-computed TF-IDF document matrix
�   +-- course_embeddings.npy              # SBERT embeddings for courses
�   +-- courses_data.pkl                   # Serialised course catalog
�   +-- category_course_map.json           # Category ? course list mapping
�   +-- model_metadata.json                # Training metadata
�   +-- recommendation_metadata.json      # Recommendation pipeline metadata
�
+-- Dataset/                        # Training data
�   +-- coding_interview_question_bank.csv
�   +-- Mock_interview_questions.json
�   +-- Software Questions.csv
�
+-- docs/                           # Additional documentation
+-- final_knowledge_base.csv        # Interview questions used at runtime
�                                   #   columns: Category, Question, Answer, Difficulty
+-- course_catalog.csv              # Course catalog used at runtime
�                                   #   columns: Course_Title, Category, Platform,
�                                   #            Provider, Difficulty, URL
+-- ai_voice_complete.ipynb         # Jupyter notebook (model training & exploration)
+-- Names_Role.md                   # Team members and roles
+-- README.md                       # This file
```

---

## Tech Stack

### Backend

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.6 | Web framework |
| `uvicorn[standard]` | 0.34.0 | ASGI server |
| `pydantic[email]` | 2.10.6 | Request validation |
| `python-multipart` | 0.0.20 | Form data parsing |
| `python-jose[cryptography]` | 3.3.0 | JWT creation & verification |
| `bcrypt` + `passlib[bcrypt]` | 4.2.1 / 1.7.4 | Password hashing |
| `slowapi` | 0.1.9 | Rate limiting |
| `psycopg2-binary` | 2.9.9 | PostgreSQL driver + connection pool |
| `sentence-transformers` | 2.2.2 | Semantic answer scoring |
| `torch` | 2.0.1 | PyTorch runtime |
| `scikit-learn` | 1.3.2 | Classifiers & TF-IDF |
| `numpy` | 1.23.5 | Numerical operations |
| `pandas` | 2.0.3 | CSV data loading |
| `python-dotenv` | 1.0.1 | .env file loading |

### Frontend

| Package | Purpose |
|---------|---------|
| React 18 | UI library |
| Vite 5 | Build tool & dev server |
| lucide-react | Icon library |
| Web Speech API | Browser speech recognition (built-in) |

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **PostgreSQL 14+** running locally or a managed instance (e.g. Supabase, Neon, Railway)
- ~2 GB disk space (PyTorch + sentence-transformers)

---

## Quick Start

### Option 1: Docker (Recommended) 🐳

The fastest way to get started with Docker and Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd Ai_voice_interview

# Copy environment file
cp .env.example .env
# Edit .env and set SECRET_KEY (generate with: openssl rand -hex 32)

# Start all services (backend + database)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access the API
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker and CI/CD documentation.**

---

### Option 2: Manual Setup

#### 1. Clone the repository

```bash
git clone <repository-url>
cd Ai_voice_interview
```

#### 2. Set up the backend

```bash
cd backend

# Copy and edit the environment file
cp .env.example .env
# Open .env and fill in both required values:
#   SECRET_KEY  – generate with: python -c "import secrets; print(secrets.token_hex(32))"
#   DATABASE_URL – e.g. postgresql://postgres:password@localhost:5432/smart_interviewer

# Create a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create the PostgreSQL database (one-time setup)
# Connect to psql as a superuser and run:
#   CREATE DATABASE smart_interviewer;
# Tables are created automatically on first server start.

# Start the server
python app.py
# Server is now running at http://localhost:8000
```

#### 3. Set up the frontend

Open a second terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
# App is now running at http://localhost:5173
```

### 4. Open the app

Navigate to **http://localhost:5173** in your browser, register an account, and start an interview.

---

## Environment Variables

All backend configuration is controlled through a `.env` file in the `backend/` directory.
Copy `backend/.env.example` to `backend/.env` and edit as needed.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | � | JWT signing secret. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `PORT` | No | `8000` | Port the server binds to |
| `WORKERS` | No | `1` | Number of uvicorn worker processes |
| `LOG_LEVEL` | No | `info` | Logging level (`debug`, `info`, `warning`, `error`) |
| `RELOAD` | No | `false` | Hot-reload (set `true` in development only) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` (7 days) | JWT expiry in minutes |
| `ALLOWED_ORIGINS` | No | `http://localhost:5173` | Comma-separated list of allowed CORS origins |
| `SIMILARITY_THRESHOLD` | No | `0.6` | Minimum cosine similarity score to pass a question |
| `NUM_QUESTIONS` | No | `3` | Number of questions per interview session |
| `KB_FILE` | No | `../final_knowledge_base.csv` | Path to interview questions CSV |
| `COURSES_FILE` | No | `../course_catalog.csv` | Path to course catalog CSV |

---

## API Reference

Base URL: `http://localhost:8000`

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API metadata |
| `GET` | `/health` | Health check |
| `GET` | `/categories` | List all available interview categories |
| `GET` | `/statistics` | Dataset statistics (question counts per category) |

### Authentication

| Method | Endpoint | Rate limit | Description |
|--------|----------|-----------|-------------|
| `POST` | `/register` | 5/min | Create a new user account |
| `POST` | `/login` | 10/min | Authenticate and receive a JWT token |

#### Register � `POST /register`

```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "password": "StrongPass123!",
  "name": "Jane Doe",
  "bio": "Software engineer",
  "experience_level": "Intermediate",
  "interests": ["Python", "System Design"]
}
```

Response: `{ "message": "User created", "user_id": "...", "token": "..." }`

#### Login � `POST /login`

```json
{ "username": "jdoe", "password": "StrongPass123!" }
```

Response: `{ "access_token": "...", "token_type": "bearer", "user_id": "...", "username": "..." }`

### Interview

All interview endpoints are stateless (session data stored server-side by `session_id`).

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/interview/start` | No | Start a new interview session |
| `POST` | `/interview/answer` | No | Submit an answer and receive a score |
| `GET` | `/interview/results/{session_id}` | No | Full results + course recommendations |
| `DELETE` | `/interview/{session_id}` | No | Delete a session |
| `GET` | `/interview/sessions` | No | List active sessions |

#### Start interview � `POST /interview/start`

```json
{ "category": "Python", "user_id": "optional-user-id" }
```

Response: `{ "session_id": "...", "question": "...", "question_number": 1, "total_questions": 3 }`

#### Submit answer � `POST /interview/answer`

```json
{
  "session_id": "...",
  "answer": "A list is mutable, a tuple is immutable..."
}
```

Response: `{ "score": 82.5, "passed": true, "feedback": "...", "expected_answer": "...", "next_question": "...", "session_complete": false }`

### Profile (JWT required)

Send the token as `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/me` | Current user info |
| `GET` | `/profile/{user_id}` | Full profile |
| `PUT` | `/profile/{user_id}` | Update profile fields |
| `GET` | `/profile/{user_id}/stats` | Stats summary |
| `GET` | `/profile/{user_id}/history` | Interview history (paginated) |
| `GET` | `/profile/{user_id}/analytics` | Per-category performance breakdown |
| `POST` | `/profile/{user_id}/update-after-interview` | Save results, update stats, award achievements |

---

## Database Schema

PostgreSQL. Tables are created automatically on first server start via `init_db()`.

```sql
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    user_id          TEXT   UNIQUE NOT NULL,  -- UUID
    username         TEXT   UNIQUE NOT NULL,
    email            TEXT   UNIQUE NOT NULL,
    password_hash    TEXT   NOT NULL,
    name             TEXT   NOT NULL,
    bio              TEXT,
    experience_level TEXT   NOT NULL DEFAULT 'Beginner',  -- Beginner | Intermediate | Advanced
    interests        TEXT,                                -- JSON array
    created_at       TEXT   NOT NULL,
    updated_at       TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS user_stats (
    id                  SERIAL  PRIMARY KEY,
    user_id             TEXT    UNIQUE NOT NULL
                        REFERENCES users(user_id) ON DELETE CASCADE,
    interview_count     INTEGER NOT NULL DEFAULT 0,
    total_score         REAL    NOT NULL DEFAULT 0.0,
    current_streak      INTEGER NOT NULL DEFAULT 0,
    best_streak         INTEGER NOT NULL DEFAULT 0,
    last_interview_date TEXT,
    achievements        TEXT    -- JSON array of achievement IDs
);

CREATE TABLE IF NOT EXISTS interview_history (
    id              SERIAL  PRIMARY KEY,
    user_id         TEXT    NOT NULL
                    REFERENCES users(user_id) ON DELETE CASCADE,
    session_id      TEXT    NOT NULL,
    topic           TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pass_rate       REAL    NOT NULL,
    average_score   REAL    NOT NULL,
    questions_count INTEGER NOT NULL,
    passed          INTEGER NOT NULL  -- 1 = majority passed
);
```

---

## AI and ML Pipeline

### Semantic Answer Scoring

1. On startup the backend loads `sentence-transformers/all-MiniLM-L6-v2` (384-dim embeddings).
2. All reference answers from `final_knowledge_base.csv` are encoded once and cached in memory.
3. When a candidate submits an answer, it is encoded and cosine similarity is computed against the reference embedding.
4. Score = `cosine_similarity * 100`. Score = `SIMILARITY_THRESHOLD * 100` (default 60) counts as a pass.

### Course Recommendations

After an interview session, the pipeline:

1. Identifies the weakest questions (below threshold) and their categories.
2. Uses `TfidfVectorizer` + pre-computed `tfidf_matrix.joblib` to retrieve semantically relevant courses from `course_catalog.csv`.
3. Applies `category_classifier.joblib` and `difficulty_classifier.joblib` (RandomForest) to re-rank results.
4. Returns the top-N courses with title, platform, provider, difficulty, and direct URL.

### Pre-trained Model Files

| File | Description |
|------|-------------|
| `category_classifier.joblib` | RandomForest predicting interview topic category |
| `difficulty_classifier.joblib` | RandomForest predicting question difficulty |
| `label_encoder_category.joblib` | Encodes/decodes category class labels |
| `label_encoder_difficulty.joblib` | Encodes/decodes difficulty class labels |
| `tfidf_vectorizer.joblib` | Fitted TF-IDF vectorizer for course text |
| `tfidf_matrix.joblib` | Pre-computed TF-IDF document matrix |
| `course_embeddings.npy` | SBERT embeddings for course descriptions |
| `courses_data.pkl` | Serialised course catalog DataFrame |
| `category_course_map.json` | Category ? recommended course list mapping |
| `model_metadata.json` | Training dataset and hyper-parameter metadata |
| `recommendation_metadata.json` | Recommendation pipeline configuration |

Training code and exploration notebooks are in `ai_voice_complete.ipynb`.

---

## Achievements System

Achievements are evaluated automatically after every interview session saved via `POST /profile/{user_id}/update-after-interview`.

| ID | Badge | Unlock Condition |
|----|-------|-----------------|
| `first_interview` | Getting Started | Complete your first interview |
| `ten_interviews` | Dedicated Learner | Complete 10 interviews |
| `fifty_interviews` | Master Learner | Complete 50 interviews |
| `perfect_score` | Perfect! | Achieve a 100% pass rate in a session |
| `five_day_streak` | On Fire! | Maintain a 5-day daily streak |

---

## Development

### Running Both Services Together

**Terminal 1 � Backend (with hot reload):**

```bash
cd backend
# Set RELOAD=true in .env, then:
python app.py
```

**Terminal 2 � Frontend:**

```bash
cd frontend
npm run dev
```

### Building the Frontend for Production

```bash
cd frontend
npm run build
# Output is in frontend/dist/
```

Serve `dist/` with any static file server or configure nginx/caddy to proxy `/api` to the FastAPI backend.

### Backend Production Deployment

```bash
cd backend
# Set RELOAD=false, WORKERS=4 (or 2*CPU+1) in .env
python app.py
# or directly:
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Troubleshooting

### `RuntimeError: Missing required environment variables: SECRET_KEY, DATABASE_URL`

The backend hard-fails at startup if either `SECRET_KEY` or `DATABASE_URL` is missing.

```bash
cd backend
cp .env.example .env
# Edit .env — set both SECRET_KEY and DATABASE_URL
python -c "import secrets; print(secrets.token_hex(32))"  # generate SECRET_KEY
```

### Sentence-Transformers model download on first run

The model `all-MiniLM-L6-v2` (~90 MB) is downloaded automatically on the first startup from the Hugging Face Hub. Ensure you have an internet connection. Subsequent starts use the local cache.

### CORS errors in the browser

Make sure `ALLOWED_ORIGINS` in `backend/.env` contains the exact origin your frontend is served from (e.g. `http://localhost:5173`). No trailing slash.

### Cannot connect to PostgreSQL

Verify that PostgreSQL is running and the database exists:

```bash
psql -U postgres -c "\l"                         # list databases
psql -U postgres -c "CREATE DATABASE smart_interviewer;"  # create if missing
psql "$DATABASE_URL" -c "\dt"                    # list tables (should show 3 after first start)
```

Check that `DATABASE_URL` in `backend/.env` uses the correct host, port, user, password, and database name.

### Port conflict

Change the backend port with `PORT=8001` in `.env`, then update the frontend env:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8001
```

---

## Team

| Name | Role |
|------|------|
| **Afyf Badreddine** | Scrum Master / Product Owner � backlog management, sprint supervision, JIRA |
| **Mohamed Ben Difi** | AI Developer � data preparation, model training and evaluation |
| **Ayman Chabbaki** | Full-Stack Developer � backend architecture, AI integration, frontend |
| **Hiba Dellaji** | Design / QA � UML design, UI mockups, functional testing, validation |

---

## License

This project is licensed under the MIT License.
