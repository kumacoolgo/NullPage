"""FastAPI application for Web Text Board."""
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import create_session_token, validate_credentials, verify_session_token
from .redis_store import get_redis_client
from .schemas import ClearRequest, DocumentResponse, OkResponse, SaveRequest

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

_redis_client = get_redis_client()


def get_redis():
    return _redis_client


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiting
# ─────────────────────────────────────────────────────────────────────────────

LOGIN_RATE_LIMIT_KEY = "textboard:login:fail:{ip}"


def check_login_rate_limit(client, ip: str) -> bool:
    """Check if IP exceeded 5 failed login attempts per minute."""
    key = LOGIN_RATE_LIMIT_KEY.format(ip=ip)
    count = client.incr(key)
    if count == 1:
        client.expire(key, 60)
    return count <= 5


# ─────────────────────────────────────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/")
async def root(request: Request):
    """Redirect to editor if authenticated, otherwise to login."""
    token = request.cookies.get("session")
    ip = request.client.host
    if token and verify_session_token(token, ip):
        return RedirectResponse(url="/editor")
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    """Handle login with rate limiting."""
    client = get_redis()
    ip = request.client.host

    if not check_login_rate_limit(client, ip):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Too many attempts. Try later."}
        )

    if validate_credentials(username, password):
        token = create_session_token(ip)
        response = RedirectResponse(url="/editor", status_code=302)
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )
        return response

    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/editor", response_class=HTMLResponse)
async def editor_page(request: Request):
    """Render editor page (requires authentication)."""
    token = request.cookies.get("session")
    ip = request.client.host
    if not token or not verify_session_token(token, ip):
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


def require_auth(request: Request) -> tuple[bool, str]:
    """Check authentication for API routes. Returns (authorized, ip)."""
    token = request.cookies.get("session")
    ip = request.client.host
    return token and verify_session_token(token, ip), ip


@app.get("/api/document", response_model=DocumentResponse)
async def get_doc(request: Request):
    """Get document content and settings."""
    ok, _ = require_auth(request)
    if not ok:
        return Response(status_code=401)

    client = get_redis()
    content, font_size = get_document(client)
    return DocumentResponse(content=content, font_size_px=font_size)


@app.post("/api/save", response_model=OkResponse)
async def save_doc(request: Request, data: SaveRequest):
    """Save document content and font size."""
    ok, _ = require_auth(request)
    if not ok:
        return Response(status_code=401)

    client = get_redis()
    save_document(client, data.content, data.font_size_px)
    return OkResponse()


@app.post("/api/clear", response_model=OkResponse)
async def clear_doc(request: Request, data: ClearRequest):
    """Clear document (save empty content with current font size)."""
    ok, _ = require_auth(request)
    if not ok:
        return Response(status_code=401)

    client = get_redis()
    save_document(client, "", data.font_size_px)
    return OkResponse()


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        client = get_redis()
        client.ping()
        return {"status": "ok"}
    except Exception:
        return Response(status_code=500, content="{}")
