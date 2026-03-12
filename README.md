# 🎙️ AI Voice Interview Platform

<div align="center">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Tests](https://img.shields.io/badge/tests-200+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**An intelligent interview preparation platform powered by AI semantic scoring, personalized learning paths, and comprehensive progress tracking.**

[🚀 Quick Start](#-quick-start) • [✨ Features](#-key-features) • [🏗️ Architecture](#️-architecture) • [📚 Documentation](#-documentation) • [👥 Team](#-team)

</div>

---

## 📖 Table of Contents

- [What is AI Voice Interview?](#-what-is-ai-voice-interview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Architecture](#️-architecture)
- [API Documentation](#-api-documentation)
- [AI & ML Pipeline](#-ai--ml-pipeline)
- [Testing](#-testing)
- [Docker & CI/CD](#-docker--cicd)
- [Development Guide](#-development-guide)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Team](#-team)
- [License](#-license)

---

## 🎯 What is AI Voice Interview?

**AI Voice Interview Platform** is a comprehensive intelligent interview preparation system designed to help candidates practice and improve their technical interview skills. Unlike traditional practice platforms that rely on keyword matching, our platform uses advanced **semantic AI** to understand the meaning behind answers, providing more accurate and helpful feedback.

### 🎓 The Problem We Solve

Job candidates often struggle with:
- ❌ Limited access to realistic interview practice
- ❌ No feedback on answer quality or areas to improve
- ❌ Difficulty finding relevant learning resources for weak areas
- ❌ Lack of progress tracking and motivation

### 💡 Our Solution

Our platform provides:
- ✅ **AI-Powered Semantic Scoring** - Understands meaning, not just keywords
- ✅ **Personalized Course Recommendations** - Suggests learning resources for weak areas
- ✅ **Comprehensive Progress Tracking** - Monitor improvement over time
- ✅ **Achievement System** - Stay motivated with milestone badges
- ✅ **Multi-Category Support** - Practice across different technical domains

---

## ✨ Key Features

### 🤖 Intelligent AI Scoring
- **Semantic Understanding**: Uses Sentence-BERT (all-MiniLM-L6-v2) to evaluate answers based on meaning
- **Cosine Similarity Scoring**: Compares candidate answers with reference answers semantically
- **Configurable Thresholds**: Adjust passing scores based on difficulty levels
- **Real-time Feedback**: Instant scoring and detailed feedback after each answer

### 📊 Comprehensive Analytics
- **Performance Tracking**: Per-category performance breakdown
- **Interview History**: Complete record of all interview sessions
- **Streak System**: Track daily practice streaks for motivation
- **Statistical Insights**: Average scores, pass rates, and improvement trends

### 🎓 Personalized Learning
- **Smart Course Recommendations**: TF-IDF + ML classifiers suggest relevant courses
- **Weakness Analysis**: Identifies topics that need improvement
- **Multi-Platform Courses**: Recommendations from Udemy, Coursera, and more
- **Difficulty Matching**: Courses aligned with your experience level

### 🔒 Secure & Scalable
- **JWT Authentication**: Secure user authentication with Bearer tokens
- **Rate Limiting**: Protection against abuse (5 req/min register, 10 req/min login)
- **PostgreSQL Database**: Reliable data storage with connection pooling
- **Docker Ready**: Easy deployment with Docker Compose
- **Production Ready**: Comprehensive error handling and logging

### 🏆 Gamification
- **Achievement Badges**: Five milestone badges to unlock
- **Streak Tracking**: Maintain daily practice streaks
- **Progress Visualization**: See your improvement over time
- **Leaderboard Ready**: Infrastructure for competitive features

### 🧪 Thoroughly Tested
- **200+ Tests**: Comprehensive test coverage
- **Unit Tests**: 100 passing unit tests
- **Integration Tests**: Full API endpoint testing
- **CI/CD Pipeline**: Automated testing with Jenkins
- **Coverage Reports**: HTML coverage reports generated

---

## 🔄 How It Works

### 1️⃣ **User Registration & Profile**
```
Register → Create Profile → Set Experience Level → Define Interests
```
- Create account with secure password hashing (bcrypt)
- Set up profile with bio, experience level, and technical interests
- JWT tokens for secure authenticated sessions

### 2️⃣ **Start Interview Session**
```
Select Category → System Generates Questions → Interview Begins
```
- Choose from multiple technical categories (Python, JavaScript, System Design, etc.)
- System selects questions based on difficulty and category
- Questions sourced from comprehensive knowledge base (1000+ questions)

### 3️⃣ **Answer Questions & Get Scored**
```
Submit Answer → AI Semantic Analysis → Instant Score & Feedback
```
- AI compares your answer with reference answer using semantic similarity
- Score based on meaning, not exact word matching
- Detailed feedback explaining what was expected
- Real-time progress tracking within session

### 4️⃣ **View Results & Recommendations**
```
Session Complete → Performance Report → Personalized Course Suggestions
```
- Comprehensive results showing scores per question
- Identification of strong and weak areas
- ML-powered course recommendations for improvement
- Results saved to interview history

### 5️⃣ **Track Progress & Unlock Achievements**
```
Dashboard → Performance Analytics → Achievements → Streaks
```
- View all historical sessions and performance trends
- Per-category performance breakdown
- Unlock badges (First Interview, 10 Interviews, Perfect Score, etc.)
- Maintain daily streaks for consistency

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115.6 | Modern async web framework |
| **Python** | 3.11+ | Backend programming language |
| **PostgreSQL** | 15+ | Relational database |
| **psycopg2** | 2.9.9 | PostgreSQL adapter with connection pooling |
| **Sentence Transformers** | 2.7.0 | Semantic answer scoring (SBERT) |
| **PyTorch** | 2.2.0 | Deep learning framework |
| **scikit-learn** | 1.3.2 | ML classifiers and TF-IDF |
| **JWT (python-jose)** | 3.3.0 | Authentication tokens |
| **bcrypt/passlib** | 4.2.1/1.7.4 | Password hashing |
| **slowapi** | 0.1.9 | Rate limiting |
| **pytest** | 8.3.4 | Testing framework |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React** | 18.x - UI library |
| **Vite** | 5.x - Build tool & dev server |
| **lucide-react** | Icon library |
| **CSS3** | Styling |

### DevOps & Infrastructure
| Tool | Purpose |
|------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Jenkins** | CI/CD pipeline |
| **Git** | Version control |
| **pytest** | Automated testing |

### AI & ML Models
- **Sentence-BERT**: `all-MiniLM-L6-v2` (384-dim embeddings)
- **TF-IDF Vectorizer**: Course recommendation retrieval
- **Random Forest Classifiers**: Category & difficulty prediction
- **Cosine Similarity**: Answer scoring metric

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and npm
- **PostgreSQL 15+** (or use Docker)
- **Docker & Docker Compose** (recommended)
- ~2 GB disk space (for ML models)

### Option 1: Docker (Recommended) 🐳

**Fastest way to get started:**

```bash
# 1. Clone the repository
git clone <repository-url>
cd Ai_voice_interview

# 2. Copy and configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY:
#   SECRET_KEY=$(openssl rand -hex 32)

# 3. Start all services (backend + database)
docker-compose up -d

# 4. View logs
docker-compose logs -f backend

# 5. Access the application
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
```

**Alternative commands:**
```bash
# Using Makefile (if available)
make up          # Start services
make logs        # View logs
make test        # Run tests
make down        # Stop services

# View all available commands
make help
```

See **[DOCKER_SETUP.md](DOCKER_SETUP.md)** for detailed Docker documentation.

---

### Option 2: Manual Setup

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd Ai_voice_interview
```

#### Step 2: Setup Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set:
#   - SECRET_KEY (generate: python -c "import secrets; print(secrets.token_hex(32))")
#   - DATABASE_URL (format: postgresql://user:password@localhost:5432/dbname)

# 5. Create PostgreSQL database
# Option A: Using psql
psql -U postgres -c "CREATE DATABASE interview_db;"
psql -U postgres -c "CREATE USER interview_user WITH PASSWORD 'interview_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE interview_db TO interview_user;"

# Option B: Using Docker for database only
docker run -d \
  -e POSTGRES_USER=interview_user \
  -e POSTGRES_PASSWORD=interview_password \
  -e POSTGRES_DB=interview_db \
  -p 5432:5432 \
  --name postgres-interview \
  postgres:15-alpine

# 6. Start backend server
python app.py
# Server running at: http://localhost:8000
```

#### Step 3: Setup Frontend

Open a new terminal:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start development server
npm run dev
# App running at: http://localhost:5173
```

#### Step 4: Access Application

Open browser and navigate to: **http://localhost:5173**

---

## 📁 Project Structure

```
Ai_voice_interview/
│
├── backend/                         # FastAPI Backend
│   ├── app.py                       # Main application (routes, AI scoring)
│   ├── database.py                  # PostgreSQL connection & queries
│   ├── init_user.py                 # Database initialization script
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── Dockerfile                   # Docker image configuration
│   ├── .dockerignore               # Docker build exclusions
│   │
│   └── tests/                       # Test Suite (200+ tests)
│       ├── conftest.py              # Pytest fixtures & configuration
│       ├── pytest.ini               # Pytest settings
│       ├── test_auth.py             # Authentication tests (35+)
│       ├── test_database.py         # Database layer tests (40+)
│       ├── test_interview.py        # Interview flow tests (45+)
│       ├── test_profile.py          # Profile management tests (40+)
│       ├── test_general.py          # General endpoint tests (50+)
│       ├── .env.test                # Test environment config
│       ├── run_tests.ps1            # PowerShell test runner
│       ├── run_tests.py             # Python test runner
│       └── README.md                # Testing documentation
│
├── frontend/                        # React Frontend
│   ├── src/
│   │   ├── App.jsx                  # Main application component
│   │   ├── App.css                  # Global styles
│   │   ├── confetti.js              # Achievement celebration animation
│   │   ├── index.css                # Base CSS
│   │   └── main.jsx                 # React entry point
│   ├── public/                      # Static assets
│   ├── package.json                 # Node dependencies
│   ├── vite.config.js               # Vite configuration
│   └── eslint.config.js             # ESLint rules
│
├── models/                          # Pre-trained ML Models
│   ├── category_classifier.joblib       # RandomForest for category prediction
│   ├── difficulty_classifier.joblib     # RandomForest for difficulty prediction
│   ├── label_encoder_category.joblib    # Category label encoder
│   ├── label_encoder_difficulty.joblib  # Difficulty label encoder
│   ├── tfidf_vectorizer.joblib          # TF-IDF vectorizer
│   ├── tfidf_matrix.joblib              # Pre-computed TF-IDF matrix
│   ├── course_embeddings.npy            # SBERT course embeddings
│   ├── category_course_map.json         # Category-to-course mapping
│   ├── model_metadata.json              # Training metadata
│   └── recommendation_metadata.json     # Recommendation config
│
├── Dataset/                         # Training Data
│   ├── coding_interview_question_bank.csv
│   ├── Mock_interview_questions.json
│   ├── Software Questions.csv
│   └── udemy_courses.csv
│
├── docs/                           # Additional Documentation
│   ├── API.md                      # Detailed API reference
│   └── USER_GUIDE.md               # User guide
│
├── final_knowledge_base.csv        # Interview questions (runtime)
├── course_catalog.csv              # Course catalog (runtime)
├── ai_voice_complete.ipynb         # ML training notebook
│
├── docker-compose.yml              # Docker Compose orchestration
├── Dockerfile                      # Backend Docker configuration
├── .dockerignore                   # Docker exclusions
├── Jenkinsfile                     # CI/CD pipeline configuration
├── Makefile                        # Quick commands
│
├── .env.example                    # Root environment template
├── .gitignore                      # Git exclusions
│
├── DOCKER_SETUP.md                 # Docker documentation
├── JENKINS_SETUP.md                # Jenkins CI/CD guide
├── JENKINS_QUICKSTART.md           # Quick Jenkins setup
├── DATABASE_SETUP.md               # Database configuration guide
├── TESTING_QUICKSTART.md           # Testing quick start
├── TEST_SUMMARY.md                 # Test suite summary
│
├── Names_Role.md                   # Team roles
└── README.md                       # This file
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser / Client                          │
│                     (React 18 + Vite)                        │
│  Home • Dashboard • Interview • Profile • Authentication     │
│                      Port: 5173                              │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Server                      │
│                      (Python 3.11)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Layer                                             │ │
│  │  • JWT Authentication (python-jose)                    │ │
│  │  • Rate Limiting (slowapi)                             │ │
│  │  • Request Validation (Pydantic v2)                    │ │
│  │  • CORS Middleware                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────────┐ │
│  │  Business Logic        │                                │ │
│  │  ┌─────────────────────▼──────────────────┐            │ │
│  │  │   AI Scoring Engine                    │            │ │
│  │  │   • Sentence-BERT (all-MiniLM-L6-v2)   │            │ │
│  │  │   • Semantic Similarity (Cosine)       │            │ │
│  │  │   • Real-time Answer Evaluation        │            │ │
│  │  └────────────────────────────────────────┘            │ │
│  │                      │                                  │ │
│  │  ┌───────────────────▼───────────────────┐             │ │
│  │  │   Course Recommendation Engine        │             │ │
│  │  │   • TF-IDF Retrieval                  │             │ │
│  │  │   • RandomForest Classifiers          │             │ │
│  │  │   • Category & Difficulty Prediction  │             │ │
│  │  └───────────────────────────────────────┘             │ │
│  │                      │                                  │ │
│  │  ┌───────────────────▼───────────────────┐             │ │
│  │  │   Achievement System                  │             │ │
│  │  │   • Badge Logic                       │             │ │
│  │  │   • Streak Tracking                   │             │ │
│  │  │   • Statistics Calculator             │             │ │
│  │  └───────────────────────────────────────┘             │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────────┐ │
│  │  Data Access Layer (database.py)                       │ │
│  │  • Connection Pooling (psycopg2.pool)                  │ │
│  │  • CRUD Operations                                     │ │
│  │  • Transaction Management                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                      Port: 8000                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                         │
│                      (Version 15+)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Tables:                                               │ │
│  │  • users             (authentication & profiles)       │ │
│  │  • user_stats        (achievements & streaks)          │ │
│  │  • interview_history (session records)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                      Port: 5432                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Request** → FastAPI receives HTTP request
2. **Authentication** → JWT token validated (if protected route)
3. **Rate Limiting** → Request checked against limits
4. **Validation** → Pydantic validates request data
5. **Business Logic** → AI scoring or recommendation processing
6. **Database** → CRUD operations via connection pool
7. **Response** → JSON response sent back to client

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API metadata & welcome message |
| `GET` | `/health` | Health check (uptime, database status) |
| `GET` | `/categories` | List all interview categories |
| `GET` | `/statistics` | Question count statistics per category |

### Authentication Endpoints

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| `POST` | `/register` | 5/min | Create new user account |
| `POST` | `/login` | 10/min | Authenticate and get JWT token |

**Register Example:**
```json
POST /register
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "bio": "Software Engineer",
  "experience_level": "Intermediate",
  "interests": ["Python", "Machine Learning"]
}

Response:
{
  "message": "User created successfully",
  "user_id": "uuid-here",
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

**Login Example:**
```json
POST /login
{
  "username": "johndoe",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "jwt-token-here",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "username": "johndoe",
  "user": { /* full user object */ }
}
```

### Interview Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/interview/start` | Optional | Start new interview session |
| `POST` | `/interview/answer` | No | Submit answer & get score |
| `GET` | `/interview/results/{session_id}` | No | Get full session results |
| `GET` | `/interview/sessions` | No | List active sessions |
| `DELETE` | `/interview/{session_id}` | No | Delete session |

**Start Interview:**
```json
POST /interview/start
{
  "category": "Python Programming",
  "user_id": "optional-user-id-here",
  "num_questions": 3
}

Response:
{
  "session_id": "session_20260312_120000_abcd",
  "topic": "Python Programming",
  "total_questions": 3,
  "current_question": {
    "index": 0,
    "question": "What is the difference between a list and a tuple?",
    "category": "Python Programming",
    "difficulty": "Easy"
  },
  "threshold": 60.0
}
```

**Submit Answer:**
```json
POST /interview/answer
{
  "session_id": "session_20260312_120000_abcd",
  "answer": "A list is mutable and uses square brackets, while a tuple is immutable and uses parentheses."
}

Response:
{
  "score": 87.5,
  "passed": true,
  "feedback": "Excellent answer!",
  "expected_answer": "Lists are mutable...",
  "similarity_score": 0.875,
  "next_question": { /* next question object */ },
  "session_complete": false,
  "progress": {
    "answered": 1,
    "total": 3,
    "passed": 1
  }
}
```

### Profile Endpoints (JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/me` | Get current user info |
| `GET` | `/profile/{user_id}` | Get user profile |
| `PUT` | `/profile/{user_id}` | Update profile |
| `GET` | `/profile/{user_id}/stats` | Get statistics |
| `GET` | `/profile/{user_id}/history` | Get interview history |
| `GET` | `/profile/{user_id}/analytics` | Per-category analytics |
| `POST` | `/profile/{user_id}/update-after-interview` | Save results & update stats |

**Authentication Header:**
```
Authorization: Bearer <jwt-token>
```

See **[docs/API.md](docs/API.md)** for complete API documentation.

---

## 🤖 AI & ML Pipeline

### 1. Semantic Answer Scoring

**Technology**: Sentence-BERT (all-MiniLM-L6-v2)

**How it works:**

1. **Model Loading** (on startup):
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer("all-MiniLM-L6-v2")
   ```

2. **Reference Answer Encoding** (cached):
   - All reference answers from `final_knowledge_base.csv` are encoded once
   - 384-dimensional embeddings stored in memory
   - Fast lookup during interview sessions

3. **Candidate Answer Evaluation**:
   ```python
   # Encode candidate answer
   candidate_embedding = model.encode(user_answer)
   
   # Compute cosine similarity
   similarity = cosine_similarity(candidate_embedding, reference_embedding)
   
   # Convert to percentage score
   score = similarity * 100
   
   # Determine pass/fail
   passed = score >= SIMILARITY_THRESHOLD  # default: 60%
   ```

4. **Benefits**:
   - ✅ Understands semantic meaning, not just keywords
   - ✅ Handles paraphrasing and different explanations
   - ✅ More accurate than keyword matching
   - ✅ Works with natural language variations

**Example:**
```
Reference: "A list is mutable and uses square brackets []"
Candidate: "Lists can be modified after creation and are written with []"
Traditional Match: 30% (few common words)
Semantic Match: 92% (same meaning) ✓
```

### 2. Course Recommendation Engine

**Multi-stage pipeline**:

#### Stage 1: Weakness Identification
```python
# Identify failed questions
weak_topics = [q for q in session if q['score'] < threshold]

# Extract categories
weak_categories = set(q['category'] for q in weak_topics)
```

#### Stage 2: TF-IDF Retrieval
```python
# Create query from weak categories
query = " ".join(weak_categories)

# Compute TF-IDF similarity
query_vector = tfidf_vectorizer.transform([query])
similarities = cosine_similarity(query_vector, tfidf_matrix)

# Get top-N courses
top_courses = courses.iloc[similarities.argsort()[0][-N:]]
```

#### Stage 3: ML Classification
```python
# Predict category for each course
predicted_categories = category_classifier.predict(course_features)

# Predict difficulty level
predicted_difficulty = difficulty_classifier.predict(course_features)

# Filter by relevance
filtered_courses = courses[
    (courses['category'].isin(weak_categories)) &
    (courses['difficulty'] == user_level)
]
```

#### Stage 4: Ranking & Presentation
```python
# Rank by multiple factors
scores = (
    0.4 * tfidf_similarity +
    0.3 * category_match +
    0.2 * difficulty_match +
    0.1 * platform_rating
)

# Return top recommendations
top_recommendations = courses.nlargest(5, 'score')
```

### 3. Pre-trained Models

| Model | Type | Purpose | Accuracy |
|-------|------|---------|----------|
| `category_classifier.joblib` | Random Forest | Predict topic category | ~85% |
| `difficulty_classifier.joblib` | Random Forest | Predict difficulty level | ~82% |
| `tfidf_vectorizer.joblib` | TF-IDF | Text feature extraction | N/A |
| `label_encoder_*.joblib` | Label Encoder | Encode/decode labels | N/A |

**Training Details** (see `ai_voice_complete.ipynb`):
- Training data: 5000+ interview questions
- Course catalog: 2000+ courses from Udemy, Coursera
- Features: Question text, category, difficulty, keywords
- Cross-validation: 5-fold CV
- Optimization: GridSearchCV for hyperparameters

---

## 🧪 Testing

### Test Suite Overview

Our platform includes a comprehensive test suite with **200+ tests** ensuring reliability and quality.

#### Test Structure
```
backend/tests/
├── conftest.py              # Shared fixtures & configuration
├── pytest.ini               # Pytest settings
├── test_auth.py            # 35+ authentication tests
├── test_database.py        # 40+ database layer tests
├── test_interview.py       # 45+ interview flow tests
├── test_profile.py         # 40+ profile management tests
├── test_general.py         # 50+ general endpoint tests
├── .env.test               # Test environment
└── README.md               # Testing documentation
```

### Test Coverage

| Category | Tests | Description |
|----------|-------|-------------|
| **Authentication** | 35+ | Registration, login, JWT tokens, rate limiting |
| **Database** | 40+ | User CRUD, stats, history, transactions |
| **Interview Flow** | 45+ | Start, answer submission, scoring, results |
| **Profile Management** | 40+ | Profile CRUD, analytics, achievements |
| **General Endpoints** | 50+ | Health, categories, CORS, error handling |
| **Total** | **200+** | Comprehensive coverage |

### Running Tests

#### Quick Test (Unit Tests Only)
```bash
cd backend

# Activate environment
conda activate temp  # or: source venv/bin/activate

# Run unit tests (no database required)
pytest -m unit -v

# With coverage report
pytest -m unit --cov=. --cov-report=html

# Open coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

#### Full Test Suite
```bash
# Requires PostgreSQL test database
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::TestLogin::test_login_success -v
```

#### Using Test Runners
```bash
# PowerShell
.\run_tests.ps1

# Python script
python run_tests.py

# Makefile (if using Docker)
make test
```

### Test Results Summary

```
✅ 100 passing   - Unit tests (mocked dependencies)
⏭️  102 skipped  - Integration tests (require database)
❌ 0 failing     - All tests pass!

Total Coverage: ~85%
```

### CI/CD Testing

Tests run automatically in Jenkins pipeline:
1. Unit tests on every commit
2. Integration tests on pull requests
3. Full test suite before deployment
4. Coverage reports published

See **[TESTING_QUICKSTART.md](backend/tests/TESTING_QUICKSTART.md)** for detailed testing guide.

---

## 🐳 Docker & CI/CD

### Docker Setup

#### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Run tests in container
docker-compose exec backend pytest -v
```

#### Docker Architecture

```
┌─────────────────────────────────────────────┐
│  docker-compose.yml                         │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Backend API    │  │  PostgreSQL     │  │
│  │  Port: 8000     │◄─┤  Port: 5432     │  │
│  │  (FastAPI)      │  │  Volume: pgdata │  │
│  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────┘
```

### Jenkins CI/CD Pipeline

**10-Stage Automated Pipeline:**

1. **Checkout** - Clone repository
2. **Setup Python** - Create virtual environment
3. **Lint & Code Quality** - flake8, black
4. **Run Tests** - pytest with coverage (200+ tests)
5. **Security Scan** - safety check for vulnerabilities
6. **Build Docker Image** - Multi-stage build
7. **Test Docker Image** - Container health check
8. **Push Image** - To registry (main branch only)
9. **Deploy Staging** - Automatic (develop branch)
10. **Deploy Production** - Manual approval (main branch)

#### Pipeline Configuration

```groovy
// Jenkinsfile
pipeline {
    environment {
        DOCKER_IMAGE = 'ai-voice-interview-backend'
        DATABASE_URL = credentials('test-database-url')
        SECRET_KEY = credentials('test-secret-key')
    }
    
    stages {
        stage('Test') {
            steps {
                sh 'pytest -v --cov --junit-xml=results.xml'
            }
        }
        // ... more stages
    }
}
```

#### Jenkins Credentials Setup

Required credentials in Jenkins:
- `test-database-url` (Secret text)
- `test-secret-key` (Secret text)  
- `docker-credentials` (Username/Password)

**Quick Setup Guide**: See **[JENKINS_QUICKSTART.md](JEN KINS_QUICKSTART.md)**

### Documentation

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Complete Docker guide
- **[DOCKER_SETUP.md#jenkins-cicd-pipeline](DOCKER_SETUP.md#-jenkins-cicd-pipeline)** - Jenkins pipeline details
- **[JENKINS_SETUP.md](JENKINS_SETUP.md)** - Full Jenkins configuration
- **[JENKINS_QUICKSTART.md](JENKINS_QUICKSTART.md)** - 5-minute Jenkins setup
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Database configuration guide

---

## 💻 Development Guide

### Local Development Setup

#### 1. Backend Development

```bash
cd backend

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Enable hot reload in .env
RELOAD=true

# Start server
python app.py
```

#### 2. Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Lint code
npm run lint

# Build for production
npm run build
```

### Code Style

#### Backend (Python)
- Follow PEP 8 guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use black for formatting: `black .`
- Use flake8 for linting: `flake8 .`

#### Frontend (JavaScript/React)
- Use ESLint configuration
- Functional components with hooks
- PropTypes for type checking
- Consistent naming conventions

### Database Migrations

```bash
# Current setup: Auto-migration on startup
# Tables created automatically via init_db()

# Manual database operations
python -c "from database import init_db; init_db()"
```

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Write tests first** (TDD approach)
3. **Implement feature**
4. **Run tests**: `pytest -v`
5. **Check coverage**: `pytest --cov`
6. **Lint code**: `flake8 .` and `black .`
7. **Commit changes**: `git commit -m "feat: description"`
8. **Push and create PR**: `git push origin feature/my-feature`

### Debugging

#### Backend Debugging

```python
# Add logging
import logging
logger = logging.getLogger("smart_interviewer")
logger.debug("Debug message")

# Set log level in .env
LOG_LEVEL=debug

# Interactive debugging
import pdb; pdb.set_trace()
```

#### Frontend Debugging

```javascript
// Browser DevTools
console.log('Debug info:', data)

// React DevTools extension
// Network tab for API calls
```

---

## ⚙️ Environment Variables

### Backend Configuration

**Location**: `backend/.env`

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing secret (32+ chars) | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/interview_db` |

#### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `WORKERS` | `1` | Number of workers (production: 4+) |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warning/error) |
| `RELOAD` | `false` | Hot reload (true for development only) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT expiry (7 days = 10080 minutes) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated) |
| `SIMILARITY_THRESHOLD` | `0.6` | Minimum score to pass (0.0-1.0) |
| `NUM_QUESTIONS` | `3` | Questions per interview |
| `KB_FILE` | `../final_knowledge_base.csv` | Interview questions file |
| `COURSES_FILE` | `../course_catalog.csv` | Course catalog file |
| `DB_POOL_SIZE` | `10` | PostgreSQL connection pool size |

### Frontend Configuration

**Location**: `frontend/.env` (optional)

```env
VITE_API_URL=http://localhost:8000
```

### Docker Environment

**Location**: `.env` (root directory)

```env
# Database
POSTGRES_USER=interview_user
POSTGRES_PASSWORD=interview_password
POSTGRES_DB=interview_db

# Backend (@ db for Docker, @localhost for local)
DATABASE_URL=postgresql://interview_user:interview_password@db:5432/interview_db
SECRET_KEY=your-secret-key-here

# Application
SIMILARITY_THRESHOLD=0.6
NUM_QUESTIONS=3
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. "Missing required environment variables: SECRET_KEY, DATABASE_URL"

**Cause**: `.env` file not configured

**Solution**:
```bash
cd backend
cp .env.example .env
# Edit .env and set SECRET_KEY and DATABASE_URL
```

#### 2. "Connection to database failed"

**Cause**: PostgreSQL not running or wrong credentials

**Solution**:
```bash
# Check if PostgreSQL is running
# Windows:
Get-Service postgresql*

# macOS:
brew services list

# Linux:
sudo systemctl status postgresql

# Test connection
psql -U interview_user -d interview_db -h localhost

# If database doesn't exist, create it
psql -U postgres -c "CREATE DATABASE interview_db;"
```

#### 3. "ModuleNotFoundError: No module named 'X'"

**Cause**: Dependencies not installed

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

#### 4. "CORS policy error" in browser

**Cause**: Frontend origin not in ALLOWED_ORIGINS

**Solution**:
```bash
# In backend/.env, add frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
# No trailing slash!
```

#### 5. "Port 8000 already in use"

**Cause**: Another process using port 8000

**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or change port in .env
PORT=8001
```

#### 6. "Sentence-Transformers model download fails"

**Cause**: No internet connection or Hugging Face Hub down

**Solution**:
```bash
# Manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Or use offline mode (if model already cached)
export TRANSFORMERS_OFFLINE=1
```

#### 7. "Tests failing: Test database not available"

**Cause**: No test database configured

**Solution**:
```bash
# Run unit tests only (no database needed)
pytest -m unit -v

# Or create test database
psql -U postgres -c "CREATE DATABASE test_interview_db;"
```

#### 8. "Docker container won't start"

**Cause**: Various Docker issues

**Solution**:
```bash
# Check logs
docker-compose logs backend
docker-compose logs db

# Rebuild images
docker-compose build --no-cache

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Getting Help

- **Check Logs**: Always check logs first
  ```bash
  # Backend logs
  tail -f backend/logs/*.log
  
  # Docker logs
  docker-compose logs -f
  ```

- **Enable Debug Mode**:
  ```bash
  # In backend/.env
  LOG_LEVEL=debug
  ```

- **Documentation**: See detailed guides in [Documentation](#-documentation)

---

## 📚 Documentation

### Complete Documentation Set

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | Main documentation (this file) |
| **[DOCKER_SETUP.md](DOCKER_SETUP.md)** | Docker & deployment guide |
| **[JENKINS_SETUP.md](JENKINS_SETUP.md)** | Complete Jenkins CI/CD configuration|
| **[JENKINS_QUICKSTART.md](JENKINS_QUICKSTART.md)** | 5-minute Jenkins setup |
| **[DATABASE_SETUP.md](DATABASE_SETUP.md)** | PostgreSQL configuration guide |
| **[TESTING_QUICKSTART.md](backend/tests/TESTING_QUICKSTART.md)** | Testing quick start |
| **[TEST_SUMMARY.md](TEST_SUMMARY.md)** | Test suite overview |
| **[backend/tests/README.md](backend/tests/README.md)** | Detailed testing documentation |
| **[docs/API.md](docs/API.md)** | Complete API reference |
| **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** | End-user guide |
| **[Names_Role.md](Names_Role.md)** | Team roles & responsibilities |

### Quick Links

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)
- **Coverage Reports**: `backend/htmlcov/index.html`

---

## 👥 Team

###  Project Team

| Name | Role | Responsibilities |
|------|------|------------------|
| **Afyf Badreddine** | Scrum Master / Product Owner | Sprint planning, backlog management, stakeholder communication, JIRA administration |
| **Mohamed Ben Difi** | AI/ML Developer | Data preparation, model training, evaluation, recommendation engine |
| **Ayman Chabbaki** | Full-Stack Developer | Backend architecture, FastAPI implementation, AI integration, React frontend |
| **Hiba Dellaji** | UX/UI Designer & QA | UML design, interface mockups, usability testing, quality assurance, test validation |

### Contributions

- **Backend**: FastAPI server, database design, JWT authentication, rate limiting
- **Frontend**: React application, responsive UI, interview flow, progress tracking
- **AI/ML**: Sentence-BERT integration, TF-IDF course recommendations, classifiers
- **Testing**: 200+ tests, CI/CD pipeline, Docker configuration
- **DevOps**: Docker Compose, Jenkinsfile, deployment guides
- **Documentation**: Comprehensive docs, API reference, setup guides

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 AI Voice Interview Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🚀 Getting Started Checklist

Ready to start? Follow this checklist:

- [ ] Clone the repository
- [ ] Install Python 3.11+ and Node.js 18+
- [ ] Install PostgreSQL 15+ (or use Docker)
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Set DATABASE_URL in `.env`
- [ ] Install backend dependencies: `pip install -r requirements.txt`
- [ ] Install frontend dependencies: `npm install`
- [ ] Create database: `CREATE DATABASE interview_db;`
- [ ] Start backend: `python app.py`
- [ ] Start frontend: `npm run dev`
- [ ] Open browser: http://localhost:5173
- [ ] Register account and start interviewing! 🎉

**Or use Docker (even easier)**:
```bash
docker-compose up -d
```

---

## 🌟 Project Highlights

- ✅ **Production-Ready**: Comprehensive error handling, logging, security
- ✅ **Well-Tested**: 200+ tests with good coverage
- ✅ **Well-Documented**: Extensive documentation for all components
- ✅ **Docker-Ready**: Easy deployment with Docker Compose
- ✅ **CI/CD Pipeline**: Automated testing and deployment
- ✅ **Scalable Architecture**: Connection pooling, rate limiting, async operations
- ✅ **Modern Stack**: FastAPI, React 18, PostgreSQL, Docker
- ✅ **AI-Powered**: Semantic scoring with Sentence-BERT
- ✅ **User-Friendly**: Clean UI, progress tracking, achievements

---

<div align="center">

**Made with ❤️ by the AI Voice Interview Team**

[⬆ Back to Top](#️-ai-voice-interview-platform)

</div>
