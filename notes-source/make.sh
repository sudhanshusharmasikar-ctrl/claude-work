#!/bin/bash
# Full build: two passes so the table of contents gets real page numbers.
set -e
cd "$(dirname "$0")"
rm -f pages.json
python3 build.py
node render.js notes.html raw.pdf
python3 finalize.py pages raw.pdf
python3 build.py pages.json
node render.js notes.html raw.pdf
python3 finalize.py pages raw.pdf
python3 build.py pages.json
node render.js notes.html raw.pdf
python3 finalize.py stamp raw.pdf "${1:-JavaScript_Notes.pdf}"
