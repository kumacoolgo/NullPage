"""Tests for document API."""
import os
import pytest
from fastapi.testclient import TestClient

# Set required env vars before importing app
os.environ["EDIT_USER"] = "testuser"
os.environ["EDIT_PASSWORD"] = "testpass"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["SESSION_SECRET"] = "test-secret-key-for-testing-only"

from app.main import app
from app.auth import create_session_token


class TestDocumentAPI:
    """Test document API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_cookies(self):
        """Create authenticated session cookies."""
        token = create_session_token()
        return {"session": token}

    @pytest.fixture
    def redis_client(self):
        """Create Redis client for test database."""
        import redis
        client = redis.from_url("redis://localhost:6379/15", decode_responses=True)
        # Clear test keys before and after tests
        client.delete("textboard:document", "textboard:settings")
        yield client
        client.delete("textboard:document", "textboard:settings")

    def test_get_document_returns_defaults_when_empty(self, client, auth_cookies, redis_client):
        """Empty Redis returns default content and font size."""
        response = client.get("/api/document", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == ""
        assert data["font_size_px"] == 18

    def test_save_api_persists_content(self, client, auth_cookies, redis_client):
        """Save API persists content exactly."""
        test_content = "Hello, World!"
        response = client.post("/api/save", json={
            "content": test_content,
            "font_size_px": 18
        }, cookies=auth_cookies)
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify Redis stored it
        doc_data = redis_client.hgetall("textboard:document")
        assert doc_data["content"] == test_content

    def test_clear_api_stores_empty_string(self, client, auth_cookies, redis_client):
        """Clear API stores empty string."""
        # First save some content
        client.post("/api/save", json={
            "content": "Some text",
            "font_size_px": 18
        }, cookies=auth_cookies)

        # Then clear
        response = client.post("/api/clear", json={
            "font_size_px": 18
        }, cookies=auth_cookies)
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify Redis is empty
        doc_data = redis_client.hgetall("textboard:document")
        assert doc_data["content"] == ""

    def test_font_size_clamped_to_min(self, client, auth_cookies, redis_client):
        """Font size is clamped to minimum (12px)."""
        response = client.post("/api/save", json={
            "content": "test",
            "font_size_px": 5  # Below minimum
        }, cookies=auth_cookies)
        assert response.status_code == 200

        settings = redis_client.hgetall("textboard:settings")
        assert int(settings["font_size_px"]) == 12

    def test_font_size_clamped_to_max(self, client, auth_cookies, redis_client):
        """Font size is clamped to maximum (40px)."""
        response = client.post("/api/save", json={
            "content": "test",
            "font_size_px": 100  # Above maximum
        }, cookies=auth_cookies)
        assert response.status_code == 200

        settings = redis_client.hgetall("textboard:settings")
        assert int(settings["font_size_px"]) == 40

    def test_whitespace_sensitive_content_round_trip(self, client, auth_cookies, redis_client):
        """Whitespace-sensitive content survives round-trip."""
        whitespace_content = (
            "\tLine 1\n"
            "Line 2\n"
            "\n"
            "　FullWidthSpace\n"
            "  leading space\n"
            "trailing space  \n"
        )

        response = client.post("/api/save", json={
            "content": whitespace_content,
            "font_size_px": 18
        }, cookies=auth_cookies)
        assert response.status_code == 200

        # Retrieve and verify
        response = client.get("/api/document", cookies=auth_cookies)
        assert response.json()["content"] == whitespace_content

    def test_updated_at_is_set(self, client, auth_cookies, redis_client):
        """Updated_at timestamp is set on save."""
        response = client.post("/api/save", json={
            "content": "test",
            "font_size_px": 18
        }, cookies=auth_cookies)
        assert response.status_code == 200

        doc_data = redis_client.hgetall("textboard:document")
        assert "updated_at" in doc_data
        assert len(doc_data["updated_at"]) > 0
