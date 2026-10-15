

# =====================================================================================
# Frontend practice guide (appended to diagrams.py by frontend-practice-source/make.sh)
# =====================================================================================
PURPLE, PURPLE_L, ORANGE, NAVY = "#7c3aed", "#ede9fe", "#e8792a", "#16213e"


def _code_lines(s, x, y, lines, size=10.5, lh=15.5, color=INK):
    for i, ln in enumerate(lines):
        s.text(x, y + i * lh, ln, size=size, mono=True, anchor="start", color=color)


def _browser(s, x, y, w, h, title="index.html"):
    """An empty browser window; returns the content area's top y."""
    s.rect(x, y, w, h, fill="#ffffff", stroke="#c3cad6", sw=1.4, rx=10)
    s.rect(x, y, w, 24, fill="#eef1f6", stroke="#c3cad6", sw=1.4, rx=10)
    s.rect(x + 1, y + 14, w - 2, 10, fill="#eef1f6", stroke="#eef1f6", sw=0, rx=0)
    for i, c in enumerate(["#f87171", "#fbbf24", "#34d399"]):
        s.circle(x + 14 + i * 13, y + 12, 4, fill=c, stroke=c, sw=0.5)
    s.rect(x + 60, y + 5, w - 74, 14, fill="#ffffff", stroke="#dfe3ea", sw=1, rx=7)
    s.text(x + 70, y + 15.5, title, size=9, color=MUTED, anchor="start", mono=True)
    return y + 24


def _button(s, x, y, w, label, kind="purple"):
    fill, stroke, col = {"purple": (PURPLE, PURPLE, "#ffffff"),
                         "white": ("#ffffff", "#cbd5e1", "#475569")}[kind]
    s.rect(x, y, w, 24, fill=fill, stroke=stroke, sw=1.2, rx=6)
    s.text(x + w / 2, y + 16, label, size=10.5, weight=700, color=col)


@fig
def fp_plan():
    s = Svg(680, 300, "fpplan")
    days = [
        ("DAY 0", "tools + grader", [("Setup", "grey")]),
        ("DAY 1", "first JavaScript", [("03 Counter", "purple")]),
        ("DAY 2", "forms & toggles", [("01 Form", "orange"), ("08 Password", "purple")]),
        ("DAY 3", "CSS layout", [("02 Card", "orange"), ("04 Center", "orange")]),
        ("DAY 4", "lists from data", [("05 Search ★", "yellow")]),
        ("DAY 5", "build & switch", [("06 To-do", "purple"), ("09 Dark mode", "purple")]),
        ("DAY 6", "validation", [("07 Validation", "purple")]),
        ("DAY 7", "one at a time", [("13 Accordion", "purple"), ("14 Tabs", "purple")]),
        ("DAY 8", "circles & time", [("16 Carousel", "purple"), ("17 Clock ★", "yellow")]),
        ("DAY 9", "state + render", [("15 Table", "purple")]),
        ("DAY 10", "mock round", [("05 · 17 · 12", "navy"), ("revision", "grey")]),
        ("AFTER", "bonus", [("10 11 12", "white"), ("19 20 18", "white")]),
    ]
    w, h, gap = 104, 118, 9
    for i, (day, theme, chips) in enumerate(days):
        row, col = divmod(i, 6)
        x, y = 4 + col * (w + gap), 6 + row * (h + 14)
        last = day in ("DAY 10", "AFTER")
        s.rect(x, y, w, h, fill="#f8fafc" if not last else "#f5f3ff",
               stroke="#dfe3ea" if not last else "#c4b5fd", sw=1.2, rx=10, dash="4 3" if day == "AFTER" else None)
        s.text(x + 10, y + 19, day, size=11, weight=800, color=NAVY, anchor="start")
        s.text(x + 10, y + 34, theme, size=9.5, color=MUTED, anchor="start", italic=True)
        for j, (label, kind) in enumerate(chips):
            s.box(x + 7, y + 44 + j * 34, w - 14, 28, title=label, kind=kind, tsize=10, rx=7)
    ly = 282
    for i, (label, kind) in enumerate([("HTML / CSS", "orange"), ("JavaScript + DOM", "purple"),
                                       ("reported from the real round", "yellow"), ("timed mock", "navy")]):
        x = 8 + [0, 110, 262, 482][i]
        fill, stroke, _ = KIND[kind]
        s.rect(x, ly - 9, 14, 12, fill=fill, stroke=stroke, sw=1.2, rx=3)
        s.text(x + 20, ly + 1, label, size=10, color=INK, anchor="start")
    return s.render()


