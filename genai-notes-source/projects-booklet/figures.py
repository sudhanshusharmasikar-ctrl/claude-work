

# =====================================================================================
# Projects booklet (appended to diagrams.py by projects-booklet/make.sh)
# =====================================================================================
def _badge(s, cx, cy, n, r=10):
    s.circle(cx, cy, r, fill="#16213e", stroke="#ffffff", sw=1.6)
    s.text(cx, cy + 3.8, str(n), size=10.5, weight=800, color="#ffffff")


def _steps(s, x, y, items, w=92, gap=19, h=80, tsize=11, bsize=9, labels=None):
    """Numbered boxes left to right. items = [(title, [body...], kind)]. Returns box x positions."""
    xs = hchain(s, x, y, items, w=w, h=h, gap=gap, tsize=tsize, bsize=bsize, labels=labels, lsize=9)
    for i, (bx, bw) in enumerate(xs, start=1):
        _badge(s, bx + bw / 2, y, i)
    return [bx for bx, _ in xs]


@fig
def pb_paperrag_pipeline():
    s = Svg(680, 420, "pbprp")
    s.rect(4, 6, 672, 146, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=12)
    s.rich(16, 27, [("A · BUILD THE LIBRARY", {"weight": 800, "color": "#4c1d95"}),
                    ("   once, when you run  ", {"color": "#5b21b6"}),
                    ("python -m app.index", {"mono": True, "color": "#5b21b6"})], size=11)
    a = [("Your PDFs", ["papers you", "put in", "data/pdfs/"], "white"),
         ("Read blocks", ["PyMuPDF: text", "+ position,", "junk removed"], "white"),
         ("Reading order", ["column by", "column on", "2-column pages"], "white"),
         ("Cut chunks", ["≤ 900 characters", "150 overlap", "1 page each"], "white"),
         ("To numbers", ["MiniLM model:", "384 numbers", "per chunk"], "white"),
         ("Save", ["faiss.index", "+ chunks.jsonl", "(text, file, page)"], "navy")]
    xa = _steps(s, 17, 48, a, h=86)
    s.rect(4, 180, 672, 190, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=12)
    s.rich(16, 201, [("B · ANSWER A QUESTION", {"weight": 800, "color": "#1e3a8a"}),
                     ("   every time", {"color": "#1e40af"})], size=11)
    b = [("Question", ["typed on", "the web page"], "white"),
         ("To numbers", ["the same", "MiniLM model"], "white"),
         ("Find closest", ["FAISS: top 5", "chunks + scores"], "white"),
         ("Guard", ["best score", "≥ 0.50 ?"], "orange"),
         ("Write answer", ["quote the chunks,", "or ask Mistral"], "purple"),
         ("Answer", ["+ file & page", "citations"], "green")]
    xb = _steps(s, 17, 224, b, h=78, labels=[None, None, None, "yes", None])
    # the library built in A is what B searches
    s.path(f"M {xa[5] + 46} 136 L {xa[5] + 46} 166 L {xb[2] + 22} 166 L {xb[2] + 22} 220",
           color="#7c3aed", dash="4 3")
    s.text(xb[2] + 30, 206, "the library is loaded once, when the server starts", size=9, italic=True,
           color="#5b21b6", anchor="start")
    gx = xb[3] + 46
    s.line(gx, 304, gx, 329, color="#dc2626")
    s.text(gx + 7, 320, "no", size=9, weight=700, color="#b91c1c", anchor="start")
    s.box(gx - 110, 332, 220, 30, title="\"I don't know\": the papers don't cover it", kind="red", tsize=10)
    for i, t in enumerate(["server: FastAPI  (app/api.py)", "web page: Streamlit  (ui/)",
                           "checks: 51-question eval + 51 tests"]):
        s.box(8 + i * 224, 382, 216, 30, title=t, kind="grey", tsize=10)
    return s.render()


