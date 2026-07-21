#!/usr/bin/env bash
# Install FrameCrew's model-routing rules into Hermes.
set -euo pipefail
cd "$(dirname "$0")/.."

DEST="${HERMES_HOME:-$HOME/.hermes}/memories/user"
mkdir -p "$DEST"
cp -v memories/model-routing.md "$DEST/model-routing.md"

if command -v hermes >/dev/null 2>&1; then
  echo "Hermes CLI detected."
else
  echo "NOTE: 'hermes' CLI not found on PATH. Install Hermes so it can load these skills." >&2
fi
echo "Routing rules installed to $DEST/model-routing.md"