@fig
def fp_three_files():
    s = Svg(680, 300, "fp3f")
    boxes = [("index.html", "WHAT is on the page", ["headings, text, inputs, buttons"], "orange", 8, 112),
             ("style.css", "HOW it looks", ["colours, sizes, spacing, layout"], "purple", 132, 74),
             ("script.js", "WHAT HAPPENS", ["on a click or on typing:", "change the page"], "yellow", 218, 78)]
    for name, role, body, kind, y, h in boxes:
        fill, stroke, tcol = KIND[kind]
        s.rect(8, y, 262, h, fill=fill, stroke=stroke, sw=1.5, rx=10)
        s.text(22, y + 24, name, size=13, weight=800, mono=True, color=tcol, anchor="start")
        s.text(22, y + 44, role, size=11, weight=700, color=INK, anchor="start")
        s.lines(22, y + 60, body, size=10.5, lh=14, color=INK, anchor="start")
    s.text(22, 86, '<link href="style.css">', size=9.3, mono=True, color="#9a3412", anchor="start")
    s.text(22, 102, '<script src="script.js">', size=9.3, mono=True, color="#9a3412", anchor="start")
    s.text(236, 94, "links the", size=8.5, italic=True, color="#9a3412", anchor="middle")
    s.text(236, 105, "other two", size=8.5, italic=True, color="#9a3412", anchor="middle")
    top = _browser(s, 332, 24, 342, 252, "exercises/03-click-counter/index.html")
    s.rect(380, top + 28, 248, 164, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=12)
    s.text(504, top + 60, "Click Counter", size=14, weight=800, color=NAVY)
    s.rich(458, top + 96, [("Count: ", {}), ("3", {"weight": 800, "color": PURPLE})], size=13)
    _button(s, 426, top + 122, 80, "Click me")
    _button(s, 514, top + 122, 70, "Reset", "white")
    for (y, txt, col, ty) in [(40, "structure", "#c2410c", 110), (169, "looks", "#6d28d9", 150),
                              (257, "behaviour", "#a16207", 196)]:
        s.line(274, y, 328, ty, color=col, sw=1.8)
        s.text(278, y - 6 if y < 200 else y + 14, txt, size=9.5, italic=True, color=col, anchor="start")
    return s.render()


@fig
def fp_dom_tree():
    s = Svg(680, 340, "fpdom")
    s.rect(4, 6, 300, 250, fill="#fbfaf7", stroke="#e5e0d5", sw=1.2, rx=10)
    s.text(16, 26, "index.html  (text)", size=10.5, weight=800, color="#9a3412", anchor="start")
    _code_lines(s, 16, 50, [
        '<section class="card">',
        '  <h1>Click Counter</h1>',
        '  <p class="count-row">',
        '    Count:',
        '    <span id="count">0</span>',
        '  </p>',
        '  <div class="actions">',
        '    <button id="increment">',
        '    <button id="reset">',
        '  </div>',
        '</section>',
    ], size=10, lh=18)
    s.rect(36, 108, 160, 19, fill="none", stroke=PURPLE, sw=1.4, rx=4)
    s.text(340, 26, "the DOM  (objects in memory)", size=10.5, weight=800, color=NAVY, anchor="start")
    nodes = {"section": (500, 50, "section", ".card", "white"),
             "h1": (372, 122, "h1", "Click Counter", "white"),
             "p": (474, 122, "p", ".count-row", "white"),
             "div": (590, 122, "div", ".actions", "white"),
             "span": (430, 196, "span", "#count · 0", "purple"),
             "inc": (530, 196, "button", "#increment", "white"),
             "res": (626, 196, "button", "#reset", "white")}
    edges = [("section", "h1"), ("section", "p"), ("section", "div"), ("p", "span"), ("div", "inc"), ("div", "res")]
    nw, nh = 88, 40
    for a, b in edges:
        ax, ay = nodes[a][0], nodes[a][1] + nh / 2
        bx, by = nodes[b][0], nodes[b][1] - nh / 2
        s.line(ax, ay, bx, by, color="#94a3b8", sw=1.3, arrow=False)
    for key, (cx, cy, tag, sub, kind) in nodes.items():
        w = nw if key not in ("inc",) else 92
        s.box(cx - w / 2, cy - nh / 2, w, nh, title=tag, body=[sub], kind=kind, tsize=10.5, bsize=9.5, rx=8)
    s.box(320, 262, 356, 70, kind="yellow", rx=10)
    s.text(332, 284, "script.js", size=10, weight=800, color="#5c4a00", anchor="start")
    s.text(332, 302, "const countEl = document.getElementById('count');", size=9.6, mono=True, anchor="start")
    s.text(332, 320, "countEl.textContent = 5;   // the page now shows 5", size=9.6, mono=True, anchor="start")
    s.path("M 420 262 C 410 240, 418 232, 426 218", color=PURPLE, sw=1.8)
    s.text(16, 284, "JavaScript never edits the file.", size=10.5, weight=700, anchor="start")
    s.text(16, 302, "It changes the objects on the right,", size=10.5, anchor="start")
    s.text(16, 320, "and the browser redraws at once.", size=10.5, anchor="start")
    return s.render()


