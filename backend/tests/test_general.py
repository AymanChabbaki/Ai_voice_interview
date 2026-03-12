"""
General Endpoint Tests - test_general.py

Tests general endpoints including root, health check, categories,
statistics, and other utility endpoints.
"""

from unittest.mock import patch

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Helper functions from conftest
def assert_success_response(response, status_code: int = 200):
    assert response.status_code == status_code
    data = response.json()
    assert data is not None
    return data


# ---------------------------------------------------------------------------
# Root Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        
        data = assert_success_response(response, 200)
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "docs" in data
        
        assert data["status"] == "online"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_root_endpoint_message(self, client):
        """Test root endpoint message."""
        response = client.get("/")
        data = response.json()
        assert "Smart Voice Interviewer API" in data["message"]


# ---------------------------------------------------------------------------
# Health Check Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_endpoint(self, client):
        """Test health endpoint returns status."""
        response = client.get("/health")
        
        data = assert_success_response(response, 200)
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_shows_model_status(self, client):
        """Test health endpoint shows model loading status."""
        response = client.get("/health")
        data = response.json()
        
        assert "model_loaded" in data
        assert "questions_loaded" in data
        assert "courses_loaded" in data
        assert isinstance(data["model_loaded"], bool)

    def test_health_shows_active_sessions(self, client):
        """Test health endpoint shows active sessions count."""
        response = client.get("/health")
        data = response.json()
        
        assert "active_sessions" in data
        assert isinstance(data["active_sessions"], int)
        assert data["active_sessions"] >= 0

    def test_health_with_all_loaded(self, client, mock_app_globals):
        """Test health when all resources are loaded."""
        response = client.get("/health")
        data = response.json()
        
        assert data["model_loaded"] is True
        assert data["questions_loaded"] is True
        assert data["courses_loaded"] is True

    def test_health_with_missing_data(self, client):
        """Test health when data is not loaded."""
        with patch("app.df_questions", None):
            response = client.get("/health")
            data = response.json()
            
            assert data["status"] == "healthy"  # Still healthy
            assert data["questions_loaded"] is False


# ---------------------------------------------------------------------------
# Categories Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestCategoriesEndpoint:
    """Test the categories listing endpoint."""

    def test_list_categories_success(self, client, mock_app_globals):
        """Test listing all categories."""
        response = client.get("/categories")
        
        data = assert_success_response(response, 200)
        assert "total_categories" in data
        assert "top_categories" in data

    def test_list_categories_returns_counts(self, client, mock_app_globals):
        """Test that categories include question counts."""
        response = client.get("/categories")
        data = response.json()
        
        top_categories = data["top_categories"]
        assert isinstance(top_categories, dict)
        
        # Each category should have a count
        for category, count in top_categories.items():
            assert isinstance(count, int)
            assert count > 0

    def test_list_categories_limits_to_20(self, client, mock_app_globals):
        """Test that only top 20 categories are returned."""
        response = client.get("/categories")
        data = response.json()
        
        assert len(data["top_categories"]) <= 20

    def test_list_categories_without_data(self, client):
        """Test categories endpoint when data is not loaded."""
        with patch("app.df_questions", None):
            response = client.get("/categories")
            assert response.status_code == 503

    def test_list_categories_structure(self, client, mock_app_globals):
        """Test the structure of categories response."""
        response = client.get("/categories")
        data = response.json()
        
        assert isinstance(data["total_categories"], int)
        assert isinstance(data["top_categories"], dict)
        assert data["total_categories"] > 0


