#!/usr/bin/env bash
# Load the FrameCrew agent skills into Hermes.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/video"
DEST="${HERMES_HOME:-$HOME/.hermes}/skills/video"

for source in "$SRC"/*.md; do
  filename="${source##*/}"
  name="${filename%.md}"
  description=$(sed -n 's/^\*\*Role:\*\* //p' "$source")
  if [ -z "$description" ]; then
    echo "Missing role description in $source" >&2
    exit 1
  fi
  mkdir -p "$DEST/$name"
  {
    printf -- '---\nname: %s\ndescription: >-\n  %s\n---\n\n' "$name" "$description"
    cat "$source"
  } > "$DEST/$name/SKILL.md"
  echo "Installed $name"
done
cp "$SRC/../../scripts/check_windows_job.py" "$DEST/watcher-agent/check_windows_job.py"
cp "$SRC/../../scripts/export_resolve.py" "$DEST/delivery-agent/export_resolve.py"
