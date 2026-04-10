"""Tests for authentication."""
import os
import pytest
from fastapi.testclient import TestClient

os.environ["EDIT_USER"] = "testuser"
os.environ["EDIT_PASSWORD"] = "testpass"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SESSION_SECRET"] = "test-secret-key-for-testing"

from app.main import app
from app.auth import create_session_token, verify_session_token


class TestAuthHelpers:
    """Test auth helper functions."""

    def test_create_and_verify_token(self):
        """Token creation and verification works."""
        token = create_session_token("127.0.0.1")
        assert verify_session_token(token, "127.0.0.1")

    def test_verify_token_wrong_ip(self):
        """Token verification fails with wrong IP."""
        token = create_session_token("127.0.0.1")
        assert not verify_session_token(token, "192.168.1.1")


class TestAuthenticatedPages:
    """Test pages that require authentication."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_root_redirects_to_editor_when_authenticated(self, client):
        """Root path redirects to editor when session is valid."""
        token = create_session_token("127.0.0.1")
        response = client.get("/", cookies={"session": token}, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/editor"

    def test_root_redirects_to_login_when_not_authenticated(self, client):
        """Root path redirects to login when no session."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

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