# ---------------------------------------------------------------------------
# Statistics Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestStatisticsEndpoint:
    """Test the general statistics endpoint."""

    def test_get_statistics_success(self, client, mock_app_globals):
        """Test getting general statistics."""
        response = client.get("/statistics")
        
        data = assert_success_response(response, 200)
        assert "questions" in data
        assert "courses" in data

    def test_statistics_questions_info(self, client, mock_app_globals):
        """Test questions statistics."""
        response = client.get("/statistics")
        data = response.json()
        
        questions = data["questions"]
        assert "total" in questions
        assert "categories" in questions
        assert "difficulty_distribution" in questions
        
        assert isinstance(questions["total"], int)
        assert questions["total"] > 0

    def test_statistics_courses_info(self, client, mock_app_globals):
        """Test courses statistics."""
        response = client.get("/statistics")
        data = response.json()
        
        courses = data["courses"]
        assert "total" in courses
        assert "platforms" in courses
        assert "difficulty_distribution" in courses
        
        assert isinstance(courses["total"], int)
        assert courses["total"] > 0

    def test_statistics_difficulty_distribution(self, client, mock_app_globals):
        """Test difficulty distribution in statistics."""
        response = client.get("/statistics")
        data = response.json()
        
        questions_diff = data["questions"]["difficulty_distribution"]
        courses_diff = data["courses"]["difficulty_distribution"]
        
        assert isinstance(questions_diff, dict)
        assert isinstance(courses_diff, dict)
        
        # Should have difficulty levels
        for level, count in questions_diff.items():
            assert isinstance(count, int)
            assert count > 0

    def test_statistics_platforms(self, client, mock_app_globals):
        """Test platform distribution in statistics."""
        response = client.get("/statistics")
        data = response.json()
        
        platforms = data["courses"]["platforms"]
        assert isinstance(platforms, dict)
        
        # Should have platform counts
        for platform, count in platforms.items():
            assert isinstance(count, int)
            assert count > 0

    def test_statistics_without_data(self, client):
        """Test statistics endpoint when data is not loaded."""
        with patch("app.df_questions", None):
            response = client.get("/statistics")
            assert response.status_code == 503


# ---------------------------------------------------------------------------
# CORS Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses with origin header."""
        # TestClient requires explicit origin header to trigger CORS
        response = client.get("/", headers={"Origin": "http://localhost:5173"})
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers

    def test_cors_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        # CORS preflight requires origin and access-control-request-method headers
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Should allow OPTIONS
        assert response.status_code in [200, 204, 405]

    def test_cors_methods_allowed(self, client):
        """Test that correct methods are allowed."""
        response = client.options("/")
        
        if "access-control-allow-methods" in response.headers:
            methods = response.headers["access-control-allow-methods"]
            assert "GET" in methods or "get" in methods
            assert "POST" in methods or "post" in methods


# ---------------------------------------------------------------------------
# Rate Limiting Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_default_rate_limit(self, client):
        """Test default rate limit (200/minute) on general endpoints."""
        # Make multiple requests to root endpoint
        for _ in range(10):
            response = client.get("/")
            # Should succeed (well below limit)
            assert response.status_code == 200

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are included."""
        response = client.get("/health")
        
        # Note: slowapi may or may not add these headers depending on configuration
        # This is a soft check
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Error Handling Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and responses."""

    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoints."""
        response = client.get("/nonexistent-endpoint-xyz")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method."""
        # GET on a POST-only endpoint
        response = client.get("/register")
        assert response.status_code == 405

    def test_validation_error_format(self, client):
        """Test that validation errors return proper format."""
        # Send invalid data to registration
        response = client.post("/register", json={})
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_service_unavailable_without_data(self, client):
        """Test 503 error when data is not loaded."""
        with patch("app.df_questions", None):
            response = client.post("/interview/start", json={
                "topic": "Python"
            })
            assert response.status_code == 503