def _page(s, x, y, w, h, blocks, order, title, verdict, good, bands=()):
    """A page mock-up. blocks = {label: (rx, ry, rw, rh, kind)} relative to the page."""
    s.text(x + w / 2, y - 12, title, size=11.5, weight=700, color=INK)
    s.rect(x, y, w, h, fill="#ffffff", stroke="#9ca3af", sw=1.3, rx=6)
    for by, bh in bands:
        s.rect(x + 4, y + by, w - 8, bh, fill="#fef3c7", stroke="#fde68a", sw=1, rx=4)
    centers = {label: (x + rx + rw / 2, y + ry + rh / 2) for label, (rx, ry, rw, rh, _) in blocks.items()}
    pts = [centers[k] for k in order]
    s.path("M " + " L ".join(f"{px:.0f} {py:.0f}" for px, py in pts), color="#dc2626" if not good else "#16a34a",
           sw=2, dash="5 3", arrow=False)
    for label, (rx, ry, rw, rh, kind) in blocks.items():
        fill, stroke, tcol = KIND[kind]
        s.rect(x + rx, y + ry, rw, rh, fill=fill, stroke=stroke, sw=1.1, rx=4)
        s.text(x + rx + rw / 2, y + ry + rh / 2 + 4, label, size=10, weight=700, color=tcol)
    for i, k in enumerate(order, start=1):
        rx, ry = blocks[k][0], blocks[k][1]
        _badge(s, x + rx + 2, y + ry + 2, i, r=8)
    s.text(x + w / 2, y + h + 20, verdict, size=10.5, weight=700,
           color="#14532d" if good else "#991b1b")


@fig
def pb_reading_order():
    s = Svg(680, 318, "pbro")
    blocks = {
        "Title": (14, 12, 272, 24, "grey"),
        "L1": (14, 50, 128, 34, "blue"), "L2": (14, 92, 128, 34, "blue"),
        "R1": (158, 62, 128, 34, "orange"), "R2": (158, 104, 128, 34, "orange"),
        "Wide figure caption": (14, 150, 272, 24, "grey"),
        "L3": (14, 188, 128, 40, "blue"), "R3": (158, 198, 128, 40, "orange"),
    }
    old = ["Title", "L1", "R1", "L2", "R2", "Wide figure caption", "L3", "R3"]
    new = ["Title", "L1", "L2", "R1", "R2", "Wide figure caption", "L3", "R3"]
    _page(s, 16, 34, 300, 250, blocks, old, "Before: sorted top to bottom",
          "L1, R1, L2, R2 … the columns get mixed", good=False)
    _page(s, 364, 34, 300, 250, blocks, new, "After: column by column, band by band",
          "L1, L2, then R1, R2: reading order", good=True, bands=[(44, 100), (182, 62)])
    s.text(358, 34 + 96, "band 1", size=8.5, italic=True, color="#92400e", anchor="end")
    s.text(358, 34 + 216, "band 2", size=8.5, italic=True, color="#92400e", anchor="end")
    return s.render()


@fig
def pb_chunking():
    s = Svg(680, 262, "pbch")
    k = 0.4  # px per character
    s.text(20, 22, "Page 1: blocks in reading order", size=11, weight=700, anchor="start")
    s.text(566, 22, "Page 2", size=11, weight=700, anchor="start")
    x = 20
    blocks = [("A", 300), ("B", 350), ("C", 420), ("D", 180)]
    pos = {}
    for name, n in blocks:
        w = n * k
        s.rect(x, 34, w, 30, fill=KIND["blue"][0], stroke=KIND["blue"][1], sw=1.2, rx=4)
        s.text(x + w / 2, 53, f"{name} · {n} chars", size=9.5, weight=600, color=KIND["blue"][2])
        pos[name] = (x, w)
        x += w + 4
    s.rect(566, 34, 100, 30, fill=KIND["blue"][0], stroke=KIND["blue"][1], sw=1.2, rx=4)
    s.text(616, 53, "E · 250 chars", size=9.5, weight=600, color=KIND["blue"][2])
    s.line(552, 14, 552, 236, color="#9ca3af", sw=1.2, dash="5 4", arrow=False)
    s.text(20, 98, "Chunks: whole blocks packed up to 900 characters", size=11, weight=700, anchor="start")
    # chunk 1 = A + B
    c1x, c1w = 20, pos["B"][0] + pos["B"][1] - 20
    s.rect(c1x, 110, c1w, 34, fill=KIND["green"][0], stroke=KIND["green"][1], sw=1.4, rx=5)
    s.text(c1x + c1w / 2, 131, "chunk 1 = A + B  (651 chars)", size=10, weight=700, color=KIND["green"][2])
    # chunk 2 = last 150 chars of chunk 1 + C + D
    ov = 150 * k
    c2x = c1x + c1w - ov
    c2w = (pos["D"][0] + pos["D"][1]) - c2x
    s.rect(c2x, 156, c2w, 34, fill=KIND["green"][0], stroke=KIND["green"][1], sw=1.4, rx=5)
    s.rect(c2x, 156, ov, 34, fill="#fed7aa", stroke=KIND["orange"][1], sw=1.4, rx=5)
    s.text(c2x + ov / 2, 177, "overlap", size=9.5, weight=700, color=KIND["orange"][2])
    s.text(c2x + ov + (c2w - ov) / 2, 177, "chunk 2 = overlap + C + D  (752)", size=10, weight=700,
           color=KIND["green"][2])
    s.line(c2x, 146, c2x, 154, color=KIND["orange"][1], sw=1.2, arrow=False)
    s.line(c1x + c1w, 146, c1x + c1w, 154, color=KIND["orange"][1], sw=1.2, arrow=False)
    s.rect(566, 110, 100, 34, fill=KIND["green"][0], stroke=KIND["green"][1], sw=1.4, rx=5)
    s.text(616, 131, "chunk 3 = E", size=10, weight=700, color=KIND["green"][2])
    s.lines(20, 214, ["The last 150 characters of chunk 1 are repeated at the start of chunk 2, so a sentence",
                      "cut at the edge is complete in one of them. A new page always starts a new chunk."],
            size=9.5, color=MUTED, anchor="start", lh=14)
    s.lines(566, 164, ["never mixed", "with page 1:", "1 chunk =", "1 page"], size=9.5, color=MUTED,
            anchor="start", lh=13)
    return s.render()


