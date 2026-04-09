"""Tests for editor page."""
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


class TestEditorPage:
    """Test editor page rendering."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_cookies(self):
        """Create authenticated session cookies."""
        token = create_session_token()
        return {"session": token}

    def test_editor_page_renders_textarea(self, client, auth_cookies):
        """Authenticated editor page renders textarea."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200
        assert "<textarea" in response.text
        assert 'id="editor"' in response.text

    def test_editor_page_has_four_toolbar_buttons(self, client, auth_cookies):
        """Editor page renders exactly 4 toolbar buttons."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200
        html = response.text

        # Count button elements in toolbar
        assert html.count('<button') >= 4
        assert 'id="btn-clear"' in html
        assert 'id="btn-a-minus"' in html
        assert 'id="btn-a-plus"' in html
        assert 'id="btn-save"' in html

    def test_textarea_disables_spellcheck(self, client, auth_cookies):
        """Textarea has spellcheck disabled."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200
        html = response.text

        # Check spellcheck related attributes are disabled
        assert 'spellcheck="false"' in html or "spellcheck=" in html
        assert 'autocorrect="off"' in html
        assert 'autocapitalize="off"' in html
        assert 'autocomplete="off"' in html

    def test_editor_page_loads_css_and_js(self, client, auth_cookies):
        """Editor page loads CSS and JS assets."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200

        # Check static file references
        assert '/static/app.css' in response.text
        assert '/static/app.js' in response.text

    def test_editor_page_initializes_with_font_size(self, client, auth_cookies):
        """Editor page initializes JavaScript with font size."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200

        # Should have initEditor call with font_size_px
        assert 'initEditor(' in response.text
        assert 'font_size_px' in response.text

    def test_editor_page_mobile_viewport(self, client, auth_cookies):
        """Editor page has mobile-first viewport."""
        response = client.get("/editor", cookies=auth_cookies)
        assert response.status_code == 200

        assert 'width=device-width' in response.text
        assert 'initial-scale=1.0' in response.text

    def test_unauthenticated_editor_redirects(self, client):
        """Unauthenticated access to editor redirects to login."""
        response = client.get("/editor", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
