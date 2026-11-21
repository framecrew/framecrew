#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  echo "Run bash install.sh first." >&2
  exit 1
fi
export PATH="$ROOT/.venv/bin:${HERMES_HOME:-$HOME/.hermes}/bin:$HOME/.local/bin:$PATH"
cd "$ROOT"
exec hermes "$@"