@fig
def pb_embedding_space():
    s = Svg(680, 300, "pbem")
    # left: text -> numbers
    s.box(12, 40, 236, 70, title="A chunk of text",
          body=["\"We train with the Adam", "optimizer and a learning", "rate warmup …\""], kind="white",
          tsize=11, bsize=9.5)
    s.line(130, 114, 130, 140)
    s.text(140, 131, "MiniLM", size=10, weight=700, color="#4c1d95", anchor="start")
    s.box(12, 144, 236, 52, title="[0.12, −0.05, 0.33, … , 0.08]", body=["384 numbers, scaled to length 1"],
          kind="purple", tsize=10.5, bsize=9.5, mono_title=True)
    s.lines(12, 222, ["The numbers describe meaning. Texts", "about the same thing get similar",
                      "numbers, even with different words.", "The question goes through the same",
                      "model, so it can be compared."], size=9.5, color=MUTED, anchor="start", lh=13.5)
    # right: a 2-D cartoon of the 384-D space
    ox, oy = 300, 262
    s.rect(282, 22, 390, 262, fill="#fafbff", stroke="#d7def5", sw=1, rx=10)
    s.text(477, 40, "A 2-D cartoon of the meaning space (the real one has 384 directions)", size=9.5,
           italic=True, color=MUTED)
    s.rect(330, 52, 11, 11, fill="#7c3aed", stroke="#ffffff", sw=1.2, rx=2)
    s.text(347, 62, "Q = the question \"Which optimizer did they use?\"", size=9.5, weight=700,
           color="#5b21b6", anchor="start")
    pts = [("training details (p.2)", 590, 112, "green", "above"), ("attention (p.1)", 392, 96, "blue", "right"),
           ("positional encodings (p.1)", 352, 128, "blue", "right"),
           ("keyword search, BM25", 612, 214, "grey", "left"), ("dense retrieval", 592, 240, "grey", "left")]
    for label, px, py, kind, where in pts:
        s.line(ox, oy, px, py, color="#cbd5e1", sw=1.1, arrow=False)
        s.circle(px, py, 5, fill=KIND[kind][1], stroke="#ffffff", sw=1.2)
        if where == "above":
            s.text(px, py - 11, label, size=9.5, color=KIND[kind][2])
        elif where == "right":
            s.text(px + 9, py + 4, label, size=9.5, color=KIND[kind][2], anchor="start")
        else:
            s.text(px - 9, py + 4, label, size=9.5, color=KIND[kind][2], anchor="end")
    qx, qy = 552, 140
    s.line(ox, oy, qx, qy, color="#7c3aed", sw=1.8, arrow=False)
    s.rect(qx - 6, qy - 6, 12, 12, fill="#7c3aed", stroke="#ffffff", sw=1.2, rx=2)
    s.text(qx + 10, qy + 4, "Q", size=10.5, weight=800, color="#5b21b6", anchor="start")
    s.circle(ox, oy, 3, fill=INK, stroke=INK, sw=1)
    s.text(ox + 6, oy + 14, "0", size=9, color=MUTED, anchor="start")
    s.text(477, 276, "small angle = similar meaning = high score", size=9.5, weight=600, color="#14532d")
    return s.render()


