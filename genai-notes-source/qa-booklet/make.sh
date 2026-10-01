#!/bin/bash
# Build the Lecture Q&A booklet with the main notes' toolchain (one directory up).
# Run ../fonts/get_fonts.sh once first.   usage: ./make.sh [output.pdf]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/.." && pwd)"
OUT="$(realpath -m "${1:-$HERE/../../Lecture-QA-Interview-Practice.pdf}")"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
cp "$SRC"/{build.py,diagrams.py,svg.py,finalize.py,render.js,make.sh,template.html,style.css,cover.css} "$BUILD"/
ln -s "$SRC/fonts" "$BUILD/fonts"
cp -r "$HERE/content" "$BUILD/content"
cp "$HERE/cover.html" "$HERE/book.json" "$BUILD"/
cat "$HERE/booklet.css" >> "$BUILD/cover.css"   # cover.css loads last, so these rules win
"$BUILD/make.sh" "$OUT"
