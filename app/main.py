"""FastAPI application for Web Text Board."""
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import create_session_token, validate_credentials, verify_session_token
from .config import DEFAULT_FONT_SIZE_PX
from .redis_store import clear_document, get_document, get_redis_client, save_document
from .schemas import ClearRequest, DocumentResponse, OkResponse, SaveRequest

app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_redis():
    """Get Redis client."""
    return get_redis_client()


# ─────────────────────────────────────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to editor if authenticated, otherwise to login."""
    return "/editor"


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    """Handle login submission."""
    if validate_credentials(username, password):
        token = create_session_token()
        response = RedirectResponse(url="/editor", status_code=302)
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7 days
        )
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/editor", response_class=HTMLResponse)
async def editor_page(request: Request):
    """Render editor page (requires authentication)."""
    token = request.cookies.get("session")
    if not token or not verify_session_token(token):
        return RedirectResponse(url="/login")

    client = get_redis()
    content, font_size = get_document(client)

    return templates.TemplateResponse("editor.html", {
        "request": request,
        "content": content,
        "font_size_px": font_size,
    })


# ─────────────────────────────────────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────────────────────────────────────


def require_auth(request: Request) -> bool:
    """Check authentication for API routes."""
    token = request.cookies.get("session")
    return token and verify_session_token(token)


@app.get("/api/document", response_model=DocumentResponse)
async def get_doc(request: Request):
    """Get document content and settings."""
    if not require_auth(request):
        return Response(status_code=401)

    client = get_redis()
    content, font_size = get_document(client)
    return DocumentResponse(content=content, font_size_px=font_size)


@app.post("/api/save", response_model=OkResponse)
async def save_doc(request: Request, data: SaveRequest):
    """Save document content and font size."""
    if not require_auth(request):
        return Response(status_code=401)

    client = get_redis()
    save_document(client, data.content, data.font_size_px)
    return OkResponse()


@app.post("/api/clear", response_model=OkResponse)
async def clear_doc(request: Request, data: ClearRequest):
    """Clear document (save empty content immediately)."""
    if not require_auth(request):
        return Response(status_code=401)

    client = get_redis()
    clear_document(client)
    return OkResponse()
