#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin ]]; then
  echo "Use Install FrameCrew.cmd on Windows. This launcher supports macOS." >&2
  exit 1
fi
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v brew >/dev/null 2>&1; then
  echo "Installing Homebrew. Follow its prompts if it needs your approval."
  installer="$(mktemp)"
  trap 'rm -f "$installer"' EXIT
  curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$installer"
  /bin/bash "$installer"
fi
if command -v python3.11 >/dev/null 2>&1; then
  exec python3.11 scripts/install_framecrew.py "$@"
fi
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(not ((3,11) <= sys.version_info[:2] <= (3,12)))'; then
  exec python3 scripts/install_framecrew.py "$@"
fi
brew install python@3.11
exec "$(brew --prefix python@3.11)/bin/python3.11" scripts/install_framecrew.py "$@"
