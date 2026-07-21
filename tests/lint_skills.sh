#!/usr/bin/env bash
# Lint agent skills: required structure + secret / hardcoded-personal-value scan.
set -uo pipefail
fail=0

for f in skills/video/*.md; do
  grep -q "^# " "$f"    || { echo "FAIL $f: missing H1 title"; fail=1; }
  grep -qi "Role:" "$f" || { echo "FAIL $f: missing Role line"; fail=1; }
done

# Block secrets and leftover personal values from being committed.
if grep -RniE "(sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|/Users/|aperture)" skills/ templates/ config/ 2>/dev/null; then
  echo "FAIL: possible secret or hardcoded personal value found"; fail=1
fi

[ "$fail" -eq 0 ] && { echo "PASS: skills lint clean"; exit 0; } || { echo "skill lint failed"; exit 1; }
