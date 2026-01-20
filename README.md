# Smart Voice Interviewer 🎯

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**AI-Powered Interview Practice Platform with Voice Recognition**

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [API Reference](#api-reference)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

Smart Voice Interviewer is an advanced AI-powered interview preparation platform that helps candidates practice and improve their interview skills through intelligent mock interviews. The system uses Sentence-BERT for semantic answer evaluation, speech recognition for voice input, and provides real-time feedback with comprehensive analytics.

### Key Highlights

- **AI-Powered Evaluation**: Uses Sentence-BERT (all-MiniLM-L6-v2) for semantic similarity scoring
- **Voice Interaction**: Speech recognition and text-to-speech capabilities
- **Real-Time Feedback**: Instant scoring and detailed explanations
- **Progress Tracking**: Comprehensive analytics, achievements, and streak tracking
- **Multi-Category Support**: Practice across various technical domains
- **Modern UI**: Professional design with smooth animations and responsive layout

---

## ✨ Features

### Core Functionality

#### 🎤 Voice-Enabled Interviews
- **Speech Recognition**: Real-time voice input using Web Speech API
- **Text-to-Speech**: Questions are read aloud automatically
- **Manual Override**: Option to type answers or use voice input
- **Multi-Language Support**: Configurable language settings

#### 🤖 AI-Powered Evaluation
- **Semantic Similarity**: Sentence-BERT model evaluates answer quality
- **Intelligent Scoring**: 0-100 score based on semantic understanding
- **Detailed Feedback**: Explanations for each score
- **Expected Answers**: Shows ideal responses for learning

#### 📊 Progress Tracking
- **Interview History**: Complete record of all practice sessions
- **Performance Analytics**: Track improvement over time
- **Streak Tracking**: Daily practice streak monitoring
- **Category-wise Stats**: Performance breakdown by topic

#### 🏆 Gamification
- **Achievement System**: Unlock badges for milestones
  - First Interview
  - Perfect Score
  - Practice Marathon
  - Week Warrior
  - Perfect Streak
  - Interview Master
  - Speed Demon
  - Knowledge Seeker
- **Leaderboards**: Compare with other users (coming soon)
- **XP System**: Earn experience points (coming soon)

#### 📈 Dashboard & Analytics
- **Personal Dashboard**: Overview of stats and recent activity
- **KPI Cards**: Total interviews, pass rate, streak, achievements
- **Recent Activity**: Latest interview sessions with scores
- **Quick Actions**: Fast access to common tasks

#### 🏠 Landing Pages
- **Public Home Page**: Hero section, features showcase, how-it-works
- **Authenticated Home**: Personalized stats and quick access
- **Stats Showcase**: Platform achievements and user count

### User Management

#### 👤 Authentication & Profile
- **User Registration**: Create account with profile details
- **Secure Login**: JWT-based authentication
- **Profile Management**: Update bio, experience level, interests
- **Avatar System**: Auto-generated profile avatars

#### 🔒 Security Features
- **Password Hashing**: Secure password storage
- **JWT Tokens**: Stateless authentication
- **Token Expiry**: Automatic session management
- **CORS Protection**: Secure cross-origin requests

---

## 🏗 Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Home Page   │  │  Dashboard   │  │  Interview   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Achievements │  │   History    │  │   Profile    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                    REST API (FastAPI)
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Backend Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Auth Service │  │ Interview    │  │  Analytics   │     │
│  │              │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                            │                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ User Manager │  │  Question    │  │ Achievement  │     │
│  │              │  │   Manager    │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                   AI/ML Layer (PyTorch)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Sentence-    │  │  Embedding   │  │  Similarity  │     │
│  │   BERT       │  │  Generator   │  │  Calculator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer (SQLite)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Users     │  │ Interview    │  │ Achievements │     │
│  │              │  │   History    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Flow

```
User Interaction → Frontend → API Request → Backend Processing
                                              ↓
                                    AI Model Evaluation
                                              ↓
                                    Database Update
                                              ↓
                                    Response with Score
                                              ↓
Frontend Update ← API Response ←──────────────┘
```

---

## 💻 Technology Stack

### Frontend
- **React 18.3**: Modern UI library with hooks
- **Vite 5.4**: Fast build tool and dev server
- **Lucide React**: Beautiful icon library
- **Web Speech API**: Browser-based speech recognition
- **CSS3**: Custom animations and modern styling

### Backend
- **FastAPI**: High-performance async web framework
- **Python 3.8+**: Core programming language
- **Uvicorn**: ASGI server for production
- **Sentence-Transformers**: NLP model for semantic similarity
- **PyTorch**: Deep learning framework
- **JWT**: JSON Web Token authentication

### Database
- **SQLite**: Lightweight embedded database
- **SQLAlchemy**: ORM for database operations (optional)

### AI/ML
- **Sentence-BERT**: `all-MiniLM-L6-v2` model
- **Transformers**: Hugging Face library
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing utilities

### DevOps
- **Git**: Version control
- **npm/pip**: Package management
- **Postman**: API testing

---

## 📦 Installation

### Prerequisites

- **Node.js**: v16.0 or higher
- **Python**: 3.8 or higher
- **pip**: Latest version
- **Git**: For cloning the repository

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/smart-voice-interviewer.git
cd smart-voice-interviewer
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### 2.2 Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
sentence-transformers==2.2.2
torch==2.1.0
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
```

#### 2.4 Initialize Database

The database will be created automatically on first run. To manually initialize:

```bash
python database.py
```

#### 2.5 Start Backend Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

### Step 3: Frontend Setup

#### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

**Key dependencies:**
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "lucide-react": "^0.263.1",
  "vite": "^5.4.2"
}
```

#### 3.2 Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Step 4: Load Question Dataset

Place your question datasets in the `Dataset/` folder:

- `coding_interview_question_bank.csv`
- `Mock_interview_questions.json`
- `Software Questions.csv`

Format examples in [Database Schema](#database-schema) section.

---

## ⚙️ Configuration

### Backend Configuration

**app.py:**
```python
# API Configuration
API_BASE_URL = "http://localhost:8000"
CORS_ORIGINS = ["http://localhost:5173"]

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Model Configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.6  # 60% similarity for passing
```

### Frontend Configuration

**App.jsx:**
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Environment Variables (Production)

Create `.env` file:

```env
# Backend
SECRET_KEY=your-production-secret-key
DATABASE_URL=sqlite:///./interview_system.db
CORS_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

---

## 🚀 Usage

### For Users

#### 1. Registration
1. Navigate to the home page
2. Click "Get Started Free" or "Login" button
3. Switch to "Register" tab
4. Fill in:
   - Username (required)
   - Email (required)
   - Password (min 6 characters)
   - Full Name (required)
   - Bio (optional)
   - Experience Level (Beginner/Intermediate/Advanced/Expert)
5. Click "Register"

#### 2. Starting an Interview
1. Login to your account
2. Navigate to Dashboard or click "Start Interview"
3. Select interview category (e.g., Python, JavaScript, Data Structures)
4. Choose number of questions (1-20)
5. Enable/disable voice input
6. Click "Start Interview"

#### 3. Answering Questions
1. Read or listen to the question
2. Click microphone icon to use voice input (or type manually)
3. Speak your answer clearly
4. Click "Submit Answer"
5. View instant feedback and score
6. Click "Next Question" to continue

#### 4. Reviewing Results
1. Complete all questions in the session
2. View comprehensive results:
   - Total score and pass/fail status
   - Individual question scores
   - Correct answers for learning
3. Celebrate achievements unlocked! 🎉
4. Click "Back to Dashboard" to view history

#### 5. Tracking Progress
- **Dashboard**: View KPIs (interviews, pass rate, streak)
- **History**: Click history icon to see all sessions
- **Achievements**: Click trophy icon to view unlocked badges
- **Profile**: Update your information and preferences

### For Developers

#### Running Tests

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

#### Building for Production

**Frontend:**
```bash
npm run build
```

Output in `frontend/dist/`

**Backend:**
```bash
# Use production WSGI server
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📚 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### Register User
```http
POST /register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "name": "John Doe",
  "bio": "Software Engineer",
  "experience_level": "Intermediate"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

#### Login
```http
POST /login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": { /* user object */ }
}
```

### Interview Endpoints

#### Get Categories
```http
GET /categories
Authorization: Bearer {token}

Response 200:
[
  "Python",
  "JavaScript",
  "Data Structures",
  "Algorithms",
  "System Design"
]
```

#### Start Interview
```http
POST /interview/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "category": "Python",
  "num_questions": 5,
  "user_id": 1
}