@fig
def pb_guard():
    s = Svg(680, 182, "pbgd")
    x0, x1, y = 60, 620, 110
    t = 0.50
    xt = x0 + t * (x1 - x0)
    s.rect(x0, y - 16, xt - x0, 32, fill="#ffe4e4", stroke="#ffe4e4", sw=0.5, rx=0)
    s.rect(xt, y - 16, x1 - xt, 32, fill="#dcf5e6", stroke="#dcf5e6", sw=0.5, rx=0)
    s.text((x0 + xt) / 2, y + 4, "refuse: \"I don't know\"", size=10, weight=700, color="#991b1b")
    s.text((xt + x1) / 2, y + 4, "answer, with citations", size=10, weight=700, color="#14532d")
    for v in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        xv = x0 + v * (x1 - x0)
        s.line(xv, y + 16, xv, y + 22, color="#6b7280", sw=1, arrow=False)
        s.text(xv, y + 34, f"{v:.1f}", size=9.5, color=MUTED)
    s.text((x0 + x1) / 2, y + 52, "best (top-1) similarity score of the question with any chunk", size=10,
           color=INK)
    s.line(xt, y - 40, xt, y + 22, color="#dc2626", sw=1.8, dash="4 3", arrow=False)
    s.text(xt, y - 46, "threshold 0.50", size=10, weight=700, color="#b91c1c")
    for v, label, kind in [(0.12, "\"Chocolate cake recipe?\" → 0.12", "red"),
                           (0.71, "\"Which optimizer did they use?\" → 0.71", "green")]:
        xv = x0 + v * (x1 - x0)
        s.line(xv, 34, xv, y - 18, color=KIND[kind][1], sw=1.6)
        s.chip(xv, 14, label, kind=kind, size=9.5, anchor="middle")
    return s.render()


@fig
def pb_tradeoff():
    """The real sweep (session 7): 51 questions, 8 papers, 905 chunks."""
    s = Svg(680, 290, "pbto")
    thr = [round(0.20 + 0.02 * i, 2) for i in range(24)]
    answered = [16, 16, 16, 16, 15, 14, 12, 10, 10, 10, 9, 8, 8, 7, 5, 3, 2, 1, 0, 0, 0, 0, 0, 0]  # of 17
    refused = [0] * 12 + [2, 3, 4, 4, 5, 8, 11, 13, 17, 20, 23, 27]                              # of 34
    blue, orange, grid = "#2a78d6", "#eb6834", "#e5e7eb"
    x0, x1, yb, yt = 64, 560, 236, 64

    def X(t):
        return x0 + (t - 0.20) / 0.46 * (x1 - x0)

    def Y(pct):
        return yb - pct / 100 * (yb - yt)

    for pct in (0, 25, 50, 75, 100):  # recessive grid, labels in muted ink
        s.line(x0, Y(pct), x1, Y(pct), color=grid if pct else "#9ca3af", sw=1, arrow=False)
        s.text(x0 - 8, Y(pct) + 3.5, f"{pct}%", size=9, color=MUTED, anchor="end")
    for t in (0.20, 0.30, 0.40, 0.50, 0.60):
        s.text(X(t), yb + 15, f"{t:.2f}", size=9, color=MUTED)
    s.text((x0 + x1) / 2, yb + 33, "threshold  (higher = stricter guard)", size=10, color=INK)
    for t, label, dark in ((0.35, "old: 0.35", False), (0.50, "chosen: 0.50", True)):
        s.line(X(t), yt - 6, X(t), yb, color="#374151" if dark else "#9ca3af", sw=1.2, dash="4 3", arrow=False)
        s.text(X(t), yt - 12, label, size=9.5, weight=700 if dark else 400, color=INK if dark else MUTED)
    for counts, total, color in ((answered, 17, blue), (refused, 34, orange)):
        pts = [(X(t), Y(c / total * 100)) for t, c in zip(thr, counts)]
        s.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts), color=color, sw=2, arrow=False)
        for t in (0.35, 0.50):  # markers with a surface ring where the reference lines cross
            c = counts[thr.index(0.34)] if t == 0.35 else counts[thr.index(t)]
            s.circle(X(t), Y(c / total * 100), 4, fill=color, stroke="#ffffff", sw=2)
    # direct labels at the line ends, in ink, beside a swatch of the series colour
    s.line(x1 + 8, Y(27 / 34 * 100), x1 + 22, Y(27 / 34 * 100), color=orange, sw=2, arrow=False)
    s.text(x1 + 26, Y(27 / 34 * 100) + 3.5, "good questions", size=9.5, color=INK, anchor="start")
    s.text(x1 + 26, Y(27 / 34 * 100) + 15.5, "refused", size=9.5, color=INK, anchor="start")
    s.line(x1 + 8, Y(0) - 10, x1 + 22, Y(0) - 10, color=blue, sw=2, arrow=False)
    s.text(x1 + 26, Y(0) - 6.5, "unanswerable", size=9.5, color=INK, anchor="start")
    s.text(x1 + 26, Y(0) + 5.5, "ones answered", size=9.5, color=INK, anchor="start")
    # legend row (two series: always a legend)
    s.line(x0, 16, x0 + 16, 16, color=blue, sw=2, arrow=False)
    s.text(x0 + 22, 19.5, "unanswerable questions that still got an answer (of 17)", size=9.5, color=INK,
           anchor="start")
    s.line(x0, 33, x0 + 16, 33, color=orange, sw=2, arrow=False)
    s.text(x0 + 22, 36.5, "answerable questions refused (of 34)", size=9.5, color=INK, anchor="start")
    # what the two marked thresholds mean, in counts (in the empty space right of each line)
    for t, lines in ((0.35, ["10 of 17 answered", "0 of 34 refused"]),
                     (0.50, ["3 of 17 answered", "4 of 34 refused"])):
        for i, line in enumerate(lines):
            s.text(X(t) + 7, Y(86) + 12 * i, line, size=9, color=INK, anchor="start")
    return s.render()


