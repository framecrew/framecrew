#!/usr/bin/env bash
# FrameCrew one-shot installer (macOS / Apple Silicon).
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/5 Installing system tools (Homebrew)"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh first." >&2; exit 1
fi
brew install ffmpeg imagemagick || true

echo "==> 2/5 Installing Python tools"
pip3 install --break-system-packages scenedetect openai-whisper watchdog rembg realesrgan || true

echo "==> 3/5 Creating config from example (if missing)"
[ -f config/framecrew.yaml ] || cp config/framecrew.example.yaml config/framecrew.yaml
[ -f .env ] || cp .env.example .env

echo "==> 4/5 Creating project folders"
PROJECTS_ROOT="${PROJECTS_ROOT:-$HOME/FrameCrew/Projects}"
TEMPLATES_ROOT="${TEMPLATES_ROOT:-$HOME/FrameCrew/Templates}"
mkdir -p "$PROJECTS_ROOT" "$TEMPLATES_ROOT"
cp -n templates/*.txt "$TEMPLATES_ROOT"/ 2>/dev/null || true

echo "==> 5/5 Installing agent skills"
bash scripts/install_skills.sh

echo
echo "Done. Next steps:"
echo "  1. Edit config/framecrew.yaml for your brand"
echo "  2. Add your OPENAI_API_KEY to .env"
echo "  3. Run ./scripts/doctor.sh"
echo "  4. Run ./tests/e2e_smoke.sh"
