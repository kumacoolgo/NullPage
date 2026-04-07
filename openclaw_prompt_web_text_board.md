# OpenClaw Execution Prompt — Web Text Board

## Mission

Build, test, containerize, and push to GitHub a **minimal web-based temporary text board**.

This product is **not** a rich-text editor.  
Its only purpose is:

- paste a large block of plain text,
- manually select any small fragment on mobile or desktop,
- long-press / copy exactly that fragment,
- save manually,
- reopen later and see the last saved content.

The implementation must be **small, stable, easy to deploy on Zeabur**, and use **Redis** for persistence.

---

## Non-Negotiable Product Rules

1. There is only **one user**.
2. Login credentials come from environment variables:
   - `EDIT_USER`
   - `EDIT_PASSWORD`
3. There is only **one saved document**.
4. The editor is **plain text only**.
5. URLs must remain plain text and must **not** become hyperlinks.
6. Preserve text exactly as entered:
   - line breaks
   - blank lines
   - tabs
   - full-width spaces
   - leading spaces
   - trailing spaces
7. No auto-save.
8. Manual save only.
9. Bottom toolbar has exactly **4 buttons**:
   - Clear
   - A-
   - A+
   - Save
10. Clear must show a confirmation dialog first.
11. After confirmation, clear must immediately save an empty document to Redis.
12. No save-status UI.
13. No version history.
14. No logout.
15. Keep user logged in for **7 days**.
16. Mobile-first UI, but desktop should also look clean.
17. Support both:
   - pinch-to-zoom font size on mobile
   - `A-` / `A+` buttons

---

## Required Tech Stack

Use this stack exactly unless absolutely necessary to fix a real issue:

- Backend: **Python 3.12**
- Framework: **FastAPI**
- HTML rendering: **Jinja2**
- Frontend: **plain HTML + plain JavaScript + plain CSS**
- Database: **Redis**
- Session: **signed cookie session**
- Container: **Docker**
- Deployment target: **Zeabur**

Do **not** use React, Vue, TypeScript, Tailwind, or a heavy frontend framework.

---

## Expected Repository Structure

```text
web-text-board/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ auth.py
│  ├─ redis_store.py
│  ├─ schemas.py
│  ├─ templates/
│  │  ├─ login.html
│  │  └─ editor.html
│  └─ static/
│     ├─ app.css
│     └─ app.js
├─ tests/
│  ├─ test_auth.py
│  ├─ test_document_api.py
│  └─ test_editor_page.py
├─ requirements.txt
├─ Dockerfile
├─ .dockerignore
├─ .gitignore
├─ README.md
└─ pytest.ini
```

If the current repo already exists, adapt to it cleanly.  
Do not break existing unrelated files.

---

## Environment Variables

The app must read these variables:

```env
EDIT_USER=your_username
EDIT_PASSWORD=your_password
REDIS_URL=redis://...
SESSION_SECRET=long_random_secret
```

Behavior requirements:

- App must fail fast at startup if any required variable is missing.
- Session lifetime must be **7 days**.
- Default font size must be **18px**.
- Allowed font size range: **12px to 40px**.

---

## Redis Data Model

Use Redis as the single source of truth.

### Key: `textboard:document`

Redis hash fields:

- `content` → string, required, default `""`
- `updated_at` → ISO 8601 timestamp string, required

### Key: `textboard:settings`

Redis hash fields:

- `font_size_px` → integer, required, default `18`

No version history.  
No multiple documents.  
No extra metadata.

---

## Routes to Implement

### Page Routes

- `GET /`
  - if authenticated: redirect to `/editor`
  - if not authenticated: redirect to `/login`

- `GET /login`
  - render login page

- `POST /login`
  - validate against `EDIT_USER` and `EDIT_PASSWORD`
  - on success: set signed session cookie valid for 7 days
  - on failure: render login page with simple error message

- `GET /editor`
  - requires authentication
  - render editor page

### API Routes

- `GET /api/document`
  - requires authentication
  - return:
    ```json
    {
      "content": "",
      "font_size_px": 18
    }
    ```

- `POST /api/save`
  - requires authentication
  - request body:
    ```json
    {
      "content": "string",
      "font_size_px": 18
    }
    ```
  - save content exactly as received
  - clamp font size into range 12..40
  - update `updated_at`
  - return `{ "ok": true }`

- `POST /api/clear`
  - requires authentication
  - request body:
    ```json
    {
      "font_size_px": 18
    }
    ```
  - save empty content string `""`
  - update `updated_at`
  - save current font size
  - return:
    ```json
    {
      "ok": true,
      "content": ""
    }
    ```

---

## Frontend Requirements

### Login Page

Must contain:

- username input
- password input
- login button

Must be simple and mobile-friendly.

### Editor Page

Must contain:

- one large `<textarea>`
- one fixed bottom toolbar
- toolbar contains exactly 4 buttons:
  - Clear
  - A-
  - A+
  - Save

### Textarea Requirements

Use `<textarea>`, not `contenteditable`.

Set attributes to reduce unwanted mobile behavior:

