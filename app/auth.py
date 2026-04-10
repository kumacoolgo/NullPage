"""Authentication utilities."""
from datetime import datetime, timedelta, timezone

from itsdangerous import URLSafeTimedSerializer

from .config import EDIT_PASSWORD, EDIT_USER, SESSION_LIFETIME_DAYS, SESSION_SECRET

serializer = URLSafeTimedSerializer(SESSION_SECRET)


def create_session_token(ip: str) -> str:
    """Create a signed session token bound to IP."""
    data = {
        "authenticated": True,
        "user": EDIT_USER,
        "ip": ip,
        "exp": (datetime.now(timezone.utc) + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat(),
    }
    return serializer.dumps(data)


def verify_session_token(token: str, ip: str) -> bool:
    """Verify session token is valid, not expired, and IP matches."""
    try:
        data = serializer.loads(token, max_age=SESSION_LIFETIME_DAYS * 86400)

        if data.get("authenticated") is not True:
            return False

        if data.get("ip") != ip:
            return False

        exp = datetime.fromisoformat(data["exp"])
        if datetime.now(timezone.utc) > exp:
            return False

        return True
    except Exception:
        return False


def validate_credentials(username: str, password: str) -> bool:
    """Validate login credentials against environment variables."""
    return username == EDIT_USER and password == EDIT_PASSWORD
