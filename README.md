# Web Text Board

A minimal web-based temporary text board for pasting, editing, and saving plain text. Designed for single-user use with Redis persistence.

## Features

- Plain text only editor
- Manual save (no auto-save)
- Font size controls (A-, A+) and pinch-to-zoom on mobile
- 7-day session persistence
- Redis-backed persistence
- Mobile-first responsive design

## Tech Stack

- **Backend**: Python 3.12 + FastAPI
- **Templates**: Jinja2
- **Frontend**: Plain HTML + CSS + JavaScript (no frameworks)
- **Database**: Redis
- **Session**: Signed cookie (itsdangerous)
- **Container**: Docker

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EDIT_USER` | Yes | Username for login |
| `EDIT_PASSWORD` | Yes | Password for login |
| `REDIS_URL` | Yes | Redis connection URL (e.g., `redis://localhost:6379`) |
| `SESSION_SECRET` | Yes | Secret key for signing session cookies |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_LIFETIME_DAYS` | 7 | Session cookie lifetime |
| `DEFAULT_FONT_SIZE_PX` | 18 | Default editor font size |
| `MIN_FONT_SIZE_PX` | 12 | Minimum font size |
| `MAX_FONT_SIZE_PX` | 40 | Maximum font size |

## Local Development

### Prerequisites

- Python 3.12
- Redis server running

### Setup

1. Clone the repository
2. Create a `.env` file with required variables:

```env
EDIT_USER=myuser
EDIT_PASSWORD=mypassword
REDIS_URL=redis://localhost:6379
SESSION_SECRET=your-super-secret-key-here
```

3. Install dependencies:

```bash
cd web-text-board
pip install -r requirements.txt
```

4. Run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open http://localhost:8000 in your browser

## Running Tests

### Prerequisites

- Redis server running
- Test Redis database (uses DB 15 by default for isolation)

### Run Tests

```bash
cd web-text-board
pytest -v
```

## Docker

### Build Image

```bash
cd web-text-board
docker build -t web-text-board .
```

### Run Container

```bash
docker run -d \
  --name web-text-board \
  -p 8000:8000 \
  -e EDIT_USER=myuser \
  -e EDIT_PASSWORD=mypassword \
  -e REDIS_URL=redis://redis-server:6379 \
  -e SESSION_SECRET=your-secret-key \
  web-text-board
```

## Zeabur Deployment

Zeabur supports Docker container deployment with Redis.

### Steps

1. Push your code to GitHub
2. Connect your repository to Zeabur
3. Add environment variables in Zeabur dashboard:
   - `EDIT_USER`
   - `EDIT_PASSWORD`
   - `REDIS_URL` (use Zeabur's Redis service binding)
   - `SESSION_SECRET` (generate a secure random string)
4. Deploy

### Zeabur Redis Requirement

Zeabur provides Redis as a service binding. Use the provided `REDIS_URL` environment variable from the Redis service.

## API Endpoints

### Pages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirect to `/editor` or `/login` |
| `/login` | GET | Render login page |
| `/login` | POST | Handle login submission |
| `/editor` | GET | Render editor page (requires auth) |

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/document` | GET | Get current document content and font size |
| `/api/save` | POST | Save document content and font size |
| `/api/clear` | POST | Clear document (save empty) |

### API Examples

```bash
# Get document
curl -b "session=YOUR_SESSION_TOKEN" http://localhost:8000/api/document

# Save document
curl -b "session=YOUR_SESSION_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello world", "font_size_px": 18}' \
  http://localhost:8000/api/save

# Clear document
curl -b "session=YOUR_SESSION_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"font_size_px": 18}' \
  http://localhost:8000/api/clear
```

## Project Structure

```
web-text-board/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration & env vars
│   ├── auth.py          # Authentication helpers
│   ├── redis_store.py   # Redis operations
│   ├── schemas.py       # Pydantic models
│   ├── templates/
│   │   ├── login.html
│   │   └── editor.html
│   └── static/
│       ├── app.css
│       └── app.js
├── tests/
│   ├── test_auth.py
│   ├── test_document_api.py
│   └── test_editor_page.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini
└── README.md
```

## License

MIT
