#!/usr/bin/env python3
"""finalize.py pages raw.pdf        -> pages.json (heading id -> page number)
   finalize.py stamp raw.pdf out.pdf -> add running header + page number, metadata"""
import json
import pathlib
import re
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parent


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower().replace("’", "'"))


def outline_entries(reader):
    out = []

    def walk(items, depth):
        for it in items:
            if isinstance(it, list):
                walk(it, depth + 1)
            else:
                out.append((depth, it.title, reader.get_destination_page_number(it) + 1))

    walk(reader.outline, 0)
    return out


def heading_pages(pdf):
    reader = PdfReader(pdf)
    heads = json.loads((ROOT / "headings.json").read_text())
    entries = outline_entries(reader)
    if len(entries) != len(heads):
        print(f"WARNING: outline has {len(entries)} entries, headings.json has {len(heads)}")
    pages, bad = {}, 0
    for h, (depth, title, page) in zip(heads, entries):
        if norm(h["text"]) not in norm(title) and norm(title) not in norm(h["text"]):
            bad += 1
            print("MISMATCH:", repr(h["text"]), "vs outline", repr(title))
        pages[h["id"]] = page
    if bad:
        raise SystemExit(f"{bad} outline mismatches")
    return pages, heads, len(reader.pages)


def cmd_pages(pdf):
    pages, heads, n = heading_pages(pdf)
    old = {}
    p = ROOT / "pages.json"
    if p.exists():
        old = json.loads(p.read_text())
    p.write_text(json.dumps(pages, indent=1))
    changed = sum(1 for k, v in pages.items() if old.get(k) != v)
    print(f"{n} pages; {len(pages)} headings mapped; {changed} changed since last run")


def cmd_stamp(pdf, out):
    pages, heads, n = heading_pages(pdf)
    pdfmetrics.registerFont(TTFont("Inter", str(ROOT / "fonts/static/Inter-400.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-SemiBold", str(ROOT / "fonts/static/Inter-600.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Bold", str(ROOT / "fonts/static/Inter-700.ttf")))

    # chapter label for every page
    chapters = [(pages[h["id"]], h["label"], h["text"]) for h in heads if h["level"] == 1]
    chapters.sort()

    def chapter_for(pg):
        cur = ("", "Before You Start")
        for start, label, text in chapters:
            if start <= pg:
                cur = (label, text)
        return cur

    overlay_path = ROOT / "overlay.pdf"
    c = canvas.Canvas(str(overlay_path), pagesize=A4)
    W, H = A4
    left, right = 17 * mm, W - 17 * mm
    navy, muted, line, yellow = HexColor("#16213e"), HexColor("#6b7280"), HexColor("#dfe3ea"), HexColor("#f7df1e")
    for pg in range(1, n + 1):
        if pg > 1:
            label, text = chapter_for(pg)
            y = H - 13 * mm
            # left: yellow tab + chapter label + title
            c.setFillColor(yellow)
            c.roundRect(left, y - 1.2, 3.2 * mm, 3.2 * mm, 0.8 * mm, stroke=0, fill=1)
            x = left + 5 * mm
            if label:
                c.setFillColor(navy)
                c.setFont("Inter-Bold", 7.6)
                c.drawString(x, y, label.upper())
                x += pdfmetrics.stringWidth(label.upper(), "Inter-Bold", 7.6) + 2.6 * mm
            c.setFillColor(muted)
            c.setFont("Inter", 7.8)
            max_w = right - x - 52 * mm
            t = text
            while pdfmetrics.stringWidth(t, "Inter", 7.8) > max_w and len(t) > 5:
                t = t[:-2].rstrip() + "…"
            c.drawString(x, y, t)
            c.setFont("Inter-SemiBold", 7.6)
            c.setFillColor(muted)
            c.drawRightString(right, y, "JavaScript — Explained Simply")
            c.setStrokeColor(line)
            c.setLineWidth(0.6)
            c.line(left, H - 15.5 * mm, right, H - 15.5 * mm)
            # footer: page number pill
            s = str(pg)
            w = pdfmetrics.stringWidth(s, "Inter-Bold", 8) + 5 * mm
            fy = 9 * mm
            c.setFillColor(navy)
            c.roundRect(W / 2 - w / 2, fy - 1.6 * mm, w, 5.2 * mm, 2.6 * mm, stroke=0, fill=1)
            c.setFillColor(HexColor("#ffffff"))
            c.setFont("Inter-Bold", 8)
            c.drawCentredString(W / 2, fy, s)
            c.setFillColor(muted)
            c.setFont("Inter", 7)
            c.drawString(left, fy, "Lectures 12 & 17–22  ·  Day 17–22 code")
            c.drawRightString(right, fy, "C++ student edition")
        c.showPage()
    c.save()

    import pikepdf
    with pikepdf.open(pdf) as doc, pikepdf.open(str(overlay_path)) as ov:
        for i, page in enumerate(doc.pages):
            if i == 0:
                continue
            page.add_overlay(ov.pages[i])
        with doc.open_metadata() as meta:
            meta["dc:title"] = "JavaScript — Explained Simply (Lectures 12 & 17–22, Day 17–22 code)"
            meta["dc:description"] = ("Array methods, Set & Map, Event Loop, Callbacks, Promises, JSON, "
                                      "async/await, Prototypes & Classes, Strict mode, this")
        doc.docinfo["/Title"] = "JavaScript — Explained Simply (Lectures 12 & 17–22, Day 17–22 code)"
        doc.docinfo["/Subject"] = ("Array methods, Set & Map, Event Loop, Callbacks, Promises, JSON, "
                                   "async/await, Prototypes & Classes, Strict mode, this")
        doc.Root.PageMode = pikepdf.Name.UseOutlines
        # Rewrite every bookmark title from headings.json (Chromium drops the space where a heading
        # wraps onto a second line) and prefix chapters with their label ("Chapter 3 — …").
        with doc.open_outline() as outline:
            flat = []

            def walk(items):
                for it in items:
                    flat.append(it)
                    walk(it.children)

            walk(outline.root)
            assert len(flat) == len(heads), (len(flat), len(heads))
            for it, h in zip(flat, heads):
                title = h["text"]
                if h["level"] == 1 and h["label"]:
                    title = f'{h["label"]} — {title}'
                it.title = title
        doc.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate,
                 recompress_flate=True)
    print("stamped", out, n, "pages")


if __name__ == "__main__":
    if sys.argv[1] == "pages":
        cmd_pages(sys.argv[2])
    elif sys.argv[1] == "stamp":
        cmd_stamp(sys.argv[2], sys.argv[3])
