"""
Smart Voice Interviewer - FastAPI Backend
AI-Powered Interview System with RESTful API
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
from datetime import datetime, timedelta
import random
import joblib
import json
from jose import JWTError, jwt
import database as db

# =============================================================================
# CONFIGURATION
# =============================================================================

import os

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Security
security = HTTPBearer()

# Get parent directory for data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "final_knowledge_base.csv")
COURSE_CATALOG_FILE = os.path.join(BASE_DIR, "course_catalog.csv")
SIMILARITY_THRESHOLD = 0.6
NUM_QUESTIONS = 3
PASS_THRESHOLD = 0.6

# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Smart Voice Interviewer API",
    description="AI-Powered Interview System with Semantic Similarity Scoring",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

model = None
df_questions = None
df_courses = None
active_interviews = {}

# =============================================================================
# AUTHENTICATION HELPERS
# =============================================================================

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    username: str
    password: str

class InterviewStartRequest(BaseModel):
    topic: str
    num_questions: Optional[int] = NUM_QUESTIONS
    session_id: Optional[str] = None
    user_id: Optional[str] = None  # Added to check user profile

class AnswerSubmitRequest(BaseModel):
    session_id: str
    question_index: int
    answer: str

class InterviewSession(BaseModel):
    session_id: str
    topic: str
    questions: List[Dict]
    answers: List[Dict]
    current_question: int
    completed: bool

class SimilarityScore(BaseModel):
    score: float
    passed: bool
    threshold: float

class CourseRecommendation(BaseModel):
    category: str
    course_title: str
    platform: str
    provider: str
    difficulty: str
    url: str
    relevance_score: float

class InterviewResult(BaseModel):
    session_id: str
    topic: str
    total_questions: int
    answered: int
    passed: int
    average_score: float
    pass_rate: float
    answers: List[Dict]
    recommendations: List[CourseRecommendation]

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    bio: Optional[str] = ""
    experience_level: Optional[str] = "Beginner"
    interests: Optional[List[str]] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    experience_level: Optional[str] = None
    interests: Optional[List[str]] = None

# =============================================================================
# STARTUP AND SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Load models and data on startup."""
    global model, df_questions, df_courses, rf_difficulty, rf_category, le_difficulty, le_category
    global course_embeddings, courses_data, category_course_map, tfidf_vectorizer, tfidf_matrix
    
    print("Loading AI models and datasets...")
    
    # Initialize database
    db.init_db()
    
    # Load Sentence-BERT model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Loaded Sentence-BERT model")
    
    # Load trained custom models
    models_dir = os.path.join(BASE_DIR, "models")
    try:
        rf_difficulty = joblib.load(os.path.join(models_dir, "difficulty_classifier.joblib"))
        rf_category = joblib.load(os.path.join(models_dir, "category_classifier.joblib"))
        le_difficulty = joblib.load(os.path.join(models_dir, "label_encoder_difficulty.joblib"))
        le_category = joblib.load(os.path.join(models_dir, "label_encoder_category.joblib"))
        print("✓ Loaded trained RandomForest models")
    except FileNotFoundError:
        print("⚠️ Trained models not found. Run train_model.py first.")
        rf_difficulty = rf_category = le_difficulty = le_category = None
    except Exception as e:
        print(f"⚠️ Could not load ML classifiers (version mismatch): {e}")
        print("   Continuing without ML models (using fallback methods)")
        rf_difficulty = rf_category = le_difficulty = le_category = None
    
    # Load recommendation models
    try:
        course_embeddings = np.load(os.path.join(models_dir, "course_embeddings.npy"))
        courses_data = pd.read_pickle(os.path.join(models_dir, "courses_data.pkl"))
        with open(os.path.join(models_dir, "category_course_map.json"), 'r') as f:
            category_course_map = json.load(f)
        tfidf_vectorizer = joblib.load(os.path.join(models_dir, "tfidf_vectorizer.joblib"))
        tfidf_matrix = joblib.load(os.path.join(models_dir, "tfidf_matrix.joblib"))
        print("✓ Loaded recommendation models")
    except FileNotFoundError:
        print("⚠️ Recommendation models not found")
        course_embeddings = courses_data = category_course_map = None
        tfidf_vectorizer = tfidf_matrix = None
    except Exception as e:
        print(f"⚠️ Could not load recommendation models: {e}")
        course_embeddings = courses_data = category_course_map = None
        tfidf_vectorizer = tfidf_matrix = None
    
    # Load datasets
    df_questions = pd.read_csv(KNOWLEDGE_BASE_FILE)
    df_courses = pd.read_csv(COURSE_CATALOG_FILE)
    print(f"✓ Loaded {len(df_questions):,} questions")
    print(f"✓ Loaded {len(df_courses):,} courses")
    
    print("API Ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down API...")

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    user = db.create_user(request.username, request.email, request.password, request.name)
    
    if not user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    access_token = create_access_token(data={"sub": user["user_id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.post("/login")
async def login(request: LoginRequest):
    """Login user"""
    user = db.authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["user_id"]})
    
    # Get full user data with stats
    user_data = db.get_user_by_id(user["user_id"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@app.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    """Get current user profile"""
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": user}

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Smart Voice Interviewer API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "start_interview": "/interview/start",
            "submit_answer": "/interview/answer",
            "get_results": "/interview/results/{session_id}",
            "get_statistics": "/statistics",
            "list_categories": "/categories"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "questions_loaded": df_questions is not None,
        "courses_loaded": df_courses is not None,
        "active_sessions": len(active_interviews)
    }

@app.get("/categories")
async def list_categories():
    """Get list of available interview categories."""
    if df_questions is None:
        raise HTTPException(status_code=500, detail="Questions database not loaded")
    
    categories = df_questions['Category'].value_counts().head(20).to_dict()
    return {
        "total_categories": df_questions['Category'].nunique(),
        "top_categories": categories
    }

@app.get("/statistics")
async def get_statistics():
    """Get database statistics."""
    if df_questions is None or df_courses is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "questions": {
            "total": len(df_questions),
            "categories": df_questions['Category'].nunique(),
            "difficulty_distribution": df_questions['Difficulty'].value_counts().to_dict()
        },
        "courses": {
            "total": len(df_courses),
            "platforms": df_courses['Platform'].value_counts().to_dict(),
            "difficulty_distribution": df_courses['Difficulty'].value_counts().to_dict()
        }
    }

@app.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    """Start a new interview session."""
    if df_questions is None:
        raise HTTPException(status_code=500, detail="Questions database not loaded")
    
    # Filter questions by topic
    topic_questions = df_questions[
        df_questions['Category'].str.contains(request.topic, case=False, na=False)
    ]
    
    # Filter out questions with placeholder answers
    valid_questions = topic_questions[
        ~topic_questions['Answer'].str.contains('Coding solution to be provided|to be provided during interview', 
                                                case=False, na=False, regex=True)
    ]
    
    # Filter by experience level if user_id provided
    if request.user_id:
        user = db.get_user_by_id(request.user_id)
        if user:
            experience_level = user.get('experience_level', 'Beginner')
            
            # Map experience level to difficulty
            difficulty_map = {
                'Beginner': ['Easy'],
                'Intermediate': ['Easy', 'Medium'],
                'Advanced': ['Medium', 'Hard'],
                'Expert': ['Medium', 'Hard']
            }
            
            allowed_difficulties = difficulty_map.get(experience_level, ['Easy', 'Medium', 'Hard'])
            valid_questions = valid_questions[
                valid_questions['Difficulty'].isin(allowed_difficulties)
            ]
    
    if len(valid_questions) == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"No valid questions found for topic: {request.topic}"
        )
    
    # Select random questions
    num_questions = min(request.num_questions, len(valid_questions))
    selected_questions = valid_questions.sample(n=num_questions)
    
    # Create session ID
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    # Prepare questions
    questions = []
    for idx, (_, row) in enumerate(selected_questions.iterrows()):
        questions.append({
            "index": idx,
            "question": row['Question'],
            "category": row['Category'],
            "difficulty": row['Difficulty'],
            "correct_answer": row['Answer']  # Will not be sent to client
        })
    
    # Create interview session
    active_interviews[session_id] = {
        "session_id": session_id,
        "topic": request.topic,
        "questions": questions,
        "answers": [],
        "current_question": 0,
        "completed": False,
        "started_at": datetime.now().isoformat()
    }
    
    # Return first question (without correct answer)
    return {
        "session_id": session_id,
        "topic": request.topic,
        "total_questions": len(questions),
        "current_question": {
            "index": 0,
            "question": questions[0]["question"],
            "category": questions[0]["category"],
            "difficulty": questions[0]["difficulty"]
        },
        "threshold": SIMILARITY_THRESHOLD
    }

