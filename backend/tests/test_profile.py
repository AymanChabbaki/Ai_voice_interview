"""
Profile and Stats Tests - test_profile.py

Tests user profile management, statistics tracking, analytics,
and interview history endpoints.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from app import create_access_token

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
# Profile Retrieval Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetProfile:
    """Test user profile retrieval."""

    def test_get_profile_success(self, client, test_db, test_user_in_db):
        """Test successfully getting a user profile."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert "profile" in data
        
        profile = data["profile"]
        assert profile["user_id"] == test_user_in_db["user_id"]
        assert profile["username"] == test_user_in_db["username"]
        assert profile["email"] == test_user_in_db["email"]

    def test_get_profile_includes_stats(self, client, test_db, test_user_in_db):
        """Test that profile includes statistics."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        profile = data["profile"]
        
        assert "interview_count" in profile
        assert "total_score" in profile
        assert "current_streak" in profile
        assert "best_streak" in profile
        assert "achievements" in profile

    def test_get_profile_nonexistent_user(self, client, test_db, test_user_in_db):
        """Test getting profile for non-existent user."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            "/profile/nonexistent-user-id",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert_error_response(response, 404, "not found")

    def test_get_profile_requires_auth(self, client, test_user_in_db):
        """Test that getting profile requires authentication."""
        response = client.get(f"/profile/{test_user_in_db['user_id']}")
        assert response.status_code == 403

    def test_get_profile_excludes_password(self, client, test_db, test_user_in_db):
        """Test that profile does not include password hash."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        profile = data["profile"]
        
        assert "password" not in profile
        assert "password_hash" not in profile


# ---------------------------------------------------------------------------
# Profile Update Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestUpdateProfile:
    """Test user profile updates."""

    def test_update_profile_name(self, client, test_db, test_user_in_db):
        """Test updating user name."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Name"}
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert data["profile"]["name"] == "Updated Name"

    def test_update_profile_bio(self, client, test_db, test_user_in_db):
        """Test updating user bio."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"bio": "This is my new bio"}
        )
        
        data = assert_success_response(response, 200)
        assert data["profile"]["bio"] == "This is my new bio"

    def test_update_profile_experience_level(self, client, test_db, test_user_in_db):
        """Test updating user experience level."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"experience_level": "Advanced"}
        )
        
        data = assert_success_response(response, 200)
        assert data["profile"]["experience_level"] == "Advanced"

    def test_update_profile_interests(self, client, test_db, test_user_in_db):
        """Test updating user interests."""
        token = create_access_token(test_user_in_db["user_id"])
        interests = ["Python", "Machine Learning", "Web Development"]
        
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"interests": interests}
        )
        
        data = assert_success_response(response, 200)
        assert data["profile"]["interests"] == interests

    def test_update_profile_multiple_fields(self, client, test_db, test_user_in_db):
        """Test updating multiple profile fields at once."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "New Name",
                "bio": "New Bio",
                "experience_level": "Expert"
            }
        )
        
        data = assert_success_response(response, 200)
        profile = data["profile"]
        assert profile["name"] == "New Name"
        assert profile["bio"] == "New Bio"
        assert profile["experience_level"] == "Expert"

    def test_update_profile_invalid_experience_level(self, client, test_db, test_user_in_db):
        """Test updating with invalid experience level."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"experience_level": "InvalidLevel"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_update_profile_unauthorized(self, client, test_db, multiple_test_users):
        """Test that user can only update their own profile."""
        user1, user2, _ = multiple_test_users
        
        token = create_access_token(user1["user_id"])
        response = client.put(
            f"/profile/{user2['user_id']}",  # Trying to update different user
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Hacked Name"}
        )
        
        assert_error_response(response, 403, "not authorised")

    def test_update_profile_requires_auth(self, client, test_user_in_db):
        """Test that updating profile requires authentication."""
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            json={"name": "New Name"}
        )
        
        assert response.status_code == 403

    def test_update_profile_nonexistent_user(self, client, test_db, test_user_in_db):
        """Test updating non-existent user profile."""
        token = create_access_token("nonexistent-user-id")
        response = client.put(
            "/profile/nonexistent-user-id",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "New Name"}
        )
        
        assert_error_response(response, 404, "not found")


