#!/usr/bin/env bash
# FrameCrew installer for macOS with Homebrew.
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-}" in
  "") brew_packages=(python ffmpeg) ;;
  --experimental-hermes) brew_packages=(python ffmpeg imagemagick) ;;
  *) echo "Usage: bash install.sh [--experimental-hermes]" >&2; exit 2 ;;
esac

echo "==> 1/6 Installing system tools (Homebrew)"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh first." >&2; exit 1
fi
brew install "${brew_packages[@]}"
if [ "$#" -eq 0 ]; then
  bash scripts/doctor.sh
  exit
fi

echo "==> 2/6 Installing Python media tools"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install scenedetect openai-whisper watchdog rembg realesrgan
export PATH="$(pwd)/.venv/bin:$PATH"

echo "==> 3/6 Creating config and env (if missing)"
[ -f config/framecrew.yaml ] || cp config/framecrew.example.yaml config/framecrew.yaml
[ -f .env ] || cp .env.example .env

echo "==> 4/6 Creating project folders"
PROJECTS_ROOT="${PROJECTS_ROOT:-$HOME/FrameCrew/Projects}"
TEMPLATES_ROOT="${TEMPLATES_ROOT:-$HOME/FrameCrew/Templates}"
mkdir -p "$PROJECTS_ROOT" "$TEMPLATES_ROOT"
for template in templates/*.txt; do
  target="$TEMPLATES_ROOT/${template##*/}"
  [ -e "$target" ] || cp "$template" "$target"
done

echo "==> 5/6 Wiring FrameCrew into Hermes (routing rules)"
bash scripts/setup_hermes.sh

echo "==> 6/6 Loading agent skills into Hermes"
bash scripts/install_skills.sh

echo
echo "Setup complete. Two things left:"
echo "  1. Put your OPENAI_API_KEY in .env"
echo "  2. Send the kickoff prompt in KICKOFF.md to Hermes once to wake the crew"
echo
echo "Then run ./scripts/doctor.sh to confirm, and drop footage + event.txt to start a job."
