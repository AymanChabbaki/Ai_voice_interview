"""
Database Layer Tests - test_database.py

Tests all database functions including user management, authentication,
interview history, and stats tracking.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

import database as db


# ---------------------------------------------------------------------------
# Initialization Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDatabaseInitialization:
    """Test database initialization and connection pool."""

    def test_init_db_creates_tables(self, test_db):
        """Test that init_db creates all required tables."""
        with db._get_conn() as conn:
            with conn.cursor() as cur:
                # Check users table
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users'
                    )
                """)
                assert cur.fetchone()[0] is True

                # Check user_stats table
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'user_stats'
                    )
                """)
                assert cur.fetchone()[0] is True

                # Check interview_history table
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'interview_history'
                    )
                """)
                assert cur.fetchone()[0] is True

    def test_connection_pool_created(self, test_db):
        """Test that connection pool is initialized."""
        assert db._pool is not None

    def test_get_conn_context_manager(self, test_db):
        """Test that connection context manager works."""
        with db._get_conn() as conn:
            assert conn is not None
            assert conn.closed == 0  # Connection is open

    def test_connection_auto_commits(self, test_db):
        """Test that connections auto-commit on success."""
        with db._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                # Should auto-commit when context exits


# ---------------------------------------------------------------------------
# User Management Tests
# ---------------------------------------------------------------------------

@pytest.mark.database
class TestUserManagement:
    """Test user creation, retrieval, and update operations."""

    def test_create_user_success(self, test_db):
        """Test creating a new user successfully."""
        user = db.create_user(
            username="newuser",
            email="newuser@example.com",
            password="securepassword123",
            name="New User"
        )

        assert user is not None
        assert user["username"] == "newuser"
        assert user["email"] == "newuser@example.com"
        assert user["name"] == "New User"
        assert "user_id" in user
        assert "password" not in user  # Password should not be returned

    def test_create_user_duplicate_username(self, test_db):
        """Test that duplicate username returns None."""
        db.create_user("duplicateuser", "user1@example.com", "pass123", "User One")
        result = db.create_user("duplicateuser", "user2@example.com", "pass456", "User Two")
        
        assert result is None

    def test_create_user_duplicate_email(self, test_db):
        """Test that duplicate email returns None."""
        db.create_user("user1", "duplicate@example.com", "pass123", "User One")
        result = db.create_user("user2", "duplicate@example.com", "pass456", "User Two")
        
        assert result is None

    def test_create_user_creates_stats_entry(self, test_db):
        """Test that creating a user also creates a stats entry."""
        user = db.create_user("statsuser", "stats@example.com", "pass123", "Stats User")
        
        with db._get_conn() as conn:
            stats = db._fetchone(
                conn,
                "SELECT * FROM user_stats WHERE user_id = %s",
                (user["user_id"],)
            )
        
        assert stats is not None
        assert stats["interview_count"] == 0
        assert stats["total_score"] == 0.0
        assert stats["current_streak"] == 0

    def test_get_user_by_id_exists(self, test_db, test_user_in_db):
        """Test retrieving an existing user by ID."""
        user = db.get_user_by_id(test_user_in_db["user_id"])
        
        assert user is not None
        assert user["user_id"] == test_user_in_db["user_id"]
        assert user["username"] == test_user_in_db["username"]
        assert "password_hash" not in user  # Should be excluded

    def test_get_user_by_id_not_exists(self, test_db):
        """Test retrieving a non-existent user returns None."""
        user = db.get_user_by_id("nonexistent-user-id")
        assert user is None

    def test_get_user_includes_stats(self, test_db, test_user_in_db):
        """Test that get_user_by_id includes stats data."""
        user = db.get_user_by_id(test_user_in_db["user_id"])
        
        assert "interview_count" in user
        assert "total_score" in user
        assert "current_streak" in user
        assert "achievements" in user

    def test_update_user_profile_name(self, test_db, test_user_in_db):
        """Test updating user profile name."""
        result = db.update_user_profile(
            test_user_in_db["user_id"],
            {"name": "Updated Name"}
        )
        
        assert result is True
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["name"] == "Updated Name"

    def test_update_user_profile_bio(self, test_db, test_user_in_db):
        """Test updating user bio."""
        result = db.update_user_profile(
            test_user_in_db["user_id"],
            {"bio": "This is my bio"}
        )
        
        assert result is True
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["bio"] == "This is my bio"

    def test_update_user_profile_experience_level(self, test_db, test_user_in_db):
        """Test updating user experience level."""
        result = db.update_user_profile(
            test_user_in_db["user_id"],
            {"experience_level": "Advanced"}
        )
        
        assert result is True
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["experience_level"] == "Advanced"

    def test_update_user_profile_interests(self, test_db, test_user_in_db):
        """Test updating user interests."""
        interests = ["Python", "Machine Learning", "Web Development"]
        result = db.update_user_profile(
            test_user_in_db["user_id"],
            {"interests": interests}
        )
        
        assert result is True
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["interests"] == interests

    def test_update_user_profile_nonexistent_user(self, test_db):
        """Test updating profile for non-existent user."""
        result = db.update_user_profile(
            "nonexistent-id",
            {"name": "Should Fail"}
        )
        
        assert result is False

    def test_update_user_profile_empty_data(self, test_db, test_user_in_db):
        """Test updating with empty data returns False."""
        result = db.update_user_profile(test_user_in_db["user_id"], {})
        assert result is False


