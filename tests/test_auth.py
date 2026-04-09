"""Tests for authentication."""
import os
import pytest
from fastapi.testclient import TestClient

# Set required env vars before importing app
os.environ["EDIT_USER"] = "testuser"
os.environ["EDIT_PASSWORD"] = "testpass"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Use DB 15 for isolation
os.environ["SESSION_SECRET"] = "test-secret-key-for-testing-only"

from app.main import app
from app.auth import create_session_token, validate_credentials, verify_session_token


class TestAuthHelpers:
    """Test auth helper functions."""

    def test_validate_credentials_success(self):
        """Login with correct credentials succeeds."""
        assert validate_credentials("testuser", "testpass") is True

    def test_validate_credentials_wrong_password(self):
        """Login with wrong password fails."""
        assert validate_credentials("testuser", "wrongpass") is False

    def test_validate_credentials_wrong_user(self):
        """Login with wrong username fails."""
        assert validate_credentials("wronguser", "testpass") is False

    def test_create_session_token(self):
        """Session token is created successfully."""
        token = create_session_token()
        assert token is not None
        assert len(token) > 0

    def test_verify_session_token_valid(self):
        """Valid session token verifies successfully."""
        token = create_session_token()
        assert verify_session_token(token) is True

    def test_verify_session_token_invalid(self):
        """Invalid session token fails verification."""
        assert verify_session_token("invalid-token") is False

    def test_verify_session_token_empty(self):
        """Empty session token fails verification."""
        assert verify_session_token("") is False


class TestAuthPages:
    """Test authentication page routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_root_redirects_to_editor_when_authenticated(self, client):
        """Root path redirects to editor when session is valid."""
        token = create_session_token()
        response = client.get("/", cookies={"session": token})
        assert response.status_code == 200
        assert "/editor" in response.url.path or response.text

    def test_root_redirects_to_login_when_not_authenticated(self, client):
        """Root path redirects to login when no session."""
        response = client.get("/", follow_redirects=False)
        # Should redirect to login
        assert response.status_code == 302

    def test_login_page_renders(self, client):
        """Login page renders successfully."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_success(self, client):
        """Login with correct credentials succeeds and redirects."""
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/editor"

    def test_login_failure(self, client):
        """Login with wrong credentials shows error."""
        response = client.post("/login", data={
            "username": "testuser",
            "password": "wrongpass"
        })
        assert response.status_code == 200
        assert "error" in response.text.lower() or "invalid" in response.text.lower()

    def test_editor_redirects_when_not_authenticated(self, client):
        """Editor page redirects to login when not authenticated."""
        response = client.get("/editor", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]


class TestUnauthenticatedAPI:
    """Test API routes without authentication."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_get_document_without_auth_returns_401(self, client):
        """GET /api/document returns 401 without authentication."""
        response = client.get("/api/document")
        assert response.status_code == 401

    def test_save_without_auth_returns_401(self, client):
        """POST /api/save returns 401 without authentication."""
        response = client.post("/api/save", json={
            "content": "test",
            "font_size_px": 18
        })
        assert response.status_code == 401

    def test_clear_without_auth_returns_401(self, client):
        """POST /api/clear returns 401 without authentication."""
        response = client.post("/api/clear", json={
            "font_size_px": 18
        })
        assert response.status_code == 401