@fig
def fp_event_flow():
    s = Svg(680, 268, "fpev")
    panel(s, 4, 4, 672, 92, "", kind="grey")
    s.text(16, 24, "ONCE, when the page loads", size=10.5, weight=800, color=NAVY, anchor="start")
    hchain(s, 16, 34, [("script.js runs", ["top to bottom"], "white", 130),
                       ("1 · Select", ["getElementById('increment')"], "blue", 210),
                       ("2 · Listen", ["addEventListener('click', increase)"], "blue", 244)],
           h=50, gap=28, tsize=11, bsize=9.5)
    panel(s, 4, 118, 672, 146, "", kind="purple")
    s.text(16, 138, "EVERY click, for as long as the page is open", size=10.5, weight=800, color="#4c1d95",
           anchor="start")
    hchain(s, 16, 150, [("User clicks", ["Click me"], "white", 120),
                        ("Browser calls", ["increase()"], "white", 130),
                        ("3 · Change", ["count = count + 1", "textContent = count"], "green", 168),
                        ("Browser redraws", ["the page shows 1, 2, 3…"], "white", 150)],
           h=56, gap=22, tsize=11, bsize=9.5)
    s.path("M 586 208 L 586 238 L 76 238 L 76 210", color="#6d28d9", dash="4 3")
    s.text(330, 254, "next click: the same function runs again", size=9.5, italic=True, color="#5b21b6")
    s.path("M 522 86 L 522 112 L 222 112 L 222 148", color="#3f6fd6", dash="4 3")
    s.text(384, 108, "the browser keeps the function", size=9, italic=True, color="#1e3a8a")
    return s.render()


@fig
def fp_box_model():
    s = Svg(680, 292, "fpbox")
    s.rect(110, 10, 400, 240, fill="#ffffff", stroke="#94a3b8", sw=1.4, rx=4, dash="5 4")
    s.text(122, 30, "margin", size=11, weight=700, color=MUTED, anchor="start")
    s.text(122, 44, "outside, transparent: pushes others away", size=9, italic=True, color=MUTED, anchor="start")
    s.rect(150, 56, 320, 170, fill="#ede9fe", stroke=NAVY, sw=4, rx=10)
    s.text(162, 78, "border", size=11, weight=700, color=NAVY, anchor="start")
    s.text(212, 78, "+ padding", size=11, weight=700, color="#5b21b6", anchor="start")
    s.text(162, 92, "padding is inside the border and shows the background", size=9, italic=True,
           color="#5b21b6", anchor="start")
    s.rect(196, 104, 228, 86, fill="#ffffff", stroke="#8b5cf6", sw=1.2, rx=4, dash="4 3")
    s.text(310, 142, "content", size=13, weight=800, color=INK)
    s.text(310, 160, "the text, image or children", size=9.5, color=MUTED)
    # width measure (border-box)
    s.line(150, 266, 470, 266, color=PURPLE, sw=1.4, start_arrow=True)
    s.line(150, 228, 150, 272, color=PURPLE, sw=1, dash="2 3", arrow=False)
    s.line(470, 228, 470, 272, color=PURPLE, sw=1, dash="2 3", arrow=False)
    s.text(310, 284, "width  (with box-sizing: border-box)", size=9.5, weight=700, color=PURPLE)
    for y, label, code in [(70, "margin", "margin: 0 auto 12px;"), (120, "border", "border: 1px solid #ddd;"),
                           (170, "padding", "padding: 24px;")]:
        s.text(528, y, label, size=10, weight=700, anchor="start", color=INK)
        s.text(528, y + 15, code, size=9, mono=True, anchor="start", color="#5b21b6")
    return s.render()