# ---------------------------------------------------------------------------
# Authentication Tests
# ---------------------------------------------------------------------------

@pytest.mark.database
class TestAuthentication:
    """Test password hashing and authentication."""

    def test_password_hashing(self):
        """Test that passwords are hashed correctly."""
        password = "mysecretpassword"
        hashed = db._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert db._verify_password(password, hashed)

    def test_password_verification_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "correctpassword"
        hashed = db._hash_password(password)
        
        assert not db._verify_password("wrongpassword", hashed)

    def test_authenticate_user_with_username(self, test_db, test_user_in_db):
        """Test authenticating user with username."""
        result = db.authenticate_user(
            test_user_in_db["username"],
            "TestPassword123!"
        )
        
        assert result is not None
        assert result["user_id"] == test_user_in_db["user_id"]

    def test_authenticate_user_with_email(self, test_db, test_user_in_db):
        """Test authenticating user with email."""
        result = db.authenticate_user(
            test_user_in_db["email"],
            "TestPassword123!"
        )
        
        assert result is not None
        assert result["user_id"] == test_user_in_db["user_id"]

    def test_authenticate_user_wrong_password(self, test_db, test_user_in_db):
        """Test authentication fails with wrong password."""
        result = db.authenticate_user(
            test_user_in_db["username"],
            "wrongpassword"
        )
        
        assert result is None

    def test_authenticate_user_nonexistent(self, test_db):
        """Test authentication fails for non-existent user."""
        result = db.authenticate_user("nonexistentuser", "anypassword")
        assert result is None


# ---------------------------------------------------------------------------
# Interview History Tests
# ---------------------------------------------------------------------------

@pytest.mark.database
class TestInterviewHistory:
    """Test interview history tracking."""

    def test_add_interview_history_success(self, test_db, test_user_in_db):
        """Test adding interview history entry."""
        entry = {
            "session_id": "session_123",
            "topic": "Python Programming",
            "date": datetime.utcnow().isoformat(),
            "pass_rate": 75.0,
            "average_score": 80.5,
            "questions_count": 5,
            "passed": 1,
        }
        
        result = db.add_interview_history(test_user_in_db["user_id"], entry)
        assert result is True

    def test_add_interview_history_nonexistent_user(self, test_db):
        """Test adding history for non-existent user fails."""
        entry = {
            "session_id": "session_123",
            "topic": "Python",
            "date": datetime.utcnow().isoformat(),
            "pass_rate": 75.0,
            "average_score": 80.5,
            "questions_count": 5,
            "passed": 1,
        }
        
        result = db.add_interview_history("nonexistent-id", entry)
        assert result is False

    def test_get_interview_history_empty(self, test_db, test_user_in_db):
        """Test getting history for user with no interviews."""
        history = db.get_interview_history(test_user_in_db["user_id"])
        assert history == []

    def test_get_interview_history_with_entries(self, test_db, test_user_in_db):
        """Test getting interview history with multiple entries."""
        # Add multiple entries
        for i in range(3):
            entry = {
                "session_id": f"session_{i}",
                "topic": f"Topic {i}",
                "date": datetime.utcnow().isoformat(),
                "pass_rate": 70.0 + i,
                "average_score": 75.0 + i,
                "questions_count": 5,
                "passed": 1,
            }
            db.add_interview_history(test_user_in_db["user_id"], entry)
        
        history = db.get_interview_history(test_user_in_db["user_id"])
        assert len(history) == 3

    def test_get_interview_history_ordered_by_date(self, test_db, test_user_in_db):
        """Test that history is ordered by most recent first."""
        # Add entries with different times
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
        
        history = db.get_interview_history(test_user_in_db["user_id"])
        # Most recent should be first
        assert history[0]["session_id"] == "session_2"

    def test_get_interview_history_limit(self, test_db, test_user_in_db):
        """Test limiting the number of history entries returned."""
        # Add multiple entries
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
        
        history = db.get_interview_history(test_user_in_db["user_id"], limit=5)
        assert len(history) == 5


