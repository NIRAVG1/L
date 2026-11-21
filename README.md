# Lyftr AI

A modular full-stack AI chat application built with React, FastAPI, SQLite, and LiteLLM. It stores conversations by session, routes model requests through a configurable credential pool, reports per-response metadata, and enables LiteLLM's in-memory response cache.

## 1. Live URLs

- Frontend: Not deployed yet (placeholder; no deployment has been performed).
- Backend: Not deployed yet (placeholder; no deployment has been performed).

## 2. Run locally: with Docker and without

### Docker

Copy `.env.example` to `.env`, set at least two provider API keys, and then run:

```sh
make up
```

Open `http://localhost:3000`; the API is at `http://localhost:8000`. Stop it with `make down`. Compose stores SQLite in the named `lyftr_data` volume at `/data/app.db`.

### Without Docker

Backend (Python 3.11+ recommended):

```sh
cp .env.example .env
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

For a non-Docker run on a machine without `/data`, set `DATABASE_URL=sqlite:///./lyftr.db` in `.env` before starting the backend. In another terminal:

```sh
cd frontend
npm ci
VITE_API_URL=http://localhost:8000 npm run dev -- --port 3000
```

The frontend reads `VITE_API_URL` at build time. For local development set it to `http://localhost:8000`. SQLite tables are created automatically on app startup. At least two configured API keys are needed for `/health` to report readiness. Use real credentials for actual inference.

### Environment

`LLM_API_KEYS` is a comma-separated provider credential pool; `LLM_MODEL` is a LiteLLM model identifier. `DATABASE_URL` accepts SQLAlchemy SQLite URLs, `ALLOWED_ORIGINS` is a comma-separated CORS allowlist, `DEFAULT_SYSTEM_PROMPT` sets the default behavior, and `ENABLE_FAILURE_SIMULATION` gates the test header. Never commit `.env` or real credentials.

### API examples

```sh
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"session_id":"s-12345","message":"What is artificial intelligence?"}'
curl http://localhost:8000/sessions/s-12345/messages
```

A successful chat response includes `session_id`, `reply`, and metadata containing source, model, latency, per-request input and output tokens, key identifier, and fallback attempt count. The history endpoint returns messages oldest first, omits system instructions, and returns 404 when no messages exist for that session.

## 3. Design decisions: key fallback, caching, SQLite session storage

### Key fallback

The gateway calls LiteLLM `completion()` once per configured credential, in order. A provider exception advances to the next key; exhaustion is returned as a generic 503. API keys are supplied per call and are never returned to the client. Calls are bounded by the configured key count, and provider SDK retries are disabled by default. Simulation errors are request-scoped and are used only when the opt-in setting is enabled.

### Caching

LiteLLM's built-in cache is enabled in memory. Full model input messages, including system prompt and history, determine the prompt digest; session IDs do not. LiteLLM receives `caching=True` for normal calls and simulated failure requests bypass caching. Original LiteLLM token usage stays with cached responses. The SDK's cache-hit signal varies by provider/version, so the gateway also tracks successfully requested prompt digests in-process to normalize repeated cache response metadata. Cache state is intentionally ephemeral and local to one backend process.

### SQLite session storage

SQLAlchemy creates an indexed `messages` table and a `session_configs` table for a session's effective custom system prompt. User/assistant pairs are committed in one transaction after successful inference. An in-process per-session lock serializes concurrent requests within one backend worker. Messages use UTC ISO-8601 timestamps, and assistant metadata is stored as JSON text. The Docker volume makes the database persistent across container replacement.

### Architecture and structure

```text
frontend/src/              React components, hook, API client, styles
backend/app/api/            Request schemas and the three public routes
backend/app/core/           Settings and SQLAlchemy engine/session
backend/app/models/         Message and session prompt tables
backend/app/repositories/   History reads and atomic exchange writes
backend/app/services/       Context assembly and chat orchestration
backend/app/integrations/   LiteLLM gateway, cache and credential iteration
backend/tests/              Pytest contract and behavior tests
```

