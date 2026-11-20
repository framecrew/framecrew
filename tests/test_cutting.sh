#!/usr/bin/env bash
# Cutting agent behavior: produces a rough cut and never touches raw/.
set -euo pipefail
WORK="tests/.work/IntakeTest"
bash tests/fixtures/make_fixtures.sh "$WORK"
mkdir -p "$WORK/output"

before=$(shasum "$WORK"/raw/*.mp4)

list="$WORK/.concat.txt"; : > "$list"
for f in "$WORK"/raw/clip_*.mp4; do
  printf 'file raw/%s\n' "${f##*/}" >> "$list"
done
ffmpeg -v error -y -f concat -safe 1 -i "$list" -c copy "$WORK/output/rough_cut.mp4"

after=$(shasum "$WORK"/raw/*.mp4)

[ -f "$WORK/output/rough_cut.mp4" ] || { echo "FAIL: rough_cut.mp4 not created"; exit 1; }
[ "$before" = "$after" ] || { echo "FAIL: raw/ was modified"; exit 1; }
echo "PASS: rough_cut.mp4 created; raw/ untouched"
