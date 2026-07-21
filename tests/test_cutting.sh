#!/usr/bin/env bash
# Cutting agent behavior: produces a rough cut and never touches raw/.
set -euo pipefail
WORK="tests/.work/IntakeTest"
bash tests/fixtures/make_fixtures.sh "$WORK"
mkdir -p "$WORK/output"

before=$(find "$WORK/raw" -type f -print0 | sort -z | xargs -0 shasum | shasum | awk '{print $1}')

list="$WORK/.concat.txt"; : > "$list"
for f in "$WORK"/raw/clip_*.mp4; do
  echo "file '$(cd "$(dirname "$f")" && pwd)/$(basename "$f")'" >> "$list"
done
ffmpeg -y -f concat -safe 0 -i "$list" -c copy "$WORK/output/rough_cut.mp4" >/dev/null 2>&1

after=$(find "$WORK/raw" -type f -print0 | sort -z | xargs -0 shasum | shasum | awk '{print $1}')

[ -f "$WORK/output/rough_cut.mp4" ] || { echo "FAIL: rough_cut.mp4 not created"; exit 1; }
[ "$before" = "$after" ] || { echo "FAIL: raw/ was modified"; exit 1; }
echo "PASS: rough_cut.mp4 created; raw/ untouched"
