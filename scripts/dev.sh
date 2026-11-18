#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "Run 'make setup' first." >&2
  exit 1
fi

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-5173}"

"$ROOT/.venv/bin/uvicorn" app.main:app \
  --app-dir "$ROOT/backend" \
  --reload \
  --host "$API_HOST" \
  --port "$API_PORT" &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT/client"
npm run dev -- --host "$WEB_HOST" --port "$WEB_PORT"