@fig
def fp_center_three():
    s = Svg(680, 262, "fpctr")
    titles = [("1 · Flexbox", ["display: flex;", "justify-content: center;", "align-items: center;"]),
              ("2 · Grid", ["display: grid;", "place-items: center;"]),
              ("3 · Absolute", ["position: absolute;", "top: 50%; left: 50%;", "transform:",
                                "  translate(-50%, -50%);"])]
    for i, (t, code) in enumerate(titles):
        x = 6 + i * 226
        s.text(x + 104, 18, t, size=12, weight=800, color=NAVY)
        s.rect(x, 28, 208, 128, fill="#e2e8f0", stroke="#cbd5e1", sw=1.2, rx=10)
        cx, cy = x + 104, 92
        if i == 0:
            s.line(x + 14, cy, cx - 30, cy, color=ORANGE, sw=1.6)
            s.line(x + 194, cy, cx + 30, cy, color=ORANGE, sw=1.6)
            s.line(cx, 36, cx, cy - 30, color="#0d9488", sw=1.6)
            s.line(cx, 148, cx, cy + 30, color="#0d9488", sw=1.6)
            s.text(x + 14, 152, "justify →", size=8.5, color="#9a3412", anchor="start", weight=700)
            s.text(cx + 6, 46, "align ↕", size=8.5, color="#0f766e", anchor="start", weight=700)
        elif i == 1:
            s.line(x + 10, cy, x + 198, cy, color="#94a3b8", sw=1, dash="3 3", arrow=False)
            s.line(cx, 34, cx, 150, color="#94a3b8", sw=1, dash="3 3", arrow=False)
            s.text(x + 12, 46, "one cell, item in the middle", size=8.5, color=MUTED, anchor="start",
                   italic=True)
        else:
            s.line(x + 10, cy, x + 198, cy, color="#94a3b8", sw=1, dash="3 3", arrow=False)
            s.line(cx, 34, cx, 150, color="#94a3b8", sw=1, dash="3 3", arrow=False)
        s.circle(cx, cy, 22, fill=PURPLE, stroke=PURPLE, sw=1)
        s.text(cx, cy + 4, "dot", size=9, weight=700, color="#ffffff")
        if i == 2:
            s.rect(cx, cy, 44, 44, fill="none", stroke="#c2410c", sw=1.5, rx=22, dash="4 3")
            s.text(cx + 22, cy + 58, "step 1: corner at 50% / 50%", size=8.5, color="#c2410c", italic=True)
            s.path(f"M {cx + 22} {cy + 22} L {cx + 4} {cy + 4}", color="#c2410c", sw=1.8)
            s.text(x + 12, 46, "step 2: translate(-50%, -50%)", size=8.5, color="#c2410c", anchor="start",
                   italic=True, weight=700)
            s.text(x + 12, 58, "pulls it back by half its own size", size=8.5, color=MUTED, anchor="start",
                   italic=True)
        s.rect(x, 166, 208, 88, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=8)
        target = "on the parent (.stage)" if i < 2 else "on the child (.dot)"
        s.text(x + 10, 184, target, size=9, italic=True, color=MUTED, anchor="start")
        _code_lines(s, x + 10, 202, code, size=9.6, lh=14, color="#4c1d95")
    return s.render()


