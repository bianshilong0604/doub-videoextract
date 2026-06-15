#!/usr/bin/env bash
set -euo pipefail

# videoextract — First-time setup
# Usage: ./setup.sh

echo "=== videoextract Setup ==="

# --- Check Python ---
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Error: python3 (or python) is required but was not found."
  echo "Install Python 3.8+ from https://www.python.org/downloads/"
  exit 1
fi

PY_VERSION=$("$PYTHON_BIN" -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
PY_MAJOR=$("$PYTHON_BIN" -c 'import sys; print(sys.version_info[0])')
PY_MINOR=$("$PYTHON_BIN" -c 'import sys; print(sys.version_info[1])')

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
  echo "Error: Python 3.8+ required (detected $PY_VERSION)."
  exit 1
fi
echo "Found Python $PY_VERSION"

# --- Check pip ---
if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
  echo "Error: pip is not available for $PYTHON_BIN."
  echo "Install pip: $PYTHON_BIN -m ensurepip --upgrade"
  exit 1
fi

# --- Environment files ---
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it with your values"
fi

if [ ! -f config.json ] && [ -f config.example.json ]; then
  cp config.example.json config.json
  echo "Created config.json from config.example.json — edit it with your AI API key"
fi

# --- Install core dependencies ---
echo ""
echo "Installing core dependencies..."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt

# --- Optional dependencies (best-effort) ---
echo ""
echo "Installing optional: douyin-tiktok-scraper (Douyin layer-1 extractor)..."
"$PYTHON_BIN" -m pip install douyin-tiktok-scraper || echo "  (optional) skipped — Douyin will fall back to yt-dlp"

# Note: faster-whisper is large and not always needed. Install on demand:
#   pip install faster-whisper

# --- Output dir ---
mkdir -p output

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit config.json and set ai_api.api_key (DeepSeek / OpenAI / GLM / etc.)"
echo "  2. Run: python main.py \"<URL>\" --config config.json"
echo "  3. Output will appear in ./output/"
echo "  4. Optional ASR: pip install faster-whisper, then set transcribe.enabled = true"
echo "  5. Using Claude Code? CLAUDE.md has all the context."
