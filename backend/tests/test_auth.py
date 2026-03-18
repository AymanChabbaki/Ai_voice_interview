"""
Authentication Tests - test_auth.py

Tests authentication endpoints including registration, login,
JWT token generation and validation, and protected routes.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from jose import jwt

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import ALGORITHM, SECRET_KEY, create_access_token

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
# Registration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, client, test_db):
        """Test successful user registration."""
        response = client.post("/register", json={
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User"
        })
        
        data = assert_success_response(response, 200)
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "newuser123"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_invalid_username_too_short(self, client):
        """Test registration fails with too short username."""
        response = client.post("/register", json={
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 422  # Validation error

    def test_register_invalid_username_special_chars(self, client):
        """Test registration fails with special characters in username."""
        response = client.post("/register", json={
            "username": "user@name!",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email."""
        response = client.post("/register", json={
            "username": "validuser",
            "email": "not-an-email",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        """Test registration fails with short password."""
        response = client.post("/register", json={
            "username": "validuser",
            "email": "test@example.com",
            "password": "short",  # Less than 8 characters
            "name": "Test User"
        })
        
        assert response.status_code == 422

    def test_register_name_too_short(self, client):
        """Test registration fails with short name."""
        response = client.post("/register", json={
            "username": "validuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "A"  # Too short
        })
        
        assert response.status_code == 422

    def test_register_duplicate_username(self, client, test_db, test_user_in_db):
        """Test registration fails with duplicate username."""
        response = client.post("/register", json={
            "username": test_user_in_db["username"],
            "email": "different@example.com",
            "password": "SecurePass123!",
            "name": "Different User"
        })
        
        assert_error_response(response, 400, "already exists")

    def test_register_duplicate_email(self, client, test_db, test_user_in_db):
        """Test registration fails with duplicate email."""
        response = client.post("/register", json={
            "username": "differentuser",
            "email": test_user_in_db["email"],
            "password": "SecurePass123!",
            "name": "Different User"
        })
        
        assert_error_response(response, 400, "already exists")

    def test_register_missing_fields(self, client):
        """Test registration fails with missing required fields."""
        response = client.post("/register", json={
            "username": "testuser"
            # Missing other required fields
        })
        
        assert response.status_code == 422

    def test_register_rate_limit(self, client, test_db):
        """Test registration rate limiting (5/minute)."""
        # Make 6 requests (exceeds limit of 5)
        for i in range(6):
            response = client.post("/register", json={
                "username": f"ratelimituser{i}",
                "email": f"ratelimit{i}@example.com",
                "password": "SecurePass123!",
                "name": f"Rate Limit User {i}"
            })
            
            if i < 5:
                # First 5 should succeed or fail due to other reasons
                assert response.status_code in [200, 400, 422]
            else:
                # 6th should be rate limited
                assert response.status_code == 429

    def test_register_returns_valid_token(self, client, test_db):
        """Test that registration returns a valid JWT token."""
        response = client.post("/register", json={
            "username": "tokenuser",
            "email": "token@example.com",
            "password": "SecurePass123!",
            "name": "Token User"
        })
        
        data = assert_success_response(response, 200)
        token = data["access_token"]
        
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "sub" in payload  # User ID
        assert "exp" in payload  # Expiration
        assert "iat" in payload  # Issued at


# ---------------------------------------------------------------------------
# Login Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestLogin:
    """Test user login endpoint."""

    def test_login_success_with_username(self, client, test_db, test_user_in_db):
        """Test successful login with username."""
        response = client.post("/login", json={
            "username": test_user_in_db["username"],
            "password": "TestPassword123!"
        })
        
        data = assert_success_response(response, 200)
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user_in_db["username"]

    def test_login_success_with_email(self, client, test_db, test_user_in_db):
        """Test successful login with email."""
        response = client.post("/login", json={
            "username": test_user_in_db["email"],  # Can use email in username field
            "password": "TestPassword123!"
        })
        
        data = assert_success_response(response, 200)
        assert "access_token" in data
        assert data["user"]["email"] == test_user_in_db["email"]

    def test_login_wrong_password(self, client, test_db, test_user_in_db):
        """Test login fails with wrong password."""
        response = client.post("/login", json={
            "username": test_user_in_db["username"],
            "password": "WrongPassword123!"
        })
        
        assert_error_response(response, 401, "incorrect")

    def test_login_nonexistent_user(self, client, test_db):
        """Test login fails for non-existent user."""
        response = client.post("/login", json={
            "username": "nonexistentuser",
            "password": "AnyPassword123!"
        })
        
        assert_error_response(response, 401, "incorrect")

    def test_login_missing_password(self, client):
        """Test login fails without password."""
        response = client.post("/login", json={
            "username": "testuser"
            # Missing password
        })
        
        assert response.status_code == 422

    def test_login_missing_username(self, client):
        """Test login fails without username."""
        response = client.post("/login", json={
            "password": "TestPassword123!"
            # Missing username
        })
        
        assert response.status_code == 422

    def test_login_rate_limit(self, client, test_db, test_user_in_db):
        """Test login rate limiting (10/minute)."""
        # Make 11 requests (exceeds limit of 10)
        for i in range(11):
            response = client.post("/login", json={
                "username": test_user_in_db["username"],
                "password": "TestPassword123!"
            })
            
            if i < 10:
                # First 10 should succeed
                assert response.status_code in [200, 401]
            else:
                # 11th should be rate limited
                assert response.status_code == 429

    def test_login_returns_valid_token(self, client, test_db, test_user_in_db):
        """Test that login returns a valid JWT token."""
        response = client.post("/login", json={
            "username": test_user_in_db["username"],
            "password": "TestPassword123!"
        })
        
        data = assert_success_response(response, 200)
        token = data["access_token"]
        
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == test_user_in_db["user_id"]

    def test_login_returns_user_data(self, client, test_db, test_user_in_db):
        """Test that login returns complete user data."""
        response = client.post("/login", json={
            "username": test_user_in_db["username"],
            "password": "TestPassword123!"
        })
        
        data = assert_success_response(response, 200)
        user = data["user"]
        
        assert user["user_id"] == test_user_in_db["user_id"]
        assert user["username"] == test_user_in_db["username"]
        assert user["email"] == test_user_in_db["email"]
        assert "interview_count" in user
        assert "achievements" in user


# ---------------------------------------------------------------------------
# JWT Token Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test creating a JWT access token."""
        user_id = "test-user-id-123"
        token = create_access_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id

    def test_token_contains_expiration(self):
        """Test that token contains expiration time."""
        token = create_access_token("user-123")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in payload
        assert "iat" in payload
        
        # Check expiration is in the future
        exp_time = datetime.fromtimestamp(payload["exp"])
        assert exp_time > datetime.utcnow()

    def test_token_expiration_time(self):
        """Test token expiration time is correct."""
        token = create_access_token("user-123")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        
        # Should be approximately ACCESS_TOKEN_EXPIRE_MINUTES
        delta = exp_time - iat_time
        # Allow some margin for execution time
        assert timedelta(minutes=59) < delta < timedelta(minutes=61)

    def test_expired_token_rejected(self, client, test_db, test_user_in_db):
        """Test that expired tokens are rejected."""
        # Create an expired token
        payload = {
            "sub": test_user_in_db["user_id"],
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # Try to use expired token
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert_error_response(response, 401, "invalid or expired")

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid-token-string"}
        )
        
        assert_error_response(response, 401)

    def test_token_with_wrong_secret_rejected(self, client, test_user_in_db):
        """Test that tokens signed with wrong secret are rejected."""
        payload = {
            "sub": test_user_in_db["user_id"],
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }
        wrong_token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)
        
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )
        
        assert_error_response(response, 401)


