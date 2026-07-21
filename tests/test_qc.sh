#!/usr/bin/env bash
# QC gate: must PASS a complete set and REJECT a broken one with a specific error.
set -uo pipefail

make_base() { # $1=dir  $2=withlut|nolut
  local d="$1"
  rm -rf "$d"; mkdir -p "$d/output" "$d/luts" "$d/transcripts"
  ffmpeg -y -f lavfi -i "testsrc=duration=2:size=320x240:rate=25" \
         -f lavfi -i "sine=frequency=440:duration=2" \
         -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest \
         "$d/output/enhanced.mp4" >/dev/null 2>&1
  echo "hello" > "$d/transcripts/transcript.txt"
  echo "1"     > "$d/transcripts/subtitles.srt"
  [ "${2:-}" = "withlut" ] && echo "# LUT" > "$d/luts/framecrew_grade.cube"
  return 0
}

run_qc() { # $1=dir ; returns number of failed checks
  local d="$1" errs=0
  ffmpeg -v error -i "$d/output/enhanced.mp4" -f null - 2>/dev/null || { echo "  reject: file integrity"; errs=$((errs+1)); }
  ls "$d"/luts/*_grade.cube >/dev/null 2>&1 || { echo "  reject: missing luts/*_grade.cube"; errs=$((errs+1)); }
  [ -f "$d/transcripts/transcript.txt" ] || { echo "  reject: missing transcripts/transcript.txt"; errs=$((errs+1)); }
  [ -f "$d/transcripts/subtitles.srt" ]  || { echo "  reject: missing transcripts/subtitles.srt"; errs=$((errs+1)); }
  return "$errs"
}

echo "QC pass test:"
make_base tests/.work/QCPass withlut
if run_qc tests/.work/QCPass; then echo "PASS: complete set accepted"; else echo "FAIL: expected PASS"; exit 1; fi

echo "QC fail test (no LUT):"
make_base tests/.work/QCFail nolut
if run_qc tests/.work/QCFail; then echo "FAIL: QC should have rejected"; exit 1; else echo "PASS: QC rejected with a specific error"; fi