The React app sends only the newest user message. FastAPI reconstructs prior context from SQLite and returns metadata associated with the individual assistant response.

## 4. Verification: how to see failover, cache hits and per-message token usage

Run the automated suite with `make test` or `cd backend && pytest -q`. The tests mock model calls to avoid external requests; configure real provider credentials to verify live inference and provider-specific token reporting.

Cache demonstration: issue the same first-turn message in two distinct sessions. The second identical model input should be served by LiteLLM's memory cache and display the cached badge. Every assistant bubble displays its own model, latency, input tokens, output tokens, and live/cache source. Input usage is the full prompt for that request, not a session cumulative count.

With `ENABLE_FAILURE_SIMULATION=true`, force key 1 to fail and observe the genuine model response from key 2:

```sh
curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -H 'X-Simulate-Failure: key_1=429' -d '{"session_id":"fallback-demo","message":"Give me one short fact."}'
```

This must be a new uncached prompt for a useful demonstration. Force every credential to fail; no messages should be written:

```sh
curl -i -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -H 'X-Simulate-Failure: *=429' -d '{"session_id":"failure-demo","message":"This should not be saved."}'
curl -i http://localhost:8000/sessions/failure-demo/messages
```

A simulated fallback requires live credentials for the non-simulated key. The UI also exposes `data-testid` hooks for automated browser evaluation.

## 5. Setup Used: your editor and AI tools

Implemented in the Codex desktop workspace. No deployment or external service was used.

## 6. Bonus features (if any): what you added beyond the requirements and why

- A session-scoped system prompt is persisted separately from visible conversation messages.
- The interface includes suggested starter prompts, compact service status, and responsive layout.

### Docker and deployment

`make up` builds and starts the multi-stage backend and frontend images when Docker is running. `make down` stops the stack.

Deployment files are ready: [`frontend/vercel.json`](frontend/vercel.json) configures the Vite build and SPA fallback, [`backend/main.py`](backend/main.py) and [`backend/pyproject.toml`](backend/pyproject.toml) expose FastAPI to Vercel's Python runtime, and [`render.yaml`](render.yaml) defines the Docker backend and persistent disk.

To deploy after connecting this directory to a GitHub repository:

1. Create a managed PostgreSQL database and copy its connection URL. Vercel Functions have no persistent local filesystem, so SQLite is for local/Docker use only in this deployment.
2. In Vercel, import the repository as a backend project with project root `backend`. Set `LLM_API_KEYS` as a secret, `LLM_MODEL=openai/gpt-4o-mini`, `DATABASE_URL` to the PostgreSQL URL, and `ENABLE_FAILURE_SIMULATION=false`. Vercel detects the FastAPI entry point from `backend/pyproject.toml`.
3. Import the same repository as a separate frontend project with project root `frontend`. Set `VITE_API_URL` to the backend's HTTPS origin, then deploy.
4. Set the backend's `ALLOWED_ORIGINS` to the deployed frontend origin and redeploy the backend. Check the backend `/health` endpoint, then send a chat from the frontend.

The Render path remains available for a Docker deployment: create a Blueprint from the repository using `render.yaml`, provide the API keys and CORS origin, and choose a plan with persistent-disk support. No production URLs exist yet.

Never put API keys in deployment files or the Vercel frontend environment. The frontend only needs the public backend URL. See [Render Blueprint reference](https://render.com/docs/blueprint-spec), [Render persistent disks](https://render.com/docs/disks), and [Vercel's FastAPI deployment guide](https://vercel.com/kb/guide/ship-a-fastapi-app-on-vercel).

### Known limitations

- Cache state is in-memory and lost on restart; separate backend replicas do not share cache entries.
- Session serialization uses process-local locks; multi-worker deployments can interleave simultaneous turns for the same session.
- Provider compatibility and usage-field availability depend on the selected LiteLLM provider integration. Missing token usage currently fails the request rather than estimating values.
- Automated tests use controlled model-call substitutes. Separate live checks succeeded with the configured OpenAI keys for inference, cached token usage, key-2 fallback, and failed-request non-persistence.