@fig
def fp_render():
    s = Svg(680, 286, "fprender")
    s.box(6, 20, 150, 70, title="products", body=["8 names", "(never changes)"], kind="grey", tsize=11.5)
    s.box(6, 120, 150, 70, title="search box", body=["value: 'apple'"], kind="blue", tsize=11.5,
          mono_body=True)
    fill, stroke, tcol = KIND["purple"]
    s.rect(196, 8, 250, 230, fill=fill, stroke=stroke, sw=1.6, rx=12)
    s.text(321, 30, "render()", size=13, weight=800, mono=True, color=tcol)
    steps = [("1", "query = 'apple'", "trim + lower-case"),
             ("2", "filter → 3 matches", "includes(query)"),
             ("3", "empty the list", "innerHTML = ''"),
             ("4", "create 3 <li>", "createElement + append"),
             ("5", "count + empty message", "'3 results', hidden")]
    for i, (n, a, b) in enumerate(steps):
        y = 44 + i * 38
        s.circle(220, y + 14, 10, fill=NAVY, stroke="#ffffff", sw=1.4)
        s.text(220, y + 18, n, size=10, weight=800, color="#ffffff")
        s.text(238, y + 12, a, size=10.5, weight=700, anchor="start", color=INK)
        s.text(238, y + 26, b, size=9, anchor="start", color=MUTED, mono=True)
    s.line(160, 55, 192, 80, color="#475569")
    s.line(160, 155, 192, 120, color="#475569")
    top = _browser(s, 478, 20, 196, 200, "the page")
    s.text(492, top + 24, "3 results", size=9.5, color=MUTED, anchor="start")
    for i, t in enumerate(["Apple iPhone", "Apple MacBook", "Apple Watch"]):
        s.rect(490, top + 34 + i * 32, 172, 26, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6)
        s.text(500, top + 51 + i * 32, t, size=10, anchor="start", color=INK)
    s.text(576, top + 150, "No results found", size=9, color="#cbd5e1", italic=True)
    s.text(576, top + 164, "(hidden)", size=8.5, color="#cbd5e1", italic=True)
    s.line(450, 120, 474, 120, color="#475569")
    s.path("M 81 194 L 81 264 L 321 264 L 321 242", color=PURPLE, dash="4 3")
    s.text(92, 258, "every 'input' event calls render() again", size=9.5, italic=True, color="#5b21b6",
           anchor="start")
    s.text(360, 258, "+ once at page load: render();", size=9.5, italic=True, color="#5b21b6", anchor="start")
    return s.render()


@fig
def fp_todo_item():
    s = Svg(680, 226, "fptodo")
    for k, (text, done) in enumerate([("Buy milk", True), ("Revise flexbox", False)]):
        y = 16 + k * 96
        s.rect(6, y, 420, 46, fill="#f8fafc", stroke=PURPLE if k == 0 else "#0d9488", sw=1.8, rx=10)
        s.text(14, y - 4, f'<li class="todo-item{" completed" if done else ""}">  #{k + 1}', size=9,
               mono=True, color=PURPLE if k == 0 else "#0f766e", anchor="start")
        s.rect(16, y + 9, 200, 28, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=6)
        s.text(26, y + 28, text, size=11, anchor="start", color="#94a3b8" if done else INK)
        if done:
            s.line(26, y + 24, 26 + text_width(text, 11), y + 24, color="#94a3b8", sw=1.2, arrow=False)
        s.text(116, y + 52 + 4, "span.todo-text", size=8.5, mono=True, color=MUTED)
        s.rect(232, y + 9, 84, 28, fill="#dbeafe", stroke="#bfdbfe", sw=1, rx=6)
        s.text(274, y + 27, "Done", size=10.5, weight=700, color="#1d4ed8")
        s.rect(326, y + 9, 88, 28, fill="#fee2e2", stroke="#fecaca", sw=1, rx=6)
        s.text(370, y + 27, "Delete", size=10.5, weight=700, color="#b91c1c")
        col = PURPLE if k == 0 else "#0d9488"
        s.box(452, y - 8, 222, 66, kind="purple" if k == 0 else "teal", rx=8)
        s.text(462, y + 10, "Done's listener:", size=9, weight=700, anchor="start", color=col)
        s.text(462, y + 24, "li.classList.toggle('completed')", size=8.8, mono=True, anchor="start")
        s.text(462, y + 40, "Delete's listener:", size=9, weight=700, anchor="start", color=col)
        s.text(462, y + 54, "li.remove(); updateEmpty();", size=8.8, mono=True, anchor="start")
        s.line(418, y + 23, 448, y + 23, color=col, sw=1.6)
    s.box(6, 188, 668, 32, kind="yellow", rx=8,
          title="Each createTodo() call makes a new li; its two listeners remember THAT li (a closure).",
          tsize=10.5)
    return s.render()


