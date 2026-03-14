"""
Smart Voice Interviewer - FastAPI Backend  (Production-Ready)
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import logging
import os
import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, field_validator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import database as db

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("smart_interviewer")

# ---------------------------------------------------------------------------
# Configuration  (all secrets come from environment / .env - never hardcoded)
# ---------------------------------------------------------------------------

_missing = [v for v in ["SECRET_KEY", "DATABASE_URL"] if not os.getenv(v)]
if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Copy .env.example to .env and fill in the values."
    )

SECRET_KEY: str              = os.environ["SECRET_KEY"]
ALGORITHM                    = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES  = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
SIMILARITY_THRESHOLD         = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
NUM_QUESTIONS                = int(os.getenv("NUM_QUESTIONS", "3"))

BASE_DIR            = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_FILE = os.getenv("KB_FILE",      os.path.join(BASE_DIR, "final_knowledge_base.csv"))
COURSE_CATALOG_FILE = os.getenv("COURSES_FILE", os.path.join(BASE_DIR, "course_catalog.csv"))

# ---------------------------------------------------------------------------
# allowing frontend , to prevent CORS policy
# ---------------------------------------------------------------------------

ALLOWED_ORIGINS: List[str] = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",") if o.strip()
]

# Add wildcard for Kubernetes internal traffic
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"http://192\.168\.174\.\d+.*",  # allows any VMware IP
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# Rate-limiter
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

model:             Optional[SentenceTransformer] = None
df_questions:      Optional[pd.DataFrame]        = None
df_courses:        Optional[pd.DataFrame]        = None
active_interviews: Dict[str, Dict]               = {}

# ---------------------------------------------------------------------------
# Lifespan  (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load all resources on startup; clean up on shutdown."""
    global model, df_questions, df_courses

    logger.info("Initialising database ...")
    db.init_db()

    logger.info("Loading Sentence-BERT model ...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Sentence-BERT model loaded")

    if not os.path.isfile(KNOWLEDGE_BASE_FILE):
        logger.error("Knowledge base not found: %s", KNOWLEDGE_BASE_FILE)
    else:
        df_questions = pd.read_csv(KNOWLEDGE_BASE_FILE)
        logger.info("Loaded %d questions", len(df_questions))

    if not os.path.isfile(COURSE_CATALOG_FILE):
        logger.error("Course catalog not found: %s", COURSE_CATALOG_FILE)
    else:
        df_courses = pd.read_csv(COURSE_CATALOG_FILE)
        logger.info("Loaded %d courses", len(df_courses))

    logger.info("API ready on port %s", os.getenv("PORT", "8000"))
    yield
    logger.info("Shutting down - clearing %d active sessions", len(active_interviews))
    active_interviews.clear()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Smart Voice Interviewer API",
    description="AI-Powered Interview System with Semantic Similarity Scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

security = HTTPBearer()

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def create_access_token(user_id: str) -> str:
    payload = {
        "sub":  user_id,
        "exp":  datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat":  datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not _USERNAME_RE.match(v):
            raise ValueError("Username must be 3-32 characters: letters, digits and underscores only")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class InterviewStartRequest(BaseModel):
    topic: str
    num_questions: Optional[int] = NUM_QUESTIONS
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    @field_validator("num_questions")
    @classmethod
    def validate_num(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 20):
            raise ValueError("num_questions must be between 1 and 20")
        return v

class AnswerSubmitRequest(BaseModel):
    session_id: str
    question_index: int
    answer: str

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Answer cannot be empty")
        if len(v) > 10000:
            raise ValueError("Answer too long (max 10,000 characters)")
        return v

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    experience_level: Optional[str] = None
    interests: Optional[List[str]] = None

    @field_validator("experience_level")
    @classmethod
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        valid = {"Beginner", "Intermediate", "Advanced", "Expert"}
        if v is not None and v not in valid:
            raise ValueError(f"experience_level must be one of: {', '.join(sorted(valid))}")
        return v

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _assert_data_loaded() -> None:
    if df_questions is None or df_courses is None:
        raise HTTPException(status_code=503, detail="Data not yet loaded - please retry in a moment")

# ---------------------------------------------------------------------------
# Routes - General
# ---------------------------------------------------------------------------

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Smart Voice Interviewer API",
        "version": "1.0.0",
        "status":  "online",
        "docs":    "/docs",
    }