Response 200:
{
  "session_id": "uuid-here",
  "questions": [
    {
      "id": 1,
      "question": "What is a list comprehension in Python?",
      "category": "Python",
      "difficulty": "Medium",
      "expected_answer": "..."
    }
  ],
  "total_questions": 5
}
```

#### Submit Answer
```http
POST /interview/answer
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_id": "uuid-here",
  "question_id": 1,
  "user_answer": "A list comprehension is a concise way...",
  "user_id": 1
}

Response 200:
{
  "score": 85.5,
  "feedback": "Excellent explanation!",
  "is_correct": true,
  "expected_answer": "...",
  "similarity": 0.855
}
```

#### End Interview
```http
POST /interview/end
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_id": "uuid-here",
  "user_id": 1
}

Response 200:
{
  "total_score": 82.3,
  "passed": true,
  "questions_answered": 5,
  "achievements": [
    {
      "title": "First Interview",
      "description": "Completed your first interview"
    }
  ]
}
```

### User Profile Endpoints

#### Get User Profile
```http
GET /profile/{user_id}
Authorization: Bearer {token}

Response 200:
{
  "user_id": 1,
  "username": "johndoe",
  "name": "John Doe",
  "email": "john@example.com",
  "bio": "Software Engineer",
  "experience_level": "Intermediate",
  "interview_count": 15,
  "total_score": 1247.5,
  "current_streak": 7,
  "achievements": [...]
}
```

#### Update Profile
```http
PUT /profile/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John Smith",
  "bio": "Senior Developer",
  "experience_level": "Advanced"
}

