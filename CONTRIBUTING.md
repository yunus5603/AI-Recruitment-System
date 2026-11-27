# Contributing

Thanks for your interest! Bug reports, ideas and pull requests are all welcome.
Look for issues labelled
[`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
if you'd like a place to start.

## Development setup

You don't need an API key: without `GROQ_API_KEY` the backend runs in demo
mode, with offline resume parsing and skill-overlap scoring.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # optional: add GROQ_API_KEY
uvicorn main:app --reload     # http://localhost:8000/docs

# Frontend (second terminal)
cd frontend
npm ci
npm run dev                   # http://localhost:5173
```

Or run everything with `docker compose up --build`.

## Before you open a pull request

CI runs these, so running them locally saves a round trip:

```bash
cd backend && ruff check . && ruff format --check . && pytest
cd frontend && npm run lint && npm test && npm run build
```

- Tests must never call the real Groq API. Use the `fake_llm` fixture in
  `backend/tests/conftest.py` to script model replies.
- Changes to `services/code_executor.py` need a test that tries to break out,
  and an update to `SECURITY.md` if the threat model changes.
- Keep pull requests focused on one change and describe how you tested it.

## Project layout

```
backend/
  main.py              FastAPI app, CORS, routers
  routers/             HTTP endpoints (candidates, interview, analytics)
  services/            resume parsing, matching, LLM client, code sandbox
  models/              SQLModel tables and Pydantic schemas
  tests/               pytest suite
frontend/src/
  pages/, components/  React UI
  lib/api.js           backend URL (VITE_API_URL)
```
