"""Redis storage for document and settings."""
from datetime import datetime, timezone

import redis

from .config import (
    DEFAULT_FONT_SIZE_PX,
    MAX_FONT_SIZE_PX,
    MIN_FONT_SIZE_PX,
    REDIS_DOCUMENT_KEY,
    REDIS_SETTINGS_KEY,
    REDIS_URL,
)


def get_redis_client() -> redis.Redis:
    """Get Redis client from URL."""
    return redis.from_url(REDIS_URL, decode_responses=True)


def get_document(client: redis.Redis) -> tuple[str, int]:
    """Get document content and font size from Redis."""
    doc_data = client.hgetall(REDIS_DOCUMENT_KEY)
    settings_data = client.hgetall(REDIS_SETTINGS_KEY)

    content = doc_data.get("content", "")
    font_size = int(settings_data.get("font_size_px", DEFAULT_FONT_SIZE_PX))

    return content, font_size


def save_document(client: redis.Redis, content: str, font_size_px: int) -> None:
    """Save document content and font size to Redis."""
    # Clamp font size to allowed range
    font_size = max(MIN_FONT_SIZE_PX, min(MAX_FONT_SIZE_PX, font_size_px))

    pipe = client.pipeline()
    pipe.hset(REDIS_DOCUMENT_KEY, mapping={
        "content": content,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    pipe.hset(REDIS_SETTINGS_KEY, mapping={
        "font_size_px": font_size,
    })
    pipe.execute()


def clear_document(client: redis.Redis) -> None:
    """Clear document (save empty content immediately)."""
    save_document(client, "", DEFAULT_FONT_SIZE_PX)