Response 200:
{
  "message": "Profile updated successfully",
  "user": { /* updated user */ }
}
```

#### Get Interview History
```http
GET /profile/{user_id}/history
Authorization: Bearer {token}

Response 200:
[
  {
    "session_id": "uuid",
    "date": "2026-01-20T10:30:00",
    "topic": "Python",
    "questions_count": 5,
    "pass_rate": 85.5,
    "passed": true,
    "time_spent": 450
  }
]
```

### Health Check

#### Check API Status
```http
GET /health

Response 200:
{
  "status": "healthy",
  "timestamp": "2026-01-20T10:30:00",
  "version": "1.0.0",
  "model_loaded": true
}
```

---

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    bio TEXT,
    experience_level TEXT DEFAULT 'Beginner',
    interests TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interview_count INTEGER DEFAULT 0,
    total_score REAL DEFAULT 0.0,
    current_streak INTEGER DEFAULT 0,
    last_interview_date DATE
);
```

### Interview History Table
```sql
CREATE TABLE interview_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic TEXT NOT NULL,
    questions_count INTEGER NOT NULL,
    pass_rate REAL NOT NULL,
    passed BOOLEAN NOT NULL,
    time_spent INTEGER,  -- seconds
    questions TEXT,  -- JSON array
    answers TEXT,  -- JSON array
    scores TEXT,  -- JSON array
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Achievements Table
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Question Bank Format

**CSV Format (coding_interview_question_bank.csv):**
```csv
Category,Question,Expected_Answer,Difficulty
Python,What is a decorator?,A decorator is a function that modifies...,Medium
JavaScript,Explain closures,A closure is a function that has access...,Hard
```

**JSON Format (Mock_interview_questions.json):**
```json
[
  {
    "id": 1,
    "category": "Data Structures",
    "question": "What is the time complexity of searching in a balanced BST?",
    "expected_answer": "O(log n) because...",
    "difficulty": "Medium"
  }
]
```

---

## 🛠 Development Guide

### Project Structure

```
smart-voice-interviewer/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── database.py            # Database operations
│   ├── models.py              # Data models (optional)
│   ├── requirements.txt       # Python dependencies
│   └── interview_system.db    # SQLite database
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── App.css           # Styles
│   │   ├── main.jsx          # Entry point
│   │   └── confetti.js       # Celebration effects
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── Dataset/
│   ├── coding_interview_question_bank.csv
│   ├── Mock_interview_questions.json
│   └── Software Questions.csv
├── ai_voice_complete.ipynb   # Development notebook
└── README.md                 # This file
```

### Code Style

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where applicable
- Document functions with docstrings

```python
def calculate_similarity(answer1: str, answer2: str) -> float:
    """
    Calculate semantic similarity between two answers.
    
    Args:
        answer1: First answer text
        answer2: Second answer text
        
    Returns:
        Similarity score between 0 and 1
    """
    # Implementation...
```

#### JavaScript (Frontend)
- Use ES6+ features
- Functional components with hooks
- Descriptive variable names

```javascript
const handleSubmitAnswer = async () => {
  // Implementation...
};
```

### Adding New Features

#### 1. New Question Category

**Backend (app.py):**
```python
# Add to categories endpoint
CATEGORIES = [
    "Python", "JavaScript", "Java",
    "Your New Category"  # Add here
]
```

**Dataset:**
Create CSV or JSON with questions for the new category.

#### 2. New Achievement

**Backend (database.py):**
```python
def check_achievements(user_id, interview_data):
    # Add new achievement logic
    if condition_met:
        add_achievement(user_id, {
            'title': 'New Achievement',
            'description': 'Description here',
            'icon': 'icon-name'
        })