@fig
def pb_paperrag_components():
    s = Svg(680, 330, "pbpc")
    s.box(8, 120, 84, 62, title="You", body=["in a browser"], kind="white", tsize=11.5, bsize=9.5)
    s.box(120, 108, 150, 86, title="Streamlit page", body=["ui/streamlit_app.py", "localhost:8501",
                                                           "sliders: top-k, threshold"],
          kind="teal", tsize=11, bsize=9)
    s.line(94, 151, 117, 151)
    s.rect(330, 30, 342, 236, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=12)
    s.text(501, 50, "FastAPI server  ·  app/api.py  ·  localhost:8000", size=10.5, weight=700, color="#334155")
    s.line(272, 140, 327, 140)
    s.text(299, 132, "POST /ask", size=9, weight=700, color="#334155")
    s.line(327, 166, 272, 166)
    s.text(299, 182, "JSON reply", size=9, weight=700, color="#334155")
    s.chip(346, 62, "/ask", kind="purple", size=9.5, mono=True)
    s.chip(392, 62, "/health", kind="purple", size=9.5, mono=True)
    s.chip(460, 62, "/docs", kind="purple", size=9.5, mono=True)
    s.box(346, 96, 150, 62, title="Retriever", body=["embed the question,", "search FAISS, guard"],
          kind="blue", tsize=11, bsize=9)
    s.box(508, 96, 150, 62, title="Answer writer", body=["extractive (quotes)", "or Mistral"],
          kind="purple", tsize=11, bsize=9)
    s.line(498, 127, 505, 127)
    s.box(346, 186, 150, 62, title="storage/", body=["faiss.index (numbers)", "chunks.jsonl (text, page)"],
          kind="navy", tsize=11, bsize=9)
    s.line(421, 184, 421, 161)
    s.text(429, 177, "loaded once at startup", size=8.5, italic=True, color=MUTED, anchor="start")
    s.box(508, 282, 164, 40, title="Mistral API (cloud)", body=["only in mistral mode"], kind="orange",
          tsize=10.5, bsize=9, dash="4 3")
    s.line(583, 160, 583, 279, color="#e8792a", dash="4 3")
    s.box(120, 236, 190, 70, title="python -m app.index", body=["reads data/pdfs/", "writes storage/"],
          kind="grey", tsize=10.5, bsize=9, mono_title=True)
    s.line(312, 250, 343, 230, color="#64748b", dash="4 3")
    s.text(14, 300, "build the library first,", size=9, italic=True, color=MUTED, anchor="start")
    s.text(14, 313, "then start the server", size=9, italic=True, color=MUTED, anchor="start")
    return s.render()


