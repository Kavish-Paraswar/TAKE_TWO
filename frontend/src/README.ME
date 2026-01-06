# Creative Ops Desk — Multi-Agent Creative Orchestration

Virtual creative ops desk where autonomous agents plan, generate, critique, check consistency, and iterate on creative outputs from a human-provided brief. The user stays the director with approve/interrupt controls.

## System Architecture (target blueprint)

- **Frontend (React + Vite)**: Brief capture, run controls, agent timeline, and output gallery. Polls API for status/logs/outputs. Entry: `frontend/src/App.jsx`; timeline: `frontend/src/components/Timeline.jsx`; gallery: `frontend/src/components/OutputGallery.jsx`.
- **Backend (API-first, e.g., FastAPI or Node/Express)**:
  - Endpoints for runs, briefs, agent logs, outputs, approval/interrupt.
  - Orchestrator service runs the state machine and dispatches agent jobs.
  - Model adapter interface for image generation (pluggable to real models or mocks).
- **Agents (logical roles)**:
  - **Planner**: Expands brief into tasks, scope, sequencing.
  - **Generator**: Creates images via model adapters; retries with budgets.
  - **Critic**: Scores against brief; structured feedback.
  - **Consistency**: Detects stylistic/visual drift across outputs.
  - **Manager**: Governs iterations, stopping conditions, approvals.
- **State Machine (run-level)**: `CREATED → PLANNING → GENERATING → REVIEWING → ITERATING → AWAITING_APPROVAL → APPROVED|COMPLETED|FAILED|INTERRUPTED`. Only valid forward transitions; interruption always allowed; retries stay within budgets.
- **Data & Storage (Supabase/Postgres recommended)**:
  - Auth & row-level ownership.
  - Buckets for generated assets.
  - Tables: `users`, `creative_briefs`, `creative_runs`, `agent_runs`, `agent_messages`, `generations`, `assets`, `approvals`.
- **Observability**: Structured logs keyed by `creative_run_id` and `agent_run_id`; agent-level events; metrics for durations/budgets; trace IDs for replay.

## API Overview (REST sketch, idempotent where relevant)

- `POST /briefs` — create brief.
- `POST /runs` — start creative run from brief; returns `run_id`, `client_token`.
- `GET /runs/{id}` — run status (state, progress, iteration, budgets).
- `GET /runs/{id}/agents` — agent timeline/messages.
- `GET /runs/{id}/outputs` — generated assets + metadata/scores.
- `POST /runs/{id}/approve` — mark approved (client_token required).
- `POST /runs/{id}/interrupt` — graceful stop (client_token required).
- Query params: pagination (`limit`, `cursor`), filtering (`state`, `agent`), stable ordering (`created_at`, `iteration`).
- Idempotent retries via client-provided `Idempotency-Key` on mutating calls.

## Frontend Usage (dev)

```bash
cd frontend
npm install
npm run dev
# visit http://localhost:5173 (API expected at http://127.0.0.1:8000; adjust in src/App.jsx)
```

## Backend (example, FastAPI)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Database Sketch (Supabase/Postgres)

- `creative_briefs(id, user_id, title, description, created_at)`
- `creative_runs(id, brief_id, user_id, state, iteration, progress, budget_used, created_at, updated_at)`
- `agent_runs(id, creative_run_id, agent, iteration, started_at, ended_at, status)`
- `agent_messages(id, agent_run_id, role, content, meta, created_at)`
- `generations(id, creative_run_id, agent_run_id, asset_url, thumb_url, score, meta, created_at)`
- `assets(id, creative_run_id, storage_path, mime, bytes, created_at)`
- `approvals(id, creative_run_id, approved_by, approved_at, decision, notes)`

## Concurrency, Budgets, Safety

- Per-run concurrency caps (e.g., max N generator jobs).
- Iteration cap (e.g., max 3 cycles) and wall-clock budget per run.
- Graceful cancellation on interrupt; no orphaned generator tasks.
- Per-user rate limits and run caps; ownership enforced on all private operations.

## Observability & Debuggability

- Structured logs (`run_id`, `agent`, `iteration`, `event`).
- Stable ordering for timelines (by `created_at`, `agent`, `iteration`).
- Metrics: durations per state, retries, budget usage.
- Trace/replay: rehydrate a run from agent messages and generation metadata.

## Sample Brief

- Title: “Cyberpunk product launch hero”
- Description: “Two hero banners and one thumbnail; neon palette; legible product name; avoid faces; clean type.”

## Example Run (happy path)

1) Planner tasks out hero A, hero B, thumbnail; defines style guards.  
2) Generator produces variants per task; stores assets and metadata.  
3) Critic scores per brief; Consistency checks palette/layout drift.  
4) Manager iterates if score < 7 or drift detected, respecting caps.  
5) Outputs surfaced; state moves to `AWAITING_APPROVAL`; user approves or interrupts.

## Tradeoffs & Limitations (current prototype)

- Generation/critique may be mocked; swap in real adapters later.
- Auth, RLS, and rate limiting must be added for production.
- Pagination/filtering not yet wired on list endpoints.
- State machine may be simplified in code; expand per spec.

## Future Improvements

- Full Supabase integration (auth, storage, RLS, rate limits).
- Stronger idempotency and retry semantics.
- Richer frontend UX for async states, errors, retries.
- Better cancellation semantics and durable job orchestration.
- Expanded telemetry (tracing + metrics dashboards).