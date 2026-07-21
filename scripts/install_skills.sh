#!/usr/bin/env bash
# Copy the FrameCrew agent skills into the local agent skills directory.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/video"
DEST="${FRAMECREW_SKILLS_DEST:-$HOME/.framecrew/skills/video}"

mkdir -p "$DEST"
cp -v "$SRC"/*.md "$DEST"/
echo "Installed $(ls "$SRC"/*.md | wc -l | tr -d ' ') skills to $DEST"