# ---------------------------------------------------------------------------
# Protected Route Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestProtectedRoutes:
    """Test authentication requirement for protected routes."""

    def test_me_endpoint_requires_auth(self, client):
        """Test /me endpoint requires authentication."""
        response = client.get("/me")
        assert response.status_code == 403  # Forbidden without auth

    def test_me_endpoint_with_valid_token(self, client, test_db, test_user_in_db):
        """Test /me endpoint with valid token."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        assert "user" in data
        assert data["user"]["user_id"] == test_user_in_db["user_id"]

    def test_me_endpoint_returns_full_user_data(self, client, test_db, test_user_in_db):
        """Test that /me returns complete user profile."""
        token = create_access_token(test_user_in_db["user_id"])
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = assert_success_response(response, 200)
        user = data["user"]
        
        assert "username" in user
        assert "email" in user
        assert "name" in user
        assert "interview_count" in user
        assert "achievements" in user
        assert "password_hash" not in user  # Should not be exposed

    @patch("database.get_user_by_id")
    def test_me_endpoint_nonexistent_user(self, mock_get_user, client):
        """Test /me fails for non-existent user in token."""
        mock_get_user.return_value = None  # User not found in database
        
        token = create_access_token("nonexistent-user-id")
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert_error_response(response, 404, "not found")

    def test_profile_endpoint_requires_auth(self, client, test_user_in_db):
        """Test profile endpoints require authentication."""
        response = client.get(f"/profile/{test_user_in_db['user_id']}")
        assert response.status_code == 403

    def test_update_profile_requires_auth(self, client, test_user_in_db):
        """Test update profile requires authentication."""
        response = client.put(
            f"/profile/{test_user_in_db['user_id']}",
            json={"name": "New Name"}
        )
        assert response.status_code == 403

    def test_bearer_token_format_required(self, client, test_db, test_user_in_db):
        """Test that Bearer token format is required."""
        token = create_access_token(test_user_in_db["user_id"])
        
        # Without "Bearer" prefix
        response = client.get(
            "/me",
            headers={"Authorization": token}
        )
        assert response.status_code == 403

    def test_authorization_header_required(self, client):
        """Test that Authorization header is required."""
        response = client.get("/me")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Token Security Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTokenSecurity:
    """Test JWT token security features."""

    def test_token_contains_user_id_only(self):
        """Test that token only contains user ID, not sensitive data."""
        user_id = "test-user-123"
        token = create_access_token(user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Should only contain standard JWT claims
        assert set(payload.keys()) == {"sub", "exp", "iat"}
        assert payload["sub"] == user_id

    def test_different_users_get_different_tokens(self):
        """Test that different users get different tokens."""
        token1 = create_access_token("user-1")
        token2 = create_access_token("user-2")
        
        assert token1 != token2
        
        payload1 = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
        payload2 = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload1["sub"] != payload2["sub"]

    def test_token_algorithm_is_hs256(self):
        """Test that HS256 algorithm is used."""
        token = create_access_token("user-123")
        # Decode without verification to check header
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"

    def test_token_cannot_be_modified(self, client, test_user_in_db):
        """Test that modified tokens are rejected."""
        token = create_access_token(test_user_in_db["user_id"])
        
        # Try to modify the token
        parts = token.split(".")
        # Change one character in the payload
        modified_token = parts[0] + "." + parts[1][:-1] + "X" + "." + parts[2]
        
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {modified_token}"}
        )
        
        assert response.status_code == 401