@fig
def fp_css_vars():
    s = Svg(680, 256, "fpvars")
    for i, (title, dark) in enumerate([("<body>  (no class)", False), ('<body class="dark">', True)]):
        x = 6 + i * 340
        bg, txt = ("#f8fafc", "#0f172a") if not dark else ("#0f172a", "#f8fafc")
        s.text(x + 162, 18, "light theme" if not dark else "dark theme", size=12, weight=800, color=NAVY)
        s.box(x, 28, 324, 58, kind="grey", rx=8)
        s.text(x + 12, 46, ":root  (the <html> element)", size=9.5, weight=700, anchor="start", color="#374151")
        s.text(x + 12, 62, "--bg: #f8fafc;", size=9.6, mono=True, anchor="start")
        s.text(x + 12, 77, "--text: #0f172a;", size=9.6, mono=True, anchor="start")
        s.line(x + 162, 90, x + 162, 106, color="#94a3b8", sw=1.3)
        s.box(x, 110, 324, 64, kind="purple" if dark else "white", rx=8)
        s.text(x + 12, 128, title, size=9.5, weight=700, mono=True, anchor="start", color="#4c1d95")
        if dark:
            s.text(x + 12, 144, "body.dark sets new values:", size=9.3, anchor="start", italic=True)
            s.text(x + 12, 160, "--bg: #0f172a;  --text: #f8fafc;", size=9.6, mono=True, anchor="start")
        else:
            s.text(x + 12, 144, "sets nothing: uses the values", size=9.3, anchor="start", italic=True)
            s.text(x + 12, 160, "it inherits from :root", size=9.3, anchor="start", italic=True)
        s.line(x + 162, 178, x + 162, 194, color="#94a3b8", sw=1.3)
        s.rect(x, 198, 324, 52, fill=bg, stroke="#94a3b8", sw=1.2, rx=8)
        s.text(x + 14, 218, "background: var(--bg);", size=9.6, mono=True, anchor="start", color=txt)
        s.text(x + 14, 236, "color: var(--text);", size=9.6, mono=True, anchor="start", color=txt)
        s.text(x + 310, 228, "the page", size=9.5, italic=True, anchor="end", color=txt)
    return s.render()


@fig
def fp_one_active():
    s = Svg(680, 244, "fpone")
    steps = [("1 · Remember", "wasOpen = false", [False, True, False],
              "item.classList.contains('open')"),
             ("2 · All off", "every item closed", [False, False, False],
              "every x: x.classList.remove('open')"),
             ("3 · One on", "only if it wasn't open", [False, False, True],
              "item.classList.add('open')")]
    for i, (title, sub, states, code) in enumerate(steps):
        x = 6 + i * 228
        s.text(x + 104, 18, title, size=12, weight=800, color=NAVY)
        s.text(x + 104, 34, sub, size=9.5, italic=True, color=MUTED)
        for j, on in enumerate(states):
            y = 46 + j * 44
            s.rect(x + 10, y, 188, 34, fill=PURPLE_L if on else "#f8fafc", stroke=PURPLE if on else "#cbd5e1",
                   sw=1.6 if on else 1.1, rx=8)
            s.text(x + 22, y + 22, f"Question {j + 1}", size=10.5, weight=700 if on else 400, anchor="start",
                   color="#4c1d95" if on else INK)
            s.text(x + 186, y + 22, "-" if on else "+", size=13, weight=800, anchor="end", color=PURPLE)
        s.rect(x + 4, 186, 200, 26, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6)
        s.text(x + 104, 203, code, size=8.6, mono=True, color="#4c1d95")
        if i < 2:
            s.line(x + 206, 113, x + 224, 113, color="#475569")
    # the click
    s.path("M 218 167 L 196 152", color=ORANGE, sw=2)
    s.text(6, 232, "The user clicked Question 3 (orange arrow). Question 2 was open. Read the state first, "
           "then switch all off, then one on.", size=9.5, italic=True, color=MUTED, anchor="start")
    return s.render()