- `spellcheck="false"`
- `autocapitalize="off"`
- `autocomplete="off"`
- `autocorrect="off"`

Use a monospace font.

The textarea must fill most of the viewport and leave enough bottom padding so the toolbar does not cover text.

### Button Behavior

#### Clear
- show confirmation dialog
- if cancelled: do nothing
- if confirmed:
  - clear textarea
  - call `/api/clear`
  - persist empty content immediately

#### A-
- decrease font size by 1px
- minimum 12px
- do not auto-save

#### A+
- increase font size by 1px
- maximum 40px
- do not auto-save

#### Save
- send current textarea value and current font size to `/api/save`

### Mobile Pinch Zoom

Implement pinch gesture on the editor area:

- detect two-finger distance change
- map that to textarea font size changes
- clamp result to 12..40
- change only editor font size
- do not rely on whole-page browser zoom for this feature
- do not auto-save after pinch; Save button is still required

---

## Critical Content Preservation Rules

When saving and loading text:

- do not trim content
- do not normalize whitespace
- do not remove tabs
- do not remove full-width spaces
- do not remove leading or trailing spaces
- do not alter line endings beyond what HTML textarea naturally preserves in value
- do not parse or render URLs as links
- do not convert plain text into HTML

The stored content must round-trip as plain text.

---

## Authentication Rules

Use a secure signed cookie session.

Authenticated session must contain a boolean flag and expiration logic.

Expected behavior:

- unauthenticated access to `/editor` redirects to `/login`
- unauthenticated API access returns `401`
- valid login remains active for 7 days
- no logout feature

---

## Suggested Implementation Notes

Keep implementation minimal.

Recommended Python packages:

- `fastapi`
- `uvicorn`
- `jinja2`
- `redis`
- `itsdangerous`
- `python-multipart`
- `pytest`
- `httpx`

Do not add unnecessary dependencies.

Use server-side templates and one small JS file.

---

## Testing Requirements

Create automated tests with `pytest`.

Minimum coverage:

### `test_auth.py`
- login success with correct env credentials
- login failure with wrong credentials
- unauthenticated request to `/editor` is redirected
- unauthenticated request to `/api/document` returns 401

### `test_document_api.py`
- empty Redis returns default content and font size
- save API persists content exactly
- clear API stores empty string
- font size is clamped to min/max
- whitespace-sensitive content survives round-trip

Use a whitespace-sensitive example like this:

```text
\tLine 1
Line 2

　FullWidthSpace
  leading space
trailing space  
```

### `test_editor_page.py`
- authenticated editor page renders textarea
- editor page renders exactly 4 toolbar buttons
- textarea attributes disable spellcheck/autocorrect-related features

Use a test Redis database or isolated key prefix for tests.

---

## Docker Requirements

Create a `Dockerfile` that:

- uses `python:3.12-slim`
- installs dependencies
- copies project files
- exposes app port
- starts the app with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Add a `.dockerignore`.

---

## README Requirements

Write a practical `README.md` that includes:

1. project purpose
2. tech stack
3. required environment variables
4. local run steps
5. test command
6. docker build/run commands
7. Zeabur deployment notes
8. Redis requirement

---

## Development Workflow Instructions

Perform the work in this order:

1. inspect the repo
2. create or update files
3. implement backend
4. implement templates and JS
5. add tests
6. run tests
7. fix failures
8. ensure Docker build is valid
9. update README
10. commit changes
11. push to GitHub

Do not stop after code generation.  
Actually run tests and fix issues until the test suite passes.

---

## Git Rules

Create clean commits with clear messages, for example:

- `feat: add fastapi text board app`
- `test: add auth and document api coverage`
- `chore: add docker and readme`

Push to the current repository's default branch, unless the repo policy requires a feature branch.  
If branch protection prevents direct push, create a feature branch and push that branch.

---

## Acceptance Criteria

The task is complete only if all conditions below are true:

1. App starts successfully with required environment variables.
2. User can log in using env credentials.
3. User sees one plain text editor.
4. Toolbar has exactly 4 buttons: Clear / A- / A+ / Save.
5. Manual save writes content to Redis.
6. Reloading the page shows the last saved content.
7. Clear confirmation works and persists empty content.
8. Font size changes via buttons work.
9. Mobile pinch changes editor font size.
10. Saved font size is restored on reload.
11. URLs remain plain text.
12. Whitespace is preserved exactly.
13. No auto-save exists.
14. Tests pass.
15. Changes are committed and pushed to GitHub.

---

## Constraints for the Coding Agent

- Do not redesign the product.
- Do not add extra features.
- Do not add formatting tools.
- Do not add markdown support.
- Do not add history/versioning.
- Do not add logout.
- Do not add multiple documents.
- Do not add auto-save.
- Do not add status banners.
- Do not replace Redis with another store.

When a choice is ambiguous, prefer the **simplest implementation** that satisfies the requirements.

---

## Final Execution Output Required From OpenClaw

After finishing, provide:

1. summary of created/changed files
2. test results
3. docker build status
4. git commit hashes
5. pushed branch name
6. any deployment notes for Zeabur
7. any limitations honestly stated