@app.get("/health", tags=["General"])
async def health():
    return {
        "status":           "healthy",
        "model_loaded":     model is not None,
        "questions_loaded": df_questions is not None,
        "courses_loaded":   df_courses is not None,
        "active_sessions":  len(active_interviews),
    }

@app.get("/categories", tags=["General"])
async def list_categories():
    _assert_data_loaded()
    counts = df_questions["Category"].value_counts().head(20).to_dict()
    return {"total_categories": df_questions["Category"].nunique(), "top_categories": counts}

@app.get("/statistics", tags=["General"])
async def get_statistics():
    _assert_data_loaded()
    return {
        "questions": {
            "total":                   len(df_questions),
            "categories":              df_questions["Category"].nunique(),
            "difficulty_distribution": df_questions["Difficulty"].value_counts().to_dict(),
        },
        "courses": {
            "total":                   len(df_courses),
            "platforms":               df_courses["Platform"].value_counts().to_dict(),
            "difficulty_distribution": df_courses["Difficulty"].value_counts().to_dict(),
        },
    }

# ---------------------------------------------------------------------------
# Routes - Auth
# ---------------------------------------------------------------------------

@app.post("/register", tags=["Auth"])
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest):
    user = db.create_user(body.username, body.email, body.password, body.name)
    if not user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"access_token": create_access_token(user["user_id"]), "token_type": "bearer", "user": user}

@app.post("/login", tags=["Auth"])
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    raw = db.authenticate_user(body.username, body.password)
    if not raw:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user = db.get_user_by_id(raw["user_id"])
    return {"access_token": create_access_token(user["user_id"]), "token_type": "bearer", "user": user}

@app.get("/me", tags=["Auth"])
async def get_current_user(user_id: str = Depends(_require_auth)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

# ---------------------------------------------------------------------------
# Routes - Interview
# ---------------------------------------------------------------------------

@app.post("/interview/start", tags=["Interview"])
async def start_interview(body: InterviewStartRequest):
    _assert_data_loaded()

    pool = df_questions[
        df_questions["Category"].str.contains(body.topic, case=False, na=False)
    ]
    pool = pool[
        ~pool["Answer"].str.contains(
            r"Coding solution to be provided|to be provided during interview",
            case=False, na=False, regex=True,
        )
    ]

    if body.user_id:
        user = db.get_user_by_id(body.user_id)
        if user:
            diff_map = {
                "Beginner":     ["Easy"],
                "Intermediate": ["Easy", "Medium"],
                "Advanced":     ["Medium", "Hard"],
                "Expert":       ["Medium", "Hard"],
            }
            allowed  = diff_map.get(user.get("experience_level", "Beginner"), ["Easy", "Medium", "Hard"])
            filtered = pool[pool["Difficulty"].isin(allowed)]
            if not filtered.empty:
                pool = filtered

    if pool.empty:
        raise HTTPException(status_code=404, detail=f"No valid questions found for topic: {body.topic}")

    n          = min(body.num_questions or NUM_QUESTIONS, len(pool))
    selected   = pool.sample(n=n)
    session_id = (
        body.session_id
        or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000, 9999)}"
    )

    questions = [
        {
            "index":          idx,
            "question":       row["Question"],
            "category":       row["Category"],
            "difficulty":     row["Difficulty"],
            "correct_answer": row["Answer"],
        }
        for idx, (_, row) in enumerate(selected.iterrows())
    ]

    active_interviews[session_id] = {
        "session_id":       session_id,
        "topic":            body.topic,
        "questions":        questions,
        "answers":          [],
        "current_question": 0,
        "completed":        False,
        "started_at":       datetime.utcnow().isoformat(),
    }

    first = questions[0]
    logger.info("Interview started | session=%s topic=%s", session_id, body.topic)
    return {
        "session_id":       session_id,
        "topic":            body.topic,
        "total_questions":  len(questions),
        "current_question": {k: first[k] for k in ("index", "question", "category", "difficulty")},
        "threshold":        SIMILARITY_THRESHOLD,
    }