@app.post("/interview/answer")
async def submit_answer(request: AnswerSubmitRequest):
    """Submit an answer and get similarity score."""
    if request.session_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = active_interviews[request.session_id]
    
    if session["completed"]:
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    if request.question_index >= len(session["questions"]):
        raise HTTPException(status_code=400, detail="Invalid question index")
    
    # Get question and correct answer
    question_data = session["questions"][request.question_index]
    correct_answer = question_data["correct_answer"]
    
    # Calculate similarity score
    user_embedding = model.encode([request.answer])
    correct_embedding = model.encode([correct_answer])
    score = float(cosine_similarity(user_embedding, correct_embedding)[0][0])
    
    passed = score >= SIMILARITY_THRESHOLD
    
    # Store answer
    answer_data = {
        "question_index": request.question_index,
        "question": question_data["question"],
        "category": question_data["category"],
        "difficulty": question_data["difficulty"],
        "user_answer": request.answer,
        "correct_answer": correct_answer,
        "score": score,
        "passed": passed,
        "answered_at": datetime.now().isoformat()
    }
    
    session["answers"].append(answer_data)
    session["current_question"] = request.question_index + 1
    
    # Check if interview is complete
    next_question = None
    if session["current_question"] < len(session["questions"]):
        next_q = session["questions"][session["current_question"]]
        next_question = {
            "index": session["current_question"],
            "question": next_q["question"],
            "category": next_q["category"],
            "difficulty": next_q["difficulty"]
        }
    else:
        session["completed"] = True
        session["completed_at"] = datetime.now().isoformat()
    
    return {
        "score": score,
        "passed": passed,
        "threshold": SIMILARITY_THRESHOLD,
        "status": "✅ PASS" if passed else "❌ FAIL",
        "next_question": next_question,
        "completed": session["completed"],
        "progress": {
            "answered": len(session["answers"]),
            "total": len(session["questions"])
        }
    }