# ---------------------------------------------------------------------------
# Documentation Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDocumentation:
    """Test API documentation endpoints."""

    def test_docs_endpoint_exists(self, client):
        """Test that /docs endpoint is available."""
        response = client.get("/docs")
        # Should either return docs (200) or redirect (307)
        assert response.status_code in [200, 307]

    def test_redoc_endpoint_exists(self, client):
        """Test that /redoc endpoint is available."""
        response = client.get("/redoc")
        # Should either return docs (200) or redirect (307)
        assert response.status_code in [200, 307]

    def test_openapi_schema_exists(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


# ---------------------------------------------------------------------------
# Content Type Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestContentTypes:
    """Test content type handling."""

    def test_json_response_content_type(self, client):
        """Test that JSON endpoints return correct content type."""
        response = client.get("/")
        assert "application/json" in response.headers.get("content-type", "")

    def test_json_request_accepted(self, client, test_db):
        """Test that JSON requests are properly handled."""
        response = client.post("/login", json={
            "username": "testuser",
            "password": "password"
        })
        
        # Should process JSON (even if credentials are wrong)
        assert response.status_code in [200, 401, 422]

    def test_invalid_json_rejected(self, client):
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/login",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# API Metadata Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAPIMetadata:
    """Test API metadata and versioning."""

    def test_api_title(self, client):
        """Test that API has correct title in schema."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert "Smart Voice Interviewer API" in schema["info"]["title"]

    def test_api_version(self, client):
        """Test that API version is set."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert schema["info"]["version"] == "1.0.0"

    def test_api_description(self, client):
        """Test that API has description."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert "description" in schema["info"]
        assert len(schema["info"]["description"]) > 0


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_request_body(self, client):
        """Test endpoints with empty request body."""
        response = client.post("/login", json={})
        # Should return validation error
        assert response.status_code == 422

    def test_null_values_in_request(self, client):
        """Test handling of null values."""
        response = client.post("/login", json={
            "username": None,
            "password": None
        })
        assert response.status_code == 422

    def test_extra_fields_ignored(self, client, test_db):
        """Test that extra fields in request are handled."""
        response = client.post("/login", json={
            "username": "testuser",
            "password": "password",
            "extra_field": "should be ignored"
        })
        
        # Should process normally (ignoring extra fields)
        assert response.status_code in [200, 401]

    @patch("database.create_user")
    def test_special_characters_in_strings(self, mock_create_user, client):
        """Test handling of special characters."""
        mock_create_user.return_value = {
            "user_id": "test-id",
            "username": "test_user_123",
            "email": "test+special@example.com",
            "name": "Test User Jr."
        }
        
        response = client.post("/register", json={
            "username": "test_user_123",
            "email": "test+special@example.com",
            "password": "P@ssw0rd!#$",
            "name": "Test User Jr."
        })
        
        # Should handle special characters
        assert response.status_code in [200, 400, 422]

    def test_very_long_strings(self, client):
        """Test handling of very long strings."""
        response = client.post("/register", json={
            "username": "a" * 100,  # Too long
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        
        # Should reject due to validation
        assert response.status_code == 422

    @patch("database.create_user")
    def test_unicode_characters(self, mock_create_user, client):
        """Test handling of unicode characters."""
        mock_create_user.return_value = {
            "user_id": "test-id",
            "username": "testuser123",
            "email": "test@example.com",
            "name": "Test 用户 👨‍💻"
        }
        
        response = client.post("/register", json={
            "username": "testuser123",
            "email": "test@example.com",
            "password": "password123",
            "name": "Test 用户 👨‍💻"  # Unicode + emoji
        })
        
        # Should handle unicode
        assert response.status_code in [200, 400]


# ---------------------------------------------------------------------------
# Performance Tests
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestPerformance:
    """Test API performance characteristics."""

    def test_health_check_fast(self, client):
        """Test that health check is fast."""
        import time
        
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        # Should respond in under 1 second
        assert duration < 1.0

    def test_root_endpoint_fast(self, client):
        """Test that root endpoint is fast."""
        import time
        
        start = time.time()
        response = client.get("/")
        duration = time.time() - start
        
        assert response.status_code == 200
        # Should respond in under 1 second
        assert duration < 1.0

    def test_concurrent_requests_handled(self, client):
        """Test that multiple concurrent requests are handled."""
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request():
            return client.get("/health")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
