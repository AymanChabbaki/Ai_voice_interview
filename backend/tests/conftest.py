"""
Pytest Configuration and Shared Fixtures
"""

import os
import sys
from datetime import datetime
from typing import Dict, Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment
load_dotenv(".env.test")

import database as db
from app import app, create_access_token

# ---------------------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["DATABASE_URL"] = "postgresql://test_user:test_password@localhost:5432/test_interview_db"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["SIMILARITY_THRESHOLD"] = "0.6"
    os.environ["NUM_QUESTIONS"] = "3"


@pytest.fixture(scope="function")
def mock_db_pool():
    """Mock database connection pool."""
    with patch("database._pool") as mock_pool:
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        yield mock_pool


@pytest.fixture(scope="function")
def test_db():
    """Initialize test database and clean up after tests."""
    # This fixture assumes you have a test database set up
    # For unit tests, you might want to mock this
    try:
        db.init_db()
        yield
        # Cleanup: Clear test data
        with db._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM interview_history")
                cur.execute("DELETE FROM user_stats")
                cur.execute("DELETE FROM users")
    except Exception:
        # If database is not available, skip database-dependent tests
        pytest.skip("Test database not available")


# ---------------------------------------------------------------------------
# FastAPI Client
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, test_user: Dict) -> TestClient:
    """Create an authenticated test client."""
    token = create_access_token(test_user["user_id"])
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


# ---------------------------------------------------------------------------
# User Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def test_user() -> Dict:
    """Create a test user data dictionary."""
    return {
        "user_id": "test-user-id-12345",
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
    }


@pytest.fixture(scope="function")
def test_user_in_db(test_db, test_user: Dict) -> Dict:
    """Create a test user in the database."""
    user = db.create_user(
        username=test_user["username"],
        email=test_user["email"],
        password=test_user["password"],
        name=test_user["name"],
    )
    return user


@pytest.fixture(scope="function")
def multiple_test_users(test_db) -> list[Dict]:
    """Create multiple test users in the database."""
    users = []
    for i in range(3):
        user = db.create_user(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            password="TestPassword123!",
            name=f"Test User {i}",
        )
        users.append(user)
    return users


# ---------------------------------------------------------------------------
# Mock Data Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def mock_questions_df() -> pd.DataFrame:
    """Create a mock questions DataFrame."""
    return pd.DataFrame({
        "Question": [
            "What is Python?",
            "Explain OOP concepts",
            "What is a REST API?",
            "Describe SQL joins",
            "What is machine learning?",
        ],
        "Answer": [
            "Python is a high-level programming language",
            "Object-oriented programming includes concepts like encapsulation, inheritance, and polymorphism",
            "REST API is an architectural style for networked applications",
            "SQL joins combine rows from two or more tables",
            "Machine learning is a subset of AI that learns from data",
        ],
        "Category": [
            "Python Programming",
            "Python Programming",
            "Web Development",
            "Database",
            "Machine Learning",
        ],
        "Difficulty": ["Easy", "Medium", "Easy", "Medium", "Hard"],
    })


@pytest.fixture(scope="function")
def mock_courses_df() -> pd.DataFrame:
    """Create a mock courses DataFrame."""
    return pd.DataFrame({
        "Course_Title": [
            "Introduction to Python",
            "Advanced Python Programming",
            "Web Development with FastAPI",
            "SQL Masterclass",
            "Machine Learning A-Z",
        ],
        "Platform": ["Udemy", "Coursera", "Udemy", "Coursera", "Udemy"],
        "Provider": ["Jose Portilla", "University of Michigan", "Abhishek Singh", "Mosh Hamedani", "Kirill Eremenko"],
        "Category": ["Python Programming", "Python Programming", "Web Development", "Database", "Machine Learning"],
        "Difficulty": ["Beginner", "Advanced", "Intermediate", "Intermediate", "Advanced"],
        "URL": [
            "https://example.com/python-intro",
            "https://example.com/python-advanced",
            "https://example.com/fastapi",
            "https://example.com/sql",
            "https://example.com/ml",
        ],
    })


@pytest.fixture(scope="function")
def mock_sentence_model():
    """Mock SentenceTransformer model."""
    mock_model = MagicMock()
    # Mock encode method to return consistent embeddings
    mock_model.encode.return_value = [[0.5, 0.5, 0.5]]
    return mock_model


@pytest.fixture(scope="function")
def mock_app_globals(mock_questions_df, mock_courses_df, mock_sentence_model):
    """Mock global app state (model, dataframes, active_interviews)."""
    mock_active_interviews = {}
    with patch("app.model", mock_sentence_model), \
         patch("app.df_questions", mock_questions_df), \
         patch("app.df_courses", mock_courses_df), \
         patch("app.active_interviews", mock_active_interviews):
        yield mock_active_interviews


# ---------------------------------------------------------------------------
# Interview Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def sample_interview_session() -> Dict:
    """Create a sample interview session."""
    return {
        "session_id": "session_20240101_120000_1234",
        "topic": "Python Programming",
        "questions": [
            {
                "index": 0,
                "question": "What is Python?",
                "category": "Python Programming",
                "difficulty": "Easy",
                "correct_answer": "Python is a high-level programming language",
            },
            {
                "index": 1,
                "question": "Explain OOP concepts",
                "category": "Python Programming",
                "difficulty": "Medium",
                "correct_answer": "Object-oriented programming includes encapsulation, inheritance, and polymorphism",
            },
        ],
        "answers": [],
        "current_question": 0,
        "completed": False,
        "started_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture(scope="function")
def completed_interview_session(sample_interview_session) -> Dict:
    """Create a completed interview session with answers."""
    session = sample_interview_session.copy()
    session["answers"] = [
        {
            "question_index": 0,
            "question": "What is Python?",
            "category": "Python Programming",
            "difficulty": "Easy",
            "user_answer": "Python is a programming language",
            "correct_answer": "Python is a high-level programming language",
            "score": 0.85,
            "passed": True,
            "answered_at": datetime.utcnow().isoformat(),
        },
        {
            "question_index": 1,
            "question": "Explain OOP concepts",
            "category": "Python Programming",
            "difficulty": "Medium",
            "user_answer": "OOP has classes and objects",
            "correct_answer": "Object-oriented programming includes encapsulation, inheritance, and polymorphism",
            "score": 0.55,
            "passed": False,
            "answered_at": datetime.utcnow().isoformat(),
        },
    ]
    session["current_question"] = 2
    session["completed"] = True
    session["completed_at"] = datetime.utcnow().isoformat()
    return session


@pytest.fixture(scope="function")
def active_interview_sessions(sample_interview_session):
    """Mock active interviews dictionary."""
    with patch("app.active_interviews") as mock_active:
        mock_active.__getitem__ = lambda self, key: sample_interview_session if key == sample_interview_session["session_id"] else None
        mock_active.get = lambda key, default=None: sample_interview_session if key == sample_interview_session["session_id"] else default
        mock_active.__contains__ = lambda self, key: key == sample_interview_session["session_id"]
        yield mock_active


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def create_test_token(user_id: str) -> str:
    """Helper to create a test JWT token."""
    return create_access_token(user_id)


def assert_error_response(response, status_code: int, detail_contains: str = None):
    """Helper to assert error responses."""
    assert response.status_code == status_code
    if detail_contains:
        assert detail_contains.lower() in response.json().get("detail", "").lower()


def assert_success_response(response, status_code: int = 200):
    """Helper to assert successful responses."""
    assert response.status_code == status_code
    data = response.json()
    assert data is not None
    return data