@app.get("/interview/results/{session_id}")
async def get_interview_results(session_id: str):
    """Get complete interview results and recommendations."""
    if session_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = active_interviews[session_id]
    
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Interview not yet completed")
    
    # Calculate statistics
    total_score = sum(ans["score"] for ans in session["answers"])
    passed_count = sum(1 for ans in session["answers"] if ans["passed"])
    avg_score = total_score / len(session["answers"]) if session["answers"] else 0
    pass_rate = (passed_count / len(session["answers"]) * 100) if session["answers"] else 0
    
    # Get failed categories
    failed_categories = [ans["category"] for ans in session["answers"] if not ans["passed"]]
    failed_questions = [ans["question"] for ans in session["answers"] if not ans["passed"]]
    
    # Get all categories for recommendations (even if passed)
    all_categories = list(set([ans["category"] for ans in session["answers"]]))
    
    # Generate AI-based recommendations using trained recommendation models
    recommendations = []
    
    # Determine what to recommend based on
    # Priority: failed categories > all categories > topic
    recommend_categories = failed_categories if failed_categories else all_categories
    recommend_questions = failed_questions if failed_questions else [ans["question"] for ans in session["answers"][:3]]
    
    # FILTER courses by topic/category FIRST to avoid irrelevant recommendations
    topic_keywords = session['topic'].lower().split()
    category_keywords = [cat.lower() for cat in recommend_categories]
    all_keywords = set(topic_keywords + category_keywords)
    
    # Filter courses that match the topic or categories
    relevant_courses = df_courses[
        df_courses['Category'].str.lower().str.contains('|'.join(all_keywords), case=False, na=False, regex=True) |
        df_courses['Course_Title'].str.lower().str.contains('|'.join(all_keywords), case=False, na=False, regex=True)
    ]
    
    print(f"🔍 Found {len(relevant_courses)} courses matching topic '{session['topic']}' and categories {recommend_categories}")
    
    # If no matches, expand search
    if len(relevant_courses) == 0:
        print(f"⚠️ No exact matches, using broader search")
        relevant_courses = df_courses
    
    # Try 1: Use Sentence-BERT model directly with filtered courses
    if model is not None and len(relevant_courses) > 0:
        try:
            # Create specific search query emphasizing the topic
            learning_needs = f"{session['topic']} {session['topic']} " + " ".join(set(recommend_categories)) * 2
            
            # Encode user's needs
            need_embedding = model.encode([learning_needs])[0]
            
            # Limit to first 200 relevant courses for speed
            course_sample = relevant_courses.head(200)
            course_texts = (course_sample['Course_Title'] + " " + 
                          course_sample['Category'] + " " + 
                          course_sample['Category'] + " " +  # Weight category more
                          course_sample['Provider']).tolist()
            
            course_embeddings_temp = model.encode(course_texts)
            
            # Calculate similarities
            similarities = cosine_similarity([need_embedding], course_embeddings_temp)[0]
            
            # Get top courses with higher threshold for quality
            top_indices = np.argsort(similarities)[::-1][:10]
            
            for idx in top_indices:
                similarity_score = similarities[idx]
                if similarity_score > 0.3 and len(recommendations) < 3:  # Higher threshold
                    course = course_sample.iloc[idx]
                    recommendations.append({
                        "category": ", ".join(set(recommend_categories)),
                        "course_title": course['Course_Title'],
                        "platform": course['Platform'],
                        "provider": course['Provider'],
                        "difficulty": course['Difficulty'],
                        "url": course['URL'],
                        "relevance_score": round(float(similarity_score), 3)
                    })
            
            print(f"✓ Generated {len(recommendations)} AI recommendations using Sentence-BERT")
        except Exception as e:
            print(f"⚠️ Real-time AI recommendation error: {e}")
    
    # Try 2: Use category-based matching if not enough recommendations
    if len(recommendations) < 3 and recommend_categories:
        for category in set(recommend_categories):
            if len(recommendations) >= 3:
                break
            matching_courses = relevant_courses[
                relevant_courses['Category'].str.contains(category, case=False, na=False, regex=False)
            ]
            if len(matching_courses) > 0:
                # Get top course per category
                best_course = matching_courses.iloc[0]
                # Check if not already added
                if not any(r["course_title"] == best_course['Course_Title'] for r in recommendations):
                    recommendations.append({
                        "category": category,
                        "course_title": best_course['Course_Title'],
                        "platform": best_course['Platform'],
                        "provider": best_course['Provider'],
                        "difficulty": best_course['Difficulty'],
                        "url": best_course['URL'],
                        "relevance_score": 0.5
                    })
    
    # Try 3: Use topic-based matching if still not enough
    if len(recommendations) < 3:
        for i in range(min(3 - len(recommendations), len(relevant_courses))):
            course = relevant_courses.iloc[i]
            # Check if not already added
            if not any(r["course_title"] == course['Course_Title'] for r in recommendations):
                recommendations.append({
                    "category": session['topic'],
                    "course_title": course['Course_Title'],
                    "platform": course['Platform'],
                    "provider": course['Provider'],
                    "difficulty": course['Difficulty'],
                    "url": course['URL'],
                    "relevance_score": 0.4
                })
    
    # Ensure we always have at least some recommendations
    if len(recommendations) < 3 and len(df_courses) > 0:
        # Fallback: Get any courses from dataset
        for i in range(min(3 - len(recommendations), len(df_courses))):
            course = df_courses.iloc[i]
            if not any(r["course_title"] == course['Course_Title'] for r in recommendations):
                recommendations.append({
                    "category": "General",
                    "course_title": course['Course_Title'],
                    "platform": course['Platform'],
                    "provider": course['Provider'],
                    "difficulty": course['Difficulty'],
                    "url": course['URL'],
                    "relevance_score": 0.3
                })
    
    return {
        "session_id": session_id,
        "topic": session["topic"],
        "total_questions": len(session["questions"]),
        "answered": len(session["answers"]),
        "passed": passed_count,
        "average_score": round(avg_score, 4),
        "pass_rate": round(pass_rate, 2),
        "started_at": session["started_at"],
        "completed_at": session.get("completed_at"),
        "answers": session["answers"],
        "recommendations": recommendations,
        "summary": {
            "status": "PASSED" if pass_rate >= 60 else "FAILED",
            "message": "Congratulations! You passed the interview!" if pass_rate >= 60 else "Keep learning! Check the recommended courses."
        },
        "new_achievements": []  # Will be populated if user_id provided
    }