@app.post("/interview/answer", tags=["Interview"])
async def submit_answer(body: AnswerSubmitRequest):
    session = active_interviews.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session["completed"]:
        raise HTTPException(status_code=400, detail="Interview already completed")
    if body.question_index >= len(session["questions"]):
        raise HTTPException(status_code=400, detail="Invalid question index")
    if model is None:
        raise HTTPException(status_code=503, detail="AI model not loaded yet")

    q           = session["questions"][body.question_index]
    user_emb    = model.encode([body.answer])
    correct_emb = model.encode([q["correct_answer"]])
    score       = float(cosine_similarity(user_emb, correct_emb)[0][0])
    passed      = score >= SIMILARITY_THRESHOLD

    session["answers"].append({
        "question_index": body.question_index,
        "question":       q["question"],
        "category":       q["category"],
        "difficulty":     q["difficulty"],
        "user_answer":    body.answer,
        "correct_answer": q["correct_answer"],
        "score":          score,
        "passed":         passed,
        "answered_at":    datetime.utcnow().isoformat(),
    })
    session["current_question"] = body.question_index + 1

    next_question = None
    if session["current_question"] < len(session["questions"]):
        nq = session["questions"][session["current_question"]]
        next_question = {k: nq[k] for k in ("index", "question", "category", "difficulty")}
    else:
        session["completed"]    = True
        session["completed_at"] = datetime.utcnow().isoformat()

    return {
        "score":         score,
        "passed":        passed,
        "threshold":     SIMILARITY_THRESHOLD,
        "status":        "PASS" if passed else "FAIL",
        "next_question": next_question,
        "completed":     session["completed"],
        "progress":      {"answered": len(session["answers"]), "total": len(session["questions"])},
    }

@app.get("/interview/results/{session_id}", tags=["Interview"])
async def get_results(session_id: str):
    _assert_data_loaded()
    session = active_interviews.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    answers   = session["answers"]
    avg_score = sum(a["score"] for a in answers) / len(answers) if answers else 0
    passed_n  = sum(1 for a in answers if a["passed"])
    pass_rate = (passed_n / len(answers) * 100) if answers else 0

    return {
        "session_id":       session_id,
        "topic":            session["topic"],
        "total_questions":  len(session["questions"]),
        "answered":         len(answers),
        "passed":           passed_n,
        "average_score":    round(avg_score, 4),
        "pass_rate":        round(pass_rate, 2),
        "started_at":       session["started_at"],
        "completed_at":     session.get("completed_at"),
        "answers":          answers,
        "recommendations":  _get_recommendations(session, answers),
        "summary": {
            "status":   "PASSED" if pass_rate >= 60 else "FAILED",
            "message":  "Congratulations! You passed!" if pass_rate >= 60
                        else "Keep practising - check the recommended courses.",
        },
        "new_achievements": [],
    }

def _get_recommendations(session: Dict, answers: List[Dict]) -> List[Dict]:
    """Return up to 3 course recommendations relevant to the interview topic/failures."""
    topic       = session["topic"]
    failed_cats = [a["category"] for a in answers if not a["passed"]]
    target_cats = list(dict.fromkeys(failed_cats)) or [a["category"] for a in answers]

    keywords = set([topic.lower()] + [c.lower() for c in target_cats])
    pattern  = "|".join(re.escape(k) for k in keywords)

    relevant = df_courses[
        df_courses["Category"].str.lower().str.contains(pattern, na=False, regex=True) |
        df_courses["Course_Title"].str.lower().str.contains(pattern, na=False, regex=True)
    ]
    if relevant.empty:
        relevant = df_courses

    recs: List[Dict] = []
    seen: set        = set()

    if model is not None and len(relevant) > 0:
        need_text = f"{topic} " + " ".join(target_cats)
        need_emb  = model.encode([need_text])[0]
        sample    = relevant.head(200)
        texts     = (sample["Course_Title"] + " " + sample["Category"] + " " + sample["Provider"]).tolist()
        embs      = model.encode(texts)
        sims      = cosine_similarity([need_emb], embs)[0]

        for idx in np.argsort(sims)[::-1]:
            if len(recs) >= 3:
                break
            if sims[idx] < 0.25:
                break
            title = sample.iloc[idx]["Course_Title"]
            if title in seen:
                continue
            seen.add(title)
            recs.append(_course_row(sample.iloc[idx], round(float(sims[idx]), 3), ", ".join(dict.fromkeys(target_cats))))

    for _, row in relevant.iterrows():
        if len(recs) >= 3:
            break
        if row["Course_Title"] not in seen:
            seen.add(row["Course_Title"])
            recs.append(_course_row(row, 0.5, topic))

    return recs[:3]

def _course_row(row: Any, score: float, category: str) -> Dict:
    return {
        "category":        category,
        "course_title":    row["Course_Title"],
        "platform":        row["Platform"],
        "provider":        row["Provider"],
        "difficulty":      row["Difficulty"],
        "url":             row["URL"],
        "relevance_score": score,
    }

