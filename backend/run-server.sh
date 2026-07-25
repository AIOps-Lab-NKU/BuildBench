#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STARTER_KIT="${BB_STARTER_KIT_ROOT:-$(cd "$ROOT/.." && pwd)/buildbench-starter-kit}"
DATA_ROOT="${BB_WEB_DATA_ROOT:-$ROOT/runtime-data}"
HOST="${BB_WEB_HOST:-127.0.0.1}"
PORT="${BB_WEB_PORT:-8765}"
WORKERS="${BB_SMOKE_WORKERS:-2}"

mkdir -p "$DATA_ROOT"
cd "$ROOT"

python3 -m backend.server \
  --host "$HOST" \
  --port "$PORT" \
  --starter-kit "$STARTER_KIT" \
  --data-root "$DATA_ROOT" \
  --smoke-workers "$WORKERS" \
  2>&1 | tee -a "$DATA_ROOT/server.log"
