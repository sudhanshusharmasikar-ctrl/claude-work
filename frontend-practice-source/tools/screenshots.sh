#!/bin/bash
# Rebuild the before/after pictures in content/img/ from a clone of the practice repo.
# usage: tools/screenshots.sh <path-to-accenture-frontend-practice>
# Needs Node.js with playwright, and Python 3 with Pillow. Set PW_CHROMIUM to use an installed Chromium.
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$1" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/solved" "$WORK/png"
for dir in "$HERE"/verify/exercises/*/; do
  name="$(basename "$dir")"
  cp -r "$REPO/exercises/$name" "$WORK/solved/"
  cp "$dir"* "$WORK/solved/$name/"
done
node "$HERE/tools/shoot.js" "$REPO/exercises" "$WORK/solved" "$WORK/png"
python3 "$HERE/tools/compose_shots.py" "$WORK/png" "$HERE/content/img" \
  "$HERE/../genai-notes-source/fonts/static/Inter-700.ttf"
