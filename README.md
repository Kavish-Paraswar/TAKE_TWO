# Creative Ops Desk

Multi-agent creative ops desk: users submit a brief, agents plan, generate, critique, enforce consistency, and iterate while the user stays in control with approve or interrupt. This README explains the architecture, data model, APIs, and how to run the app locally.

---

## What This App Does

- Capture a creative brief from a user.
- Run multiple agents (planner, generator, critic, consistency, manager) to turn the brief into images and feedback.
- Show timeline activity and generated outputs while allowing the user to approve or stop.

## Architecture (high level)



- **Frontend (React + Vite)**:  Brief form, run controls, agent timeline, and output gallery. Polls backend for status, logs, and outputs. Key files: `frontend/src/App.jsx`, `frontend/src/components/Timeline.jsx`, `frontend/src/components/OutputGallery.jsx`.
- **Backend (API-first, FastAPI/Node-ready)**: Routes for briefs, runs, agent logs, outputs, approval, and interrupt. An orchestrator drives the state machine and dispatches work to agents.
- **Agents**: Planner (tasks and sequencing), Generator (image creation + retries), Critic (scores and feedback), Consistency (drift checks), Manager (iteration rules and approval gates).
- **State machine**: `CREATED → PLANNING → GENERATING → REVIEWING → ITERATING → AWAITING_APPROVAL → APPROVED | COMPLETED | FAILED | INTERRUPTED`. Only valid forward moves; interruption is always allowed.
- **Data & storage**: Supabase/Postgres recommended for auth, RLS, and asset storage. Tables: users, briefs, runs, agent runs, agent messages, generations, assets, approvals.
- **Observability**: Structured logs keyed by creative_run_id/agent_run_id plus metrics for timing, retries, and budgets.

## API Sketch (REST, idempotent-friendly)

- `POST /briefs` — create a brief.
- `POST /runs` — start a run from a brief; returns run_id and client_token.
- `GET /runs/{id}` — status (state, progress, iteration, budgets).
- `GET /runs/{id}/agents` — agent timeline/messages.
- `GET /runs/{id}/outputs` — generated assets with metadata/scores.
- `POST /runs/{id}/approve` — approve (client_token required).
- `POST /runs/{id}/interrupt` — graceful stop (client_token required).
- Common query params: `limit`, `cursor`, `state`, `agent`, ordered by `created_at` or `iteration`.
- Idempotent retries: clients send `Idempotency-Key` on mutating calls.

## Data Model (Supabase/Postgres sketch)

- creative_briefs(id, user_id, title, description, created_at)
- creative_runs(id, brief_id, user_id, state, iteration, progress, budget_used, created_at, updated_at)
- agent_runs(id, creative_run_id, agent, iteration, started_at, ended_at, status)
- agent_messages(id, agent_run_id, role, content, meta, created_at)
- generations(id, creative_run_id, agent_run_id, asset_url, thumb_url, score, meta, created_at)
- assets(id, creative_run_id, storage_path, mime, bytes, created_at)
- approvals(id, creative_run_id, approved_by, approved_at, decision, notes)

## Run It Locally

Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173 (API default target http://127.0.0.1:8000; adjust in src/App.jsx)
```

Backend (FastAPI example)
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## State, Concurrency, and Safety

- Forward-only state transitions; interruption always valid.
- Per-run concurrency caps (e.g., generator jobs), iteration caps, and wall-clock budgets.
- Graceful cancellation to avoid orphaned work.
- Auth, RLS, and per-user/run rate limits are expected in production.

## Observability

- Structured logs with run_id, agent, iteration, and event.
- Stable ordering for timelines (created_at, agent, iteration).
- Metrics for durations, retries, and budget use; logs enable replay.

## Sample Brief

- Title: Cyberpunk product launch hero
- Description: Two hero banners and one thumbnail; neon palette; legible product name; avoid faces; clean type.

## Example Run (happy path)

1. Planner outlines hero A, hero B, and thumbnail tasks with style guards.
2. Generator produces variants per task; assets and metadata are stored.
3. Critic scores against the brief; Consistency checks palette/layout drift.
4. Manager iterates if the score is low or drift is detected, respecting caps.
5. Outputs surface in the gallery; state moves to AWAITING_APPROVAL; user approves or interrupts.

## Known Gaps and Next Steps

- Generation/critique may be mocked; plug in real adapters.
- Add Supabase auth, storage, RLS, and rate limiting for production.
- Wire pagination and filtering on list endpoints.
- Strengthen idempotency and retry semantics.
- Improve async UI states, error handling, and cancellation UX.
- Add richer telemetry (tracing + metrics dashboards).