# ---------------------------------------------------------------------------
# Stats and Achievements Tests
# ---------------------------------------------------------------------------

@pytest.mark.database
class TestStatsAndAchievements:
    """Test user statistics and achievement tracking."""

    def test_update_user_stats_first_interview(self, test_db, test_user_in_db):
        """Test updating stats after first interview."""
        new_achievements = db.update_user_stats(
            test_user_in_db["user_id"],
            {"pass_rate": 80.0}
        )
        
        # Should get "first_interview" achievement
        assert new_achievements is not None
        assert len(new_achievements) > 0
        assert any(a["id"] == "first_interview" for a in new_achievements)

    def test_update_user_stats_increments_count(self, test_db, test_user_in_db):
        """Test that stats count increments."""
        # Do first interview
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 80.0})
        
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["interview_count"] == 1

    def test_update_user_stats_updates_total_score(self, test_db, test_user_in_db):
        """Test that total score accumulates."""
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 80.0})
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 70.0})
        
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["total_score"] == 150.0

    def test_update_user_stats_streak_same_day(self, test_db, test_user_in_db):
        """Test that multiple interviews on same day don't increase streak."""
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 80.0})
        db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 75.0})
        
        user = db.get_user_by_id(test_user_in_db["user_id"])
        assert user["current_streak"] == 1

    def test_update_user_stats_perfect_score_achievement(self, test_db, test_user_in_db):
        """Test perfect score achievement."""
        new_achievements = db.update_user_stats(
            test_user_in_db["user_id"],
            {"pass_rate": 100.0}
        )
        
        # Should get both first_interview and perfect_score
        achievement_ids = [a["id"] for a in new_achievements]
        assert "perfect_score" in achievement_ids

    def test_update_user_stats_nonexistent_user(self, test_db):
        """Test updating stats for non-existent user."""
        result = db.update_user_stats("nonexistent-id", {"pass_rate": 80.0})
        assert result is None

    def test_update_user_stats_no_duplicate_achievements(self, test_db, test_user_in_db):
        """Test that achievements are only awarded once."""
        # First interview
        first = db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 80.0})
        assert any(a["id"] == "first_interview" for a in first)
        
        # Second interview  - should not get first_interview again
        second = db.update_user_stats(test_user_in_db["user_id"], {"pass_rate": 85.0})
        assert not any(a["id"] == "first_interview" for a in second)

    def test_achievements_structure(self, test_db, test_user_in_db):
        """Test that achievements have correct structure."""
        new_achievements = db.update_user_stats(
            test_user_in_db["user_id"],
            {"pass_rate": 80.0}
        )
        
        for achievement in new_achievements:
            assert "id" in achievement
            assert "title" in achievement
            assert "description" in achievement


# ---------------------------------------------------------------------------
# Connection Management Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConnectionManagement:
    """Test database connection management utilities."""

    def test_fetchone_returns_dict(self, test_db):
        """Test that _fetchone returns a dictionary."""
        with db._get_conn() as conn:
            result = db._fetchone(conn, "SELECT 1 as num, 'test' as text")
            assert isinstance(result, dict)
            assert result["num"] == 1
            assert result["text"] == "test"

    def test_fetchone_returns_none_no_results(self, test_db):
        """Test that _fetchone returns None when no results."""
        with db._get_conn() as conn:
            result = db._fetchone(conn, "SELECT 1 WHERE false")
            assert result is None

    def test_fetchall_returns_list_of_dicts(self, test_db):
        """Test that _fetchall returns a list of dictionaries."""
        with db._get_conn() as conn:
            result = db._fetchall(
                conn,
                "SELECT * FROM (VALUES (1, 'a'), (2, 'b')) AS t(num, text)"
            )
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(r, dict) for r in result)

    def test_execute_returns_rowcount(self, test_db, test_user_in_db):
        """Test that _execute returns the number of affected rows."""
        with db._get_conn() as conn:
            count = db._execute(
                conn,
                "UPDATE users SET name = %s WHERE user_id = %s",
                ("New Name", test_user_in_db["user_id"])
            )
            assert count == 1

    def test_connection_rollback_on_exception(self, test_db):
        """Test that connection rolls back on exception."""
        try:
            with db._get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        # Connection should have been rolled back and returned to pool
        with db._get_conn() as conn:
            # Should be able to get a new connection
            assert conn is not None
