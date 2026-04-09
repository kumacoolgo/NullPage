"""API schemas."""
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """GET /api/document response."""
    content: str
    font_size_px: int


class SaveRequest(BaseModel):
    """POST /api/save request."""
    content: str
    font_size_px: int


class ClearRequest(BaseModel):
    """POST /api/clear request."""
    font_size_px: int


class OkResponse(BaseModel):
    """Generic ok response."""
    ok: bool = True
