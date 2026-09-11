# Northflank remote Docker build

No deployment performed. Existing Dockerfile includes frontend; use the new
backend-only Dockerfile.northflank. Frontend and main.py are unchanged.

## Build and networking

Choose Dockerfile build (BuildKit), not buildpacks. Repository root build context
(`/`), Dockerfile path `/Dockerfile.northflank`. No Node or Windows runtime needed.
Leave the command override empty; image CMD runs:

    sh -c 'exec python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1'

Set PORT=8000. Expose internal port 8000 as public HTTP in Northflank, which
provides public HTTPS on 443. Health/readiness: HTTP GET /health on port 8000.
Use one replica and one worker for JSON and in-memory conversation/job state.

## Runtime environment (never build arguments)

Required values to provide:
- AWS_BEARER_TOKEN_BEDROCK: backend secret
- AWS_REGION: eu-north-1 (also the image default)
- ACCESSLY_EMAIL: Gmail sender
- ACCESSLY_EMAIL_APP_PASSWORD: backend secret
- ACCESSLY_TEST_RECIPIENT: controlled test inbox, never a real organizer
- ACCESSLY_ALLOWED_ORIGINS: exact production frontend HTTPS origin; comma-separated
  if multiple origins. No wildcard. Must be supplied before public-mode startup.

Image defaults (set these explicitly in the dashboard if desired):
- PORT=8000
- ACCESSLY_PUBLIC_MODE=1
- ACCESSLY_DATA_DIR=/var/data/accessly
- STRANDS_BROWSER_HEADLESS=true
- PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
- PYTHON_DOTENV_DISABLED=1 (disables dotenv even in unchanged agent code)

Optional application quota settings:
- ACCESSLY_DAILY_ACTION_LIMIT=60
- ACCESSLY_VISITOR_DAILY_LIMIT=12

Do not add secrets to VITE variables, Docker ARG, Git, or frontend configuration.
.env is ignored by Git and excluded by the Docker build allowlist.
The image installs Playwright Chromium and Linux dependencies explicitly and
runs as the non-root accessly user. Container smoke test makes no model/email calls.

## API compatibility

Existing frontend /api endpoints remain. Public-mode data routes require the
existing visitor header: Authorization: Bearer followed by 64 lowercase hex chars.
Health routes are unauthenticated.

- GET /health and /api/health -> {"status":"ok"}
- GET /profile and /api/profile
- POST /profile or /api/profile, existing PUT /api/profile; body {"needs":["Captions"]}
- POST /chat or /api/chat: new event {"url":"https://official-event-url"}
- POST /chat follow-up: {"session_id":"returned-session-id","message":"Draft only"}
- Chat returns HTTP 202 job object. Poll GET /jobs/{id} or /api/jobs/{id} for
  completion and structured result. No new synchronous agent implementation.
- GET /requests and /api/requests
- POST /requests/{request_id}/check and /api/requests/{request_id}/check
- Existing /api/events, /api/sessions/{id}/messages and presentation retry remain.

## Local verification

Seven Python route/result tests passed. On the Windows host, container_smoke.py
passed actual FastAPI startup, /health, Strands imports and headless Chromium.
This is NOT a Linux container test. Local Docker is unavailable and is NOT a
prerequisite. Build Dockerfile.northflank remotely from GitHub using Northflank.
Inspect build logs for dependency installation and runtime logs for startup.
After startup, use the Northflank container console to run:

    python container_smoke.py

This checks Linux Chromium and imports inside the actual image without sending
email or calling Bedrock. Its temporary FastAPI server uses port 8765.

Optional commands for any other machine with Docker:

    docker build -f Dockerfile.northflank -t accessly-backend:northflank .
    docker run --rm --init accessly-backend:northflank python container_smoke.py

The smoke test creates isolated temporary storage and uses an invalid controlled
inbox placeholder, without sending mail or calling Bedrock. For normal startup,
pass the required runtime settings using a local ignored env file with docker's
--env-file option and publish -p 8000:8000. Do not publish that env file.

## Storage and remaining risks

No migration was made. The profile/request JSON files and quota SQLite database
remain on local disk. Northflank ephemeral data is lost on restart/termination;
/var/data/accessly is only a directory, not an automatically provisioned volume.
Conversation/job state is in memory and also expires on restart.
https://northflank.com/docs/v1/application/scale/increase-storage
https://northflank.com/docs/v1/application/network/configure-ports

Not yet tested: Linux image build/dependency availability, Linux Chromium launch,
container memory usage, Northflank SMTP/IMAP, or public end-to-end flow. Do not
claim runtime verification before checking the remote build, deployed /health,
container smoke test and deployment logs. Local Docker Desktop is not required.