@app.delete("/interview/{session_id}")
async def delete_interview_session(session_id: str):
    """Delete an interview session."""
    if session_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    del active_interviews[session_id]
    return {"message": "Session deleted successfully"}

@app.get("/interview/sessions")
async def list_active_sessions():
    """List all active interview sessions."""
    sessions = []
    for session_id, session in active_interviews.items():
        sessions.append({
            "session_id": session_id,
            "topic": session["topic"],
            "progress": f"{len(session['answers'])}/{len(session['questions'])}",
            "completed": session["completed"],
            "started_at": session["started_at"]
        })
    
    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }

# =============================================================================
# USER PROFILE ENDPOINTS
# =============================================================================

@app.post("/profile")
async def create_profile(profile_data: Dict):
    """Create a new user profile."""
    try:
        from datetime import datetime
        import uuid
        
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        profile = {
            "user_id": user_id,
            "name": profile_data.get("name", ""),
            "email": profile_data.get("email", ""),
            "bio": profile_data.get("bio", ""),
            "experience_level": profile_data.get("experience_level", "Beginner"),
            "interests": profile_data.get("interests", []),
            "created_at": now,
            "updated_at": now,
            "interview_count": 0,
            "total_score": 0.0,
            "interview_history": [],
            "achievements": [],
            "current_streak": 0,
            "best_streak": 0,
            "last_interview_date": None
        }
        
        user_profiles[user_id] = profile
        
        return {
            "status": "success",
            "message": "Profile created successfully",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile by ID."""
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "status": "success",
        "profile": user
    }

@app.put("/profile/{user_id}")
async def update_profile(user_id: str, update_data: Dict, current_user_id: str = Depends(verify_token)):
    """Update user profile."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    success = db.update_user_profile(user_id, update_data)
    
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    user = db.get_user_by_id(user_id)
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "profile": user
    }