@fig
def pb_schemamind_pipeline():
    s = Svg(680, 440, "pbsm")
    s.rect(4, 6, 672, 112, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=12)
    s.rich(16, 27, [("A · WHEN THE SERVER STARTS", {"weight": 800, "color": "#4c1d95"}),
                    ("   once", {"color": "#5b21b6"})], size=11)
    a = [("shop.db", ["5 tables: customers,", "orders, items, …"], "navy", 140),
         ("Read the schema", ["tables, columns, keys", "+ 2 sample rows"], "white", 140),
         ("Describe tables", ["one plain-text", "card per table"], "white", 140),
         ("To numbers", ["MiniLM: one vector", "per table card"], "white", 140)]
    xa = hchain(s, 20, 42, a, h=60, gap=30, tsize=11, bsize=9)
    s.rect(4, 136, 672, 298, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=12)
    s.rich(16, 157, [("B · EACH QUESTION", {"weight": 800, "color": "#1e3a8a"})], size=11)
    b = [("Question", ["\"How many orders", "from Pune?\""], "white"),
         ("Pick tables", ["top 3 by", "similarity"], "blue"),
         ("Write SQL", ["template mode", "or Mistral"], "purple"),
         ("Check SQL", ["one read query?", "(validator)"], "orange"),
         ("Run SQL", ["read-only, 5 s,", "200 rows max"], "orange"),
         ("Answer", ["rows + the SQL", "that made them"], "green")]
    xb = _steps(s, 17, 204, b, h=78, labels=[None, None, None, "ok", "ok"])
    ax, aw = xa[3]
    s.path(f"M {ax + aw / 2} 104 L {ax + aw / 2} 128 L {xb[1] + 22} 128 L {xb[1] + 22} 200",
           color="#7c3aed", dash="4 3")
    s.text(xb[1] + 30, 188, "table vectors made at startup", size=9, italic=True, color="#5b21b6",
           anchor="start")
    # repair loop
    c3, c4, c5 = xb[2] + 46, xb[3] + 46, xb[4] + 46
    s.path(f"M {c4} 284 L {c4} 318 L {c3} 318 L {c3} 286", color="#dc2626", sw=1.6)
    s.path(f"M {c5} 284 L {c5} 318 L {c4} 318", color="#dc2626", sw=1.6, arrow=False)
    s.text(c4 + 6, 300, "fails", size=9, weight=700, color="#b91c1c", anchor="start")
    s.text(c5 + 6, 300, "error", size=9, weight=700, color="#b91c1c", anchor="start")
    s.box(110, 330, 286, 46, title="Repair loop", body=["the error message goes back to the SQL writer:",
                                                        "it tries again, at most 2 more times"],
          kind="red", tsize=10.5, bsize=9)
    s.box(420, 338, 236, 34, title="After 3 failed tries: stop and say why", kind="grey", tsize=10)
    s.line(398, 355, 417, 355, color="#64748b")
    s.lines(20, 400, ["Template mode answers a fixed list of question shapes and refuses everything else.",
                      "Mistral mode writes new SQL from the 3 table cards (needs an API key)."],
            size=9.5, color=MUTED, anchor="start", lh=14)
    return s.render()


def _table(s, x, y, w, name, cols, rows_note, kind="blue"):
    fill, stroke, tcol = KIND[kind]
    h = 26 + 18 * len(cols) + 6
    s.rect(x, y, w, h, fill="#ffffff", stroke=stroke, sw=1.4, rx=8)
    s.rect(x, y, w, 26, fill=stroke, stroke=stroke, sw=1.4, rx=8)
    s.rect(x, y + 16, w, 10, fill=stroke, stroke=stroke, sw=0)
    s.text(x + w / 2, y + 18, name, size=11, weight=800, color="#ffffff")
    rows = {}
    for i, (c, note) in enumerate(cols):
        cy = y + 26 + 18 * i + 14
        s.text(x + 9, cy, c, size=9.5, weight=700 if note == "PK" else 400, color=INK, anchor="start",
               mono=True)
        if note:
            s.text(x + w - 8, cy, note, size=8.5, weight=700, color="#b45309" if note == "PK" else "#1d4ed8",
                   anchor="end")
        rows[c] = cy - 4
    s.text(x + w / 2, y + h + 14, rows_note, size=9, italic=True, color=MUTED)
    return rows, h


