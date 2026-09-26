#!/bin/bash
# One-pass build for quick visual checks (TOC numbers may be stale)
set -e
cd "$(dirname "$0")"
python3 build.py pages.json | grep -v "^built" || true
node render.js notes.html raw.pdf >/dev/null
python3 finalize.py pages raw.pdf
python3 finalize.py stamp raw.pdf test.pdf
