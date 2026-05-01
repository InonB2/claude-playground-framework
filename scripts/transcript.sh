#!/usr/bin/env bash
# transcript.sh — wrapper for yt_transcript.py
# Usage: bash scripts/transcript.sh <youtube_url>
#
# Resolves the repo root automatically regardless of where you call this from.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/transcript.sh <youtube_url>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python "$REPO_ROOT/scripts/yt_transcript.py" "$1"
