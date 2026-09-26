"""Tiny SVG builder used by diagrams.py (all sizes in px at ~96 dpi)."""
import html

FONT = "Inter, 'DejaVu Sans', sans-serif"
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', monospace"

# kind -> (fill, stroke, text colour)
KIND = {
    "yellow": ("#fff6c7", "#d9ae00", "#5c4a00"),
    "blue": ("#e7efff", "#3f6fd6", "#1e3a8a"),
    "green": ("#e2f7ea", "#26a05e", "#14532d"),
    "red": ("#ffe9e9", "#dc4c4c", "#7f1d1d"),
    "purple": ("#f1eaff", "#8b5cf6", "#4c1d95"),
    "grey": ("#f3f4f6", "#9ca3af", "#374151"),
    "white": ("#ffffff", "#c3cad6", "#1f2937"),
    "navy": ("#16213e", "#16213e", "#ffffff"),
    "orange": ("#fff0e2", "#e8792a", "#7c2d12"),
    "teal": ("#dff6f3", "#14a39a", "#134e4a"),
    "pink": ("#ffe8f3", "#db4b93", "#831843"),
    "dark": ("#111827", "#111827", "#e5e7eb"),
}

INK = "#1f2937"
MUTED = "#6b7280"


def esc(s):
    return html.escape(str(s), quote=True)


def text_width(s, size, mono=False, weight=400):
    """Rough width estimate (px) for Inter / JetBrains Mono."""
    if mono:
        return len(s) * size * 0.6
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!`":
            w += 0.28
        elif ch in "fjrt()[]{}\" ":
            w += 0.36
        elif ch.isupper() or ch in "mwMW@%&":
            w += 0.72
        elif ch.isdigit():
            w += 0.6
        else:
            w += 0.55
    return w * size * (1.06 if weight >= 600 else 1.0)


class Svg:
    def __init__(self, w, h, uid):
        self.w, self.h, self.uid = w, h, uid
        self.items = []
        self.markers = {}

    # ------------------------------------------------------------ primitives
    def marker(self, color):
        mid = f"{self.uid}-ah{len(self.markers)}"
        for k, (c, _) in self.markers.items():
            if c == color:
                return k
        self.markers[mid] = (
            color,
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.6" refY="5" markerWidth="6.5" '
            f'markerHeight="6.5" orient="auto-start-reverse" markerUnits="strokeWidth">'
            f'<path d="M0,0.6 L10,5 L0,9.4 z" fill="{color}"/></marker>',
        )
        return mid

    def raw(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="#fff", stroke="#333", sw=1.4, rx=8, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.items.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def circle(self, cx, cy, r, fill="#fff", stroke="#333", sw=1.4):
        self.items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=12, weight=400, color=INK, anchor="middle", mono=False, italic=False,
             spacing=None):
        fam = MONO if mono else FONT
        st = ' font-style="italic"' if italic else ""
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.items.append(
            f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}"{st}{ls} xml:space="preserve">{esc(s)}</text>')

    def rich(self, x, y, parts, size=12, anchor="start", mono=False):
        """parts = [(text, {color, weight, mono, italic}), ...] on one line."""
        spans = []
        for t, st in parts:
            a = []
            if "color" in st:
                a.append(f'fill="{st["color"]}"')
            if "weight" in st:
                a.append(f'font-weight="{st["weight"]}"')
            if st.get("mono"):
                a.append(f'font-family="{MONO}"')
            if st.get("italic"):
                a.append('font-style="italic"')
            spans.append(f'<tspan {" ".join(a)}>{esc(t)}</tspan>')
        fam = MONO if mono else FONT
        self.items.append(
            f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{INK}" '
            f'text-anchor="{anchor}" xml:space="preserve">{"".join(spans)}</text>')

    def lines(self, x, y, lines, size=12, lh=None, **kw):
        lh = lh or size * 1.35
        for i, s in enumerate(lines):
            self.text(x, y + i * lh, s, size=size, **kw)

    def line(self, x1, y1, x2, y2, color="#475569", sw=1.6, dash=None, arrow=True, start_arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{self.marker(color)})"' if arrow else ""
        ms = f' marker-start="url(#{self.marker(color)})"' if start_arrow else ""
        self.items.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'
            f' stroke-linecap="round"{d}{m}{ms}/>')

    def path(self, d, color="#475569", sw=1.6, dash=None, arrow=True, fill="none", start_arrow=False):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{self.marker(color)})"' if arrow else ""
        ms = f' marker-start="url(#{self.marker(color)})"' if start_arrow else ""
        self.items.append(
            f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round"{da}{m}{ms}/>')

    # ------------------------------------------------------------ composites
    def box(self, x, y, w, h, title=None, body=(), kind="white", tsize=13, bsize=11.5, mono_body=False,
            mono_title=False, rx=10, sw=1.5, dash=None, align="middle", body_color=None, title_color=None,
            lh=None):
        fill, stroke, tcol = KIND[kind]
        self.rect(x, y, w, h, fill, stroke, sw, rx, dash)
        rows = []
        if title:
            rows.append((title, tsize, 700, mono_title, title_color or tcol))
        for b in body:
            rows.append((b, bsize, 400, mono_body, body_color or (tcol if kind in ("navy", "dark") else INK)))
        if not rows:
            return
        gaps = [(r[1] * (lh or 1.38)) for r in rows]
        total = sum(gaps) - (gaps[-1] - rows[-1][1] * 0.95)
        cy = y + h / 2 - total / 2 + rows[0][1] * 0.8
        tx = x + w / 2 if align == "middle" else x + 10
        anchor = "middle" if align == "middle" else "start"
        for (s, sz, wt, mono, col), g in zip(rows, gaps):
            self.text(tx, cy, s, size=sz, weight=wt, color=col, anchor=anchor, mono=mono)
            cy += g

    def chip(self, x, y, s, kind="yellow", size=10.5, mono=False, pad=7, h=None, weight=700, anchor="start"):
        fill, stroke, tcol = KIND[kind]
        w = text_width(s, size, mono, weight) + 2 * pad
        h = h or size + 9
        if anchor == "middle":
            x = x - w / 2
        self.rect(x, y, w, h, fill, stroke, 1.2, h / 2)
        self.text(x + w / 2, y + h / 2 + size * 0.36, s, size=size, weight=weight, color=tcol, mono=mono)
        return w

    def render(self):
        defs = "".join(m for _, m in self.markers.values())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img">'
                f'<defs>{defs}</defs>{"".join(self.items)}</svg>')
