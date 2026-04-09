"""Authentication utilities."""
from datetime import datetime, timedelta, timezone

from itsdangerous import URLSafeTimedSerializer

from .config import EDIT_PASSWORD, EDIT_USER, SESSION_LIFETIME_DAYS, SESSION_SECRET

# Create serializer for signed cookies
serializer = URLSafeTimedSerializer(SESSION_SECRET)


def create_session_token() -> str:
    """Create a signed session token valid for SESSION_LIFETIME_DAYS."""
    data = {
        "authenticated": True,
        "user": EDIT_USER,
        "exp": (datetime.now(timezone.utc) + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat(),
    }
    return serializer.dumps(data)


def verify_session_token(token: str) -> bool:
    """Verify session token is valid and not expired."""
    try:
        data = serializer.loads(token, max_age=SESSION_LIFETIME_DAYS * 24 * 60 * 60)
        return data.get("authenticated", False) is True
    except Exception:
        return False


def validate_credentials(username: str, password: str) -> bool:
    """Validate login credentials against environment variables."""
    return username == EDIT_USER and password == EDIT_PASSWORD
