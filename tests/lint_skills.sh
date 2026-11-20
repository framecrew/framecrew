#!/usr/bin/env bash
# Lint agent skills: required structure + secret / hardcoded-personal-value scan.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

# Validate the complete intended skill inventory, not merely files that happen to exist.
expected=(watcher-agent editor-manager intake-agent edit-team-lead cutting-agent trimming-agent color-agent titles-agent transitions-agent audio-agent enhancement-agent qc-agent delivery-agent)
for skill in "${expected[@]}"; do
  if [ ! -f "skills/video/$skill.md" ]; then
    echo "FAIL: missing skill skills/video/$skill.md"
    fail=1
  fi
done
skill_count=$(find skills/video -maxdepth 1 -type f -name "*.md" | wc -l | tr -d " ")
if [ "$skill_count" -ne "${#expected[@]}" ]; then
  echo "FAIL: expected ${#expected[@]} skill definitions, found $skill_count"
  fail=1
fi

for f in skills/video/*.md; do
  grep -q "^# " "$f"    || { echo "FAIL $f: missing H1 title"; fail=1; }
  grep -qi "Role:" "$f" || { echo "FAIL $f: missing Role line"; fail=1; }
done

# Block secrets and leftover personal values from being committed.
if grep -RniE "(sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|/Users/|aperture)" skills/ templates/ config/ 2>/dev/null; then
  echo "FAIL: possible secret or hardcoded personal value found"; fail=1
fi

[ "$fail" -eq 0 ] && { echo "PASS: skills lint clean"; exit 0; } || { echo "skill lint failed"; exit 1; }
