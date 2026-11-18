# Harborline Dispatch

An internal freight operations dashboard used by Harborline Freight's dispatch team. Dispatchers review shipments, open a shipment's details, and update status or the assigned driver.

This repo is a timed practice app for a live coding interview where you work in an existing codebase with Cursor (or another AI-assisted editor). It is a small full-stack app: a Python FastAPI backend with SQLite, and a React (Vite + TypeScript) frontend.

## Run locally

```bash
make setup
make dev
```

Then open [http://localhost:5173](http://localhost:5173). The API runs on [http://localhost:8000](http://localhost:8000) and the Vite dev server proxies `/api` to it.

`make setup` creates a virtualenv, installs Python dependencies, and runs `npm install` in `client/`. `make dev` starts both servers. These commands work with `python3` on macOS.

### Manual commands

If you prefer not to use Make:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd client && npm install && cd ..

# Terminal 1 — API
source .venv/bin/activate
cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — UI
cd client && npm run dev
```

## Tests and checks

```bash
make test
```

Or, with the virtualenv activated:

```bash
pytest
```

Run the tests before you start. Some tests may already be failing.

Optional lint and type checks:

```bash
make lint
```

Or:

```bash
ruff check backend
mypy backend/app
```

In `client/`, `npx tsc --noEmit` typechecks the frontend.

## Practice

1. Read [PRACTICE_GUIDE.md](./PRACTICE_GUIDE.md) and set a 45-minute timer.
2. Work through [TASKS.md](./TASKS.md). You are not expected to finish every task.
3. After the timer, use the self-review checklist in the practice guide. Only then read [INTERVIEWER_NOTES.md](./INTERVIEWER_NOTES.md) — it contains spoilers.

A starter Cursor rules file lives at [`.cursor/rules/project.mdc`](./.cursor/rules/project.mdc).
