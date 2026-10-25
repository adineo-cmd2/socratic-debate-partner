# Socratic Debate Partner

> An AI debate partner that argues any position Socratically.

State a belief and the engine takes the opposing side: it profiles the claim, maps the reasoning chain as a navigable graph, and pressures the weakest links follow-up by followup. Runs fully in mock Socratic mode with no API keys; add a key to unlock full LLM reasoning.

## Features

- Claim profiling and stance extraction
- Reasoning-graph view of every argument chain
- Session transcripts with follow-up pressure points
- Mock mode works with zero API keys

## Architecture

| Layer | Stack | Path |
|---|---|---|
| Frontend | Astro (file-based routing) | `frontend/` |
| Backend | FastAPI + SQLAlchemy + Pydantic | `backend/` |
| Tests | pytest | `backend/tests/` |

Frontend routes: `profile, reasoning-graph, session`.

## Quick start

Backend (from `backend/`):

```bash
pip install -r requirements.txt
cp .env.example .env        # optional — works with no keys
python3 -m uvicorn app.main:app --port 8001
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Tests: `python3 -m pytest backend/tests/ -v`

## Deployment

The frontend builds to a static bundle and deploys to GitHub Pages on every
push to `main` (`.github/workflows/deploy.yml`):

**https://adineo-cmd2.github.io/socratic-debate-partner/**

## Project structure

```
backend/
  app/          FastAPI application
  tests/        pytest suite
frontend/
  src/pages/    Astro routes
```
