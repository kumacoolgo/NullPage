"""Application configuration."""
import os


def get_required(env_var: str) -> str:
    """Get required environment variable or fail fast."""
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {env_var}")
    return value


# Required config
EDIT_USER = get_required("EDIT_USER")
EDIT_PASSWORD = get_required("EDIT_PASSWORD")
REDIS_URL = get_required("REDIS_URL")
SESSION_SECRET = get_required("SESSION_SECRET")

# Optional config with defaults
SESSION_LIFETIME_DAYS = 7
DEFAULT_FONT_SIZE_PX = 18
MIN_FONT_SIZE_PX = 12
MAX_FONT_SIZE_PX = 40

# Redis key prefixes
REDIS_DOCUMENT_KEY = "textboard:document"
REDIS_SETTINGS_KEY = "textboard:settings"
