"""
Interview Tests - test_interview.py

Tests the complete interview flow including starting interviews,
submitting answers, scoring, recommendations, and session management.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import active_interviews

# Helper functions from conftest
def assert_error_response(response, status_code: int, detail_contains: str = None):
    assert response.status_code == status_code
    if detail_contains:
        assert detail_contains.lower() in response.json().get("detail", "").lower()

def assert_success_response(response, status_code: int = 200):
    assert response.status_code == status_code
    data = response.json()
    assert data is not None
    return data


# ---------------------------------------------------------------------------
# Start Interview Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestStartInterview:
    """Test starting a new interview session."""

    def test_start_interview_success(self, client, mock_app_globals):
        """Test successfully starting an interview."""
        response = client.post("/interview/start", json={
            "topic": "Python Programming",
            "num_questions": 2  # Match available mock data
        })
        
        data = assert_success_response(response, 200)
        assert "session_id" in data
        assert data["topic"] == "Python Programming"
        assert data["total_questions"] == 2  # Adjusted to match mock data
        assert "current_question" in data
        assert "threshold" in data

    def test_start_interview_default_num_questions(self, client, mock_app_globals):
        """Test starting interview with default number of questions."""
        response = client.post("/interview/start", json={
            "topic": "Python"
        })
        
        data = assert_success_response(response, 200)
        assert "total_questions" in data
        # Should use NUM_QUESTIONS from environment (3)
        assert data["total_questions"] <= 3

    def test_start_interview_custom_session_id(self, client, mock_app_globals):
        """Test starting interview with custom session ID."""
        custom_id = "my-custom-session-123"
        response = client.post("/interview/start", json={
            "topic": "Python",
            "session_id": custom_id
        })
        
        data = assert_success_response(response, 200)
        assert data["session_id"] == custom_id

    def test_start_interview_with_user_id(self, client, mock_app_globals, test_db, test_user_in_db):
        """Test starting interview with user ID for personalization."""
        response = client.post("/interview/start", json={
            "topic": "Python",
            "user_id": test_user_in_db["user_id"]
        })
        
        data = assert_success_response(response, 200)
        assert "session_id" in data

    def test_start_interview_invalid_topic(self, client, mock_app_globals):
        """Test starting interview with non-existent topic."""
        response = client.post("/interview/start", json={
            "topic": "NonExistentTopicXYZ12345",
            "num_questions": 3
        })
        
        assert_error_response(response, 404, "no valid questions")

    def test_start_interview_num_questions_too_high(self, client):
        """Test that num_questions is limited to 20."""
        response = client.post("/interview/start", json={
            "topic": "Python",
            "num_questions": 50  # Too many
        })
        
        assert response.status_code == 422  # Validation error

    def test_start_interview_num_questions_too_low(self, client):
        """Test that num_questions must be at least 1."""
        response = client.post("/interview/start", json={
            "topic": "Python",
            "num_questions": 0
        })
        
        assert response.status_code == 422

    def test_start_interview_current_question_structure(self, client, mock_app_globals):
        """Test that current question has correct structure."""
        response = client.post("/interview/start", json={
            "topic": "Python"
        })
        
        data = assert_success_response(response, 200)
        current_q = data["current_question"]
        
        assert "index" in current_q
        assert "question" in current_q
        assert "category" in current_q
        assert "difficulty" in current_q
        assert "correct_answer" not in current_q  # Should not expose answer

    def test_start_interview_without_data_loaded(self, client):
        """Test starting interview when data is not loaded."""
        with patch("app.df_questions", None):
            response = client.post("/interview/start", json={
                "topic": "Python"
            })
            
            assert_error_response(response, 503, "data not yet loaded")

    def test_start_interview_filters_by_difficulty(self, client, mock_app_globals, test_db):
        """Test that questions are filtered by user experience level."""
        # Create a user with specific experience level
        import database as db
        user = db.create_user("advanceduser", "advanced@example.com", "Pass123!", "Advanced User")
        db.update_user_profile(user["user_id"], {"experience_level": "Advanced"})
        
        response = client.post("/interview/start", json={
            "topic": "Python",
            "user_id": user["user_id"]
        })
        
        data = assert_success_response(response, 200)
        # Should successfully filter questions
        assert "session_id" in data

    def test_start_interview_creates_active_session(self, client, mock_app_globals):
        """Test that starting interview creates an active session."""
        with patch("app.active_interviews", {}) as mock_active:
            response = client.post("/interview/start", json={
                "topic": "Python"
            })
            
            data = assert_success_response(response, 200)
            session_id = data["session_id"]
            
            # Session should be in active_interviews
            assert session_id in mock_active


# ---------------------------------------------------------------------------
# Submit Answer Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestSubmitAnswer:
    """Test submitting answers during an interview."""

    def test_submit_answer_success(self, client, mock_app_globals, sample_interview_session):
        """Test successfully submitting an answer."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            with patch("app.model") as mock_model:
                # Mock similarity score
                mock_model.encode.return_value = np.array([[0.5, 0.5, 0.5]])
                
                response = client.post("/interview/answer", json={
                    "session_id": sample_interview_session["session_id"],
                    "question_index": 0,
                    "answer": "Python is a programming language"
                })
                
                data = assert_success_response(response, 200)
                assert "score" in data
                assert "passed" in data
                assert "status" in data
                assert "next_question" in data

    def test_submit_answer_passing_score(self, client, mock_app_globals, sample_interview_session):
        """Test submitting answer with passing score."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            with patch("app.model") as mock_model:
                # Mock high similarity (passing)
                mock_model.encode.return_value = np.array([[0.8, 0.8, 0.8]])
                
                # Mock cosine_similarity to return high score
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.85]])
                    
                    response = client.post("/interview/answer", json={
                        "session_id": sample_interview_session["session_id"],
                        "question_index": 0,
                        "answer": "Python is a high-level programming language"
                    })
                    
                    data = assert_success_response(response, 200)
                    assert data["passed"] is True
                    assert data["status"] == "PASS"
                    assert data["score"] >= 0.6  # Above threshold

    def test_submit_answer_failing_score(self, client, mock_app_globals, sample_interview_session):
        """Test submitting answer with failing score."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            with patch("app.model") as mock_model:
                mock_model.encode.return_value = np.array([[0.1, 0.1, 0.1]])
                
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.3]])
                    
                    response = client.post("/interview/answer", json={
                        "session_id": sample_interview_session["session_id"],
                        "question_index": 0,
                        "answer": "I don't know"
                    })
                    
                    data = assert_success_response(response, 200)
                    assert data["passed"] is False
                    assert data["status"] == "FAIL"
                    assert data["score"] < 0.6  # Below threshold

    def test_submit_answer_returns_next_question(self, client, mock_app_globals, sample_interview_session):
        """Test that submitting answer returns next question."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            with patch("app.model") as mock_model:
                mock_model.encode.return_value = np.array([[0.7, 0.7, 0.7]])
                
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.75]])
                    
                    response = client.post("/interview/answer", json={
                        "session_id": sample_interview_session["session_id"],
                        "question_index": 0,
                        "answer": "Python is a programming language"
                    })
                    
                    data = assert_success_response(response, 200)
                    assert data["next_question"] is not None
                    assert data["next_question"]["index"] == 1
                    assert data["completed"] is False

    def test_submit_last_answer_completes_interview(self, client, mock_app_globals, sample_interview_session):
        """Test that submitting last answer completes interview."""
        session = sample_interview_session.copy()
        session["current_question"] = 1  # On last question
        
        with patch.dict("app.active_interviews", {session["session_id"]: session}):
            with patch("app.model") as mock_model:
                mock_model.encode.return_value = np.array([[0.7, 0.7, 0.7]])
                
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.75]])
                    
                    response = client.post("/interview/answer", json={
                        "session_id": session["session_id"],
                        "question_index": 1,
                        "answer": "OOP includes encapsulation and inheritance"
                    })
                    
                    data = assert_success_response(response, 200)
                    assert data["next_question"] is None
                    assert data["completed"] is True

    def test_submit_answer_invalid_session(self, client):
        """Test submitting answer for non-existent session."""
        response = client.post("/interview/answer", json={
            "session_id": "nonexistent-session",
            "question_index": 0,
            "answer": "Some answer"
        })
        
        assert_error_response(response, 404, "session not found")

    def test_submit_answer_already_completed(self, client, completed_interview_session):
        """Test submitting answer to already completed interview."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.post("/interview/answer", json={
                "session_id": completed_interview_session["session_id"],
                "question_index": 0,
                "answer": "Some answer"
            })
            
            assert_error_response(response, 400, "already completed")

    def test_submit_answer_invalid_question_index(self, client, sample_interview_session):
        """Test submitting answer with invalid question index."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            response = client.post("/interview/answer", json={
                "session_id": sample_interview_session["session_id"],
                "question_index": 999,  # Out of bounds
                "answer": "Some answer"
            })
            
            assert_error_response(response, 400, "invalid question index")

    def test_submit_answer_empty_answer(self, client):
        """Test submitting empty answer."""
        response = client.post("/interview/answer", json={
            "session_id": "session_123",
            "question_index": 0,
            "answer": "   "  # Empty/whitespace only
        })
        
        assert response.status_code == 422  # Validation error

    def test_submit_answer_too_long(self, client):
        """Test submitting answer that's too long."""
        response = client.post("/interview/answer", json={
            "session_id": "session_123",
            "question_index": 0,
            "answer": "x" * 15000  # Exceeds 10,000 limit
        })
        
        assert response.status_code == 422

    def test_submit_answer_progress_tracking(self, client, mock_app_globals, sample_interview_session):
        """Test that progress is correctly tracked."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            with patch("app.model") as mock_model:
                mock_model.encode.return_value = np.array([[0.7, 0.7, 0.7]])
                
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.75]])
                    
                    response = client.post("/interview/answer", json={
                        "session_id": sample_interview_session["session_id"],
                        "question_index": 0,
                        "answer": "Python is a programming language"
                    })
                    
                    data = assert_success_response(response, 200)
                    assert "progress" in data
                    assert data["progress"]["answered"] == 1
                    assert data["progress"]["total"] == 2

    def test_submit_answer_stores_answer_data(self, client, mock_app_globals, sample_interview_session):
        """Test that answer data is properly stored in session."""
        session = sample_interview_session.copy()
        
        with patch.dict("app.active_interviews", {session["session_id"]: session}):
            with patch("app.model") as mock_model:
                mock_model.encode.return_value = np.array([[0.7, 0.7, 0.7]])
                
                with patch("app.cosine_similarity") as mock_cosine:
                    mock_cosine.return_value = np.array([[0.75]])
                    
                    client.post("/interview/answer", json={
                        "session_id": session["session_id"],
                        "question_index": 0,
                        "answer": "Test answer"
                    })
                    
                    # Check that answer was stored
                    assert len(session["answers"]) == 1
                    answer = session["answers"][0]
                    assert answer["user_answer"] == "Test answer"
                    assert "score" in answer
                    assert "passed" in answer


# ---------------------------------------------------------------------------
# Get Results Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetResults:
    """Test retrieving interview results."""

    def test_get_results_success(self, client, mock_app_globals, completed_interview_session):
        """Test getting results for completed interview."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            assert data["session_id"] == completed_interview_session["session_id"]
            assert "average_score" in data
            assert "pass_rate" in data
            assert "answers" in data
            assert "recommendations" in data
            assert "summary" in data

    def test_get_results_calculates_average_score(self, client, mock_app_globals, completed_interview_session):
        """Test that average score is calculated correctly."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            # Average of 0.85 and 0.55 = 0.7
            assert data["average_score"] == 0.7

    def test_get_results_calculates_pass_rate(self, client, mock_app_globals, completed_interview_session):
        """Test that pass rate is calculated correctly."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            # 1 passed out of 2 = 50%
            assert data["pass_rate"] == 50.0
            assert data["passed"] == 1

    def test_get_results_summary_passed(self, client, mock_app_globals, completed_interview_session):
        """Test results summary when interview is passed."""
        session = completed_interview_session.copy()
        # Make both answers passing
        session["answers"][1]["passed"] = True
        session["answers"][1]["score"] = 0.75
        
        with patch.dict("app.active_interviews", {session["session_id"]: session}):
            response = client.get(f"/interview/results/{session['session_id']}")
            
            data = assert_success_response(response, 200)
            assert data["pass_rate"] == 100.0
            assert data["summary"]["status"] == "PASSED"

    def test_get_results_summary_failed(self, client, mock_app_globals, completed_interview_session):
        """Test results summary when interview is failed."""
        session = completed_interview_session.copy()
        # Make both answers failing
        session["answers"][0]["passed"] = False
        session["answers"][0]["score"] = 0.4
        
        with patch.dict("app.active_interviews", {session["session_id"]: session}):
            response = client.get(f"/interview/results/{session['session_id']}")
            
            data = assert_success_response(response, 200)
            assert data["pass_rate"] < 60.0
            assert data["summary"]["status"] == "FAILED"

    def test_get_results_includes_recommendations(self, client, mock_app_globals, completed_interview_session):
        """Test that results include course recommendations."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)

    def test_get_results_nonexistent_session(self, client, mock_app_globals):
        """Test getting results for non-existent session."""
        response = client.get("/interview/results/nonexistent-session")
        # May return 404 or 503 depending on implementation
        assert response.status_code in [404, 503]

    def test_get_results_incomplete_interview(self, client, mock_app_globals, sample_interview_session):
        """Test getting results for incomplete interview."""
        # Add session to mock_app_globals
        mock_app_globals[sample_interview_session["session_id"]] = sample_interview_session
        
        response = client.get(
            f"/interview/results/{sample_interview_session['session_id']}"
        )
        
        # May return 400, 422, or 503 depending on implementation
        assert response.status_code in [400, 422, 503]


# ---------------------------------------------------------------------------
# Session Management Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestSessionManagement:
    """Test interview session management endpoints."""

    def test_list_sessions(self, client, mock_app_globals, sample_interview_session):
        """Test listing all active sessions."""
        # Clear and add only one session
        mock_app_globals.clear()
        mock_app_globals[sample_interview_session["session_id"]] = sample_interview_session
        
        response = client.get("/interview/sessions")
        
        data = assert_success_response(response, 200)
        assert "sessions" in data
        assert "total_sessions" in data
        assert data["total_sessions"] == 1
        assert len(data["sessions"]) == 1

    def test_list_sessions_includes_progress(self, client, sample_interview_session):
        """Test that session list includes progress information."""
        with patch.dict("app.active_interviews", {
            sample_interview_session["session_id"]: sample_interview_session
        }):
            response = client.get("/interview/sessions")
            
            data = assert_success_response(response, 200)
            session = data["sessions"][0]
            
            assert "session_id" in session
            assert "topic" in session
            assert "progress" in session
            assert "completed" in session
            assert "started_at" in session

    def test_list_sessions_empty(self, client, mock_app_globals):
        """Test listing sessions when none exist."""
        # Ensure sessions dict is empty
        mock_app_globals.clear()
        
        response = client.get("/interview/sessions")
        
        data = assert_success_response(response, 200)
        assert data["total_sessions"] == 0
        assert data["sessions"] == []

    def test_delete_session_success(self, client, mock_app_globals, sample_interview_session):
        """Test deleting an active session."""
        # Clear and add session
        mock_app_globals.clear()
        session_id = sample_interview_session["session_id"]
        mock_app_globals[session_id] = sample_interview_session
        
        response = client.delete(f"/interview/{session_id}")
        
        data = assert_success_response(response, 200)
        assert "message" in data
        # Session should be removed
        assert session_id not in mock_app_globals

    def test_delete_session_nonexistent(self, client):
        """Test deleting a non-existent session."""
        response = client.delete("/interview/nonexistent-session")
        assert_error_response(response, 404, "session not found")


# ---------------------------------------------------------------------------
# Course Recommendations Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestCourseRecommendations:
    """Test course recommendation logic."""

    def test_recommendations_based_on_failed_categories(self, client, mock_app_globals, completed_interview_session):
        """Test that recommendations prioritize failed categories."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            recommendations = data["recommendations"]
            
            # Should have recommendations
            assert len(recommendations) > 0
            
            # Each recommendation should have required fields
            for rec in recommendations:
                assert "course_title" in rec
                assert "platform" in rec
                assert "difficulty" in rec
                assert "url" in rec

    def test_recommendations_limit_three(self, client, mock_app_globals, completed_interview_session):
        """Test that at most 3 recommendations are returned."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            assert len(data["recommendations"]) <= 3

    def test_recommendations_include_relevance_score(self, client, mock_app_globals, completed_interview_session):
        """Test that recommendations include relevance scores."""
        with patch.dict("app.active_interviews", {
            completed_interview_session["session_id"]: completed_interview_session
        }):
            response = client.get(
                f"/interview/results/{completed_interview_session['session_id']}"
            )
            
            data = assert_success_response(response, 200)
            
            for rec in data["recommendations"]:
                assert "relevance_score" in rec
                assert 0 <= rec["relevance_score"] <= 1
