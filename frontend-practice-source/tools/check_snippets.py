"""Check that the code shown in the guide is the code that was tested.

* A block titled "NN/file ..." (for example "05/script.js") must appear, ignoring
  whitespace differences, in verify/exercises/NN-*/file: the files the grader passed.
* A block titled "... exercises/<folder>/solution/<file> (part)" must appear in that
  file of a clone of the practice repo (pass its path as the first argument; skipped
  without one). Blocks marked "(shortened)" are edited excerpts and are not checked.

usage: python3 tools/check_snippets.py [path-to-accenture-frontend-practice]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERIFY = ROOT / "verify" / "exercises"
REPO = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
FENCE = re.compile(r"^([ \t]*)```(\w+)([^\n]*)\n(.*?)\n\1```[ \t]*$", re.M | re.S)


def norm(text):
    return " ".join(text.split())


checked, bad, skipped = 0, 0, 0
for md in sorted((ROOT / "content").glob("*.md")):
    for m in FENCE.finditer(md.read_text()):
        title = re.search(r'title="([^"]*)"', m.group(3))
        title = title.group(1) if title else ""
        code = "\n".join(line[len(m.group(1)):] for line in m.group(4).split("\n"))
        own = re.match(r"(\d\d)/(script\.js|style\.css|index\.html)", title)
        ref = re.search(r"exercises/([\w-]+)/solution/([\w.]+) \(part\)", title)
        if own:
            target = next(VERIFY.glob(f"{own.group(1)}-*")) / own.group(2)
        elif ref and REPO:
            target = REPO / "exercises" / ref.group(1) / "solution" / ref.group(2)
        elif ref:
            skipped += 1
            continue
        else:
            continue
        checked += 1
        if norm(code) not in norm(target.read_text()):
            bad += 1
            print(f"MISMATCH {md.name}: {title!r} is not in {target.relative_to(target.parents[2])}")
print(f"{checked} code blocks checked, {bad} mismatches, {skipped} skipped (no repo path given)")
sys.exit(1 if bad else 0)