@fig
def pb_er():
    s = Svg(680, 352, "pber")
    cu, _ = _table(s, 8, 30, 150, "customers", [("customer_id", "PK"), ("name", ""), ("city", ""),
                                                ("signup_date", "")], "40 customers, 6 cities")
    od, odh = _table(s, 196, 30, 152, "orders", [("order_id", "PK"), ("customer_id", "FK"), ("order_date", ""),
                                                 ("status", "")], "150 orders")
    oi, _ = _table(s, 386, 30, 156, "order_items", [("order_item_id", "PK"), ("order_id", "FK"),
                                                    ("product_id", "FK"), ("quantity", ""), ("unit_price", "")],
                   "276 items")
    pr, _ = _table(s, 570, 30, 104, "products", [("product_id", "PK"), ("name", ""), ("category", ""),
                                                 ("price", "")], "8 products")
    pa, _ = _table(s, 196, 200, 152, "payments", [("payment_id", "PK"), ("order_id", "FK"), ("amount", ""),
                                                  ("method", ""), ("paid_on", "")], "126 payments")
    # foreign keys: child column -> parent id
    s.path(f"M 196 {od['customer_id']} L 177 {od['customer_id']} L 177 {cu['customer_id']} L 161 {cu['customer_id']}",
           color="#1d4ed8", sw=1.5)
    s.path(f"M 386 {oi['order_id']} L 367 {oi['order_id']} L 367 {od['order_id']} L 351 {od['order_id']}",
           color="#1d4ed8", sw=1.5)
    s.path(f"M 542 {oi['product_id']} L 556 {oi['product_id']} L 556 {pr['product_id']} L 567 {pr['product_id']}",
           color="#1d4ed8", sw=1.5)
    s.line(322, 198, 322, 30 + odh + 3, color="#1d4ed8", sw=1.5)
    s.text(330, 176, "payments.order_id → orders", size=8.5, italic=True, color="#1d4ed8", anchor="start")
    s.text(370, 236, "cancelled orders have no payment,", size=9, italic=True, color=MUTED, anchor="start")
    s.text(370, 250, "so 150 orders − 24 cancelled = 126", size=9, italic=True, color=MUTED, anchor="start")
    s.text(370, 282, "PK = the row's own ID (primary key)", size=9.5, color="#b45309", anchor="start")
    s.text(370, 298, "FK = points to another table's ID (foreign key)", size=9.5, color="#1d4ed8",
           anchor="start")
    s.text(370, 314, "each arrow goes from an FK to the ID it points to", size=9.5, color="#1d4ed8",
           anchor="start")
    return s.render()


@fig
def pb_template_matching():
    s = Svg(680, 250, "pbtm")
    heads = [("You ask", 12, 150), ("Normalised", 168, 150), ("Does a shape match the WHOLE question?", 324, 196),
             ("Result", 526, 146)]
    for t, x, w in heads:
        s.text(x + w / 2, 18, t, size=10.5, weight=800, color="#334155")
    rows = [
        ("\"How many orders", "from Pune?\"", "how many orders", "from pune",
         ["yes: \"how many orders", "from/in <city>\""], "green", ["SQL with", "city = 'Pune' → 22"], "green"),
        ("\"Show orders in", "the last month\"", "orders in the", "last month",
         ["only \"orders in <city>\":", "\"last month\" is left over"], "red", ["refused: \"could not", "generate a query\""],
         "red"),
    ]
    y = 32
    for q1, q2, n1, n2, m, mk, r, rk in rows:
        s.box(12, y, 150, 84, body=[q1, q2], kind="white", bsize=10)
        s.box(168, y, 150, 84, body=[n1, n2], kind="grey", bsize=10, mono_body=True)
        s.box(324, y, 196, 84, body=m, kind=mk, bsize=9.5)
        s.box(526, y, 146, 84, body=r, kind=rk, bsize=9.5)
        for xa in (164, 320, 522):
            s.line(xa - 1, y + 42, xa + 3, y + 42, color="#94a3b8", sw=1.2)
        y += 96
    s.text(340, 238, "lower case, \"show me\" / \"what is the\" / \"?\" removed; shapes are tried most specific first",
           size=9.5, italic=True, color=MUTED)
    return s.render()


@fig
def pb_sql_tree():
    s = Svg(680, 292, "pbst")
    s.text(220, 18, "SELECT COUNT(*) FROM orders o JOIN customers c ON … WHERE c.city = 'Pune'", size=9.5,
           weight=700, color="#334155", mono=True)
    root = (220, 54)
    s.box(root[0] - 50, root[1] - 16, 100, 32, title="Select", kind="blue", tsize=11.5)
    kids = [(62, "COUNT(*)", "what to return"), (168, "FROM orders", "main table"),
            (274, "JOIN customers", "ON customer_id = …"), (380, "WHERE", "the filter")]
    for x, t, note in kids:
        s.line(root[0], root[1] + 17, x, 112, color="#94a3b8", sw=1.2, arrow=False)
        s.box(x - 51, 114, 102, 40, title=t, body=[note], kind="white", tsize=10, bsize=8.5)
    s.line(380, 155, 380, 176, color="#94a3b8", sw=1.2, arrow=False)
    s.box(356, 178, 48, 26, title="=", kind="white", tsize=11)
    for x, t in [(334, "c.city"), (428, "'Pune'")]:
        s.line(380, 205, x, 226, color="#94a3b8", sw=1.2, arrow=False)
        s.box(x - 38, 228, 76, 26, title=t, kind="grey", tsize=10, mono_title=True)
    s.text(220, 280, "one statement, type Select, no write anywhere in the tree → allowed", size=10, weight=700,
           color="#14532d")
    # right: two statements
    s.rect(486, 36, 188, 212, fill="#fff5f5", stroke="#fecaca", sw=1.2, rx=10)
    s.text(580, 56, "SELECT * FROM customers;", size=8.5, weight=700, color="#7f1d1d", mono=True)
    s.text(580, 70, "DROP TABLE customers", size=8.5, weight=700, color="#7f1d1d", mono=True)
    s.box(500, 92, 76, 32, title="Select", kind="blue", tsize=10.5)
    s.box(586, 92, 76, 32, title="Drop", kind="red", tsize=10.5)
    s.lines(580, 154, ["two trees =", "two statements"], size=10, weight=700, color="#991b1b", lh=14)
    s.lines(580, 196, ["refused before it", "reaches the database"], size=9.5, color="#7f1d1d", lh=13)
    return s.render()


