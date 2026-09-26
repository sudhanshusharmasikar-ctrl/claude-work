import sys, collections
import pymupdf as fitz
doc = fitz.open(sys.argv[1])
MM = 72 / 25.4
W, H = doc[0].rect.width, doc[0].rect.height
L, R, T, B = 17 * MM, W - 17 * MM, 22 * MM, H - 20 * MM
issues = collections.defaultdict(list)

def inter(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return max(0, x1 - x0) * max(0, y1 - y0)

for pno, page in enumerate(doc, 1):
    if pno == 1:
        continue  # full-bleed cover
    words = [w for w in page.get_text("words") if w[4].strip()]
    # shrink boxes slightly: glyph boxes include line-height padding
    boxes = []
    for w in words:
        x0, y0, x1, y1 = w[:4]
        h = y1 - y0
        boxes.append((x0 + 0.3, y0 + h * 0.22, x1 - 0.3, y1 - h * 0.22, w[4]))
    # (b) margins (skip stamped header/footer zones)
    for bx in boxes:
        x0, y0, x1, y1, t = bx
        if y1 < 16 * MM or y0 > H - 13 * MM:
            continue
        if x0 < L - 1.5 or x1 > R + 1.5 or y0 < T - 3 or y1 > B + 3:
            issues[pno].append(f"OUTSIDE margin: {t!r} at ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
    # (a) word-word overlaps using a grid
    grid = collections.defaultdict(list)
    for i, bx in enumerate(boxes):
        for gx in range(int(bx[0] // 40), int(bx[2] // 40) + 1):
            for gy in range(int(bx[1] // 40), int(bx[3] // 40) + 1):
                grid[(gx, gy)].append(i)
    seen = set()
    for cell in grid.values():
        for a in range(len(cell)):
            for b in range(a + 1, len(cell)):
                i, j = cell[a], cell[b]
                if (i, j) in seen:
                    continue
                seen.add((i, j))
                A, Bx = boxes[i], boxes[j]
                ov = inter(A, Bx)
                if ov <= 0:
                    continue
                small = min((A[2] - A[0]) * (A[3] - A[1]), (Bx[2] - Bx[0]) * (Bx[3] - Bx[1]))
                if small > 0 and ov / small > 0.12:
                    issues[pno].append(f"OVERLAP: {A[4]!r} x {Bx[4]!r} at ({A[0]:.0f},{A[1]:.0f})")
    # (c) text crossing a stroked box border
    rects = []
    for d in page.get_drawings():
        if d.get("color") is None:   # no stroke
            continue
        r = d["rect"]
        if r.width < 12 or r.height < 10:
            continue
        rects.append((r.x0, r.y0, r.x1, r.y1))
    for bx in boxes:
        wb = bx[:4]
        for r in rects:
            ov = inter(wb, r)
            area = (wb[2] - wb[0]) * (wb[3] - wb[1])
            if area <= 0 or ov <= 0:
                continue
            frac = ov / area
            if 0.15 < frac < 0.85:
                issues[pno].append(f"CROSSES BORDER: {bx[4]!r} at ({wb[0]:.0f},{wb[1]:.0f}) rect=({r[0]:.0f},{r[1]:.0f},{r[2]:.0f},{r[3]:.0f})")
                break

total = 0
for p in sorted(issues):
    uniq = list(dict.fromkeys(issues[p]))
    total += len(uniq)
    print(f"--- page {p}")
    for s in uniq[:12]:
        print("   ", s)
print("pages with issues:", len(issues), "total:", total)
