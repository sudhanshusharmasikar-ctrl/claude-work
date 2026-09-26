"""Flag diagram elements that extend past their SVG canvas (rects exact, text estimated)."""
import re, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))  # the build folder
import diagrams
from svg import text_width
num = r"(-?[\d.]+)"
for name, fn in diagrams.FIGS.items():
    svg = fn()
    W, H = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    probs = []
    for m in re.finditer(rf'<rect x="{num}" y="{num}" width="{num}" height="{num}"', svg):
        x, y, w, h = map(float, m.groups())
        if x < -0.5 or y < -0.5 or x + w > W + 0.5 or y + h > H + 0.5:
            probs.append(f"rect ({x:.0f},{y:.0f},{x + w:.0f},{y + h:.0f})")
    for m in re.finditer(r'<text x="(-?[\d.]+)" y="(-?[\d.]+)" font-family="([^"]+)" font-size="([\d.]+)" '
                         r'font-weight="(\d+)"[^>]*text-anchor="(\w+)"[^>]*>(.*?)</text>', svg):
        x, y, fam, size, wt, anchor, s = m.groups()
        x, y, size, wt = float(x), float(y), float(size), int(wt)
        s = re.sub(r"<[^>]+>", "", s).replace("&quot;", '"').replace("&amp;", "&").replace("&#x27;", "'") \
            .replace("&lt;", "<").replace("&gt;", ">")
        tw = text_width(s, size, "Mono" in fam, wt)
        x0 = x - tw / 2 if anchor == "middle" else (x - tw if anchor == "end" else x)
        if x0 < -1 or x0 + tw > W + 1 or y - size * 0.8 < -1 or y + size * 0.25 > H + 1:
            probs.append(f"text {s[:30]!r} ({x0:.0f}..{x0 + tw:.0f}, y={y:.0f})")
    if probs:
        print(f"{name} [{W:.0f}x{H:.0f}]:", "; ".join(probs[:6]))
print("checked", len(diagrams.FIGS), "figures")
