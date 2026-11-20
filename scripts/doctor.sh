#!/usr/bin/env bash
# FrameCrew environment doctor — checks every dependency and prints how to fix it.
set -uo pipefail
cd "$(dirname "$0")/.."

pass=0
fail=0

ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; pass=$((pass+1)); }
bad()  { printf "  \033[31m✗\033[0m %s\n     fix: %s\n" "$1" "$2"; fail=$((fail+1)); }

if [ -x .venv/bin/python ]; then
  export PATH="$(pwd)/.venv/bin:$PATH"
  PYTHON="$(pwd)/.venv/bin/python"
else
  PYTHON=python3
fi

echo "FrameCrew doctor"
echo "----------------"

# --- CLI tools ---
command -v ffmpeg   >/dev/null 2>&1 && ok "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')" || bad "ffmpeg missing"      "brew install ffmpeg"
command -v ffprobe  >/dev/null 2>&1 && ok "ffprobe present"                                          || bad "ffprobe missing"     "comes with ffmpeg: brew install ffmpeg"
command -v scenedetect >/dev/null 2>&1 && ok "scenedetect present"                                   || bad "scenedetect missing" "./.venv/bin/python -m pip install scenedetect"
command -v whisper  >/dev/null 2>&1 && ok "whisper present"                                          || bad "whisper missing"     "./.venv/bin/python -m pip install openai-whisper"
( command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1 ) && ok "ImageMagick present" || bad "ImageMagick missing" "brew install imagemagick"
"$PYTHON" -c "import watchdog" 2>/dev/null && ok "python watchdog present"                             || bad "watchdog missing"    "./.venv/bin/python -m pip install watchdog"
"$PYTHON" -c "import rembg"    2>/dev/null && ok "rembg present"                                        || bad "rembg missing"       "./.venv/bin/python -m pip install rembg"
"$PYTHON" -c "import realesrgan" 2>/dev/null && ok "realesrgan present"                                 || bad "realesrgan missing"  "./.venv/bin/python -m pip install realesrgan"

# --- LLM API (v0.1.0 is API-first) ---
if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a; . ./.env; set +a
fi
[ -n "${OPENAI_API_KEY:-}" ] && ok "OPENAI_API_KEY set" || bad "OPENAI_API_KEY not set" "copy .env.example to .env and add your key"

# --- Config ---
[ -f config/framecrew.yaml ] && ok "config/framecrew.yaml present" || bad "config/framecrew.yaml missing" "cp config/framecrew.example.yaml config/framecrew.yaml"

# --- Hermes ---
HERMES_DIR="${HERMES_HOME:-$HOME/.hermes}"
command -v hermes >/dev/null 2>&1 && ok "hermes CLI present" || bad "hermes CLI not found" "install Hermes (the agent runtime)"
skill_count=$(ls "$HERMES_DIR"/skills/video/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$skill_count" -ge 13 ] && ok "$skill_count skills loaded in Hermes" || bad "skills not loaded ($skill_count/13)" "run ./install.sh (or bash scripts/install_skills.sh)"
[ -f "$HERMES_DIR/memories/user/model-routing.md" ] && ok "Hermes routing rules installed" || bad "routing rules missing" "run bash scripts/setup_hermes.sh"

# --- DaVinci Resolve (optional, delivery only) ---
if [ -d "/Applications/DaVinci Resolve/DaVinci Resolve.app" ]; then ok "DaVinci Resolve installed"; else
  printf "  \033[33m!\033[0m DaVinci Resolve not found (needed only for project delivery — Studio required)\n"; fi

echo "----------------"
echo "passed: $pass   failed: $fail"
[ "$fail" -eq 0 ] && echo "Environment checks passed. Run synthetic tests with bash tests/e2e_smoke.sh; this is not a real-footage acceptance test." || echo "Fix the items above, then re-run ./scripts/doctor.sh"
exit "$fail"
