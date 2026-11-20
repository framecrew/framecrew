#!/usr/bin/env bash
# Run Hermes with FrameCrew's repository-local Python tools available on PATH.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  echo "FrameCrew Python environment missing. Run ./install.sh first." >&2
  exit 1
fi
if ! command -v hermes >/dev/null 2>&1; then
  echo "Hermes CLI not found. Install/configure Hermes first." >&2
  exit 1
fi
export PATH="$ROOT/.venv/bin:$PATH"
cd "$ROOT"
exec hermes "$@"