@app.delete("/interview/{session_id}", tags=["Interview"])
async def delete_session(session_id: str):
    if session_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview session not found")
    del active_interviews[session_id]
    return {"message": "Session deleted"}

@app.get("/interview/sessions", tags=["Interview"])
async def list_sessions():
    sessions = [
        {
            "session_id": s["session_id"],
            "topic":      s["topic"],
            "progress":   f"{len(s['answers'])}/{len(s['questions'])}",
            "completed":  s["completed"],
            "started_at": s["started_at"],
        }
        for s in active_interviews.values()
    ]
    return {"total_sessions": len(sessions), "sessions": sessions}

# ---------------------------------------------------------------------------
# Routes - Profile
# ---------------------------------------------------------------------------

@app.get("/profile/{user_id}", tags=["Profile"])
async def get_profile(user_id: str, _: str = Depends(_require_auth)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "success", "profile": user}

@app.put("/profile/{user_id}", tags=["Profile"])
async def update_profile(
    user_id: str,
    body: UserProfileUpdate,
    current_user: str = Depends(_require_auth),
):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorised to update this profile")
    success = db.update_user_profile(user_id, body.model_dump(exclude_none=True))
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "success", "profile": db.get_user_by_id(user_id)}

@app.get("/profile/{user_id}/stats", tags=["Profile"])
async def get_stats(user_id: str, _: str = Depends(_require_auth)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    avg = user.get("total_score", 0) / max(user.get("interview_count", 0) or 1, 1)
    return {
        "status": "success",
        "stats": {
            "interview_count":  user.get("interview_count", 0),
            "total_score":      user.get("total_score", 0.0),
            "average_score":    round(avg, 4),
            "experience_level": user.get("experience_level", "Beginner"),
            "interests":        user.get("interests", []),
            "current_streak":   user.get("current_streak", 0),
            "best_streak":      user.get("best_streak", 0),
            "achievements":     user.get("achievements", []),
        },
    }

@app.get("/profile/{user_id}/history", tags=["Profile"])
async def get_history(user_id: str, limit: int = 50, _: str = Depends(_require_auth)):
    if not (1 <= limit <= 200):
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    history = db.get_interview_history(user_id, limit)
    return {"status": "success", "history": history, "total_interviews": len(history)}

@app.get("/profile/{user_id}/analytics", tags=["Profile"])
async def get_analytics(user_id: str, _: str = Depends(_require_auth)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")

    history = db.get_interview_history(user_id, limit=100)
    if not history:
        return {"status": "success", "analytics": {"total_interviews": 0}}

    trend = [{"date": h["date"], "score": h["pass_rate"]} for h in history[-10:]]
    cats: Dict[str, Dict] = {}
    for h in history:
        t = h.get("topic", "Unknown")
        if t not in cats:
            cats[t] = {"total": 0, "sum_score": 0.0}
        cats[t]["total"]     += 1
        cats[t]["sum_score"] += h.get("pass_rate", 0)

    breakdown = {
        k: {"average_score": round(v["sum_score"] / v["total"], 2), "attempts": v["total"]}
        for k, v in cats.items()
    }
    return {
        "status": "success",
        "analytics": {
            "total_interviews":   len(history),
            "performance_trend":  trend,
            "category_breakdown": breakdown,
            "current_streak":     user.get("current_streak", 0),
            "best_streak":        user.get("best_streak", 0),
        },
    }

@app.post("/profile/{user_id}/update-after-interview", tags=["Profile"])
async def update_after_interview(
    user_id: str,
    results: Dict,
    current_user: str = Depends(_require_auth),
):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorised to update this profile")

    entry = {
        "session_id":      results.get("session_id"),
        "topic":           results.get("topic"),
        "date":            datetime.utcnow().isoformat(),
        "pass_rate":       results.get("pass_rate", 0),
        "average_score":   results.get("average_score", 0) * 100,
        "questions_count": results.get("total_questions", 0),
        "passed":          int(bool(results.get("passed", 0))),
    }
    if not db.add_interview_history(user_id, entry):
        raise HTTPException(status_code=404, detail="User not found")

    new_achievements = db.update_user_stats(user_id, {"pass_rate": entry["pass_rate"]})
    user = db.get_user_by_id(user_id)
    return {
        "status":           "success",
        "new_achievements": new_achievements or [],
        "current_streak":   user.get("current_streak", 0) if user else 0,
        "profile":          user,
    }

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info"),
    )