@fig
def fp_carousel_ring():
    s = Svg(680, 262, "fpring")
    cx, cy, r = 160, 128, 86
    cols = [("#7c3aed", "#4f46e5"), ("#0ea5e9", "#2563eb"), ("#10b981", "#0d9488"), ("#f59e0b", "#ef4444")]
    pos = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    s.circle(cx, cy, r, fill="none", stroke="#e2e8f0", sw=10)
    for i, (px, py) in enumerate(pos):
        s.rect(px - 30, py - 22, 60, 44, fill=cols[i][0], stroke=cols[i][1], sw=2, rx=8)
        s.text(px, py + 7, str(i), size=18, weight=800, color="#ffffff")
    s.path(f"M {cx + 38} {cy - r + 6} Q {cx + r - 6} {cy - r + 6} {cx + r - 4} {cy - 30}", color=PURPLE, sw=2)
    s.text(cx + 66, cy - r + 2, "Next +1", size=10, weight=700, color=PURPLE, anchor="start")
    s.path(f"M {cx - 38} {cy - r + 6} Q {cx - r + 6} {cy - r + 6} {cx - r + 4} {cy - 30}", color=ORANGE, sw=2)
    s.text(cx - 66, cy - r + 2, "Prev −1", size=10, weight=700, color="#c2410c", anchor="end")
    s.text(cx, cy + 4, "index", size=11, weight=700, color=MUTED)
    rows = [("Next on the last slide", "show(3 + 1)", "(4 + 4) % 4 = 0", "green"),
            ("Prev on the first slide", "show(0 - 1)", "(-1 + 4) % 4 = 3", "green"),
            ("without adding 4 first", "-1 % 4", "-1: slides[-1] is undefined", "red")]
    for i, (a, b, c, kind) in enumerate(rows):
        y = 30 + i * 74
        s.box(316, y, 358, 60, kind=kind, rx=10)
        fill, stroke, tcol = KIND[kind]
        s.text(330, y + 20, a, size=10.5, weight=700, color=tcol, anchor="start")
        s.text(330, y + 42, b, size=10.5, mono=True, anchor="start")
        s.text(440, y + 42, "→  " + c, size=10.5, mono=True, anchor="start", weight=700, color=tcol)
    return s.render()


@fig
def fp_table_flow():
    s = Svg(680, 280, "fptable")
    s.box(6, 14, 160, 62, title="employees", body=["6 objects", "(never changes)"], kind="grey", tsize=11.5)
    s.box(6, 98, 160, 62, title="filter box", body=["value: 'o'"], kind="blue", tsize=11.5, mono_body=True)
    s.box(6, 182, 160, 62, title="sortBy", body=["'age'  (set by", "the sort buttons)"], kind="orange",
          tsize=11.5)
    fill, stroke, tcol = KIND["purple"]
    s.rect(200, 14, 214, 230, fill=fill, stroke=stroke, sw=1.6, rx=12)
    s.text(307, 36, "render()", size=13, weight=800, mono=True, color=tcol)
    for i, (a, b) in enumerate([("filter", "name or city has 'o'"), ("sort", "a.age - b.age"),
                                ("draw", "one <tr> per row"), ("count", "'4 employees'")]):
        y = 50 + i * 47
        s.box(214, y, 186, 38, title=a, body=[b], kind="white", tsize=10.5, bsize=9, rx=8)
    for y in (45, 129, 213):
        s.line(170, y, 196, 129 if y != 129 else 129, color="#475569")
    top = _browser(s, 446, 14, 228, 230, "the table")
    s.text(458, top + 22, "NAME", size=8.5, weight=700, color=MUTED, anchor="start")
    s.text(590, top + 22, "AGE", size=8.5, weight=700, color=MUTED, anchor="start")
    rows = [("Margaret Hamilton", 33), ("Ada Lovelace", 36), ("Grace Hopper", 45), ("Linus Torvalds", 54)]
    for i, (n, a) in enumerate(rows):
        y = top + 30 + i * 30
        s.line(456, y + 26, 664, y + 26, color="#e2e8f0", sw=1, arrow=False)
        s.text(458, y + 18, n, size=10, anchor="start")
        s.text(590, y + 18, str(a), size=10, anchor="start")
    s.text(458, top + 160, "4 employees", size=9.5, color=MUTED, anchor="start")
    s.line(418, 129, 442, 129, color="#475569")
    s.text(340, 268, "Every listener only changes the state, then calls render().", size=10, italic=True,
           color="#5b21b6")
    return s.render()