# ---------------------------------------------------------------------------
# Stats Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetStats:
    """Test user statistics retrieval."""

    def test_get_stats_success(self, client, test_db, test_user_in_db):
        """Test getting user statistics."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert "stats" in data
        
        stats = data["stats"]
        assert "interview_count" in stats
        assert "total_score" in stats
        assert "average_score" in stats
        assert "experience_level" in stats
        assert "interests" in stats
        assert "current_streak" in stats
        assert "best_streak" in stats
        assert "achievements" in stats

    def test_get_stats_calculates_average(self, client, test_db, test_user_in_db):
        """Test that average score is calculated correctly."""
        # Add some interview history and update stats
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 80.0})
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 90.0})
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        stats = data["stats"]
        
        assert stats["interview_count"] == 2
        assert stats["total_score"] == 170.0
        assert stats["average_score"] == 85.0

    def test_get_stats_new_user(self, client, test_db, test_user_in_db):
        """Test stats for new user with no interviews."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        stats = data["stats"]
        
        assert stats["interview_count"] == 0
        assert stats["total_score"] == 0.0
        assert stats["current_streak"] == 0

    def test_get_stats_requires_auth(self, client, test_user_in_db):
        """Test that getting stats requires authentication."""
        response = client.get(f"/profile/{test_user_in_db['user_id']}/stats")
        assert response.status_code == 403

    def test_get_stats_nonexistent_user(self, client, test_db, test_user_in_db):
        """Test getting stats for non-existent user."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            "/profile/nonexistent-user-id/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert_error_response(response, 404, "not found")


# ---------------------------------------------------------------------------
# History Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetHistory:
    """Test interview history retrieval."""

    def test_get_history_empty(self, client, test_db, test_user_in_db):
        """Test getting history for user with no interviews."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert data["history"] == []
        assert data["total_interviews"] == 0

    def test_get_history_with_interviews(self, client, test_db, test_user_in_db):
        """Test getting history with multiple interviews."""
        # Add interview history
        for i in range(3):
            entry = {
                "session_id": f"session_{i}",
                "topic": f"Topic {i}",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 70.0 + i * 5,
                "average_score": 75.0 + i * 5,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert len(data["history"]) == 3
        assert data["total_interviews"] == 3

    def test_get_history_ordered_by_date(self, client, test_db, test_user_in_db):
        """Test that history is ordered by most recent first."""
        # Add interviews at different times
        for i in range(3):
            entry = {
                "session_id": f"session_{i}",
                "topic": f"Topic {i}",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 70.0,
                "average_score": 75.0,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        # Most recent should be first
        assert data["history"][0]["session_id"] == "session_2"

    def test_get_history_with_limit(self, client, test_db, test_user_in_db):
        """Test limiting history results."""
        # Add multiple interviews
        for i in range(10):
            entry = {
                "session_id": f"session_{i}",
                "topic": f"Topic {i}",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 70.0,
                "average_score": 75.0,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert len(data["history"]) == 5

    def test_get_history_limit_validation(self, client, test_db, test_user_in_db):
        """Test history limit validation."""
        token = create_access_token(test_user_in_db["user_id"])
        
        # Too small
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history?limit=0",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert_error_response(response, 400, "must be between")
        
        # Too large
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/history?limit=300",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert_error_response(response, 400, "must be between")

    def test_get_history_requires_auth(self, client, test_user_in_db):
        """Test that getting history requires authentication."""
        response = client.get(f"/profile/{test_user_in_db['user_id']}/history")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Analytics Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetAnalytics:
    """Test user analytics retrieval."""

    def test_get_analytics_no_interviews(self, client, test_db, test_user_in_db):
        """Test analytics for user with no interviews."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert data["analytics"]["total_interviews"] == 0

    def test_get_analytics_with_interviews(self, client, test_db, test_user_in_db):
        """Test analytics with interview data."""
        # Add interview history
        for i in range(5):
            entry = {
                "session_id": f"session_{i}",
                "topic": "Python Programming",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 70.0 + i * 5,
                "average_score": 75.0,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        analytics = data["analytics"]
        
        assert analytics["total_interviews"] == 5
        assert "performance_trend" in analytics
        assert "category_breakdown" in analytics
        assert "current_streak" in analytics
        assert "best_streak" in analytics

    def test_get_analytics_performance_trend(self, client, test_db, test_user_in_db):
        """Test that performance trend is included."""
        # Add interviews
        for i in range(5):
            entry = {
                "session_id": f"session_{i}",
                "topic": "Python",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 60.0 + i * 10,
                "average_score": 75.0,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        trend = data["analytics"]["performance_trend"]
        
        assert isinstance(trend, list)
        assert len(trend) == 5
        # Each trend item should have date and score
        for item in trend:
            assert "date" in item
            assert "score" in item

    def test_get_analytics_category_breakdown(self, client, test_db, test_user_in_db):
        """Test category breakdown in analytics."""
        # Add interviews with different topics
        topics = ["Python", "JavaScript", "Python", "SQL"]
        for i, topic in enumerate(topics):
            entry = {
                "session_id": f"session_{i}",
                "topic": topic,
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 75.0,
                "average_score": 80.0,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            f"/profile/{test_user_in_db['user_id']}/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        breakdown = data["analytics"]["category_breakdown"]
        
        # Should have Python (2), JavaScript (1), SQL (1)
        assert "Python" in breakdown
        assert breakdown["Python"]["attempts"] == 2
        assert "average_score" in breakdown["Python"]

    def test_get_analytics_requires_auth(self, client, test_user_in_db):
        """Test that getting analytics requires authentication."""
        response = client.get(f"/profile/{test_user_in_db['user_id']}/analytics")
        assert response.status_code == 403

    def test_get_analytics_nonexistent_user(self, client, test_db, test_user_in_db):
        """Test analytics for non-existent user."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            "/profile/nonexistent-user-id/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert_error_response(response, 404, "not found")


# ---------------------------------------------------------------------------
# Update After Interview Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestUpdateAfterInterview:
    """Test updating profile after completing an interview."""

    def test_update_after_interview_success(self, client, test_db, test_user_in_db):
        """Test updating profile after interview completion."""
        token = create_access_token(test_user_in_db["user_id"])
        results = {
            "session_id": "session_123",
            "topic": "Python Programming",
            "pass_rate": 80.0,
            "average_score": 0.85,
            "total_questions": 5,
            "passed": 4,
        }
        
        response = client.post(
            f"/profile/{test_user_in_db['user_id']}/update-after-interview",
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
        assert "new_achievements" in data
        assert "current_streak" in data
        assert "profile" in data

    def test_update_after_interview_adds_history(self, client, test_db, test_user_in_db):
        """Test that update adds entry to interview history."""
        token = create_access_token(test_user_in_db["user_id"])
        results = {
            "session_id": "session_123",
            "topic": "Python Programming",
            "pass_rate": 75.0,
            "average_score": 0.80,
            "total_questions": 5,
            "passed": 4,
        }
        
        client.post(
            f"/profile/{test_user_in_db['user_id']}/update-after-interview",
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        # Check history was added
        history = db.get_interview_history(test_user_in_db["user_id"])
        assert len(history) == 1
        assert history[0]["session_id"] == "session_123"
        assert history[0]["topic"] == "Python Programming"

    def test_update_after_interview_updates_stats(self, client, test_db, test_user_in_db):
        """Test that update increments user stats."""
        token = create_access_token(test_user_in_db["user_id"])
        results = {
            "session_id": "session_123",
            "topic": "Python",
            "pass_rate": 80.0,
            "average_score": 0.85,
            "total_questions": 5,
            "passed": 4,
        }
        
        client.post(
            f"/profile/{test_user_in_db['user_id']}/update-after-interview",
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        # Check stats were updated
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["interview_count"] == 1
        assert user["total_score"] == 80.0

    def test_update_after_interview_returns_achievements(self, client, test_db, test_user_in_db):
        """Test that new achievements are returned."""
        token = create_access_token(test_user_in_db["user_id"])
        results = {
            "session_id": "session_123",
            "topic": "Python",
            "pass_rate": 80.0,
            "average_score": 0.85,
            "total_questions": 5,
            "passed": 4,
        }
        
        response = client.post(
            f"/profile/{test_user_in_db['user_id']}/update-after-interview",
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        data = assert_success_response(response, 200)
        # First interview should give achievement
        assert len(data["new_achievements"]) > 0

    def test_update_after_interview_unauthorized(self, client, test_db, multiple_test_users):
        """Test that user can only update their own profile."""
        user1, user2, _ = multiple_test_users
        
        token = create_access_token(user1["user_id"])
        results = {
            "session_id": "session_123",
            "topic": "Python",
            "pass_rate": 80.0,
            "average_score": 0.85,
            "total_questions": 5,
            "passed": 4,
        }
        
        response = client.post(
            f"/profile/{user2['user_id']}/update-after-interview",  # Different user
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        assert_error_response(response, 403, "not authorised")

    def test_update_after_interview_requires_auth(self, client, test_user_in_db):
        """Test that updating after interview requires authentication."""
        response = client.post(
            f"/profile/{test_user_in_db['user_id']}/update-after-interview",
            json={"session_id": "session_123", "topic": "Python", "pass_rate": 80.0}
        )
        
        assert response.status_code == 403

    def test_update_after_interview_nonexistent_user(self, client, test_db):
        """Test updating after interview for non-existent user."""
        token = create_access_token("nonexistent-user-id")
        results = {
            "session_id": "session_123",
            "topic": "Python",
            "pass_rate": 80.0,
            "average_score": 0.85,
            "total_questions": 5,
            "passed": 4,
        }
        
        response = client.post(
            "/profile/nonexistent-user-id/update-after-interview",
            headers={"Authorization": f"Bearer {token}"},
            json=results
        )
        
        assert_error_response(response, 404, "not found")
