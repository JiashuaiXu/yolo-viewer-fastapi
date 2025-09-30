#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v uv >/dev/null 2>&1 || {
  echo "[start.sh] 未找到 uv，请先安装：https://docs.astral.sh/uv/" >&2
  exit 1
}

command -v pnpm >/dev/null 2>&1 || {
  echo "[start.sh] 未找到 pnpm，请先安装：https://pnpm.io/installation" >&2
  exit 1
}

cd "$ROOT_DIR/backend"
uv sync
uv run uvicorn main:app --reload --port 3001 &
BACKEND_PID=$!

cleanup() {
  if ps -p $BACKEND_PID >/dev/null 2>&1; then
    kill $BACKEND_PID 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR/frontend"
pnpm install
pnpm run dev -- --host