```

#### 3. New API Endpoint

**Backend (app.py):**
```python
@app.get("/your-endpoint")
async def your_function(token: str = Depends(verify_token)):
    # Implementation
    return {"data": "response"}
```

**Frontend (App.jsx):**
```javascript
const fetchYourData = async () => {
  const data = await apiRequest('/your-endpoint');
  // Handle response
};
```

### Testing Strategy

#### Unit Tests
Test individual functions in isolation.

#### Integration Tests
Test API endpoints with database operations.

#### E2E Tests
Test complete user flows from frontend to backend.

#### Test Coverage Goals
- Backend: 80%+ coverage
- Frontend: 70%+ coverage
- Critical paths: 100% coverage

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Issue:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:**
```bash
pip install sentence-transformers torch
```

**Issue:** `Port 8000 already in use`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 2. Frontend Build Errors

**Issue:** `Cannot find module 'lucide-react'`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue:** API connection refused

**Solution:**
- Ensure backend is running on port 8000
- Check CORS configuration in `app.py`
- Verify `API_BASE_URL` in `App.jsx`

#### 3. Speech Recognition Not Working

**Issue:** Microphone not detected

**Solution:**
- Check browser permissions (Chrome/Edge recommended)
- Enable HTTPS in production (required for mic access)
- Test in Chrome DevTools → Console for errors

**Issue:** Recognition stops after few seconds

**Solution:**
- Known browser limitation
- Use continuous mode: `recognition.continuous = true`
- Implement restart logic on silence

#### 4. Low Similarity Scores

**Issue:** Correct answers getting low scores

**Solution:**
- Adjust `SIMILARITY_THRESHOLD` in backend
- Improve expected answers in dataset
- Consider answer preprocessing (lowercase, trim)

#### 5. Database Locked

**Issue:** `database is locked` error

**Solution:**
```python
# Increase timeout in database.py
conn = sqlite3.connect('interview_system.db', timeout=10)
```

#### 6. Token Expiration

**Issue:** 401 Unauthorized after some time

**Solution:**
- Increase `ACCESS_TOKEN_EXPIRE_MINUTES` in backend
- Implement token refresh logic
- Handle 401 responses in frontend

### Debug Mode

#### Enable Backend Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Frontend Console Logging
```javascript
const DEBUG = true;
if (DEBUG) console.log('API Response:', data);
```

### Performance Optimization

#### Backend
- Use Redis for caching
- Load model once at startup
- Implement request queuing for high load

#### Frontend
- Lazy load components
- Implement virtual scrolling for history
- Optimize re-renders with `useMemo` and `useCallback`

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive
- Reference issues in commit messages

### Code Review Process
- All PRs require review from maintainers
- Address review comments promptly
- Ensure CI/CD passes
- Squash commits before merging

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026 Smart Voice Interviewer

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

## 📞 Support

### Documentation
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md)
- [Developer Guide](docs/DEVELOPER.md)

### Community
- **Issues**: [GitHub Issues](https://github.com/yourusername/smart-voice-interviewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/smart-voice-interviewer/discussions)
- **Email**: support@smartvoiceinterviewer.com

### Resources
- [Sentence-BERT Documentation](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

## 🎯 Roadmap

### Version 1.1 (Q2 2026)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Video recording for behavioral interviews
- [ ] Enhanced analytics with charts
- [ ] Export results to PDF

### Version 1.2 (Q3 2026)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration (peer practice)
- [ ] AI-generated questions
- [ ] Integration with LinkedIn

### Version 2.0 (Q4 2026)
- [ ] Advanced AI models (GPT-4 integration)
- [ ] Company-specific interview prep
- [ ] Interview scheduling system
- [ ] Marketplace for interview coaches

---

## 🙏 Acknowledgments

- **Sentence-BERT**: For the amazing semantic similarity model
- **FastAPI**: For the high-performance web framework
- **React Team**: For the excellent frontend library
- **Lucide**: For the beautiful icon set
- **Community**: All contributors and users

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/smart-voice-interviewer?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/smart-voice-interviewer?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/smart-voice-interviewer?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/smart-voice-interviewer)
![GitHub issues](https://img.shields.io/github/issues/yourusername/smart-voice-interviewer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/smart-voice-interviewer)

---

<div align="center">

**Made with ❤️ by the Smart Voice Interviewer Team**

[⬆ Back to Top](#smart-voice-interviewer-)

</div>
