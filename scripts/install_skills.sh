#!/usr/bin/env bash
# Load the FrameCrew agent skills into Hermes.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/video"
DEST="${HERMES_HOME:-$HOME/.hermes}/skills/video"

mkdir -p "$DEST"
cp -v "$SRC"/*.md "$DEST"/
echo "Loaded $(ls "$SRC"/*.md | wc -l | tr -d ' ') skills into $DEST"