@fig
def pb_safety_layers():
    s = Svg(680, 336, "pbsl")
    s.box(8, 54, 110, 56, title="SQL from", body=["the SQL writer"], kind="white", tsize=11, bsize=9.5)
    layers = [("Layer 1", "Validator", "app/validate.py", 150, "orange"),
              ("Layer 2", "Read-only file", "mode=ro", 300, "orange"),
              ("Layer 3", "Limits", "5 s · 200 rows", 450, "orange")]
    for tag, name, sub, x, k in layers:
        s.rect(x, 30, 118, 104, fill=KIND[k][0], stroke=KIND[k][1], sw=1.6, rx=10)
        s.text(x + 59, 52, tag, size=9.5, weight=700, color=MUTED)
        s.text(x + 59, 72, name, size=11.5, weight=800, color=KIND[k][2])
        s.text(x + 59, 90, sub, size=9.5, color=INK, mono=sub == "mode=ro")
    s.box(600, 54, 74, 56, title="shop.db", body=["the data"], kind="navy", tsize=11, bsize=9.5)
    # a normal read goes straight through
    s.line(120, 120, 598, 120, color="#16a34a", sw=2)
    s.chip(540, 140, "a normal read passes", kind="green", size=9.5)
    # what each layer stops
    stops = [(150, ["SELECT …; DROP …", "DELETE / UPDATE /", "INSERT / ALTER", "PRAGMA, ATTACH,", "VACUUM INTO"]),
             (300, ["any write that", "slipped past", "layer 1: \"attempt", "to write a readonly", "database\""]),
             (450, ["a query still running", "after 5 seconds", "(endless recursion,", "huge cross joins);",
                    "more than 200 rows"])]
    for x, lines in stops:
        s.rect(x, 176, 118, 92, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=8)
        s.text(x + 59, 192, "stops", size=9, weight=800, color="#b91c1c")
        s.lines(x + 59, 207, lines, size=8.8, color="#7f1d1d", lh=12)
        s.line(x + 59, 136, x + 59, 173, color="#dc2626", sw=1.3)
    s.box(8, 286, 664, 42, title="Safe is not the same as correct",
          body=["valid SQL can still answer the wrong question: template mode refuses partial matches, "
                "and the eval compares results"], kind="grey", tsize=10.5, bsize=9)
    return s.render()


@fig
def pb_skeleton():
    s = Svg(680, 236, "pbsk")
    cols = [("1 · Retrieve", 112), ("2 · Generate", 254), ("3 · Check", 396), ("4 · Show evidence", 538)]
    for t, x in cols:
        s.chip(x + 66, 10, t, kind="navy", size=10, anchor="middle")
    rows = [("PaperRAG", 44, "purple",
             [["top 5 chunks", "(FAISS search)"], ["quote the chunks,", "or Mistral answer"],
              ["score guard +", "INSUFFICIENT_CONTEXT"], ["file + page", "for every passage"]]),
            ("SchemaMind", 128, "blue",
             [["top 3 tables", "(MiniLM similarity)"], ["SQL: template", "or Mistral"],
              ["validator, read-only", "file, time + row limits"], ["the SQL shown", "with the rows"]])]
    for name, y, kind, cells in rows:
        s.box(8, y, 96, 70, title=name, kind=kind, tsize=11)
        for (t, x), body in zip(cols, cells):
            s.box(x, y, 132, 70, body=body, kind="white", bsize=9.5)
        for x in (104, 246, 388, 530):
            s.line(x + 1, y + 35, x + 6, y + 35, color="#94a3b8", sw=1.2)
    s.text(340, 224, "Both refuse honestly: PaperRAG says \"I don't know\", SchemaMind says it can't write a query.",
           size=9.5, italic=True, color=MUTED)
    return s.render()
