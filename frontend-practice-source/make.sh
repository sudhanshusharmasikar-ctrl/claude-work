#!/bin/bash
# Build the frontend practice guide with the GenAI notes' toolchain (../genai-notes-source).
# Run ../genai-notes-source/fonts/get_fonts.sh once first.   usage: ./make.sh [output.pdf]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/../genai-notes-source" && pwd)"
OUT="$(realpath -m "${1:-$HERE/../Frontend-Practice-Explained-Simply.pdf}")"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
cp "$SRC"/{build.py,diagrams.py,svg.py,finalize.py,render.js,make.sh,template.html,style.css,cover.css} "$BUILD"/
ln -s "$SRC/fonts" "$BUILD/fonts"
cp -r "$HERE/content" "$BUILD/content"
# "#### Title" -> a styled paragraph: Chromium would put real <h4>s in the PDF outline,
# which the toolchain matches one-to-one against the h1-h3 headings.
python3 - "$BUILD/content" <<'PY'
import pathlib, re, sys
for f in pathlib.Path(sys.argv[1]).glob("*.md"):
    f.write_text(re.sub(r"(?m)^#### (.+)$", r'<p class="h4" markdown="span">\1</p>', f.read_text()))
PY
cp "$HERE/cover.html" "$HERE/book.json" "$BUILD"/
cat "$HERE/figures.py" >> "$BUILD/diagrams.py"   # this guide's diagrams
cat "$HERE/booklet.css" >> "$BUILD/cover.css"    # cover.css loads last, so these rules win
"$BUILD/make.sh" "$OUT"