@app.delete("/profile/{user_id}")
async def delete_profile(user_id: str):
    """Delete user profile."""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    del user_profiles[user_id]
    
    return {
        "status": "success",
        "message": "Profile deleted successfully"
    }

@app.get("/profile/{user_id}/stats")
async def get_profile_stats(user_id: str):
    """Get user statistics."""
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "status": "success",
        "stats": {
            "interview_count": user.get("interview_count", 0),
            "total_score": user.get("total_score", 0.0),
            "average_score": user.get("total_score", 0.0) / max(user.get("interview_count", 1), 1),
            "experience_level": user.get("experience_level", "Beginner"),
            "interests": user.get("interests", []),
            "current_streak": user.get("current_streak", 0),
            "best_streak": user.get("best_streak", 0),
            "achievements": user.get("achievements", [])
        }
    }

@app.get("/profile/{user_id}/history")
async def get_interview_history(user_id: str, limit: int = 10):
    """Get user's interview history."""
    history = db.get_interview_history(user_id, limit)
    
    return {
        "status": "success",
        "history": history,
        "total_interviews": len(history)
    }

@app.get("/profile/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    """Get detailed analytics for user performance."""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = user_profiles[user_id]
    history = profile.get("interview_history", [])
    
    if not history:
        return {
            "status": "success",
            "analytics": {
                "total_interviews": 0,
                "performance_trend": [],
                "category_breakdown": {},
                "difficulty_breakdown": {}
            }
        }
    
    # Calculate performance trend
    performance_trend = [{
        "date": h["date"],
        "score": h["pass_rate"]
    } for h in history[-10:]]
    
    # Category performance
    category_stats = {}
    difficulty_stats = {}
    
    for interview in history:
        topic = interview.get("topic", "Unknown")
        score = interview.get("pass_rate", 0)
        
        if topic not in category_stats:
            category_stats[topic] = {"total": 0, "sum_score": 0}
        category_stats[topic]["total"] += 1
        category_stats[topic]["sum_score"] += score
    
    # Calculate averages
    category_breakdown = {
        k: {
            "average_score": v["sum_score"] / v["total"],
            "attempts": v["total"]
        }
        for k, v in category_stats.items()
    }
    
    return {
        "status": "success",
        "analytics": {
            "total_interviews": len(history),
            "performance_trend": performance_trend,
            "category_breakdown": category_breakdown,
            "current_streak": profile.get("current_streak", 0),
            "best_streak": profile.get("best_streak", 0)
        }
    }

@app.post("/profile/{user_id}/update-after-interview")
async def update_profile_after_interview(
    user_id: str, 
    results: Dict,
    current_user_id: str = Depends(verify_token)
):
    """Update user profile after completing interview."""
    # Verify user can only update their own profile
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    from datetime import datetime
    
    # Add interview to history
    history_entry = {
        "session_id": results.get("session_id"),
        "topic": results.get("topic"),
        "date": datetime.now().isoformat(),
        "pass_rate": results.get("pass_rate", 0),
        "average_score": results.get("average_score", 0) * 100,
        "questions_count": results.get("total_questions", 0),
        "passed": results.get("passed", 0)
    }
    
    success = db.add_interview_history(user_id, history_entry)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update stats and get new achievements
    stats_update = {
        "pass_rate": results.get("pass_rate", 0)
    }
    new_achievements = db.update_user_stats(user_id, stats_update)
    
    # Get updated profile
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "new_achievements": new_achievements,
        "current_streak": user.get("current_streak", 0),
        "profile": user
    }

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("SMART VOICE INTERVIEWER - FASTAPI BACKEND")
    print("="*70)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("\n" + "="*70)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
