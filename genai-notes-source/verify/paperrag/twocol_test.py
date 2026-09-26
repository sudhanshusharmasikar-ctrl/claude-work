"""Build a small two-column PDF and compare PaperRAG's block order with a column-aware order."""
import sys
import pymupdf as fitz

import os
sys.path.insert(0, os.environ.get("PAPERRAG_REPO", "../paperrag"))   # your repo clone
from app.chunking import page_blocks, clean, _is_noise   # the real project code

doc = fitz.open()
page = doc.new_page(width=612, height=792)
W = 612
def put(x0, y0, x1, text):
    page.insert_textbox(fitz.Rect(x0, y0, x1, y0 + 60), text, fontsize=10)
filler = "words that make this paragraph long enough to survive the noise filter"
put(60, 50, 552, f"TITLE: A Two Column Paper about Retrieval, {filler}.")
# left column paragraphs, right column paragraphs at slightly different heights
put(60, 120, 296, f"L1 left column first paragraph {filler}.")
put(316, 172, 552, f"R1 right column first paragraph {filler}.")
put(60, 220, 296, f"L2 left column second paragraph {filler}.")
put(316, 272, 552, f"R2 right column second paragraph {filler}.")
put(60, 320, 296, f"L3 left column third paragraph {filler}.")
put(316, 372, 552, f"R3 right column third paragraph {filler}.")
doc.save("twocol.pdf")

pdf = fitz.open("twocol.pdf")
p = pdf[0]
print("PaperRAG order :", [b.split()[0] for b in page_blocks(p)])

def reading_order(page, blocks):
    mid = page.rect.width / 2
    def key(b):
        x0, y0, x1 = b[0], b[1], b[2]
        if x0 < mid - 20 and x1 > mid + 20:
            col = 0            # spans both columns (title, wide figure caption)
        elif x1 <= mid + 20:
            col = 1            # left column
        else:
            col = 2            # right column
        return (col, y0, x0)
    return sorted(blocks, key=key)

raw = [b for b in p.get_text("blocks") if len(b) > 6 and b[6] == 0]
fixed = [clean(b[4]) for b in reading_order(p, raw)]
print("Column-aware   :", [t.split()[0] for t in fixed if t and not _is_noise(t)])
