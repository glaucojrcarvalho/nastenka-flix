#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  cd "$ROOT_DIR"
  docker compose exec backend python -m app.db.seed
  exit 0
fi

if [[ -x "$ROOT_DIR/backend/.venv/bin/python" ]]; then
  cd "$ROOT_DIR/backend"
  "$ROOT_DIR/backend/.venv/bin/python" -m app.db.seed
  exit 0
fi

cd "$ROOT_DIR/backend"
python3 -m app.db.seed
