#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
if [[ ! -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  echo "Project environment missing. See README.md: Local Jupyter setup." >&2
  exit 1
fi
if [[ "${1:-}" == "--classic" ]]; then
  shift
  exec "$PROJECT_DIR/.venv/bin/python" -m notebook --ServerApp.root_dir="$PROJECT_DIR" "$@"
fi
exec "$PROJECT_DIR/.venv/bin/python" -m jupyterlab --ServerApp.root_dir="$PROJECT_DIR" "$@"
