"""All diagrams used in the notes. Each function returns an <svg> string."""
from svg import Svg, KIND, INK, MUTED, text_width

FIGS = {}


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


def cells(s, x, y, values, kind="white", w=34, h=32, gap=6, size=13, mono=True):
    for i, v in enumerate(values):
        s.box(x + i * (w + gap), y, w, h, title=str(v), kind=kind, tsize=size, mono_title=mono, rx=6)
    return x + len(values) * (w + gap) - gap


# =====================================================================================
# Chapter 1 — array methods
# =====================================================================================
@fig
def mfr():
    s = Svg(680, 236, "mfr")
    rows = [
        ("map(x => x * 10)", "new array · SAME length", [10, 20, 30, 40], "blue", 42),
        ("filter(x => x % 2 === 0)", "new array · FEWER items", [2, 4], "green", 34),
        ("reduce((sum, x) => sum + x, 0)", "ONE single value", [10], "yellow", 42),
    ]
    y = 18
    for label, note, out, kind, cw in rows:
        end = cells(s, 14, y, [1, 2, 3, 4], "white")
        s.line(end + 12, y + 16, 452, y + 16, color="#475569")
        s.text((end + 452) / 2, y + 8, label, size=11.2, weight=600, mono=True, color="#1e3a8a")
        s.text((end + 452) / 2, y + 30, note, size=10, color=MUTED, italic=True)
        cells(s, 466, y, out, kind, w=cw)
        y += 74
    return s.render()


@fig
def snowball():
    s = Svg(680, 138, "snow")
    xs = [52, 178, 318, 470, 626]
    rs = [19, 24, 30, 36, 43]
    vals = ["0", "10", "30", "60", "100"]
    caps = ["initialValue", "after step 1", "after step 2", "after step 3", "final result"]
    adds = ["+ 10", "+ 20", "+ 30", "+ 40"]
    cy = 58
    for i, (x, r, v, c) in enumerate(zip(xs, rs, vals, caps)):
        last = i == len(xs) - 1
        s.circle(x, cy, r, fill="#fff6c7" if last else "#eef5ff", stroke="#d9ae00" if last else "#6f9bd8", sw=1.8)
        s.text(x, cy + 5, v, size=14 if not last else 16, weight=700, mono=True,
               color="#5c4a00" if last else "#1e3a8a")
        s.text(x, cy + rs[-1] + 26, c, size=10.5, color=MUTED, italic=not last, weight=700 if last else 400)
        if i < len(xs) - 1:
            x1, x2 = x + r + 8, xs[i + 1] - rs[i + 1] - 10
            s.line(x1, cy, x2, cy, color="#475569")
            s.text((x1 + x2) / 2, cy - 9, adds[i], size=11.5, weight=700, mono=True, color="#b45309")
            s.text((x1 + x2) / 2, cy + 18, "acc + curr", size=9.5, color=MUTED, mono=True)
    return s.render()


# =====================================================================================
# Chapter 2 — Set and Map
# =====================================================================================
@fig
def set_dedupe():
    s = Svg(680, 150, "setd")
    vals = [1, 2, 3, 3, 4, 2, 5]
    dup = {3, 5}  # indexes that are duplicates
    s.text(14, 22, "Array (duplicates allowed)", size=11.5, weight=700, anchor="start", color="#374151")
    for i, v in enumerate(vals):
        x = 14 + i * 40
        kind = "red" if i in dup else "white"
        s.box(x, 34, 34, 32, title=str(v), kind=kind, tsize=13, mono_title=True, rx=6)
        if i in dup:
            s.line(x + 5, 39, x + 29, 61, color="#dc4c4c", sw=1.6, arrow=False)
    s.text(14 + 3 * 40 + 17, 86, "duplicate", size=9.5, color="#b91c1c", italic=True)
    s.text(14 + 5 * 40 + 17, 86, "duplicate", size=9.5, color="#b91c1c", italic=True)
    s.line(300, 50, 400, 50, color="#475569")
    s.text(350, 40, "new Set(array)", size=11, weight=600, mono=True, color="#1e3a8a")
    s.text(350, 68, "duplicates removed", size=9.5, color=MUTED, italic=True)
    s.text(414, 22, "Set (only unique values)", size=11.5, weight=700, anchor="start", color="#374151")
    s.rect(410, 30, 256, 40, fill="#e2f7ea", stroke="#26a05e", sw=1.5, rx=20)
    for i, v in enumerate([1, 2, 3, 4, 5]):
        s.box(422 + i * 48, 36, 38, 28, title=str(v), kind="white", tsize=13, mono_title=True, rx=6)
    s.text(538, 92, "Set(5) { 1, 2, 3, 4, 5 }   ·   .size === 5", size=10.5, color="#14532d", mono=True)
    s.text(340, 130, "The Set keeps the FIRST time it sees a value and ignores the later copies (insertion order is kept).",
           size=10.5, color="#374151", italic=True)
    return s.render()


@fig
def object_vs_map():
    s = Svg(680, 250, "ovm")
    # left panel: object
    s.rect(8, 8, 320, 234, fill="#fff7f7", stroke="#f1b4b4", sw=1.2, rx=12)
    s.text(168, 32, "Plain object  { }", size=13, weight=700, color="#7f1d1d")
    s.box(24, 50, 112, 34, title="keyObject1", body=[], kind="white", tsize=11, mono_title=True, rx=6)
    s.box(24, 100, 112, 34, title="keyObject2", body=[], kind="white", tsize=11, mono_title=True, rx=6)
    s.line(140, 67, 186, 88, color="#dc4c4c")
    s.line(140, 117, 186, 96, color="#dc4c4c")
    s.box(190, 74, 124, 36, title='"[object Object]"', kind="red", tsize=10.5, mono_title=True, rx=6)
    s.text(252, 128, "both keys become the", size=9.5, color="#7f1d1d", italic=True)
    s.text(252, 141, "SAME string key", size=9.5, color="#7f1d1d", italic=True, weight=700)
    s.rect(24, 160, 290, 64, fill="#ffffff", stroke="#e8b4b4", sw=1.2, rx=8)
    s.text(169, 182, "Result: only ONE entry", size=11, weight=700, color="#7f1d1d")
    s.text(169, 204, "{ '[object Object]': 'Value for key 2' }", size=10, mono=True, color="#374151")
    # right panel: Map
    s.rect(352, 8, 320, 234, fill="#f3fbf6", stroke="#a9dcc0", sw=1.2, rx=12)
    s.text(512, 32, "Map", size=13, weight=700, color="#14532d")
    s.box(368, 50, 112, 34, title="keyObject1", kind="white", tsize=11, mono_title=True, rx=6)
    s.box(368, 100, 112, 34, title="keyObject2", kind="white", tsize=11, mono_title=True, rx=6)
    s.line(484, 67, 526, 67, color="#26a05e")
    s.line(484, 117, 526, 117, color="#26a05e")
    s.box(530, 50, 128, 34, title='"Value for key 1"', kind="green", tsize=10, mono_title=True, rx=6)
    s.box(530, 100, 128, 34, title='"Value for key 2"', kind="green", tsize=10, mono_title=True, rx=6)
    s.text(512, 150, "the key object itself is the key", size=9.5, color="#14532d", italic=True)
    s.rect(368, 160, 290, 64, fill="#ffffff", stroke="#a9dcc0", sw=1.2, rx=8)
    s.text(513, 182, "Result: TWO separate entries", size=11, weight=700, color="#14532d")
    s.text(513, 204, "map.size === 2", size=10.5, mono=True, color="#374151")
    return s.render()


# =====================================================================================
# Chapter 3 — event loop
# =====================================================================================
@fig
def call_stack():
    s = Svg(680, 252, "cs")
    kinds = {"global": "grey", "printSquare(4)": "blue", "square(4)": "green",
             "multiply(4, 4)": "orange", "console.log(16)": "purple"}
    snaps = [
        (["global"], ["script starts", "(global code)"]),
        (["global", "printSquare(4)"], ["printSquare(4)", "is called"]),
        (["global", "printSquare(4)", "square(4)"], ["square(4)", "is called"]),
        (["global", "printSquare(4)", "square(4)", "multiply(4, 4)"], ["multiply(4, 4)", "returns 16"]),
        (["global", "printSquare(4)", "console.log(16)"], ["console.log(16)", "prints 16"]),
        ([], ["stack is empty", "— done!"]),
    ]
    x0, cw, gap = 8, 106, 6.8
    for i, (frames, desc) in enumerate(snaps):
        x = x0 + i * (cw + gap)
        s.text(x + cw / 2, 22, f"Step {i + 1}", size=11, weight=700, color="#16213e")
        s.path(f"M{x + 3},36 L{x + 3},196 L{x + cw - 3},196 L{x + cw - 3},36", color="#94a3b8", sw=1.6, arrow=False)
        for k, fr in enumerate(frames):
            top = k == len(frames) - 1
            y = 196 - 6 - (k + 1) * 30
            s.box(x + 9, y, cw - 18, 26, title=fr, kind=kinds[fr], tsize=9.4, mono_title=True, rx=5,
                  sw=2.2 if top else 1.2)
        if not frames:
            s.text(x + cw / 2, 120, "(empty)", size=10.5, color=MUTED, italic=True)
        s.text(x + cw / 2, 216, desc[0], size=9.8, weight=600, color="#1f2937", mono=desc[0].endswith(")"))
        s.text(x + cw / 2, 231, desc[1], size=9.8, color=MUTED)
        if i < len(snaps) - 1:
            s.line(x + cw + 0.5, 116, x + cw + gap - 0.5, 116, color="#cbd2dd", sw=1, arrow=False)
    s.text(340, 249, "The frame with the thick border (the top of the stack) is the one running right now.",
           size=9.5, color=MUTED, italic=True)
    return s.render()


@fig
def event_loop():
    s = Svg(680, 378, "el")
    # call stack
    s.rect(14, 36, 160, 198, fill="#e7efff", stroke="#3f6fd6", sw=1.6, rx=12)
    s.text(94, 60, "Call Stack", size=14, weight=800, color="#1e3a8a")
    s.text(94, 77, "your JS runs here,", size=10, color="#1e3a8a", italic=True)
    s.text(94, 91, "one frame at a time", size=10, color="#1e3a8a", italic=True)
    s.box(30, 158, 128, 28, title="someFunction()", kind="white", tsize=10, mono_title=True, rx=6, sw=2)
    s.box(30, 192, 128, 28, title="global code", kind="white", tsize=10, mono_title=True, rx=6)
    # web apis
    s.rect(240, 36, 426, 136, fill="#fff3e6", stroke="#e8792a", sw=1.6, rx=12)
    s.text(453, 60, "Web APIs — the browser's helpers", size=14, weight=800, color="#7c2d12")
    s.text(453, 77, "this work happens OUTSIDE the JavaScript thread", size=10, color="#9a3412", italic=True)
    x = 258
    for t in ["setTimeout / setInterval", "fetch()", "DOM events (click)"]:
        x += s.chip(x, 92, t, kind="white", size=10.2) + 10
    x = 258
    for t in ["localStorage", "location", "Node.js: fs.readFile"]:
        x += s.chip(x, 128, t, kind="white", size=10.2) + 10
    s.line(176, 104, 238, 104, color="#475569")
    s.text(207, 96, "hands over", size=9.5, color=MUTED, italic=True)
    s.text(207, 121, "slow work", size=9.5, color=MUTED, italic=True)
    # queues
    s.rect(240, 212, 426, 56, fill="#f1eaff", stroke="#8b5cf6", sw=1.6, rx=12)
    s.text(254, 235, "Microtask Queue", size=12.5, weight=800, color="#4c1d95", anchor="start")
    s.text(254, 254, "VIP line: runs FIRST — ALL of them", size=9.8, color="#5b21b6", italic=True, anchor="start")
    s.chip(478, 227, "Promise .then()", kind="white", size=10)
    s.chip(583, 227, "after await", kind="white", size=10)
    s.rect(240, 282, 426, 56, fill="#fff6c7", stroke="#d9ae00", sw=1.6, rx=12)
    s.text(254, 305, "Macrotask (Callback) Queue", size=12.5, weight=800, color="#5c4a00", anchor="start")
    s.text(254, 324, "runs AFTER microtasks — ONE at a time", size=9.8, color="#6b5600", italic=True, anchor="start")
    s.chip(478, 297, "setTimeout cb", kind="white", size=10)
    s.chip(574, 297, "click handler", kind="white", size=10)
    s.line(300, 174, 300, 208, color="#475569")
    s.text(310, 195, "when the work is done, its callback waits in a queue", size=9.8, color=MUTED,
           italic=True, anchor="start")
    # event loop
    s.circle(94, 306, 38, fill="#e2f7ea", stroke="#26a05e", sw=2)
    s.text(94, 302, "Event", size=13, weight=800, color="#14532d")
    s.text(94, 318, "Loop", size=13, weight=800, color="#14532d")
    s.line(238, 242, 136, 292, color="#8b5cf6")
    s.text(186, 254, "1st", size=10, weight=700, color="#5b21b6")
    s.line(238, 312, 138, 312, color="#b58900")
    s.text(186, 305, "2nd", size=10, weight=700, color="#6b5600")
    s.line(94, 266, 94, 238, color="#26a05e", sw=2)
    s.text(86, 252, "only when the", size=9.2, color="#14532d", anchor="end", italic=True)
    s.text(86, 264, "stack is EMPTY", size=9.2, color="#14532d", anchor="end", italic=True, weight=700)
    s.text(340, 368, "Rule: when the call stack is EMPTY → run ALL microtasks → then ONE macrotask → repeat forever",
           size=11, weight=700, color="#16213e")
    return s.render()


@fig
def never_waits():
    s = Svg(680, 214, "nw")
    s.text(10, 58, "JavaScript", size=11.5, weight=800, color="#1e3a8a", anchor="start")
    s.text(10, 73, "(call stack)", size=10, color=MUTED, anchor="start")
    s.text(10, 144, "Browser", size=11.5, weight=800, color="#7c2d12", anchor="start")
    s.text(10, 159, "(timer Web API)", size=10, color=MUTED, anchor="start")
    s.line(96, 40, 96, 176, color="#e2e6ee", sw=1, arrow=False)
    w1 = s.chip(110, 52, "log('1')", kind="blue", size=10, mono=True, h=22)
    w2 = s.chip(186, 52, "setTimeout(…) → id", kind="blue", size=10, mono=True, h=22)
    w3 = s.chip(328, 52, "log('2')", kind="blue", size=10, mono=True, h=22)
    s.line(404, 63, 588, 63, color="#94a3b8", sw=1.6, dash="4 4", arrow=False)
    s.text(496, 46, "stack empty — JS is free", size=9.6, color=MUTED, italic=True)
    s.text(496, 84, "(can handle clicks, other code…)", size=9.6, color=MUTED, italic=True)
    s.chip(600, 52, "log('3')", kind="green", size=10, mono=True, h=22)
    s.rect(250, 130, 346, 24, fill="#fff0e2", stroke="#e8792a", sw=1.4, rx=12)
    s.text(423, 146, "counting 1000 ms …", size=10.5, weight=600, color="#7c2d12")
    s.line(250, 76, 250, 128, color="#e8792a")
    s.text(258, 106, "hands over the timer", size=9.6, color="#9a3412", italic=True, anchor="start")
    s.path("M 596 142 C 624 142 632 118 632 78", color="#26a05e", sw=1.6)
    s.text(604, 104, "callback", size=9.6, color="#14532d", italic=True, anchor="end")
    s.text(604, 116, "via queue", size=9.6, color="#14532d", italic=True, anchor="end")
    s.line(110, 186, 664, 186, color="#94a3b8", sw=1.2, arrow=False)
    for x, t in [(141, "0 ms"), (250, "≈ 1 ms"), (359, "≈ 2 ms"), (631, "1000 ms")]:
        s.line(x, 182, x, 190, color="#94a3b8", sw=1.2, arrow=False)
        s.text(x, 204, t, size=10, color="#374151", weight=600)
    s.text(496, 204, "(not to scale)", size=9.5, color=MUTED, italic=True)
    return s.render()


@fig
def click_flow():
    s = Svg(680, 150, "cf")
    boxes = [
        ("You click", ["Button 1", "(the user)"], "pink"),
        ("DOM API", ["remembers: on click", "of #button1 → cb"], "orange"),
        ("Macrotask Queue", ["the callback", "waits in line"], "yellow"),
        ("Event Loop", ["is the stack", "empty? → go!"], "green"),
        ("Call Stack", ["runs the callback", "(prints the text)"], "blue"),
    ]
    x, w, gap = 6, 118, 21
    for i, (t, body, kind) in enumerate(boxes):
        s.box(x, 14, w, 78, title=t, body=body, kind=kind, tsize=11.5, bsize=9.8)
        if i < len(boxes) - 1:
            s.line(x + w + 2, 53, x + w + gap - 2, 53, color="#475569")
        x += w + gap
    s.rich(340, 124, [("Console:  ", {"color": MUTED}), ('"Button 1 is clicked"', {"mono": True, "weight": 700})],
           size=11.5, anchor="middle")
    s.text(340, 142, "…and this happens again for EVERY click.", size=10, color=MUTED, italic=True)
    return s.render()


# =====================================================================================
# Chapter 4 — callbacks
# =====================================================================================
@fig
def zomato_steps():
    s = Svg(680, 196, "zs")
    s.rect(4, 30, 104, 104, fill="#ffffff", stroke="#94a3b8", sw=1.4, rx=10)
    s.text(56, 50, "orderDetail", size=11, weight=800, mono=True, color="#16213e")
    for i, t in enumerate(["orderId: 123123", "cost: 620", "food: [3 items]", "Rohit, Dwarka", "from: Delhi"]):
        s.text(56, 68 + i * 14, t, size=8.8, mono=True, color="#374151")
    steps = [("1. Place order", "payment", "+ status: true", "yellow"),
             ("2. Prepare food", "cooking", "+ token: 123", "orange"),
             ("3. Pick up", "rider goes", "+ received: true", "blue"),
             ("4. Deliver", "on the way", "+ delivery: true", "green")]
    x = 126
    for i, (t, b, add, kind) in enumerate(steps):
        s.box(x, 30, 118, 62, title=t, body=[b + "  ·  3 s"], kind=kind, tsize=11.5, bsize=10)
        s.chip(x + 59, 102, add, kind="white", size=9.6, mono=True, anchor="middle", weight=600)
        s.line(x - 16, 61, x - 3, 61, color="#475569")
        x += 138
    s.text(340, 160, "Each step:  takes time  ·  needs the previous step  ·  adds data for the next step",
           size=10.8, weight=600, color="#16213e")
    s.text(340, 182, "The SAME orderDetail object is passed along — every step can see what earlier steps added.",
           size=10, color=MUTED, italic=True)
    return s.render()


@fig
def callback_gantt():
    s = Svg(680, 300, "cg")
    x0, x1 = 150, 646
    px = (x1 - x0) / 12

    def axis(y):
        s.line(x0, y, x1, y, color="#94a3b8", sw=1.1, arrow=False)
        for t in range(0, 13, 3):
            s.line(x0 + t * px, y - 3, x0 + t * px, y + 3, color="#94a3b8", sw=1.1, arrow=False)
            s.text(x0 + t * px, y + 15, f"{t} s", size=9.5, color="#374151", weight=600)

    s.text(8, 20, "✔ Nested callbacks (Day 18 code)", size=12, weight=800, color="#14532d", anchor="start")
    rows = [("placedOrder", 0, "yellow"), ("preparingOrder", 3, "orange"), ("pickupOrder", 6, "blue"),
            ("deliverOrder", 9, "green")]
    for i, (name, start, kind) in enumerate(rows):
        y = 32 + i * 26
        s.text(140, y + 14, name, size=10, mono=True, anchor="end", color="#1f2937")
        fill, stroke, tc = KIND[kind]
        s.rect(x0 + start * px, y, 3 * px, 19, fill=fill, stroke=stroke, sw=1.3, rx=5)
        s.text(x0 + (start + 1.5) * px, y + 13.5, "waiting 3 s", size=9, color=tc)
        if i < len(rows) - 1:
            s.path(f"M {x0 + (start + 3) * px} {y + 19} L {x0 + (start + 3) * px} {y + 27}", color="#475569",
                   sw=1.3)
    axis(142)
    s.text(8, 186, "✘ Called one after another (wrong)", size=12, weight=800, color="#991b1b", anchor="start")
    rows2 = [("placedOrder", "yellow"), ("preparingOrder", "orange"), ("pickupOrder", "blue")]
    for i, (name, kind) in enumerate(rows2):
        y = 198 + i * 26
        s.text(140, y + 14, name, size=10, mono=True, anchor="end", color="#1f2937")
        fill, stroke, tc = KIND[kind]
        s.rect(x0, y, 3 * px, 19, fill=fill, stroke=stroke, sw=1.3, rx=5)
        s.text(x0 + 1.5 * px, y + 13.5, "starts at 0 s!", size=9, color=tc)
    s.box(x0 + 3.4 * px, 198, 7.6 * px, 71, title="chaos", body=["3 s: steps run a second time", "6 s: TypeError crash"],
          kind="red", tsize=11, bsize=10)
    axis(276)
    return s.render()


@fig
def nesting_dolls():
    s = Svg(680, 214, "nd")
    layers = [
        ("placedOrder(orderDetail, (orderDetail) => {", "Level 1 · runs at 0 s", "yellow"),
        ("preparingOrder(orderDetail, (orderDetail) => {", "Level 2 · after 3 s", "orange"),
        ("pickupOrder(orderDetail, (orderDetail) => {", "Level 3 · after 6 s", "blue"),
        ("deliverOrder(orderDetail);", "Level 4 · after 9 s", "green"),
    ]
    for i, (code, tag, kind) in enumerate(layers):
        x, y = 8 + i * 30, 8 + i * 44
        w, h = 664 - i * 60, 198 - i * 44
        fill, stroke, tc = KIND[kind]
        s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=12)
        s.text(x + 14, y + 25, code, size=11, mono=True, anchor="start", color="#1f2937", weight=600)
        s.text(x + w - 14, y + 25, tag, size=9.8, anchor="end", color=tc, weight=700)
    return s.render()


# =====================================================================================
# Chapter 5 — promises
# =====================================================================================
@fig
def promise_states():
    s = Svg(680, 256, "ps")
    s.box(14, 88, 170, 74, title="PENDING", body=["“I'm working on it…”", "(initial state)"],
          kind="yellow", tsize=14, bsize=10.5)
    s.rect(300, 8, 232, 222, fill="none", stroke="#94a3b8", sw=1.3, rx=14, dash="6 5")
    s.box(316, 24, 200, 74, title="FULFILLED", body=["“I got the result!”", "has a VALUE"],
          kind="green", tsize=14, bsize=10.5)
    s.box(316, 142, 200, 74, title="REJECTED", body=["“Something went wrong!”", "has a REASON (error)"],
          kind="red", tsize=14, bsize=10.5)
    s.line(184, 108, 312, 64, color="#26a05e", sw=1.8)
    s.line(184, 142, 312, 176, color="#dc4c4c", sw=1.8)
    s.text(238, 74, "resolve(value)", size=10.5, weight=700, mono=True, color="#14532d", anchor="end")
    s.text(236, 184, "reject(reason)", size=10.5, weight=700, mono=True, color="#7f1d1d", anchor="end")
    s.text(416, 246, "SETTLED  =  final, can never change again", size=10.2, weight=700, color="#475569")
    s.line(518, 61, 548, 61, color="#26a05e")
    s.chip(552, 50, ".then(value => …)", kind="green", size=9.4, mono=True, h=22, weight=600)
    s.line(518, 179, 548, 179, color="#dc4c4c")
    s.chip(552, 168, ".catch(err => …)", kind="red", size=9.4, mono=True, h=22, weight=600)
    s.chip(552, 109, ".finally(() => …)", kind="grey", size=9.4, mono=True, h=22, weight=600)
    s.text(612, 146, "runs in BOTH cases", size=9, color=MUTED, italic=True)
    return s.render()


@fig
def promise_chain():
    s = Svg(680, 262, "pc")
    s.text(8, 18, "Values flow down the chain", size=11.5, weight=800, color="#14532d", anchor="start")
    boxes = [("Promise.resolve(5)", "green"), ("then: v * 2", "blue"), ("then: v + 3", "blue"), ("then: log(v)", "blue")]
    vals = ["5", "10", "13"]
    x = 8
    for i, (t, kind) in enumerate(boxes):
        s.box(x, 30, 146, 40, title=t, kind=kind, tsize=10.8, mono_title=True, rx=8)
        if i < len(boxes) - 1:
            s.line(x + 148, 50, x + 172, 50, color="#475569")
            s.text(x + 160, 42, vals[i], size=11, weight=800, mono=True, color="#b45309")
        x += 172
    s.text(8, 112, "An error jumps straight to .catch()", size=11.5, weight=800, color="#991b1b", anchor="start")
    row = [("resolve(1)", "green", None), ("then: throw", "red", None), ("then", "grey", "skipped"),
           ("then", "grey", "skipped"), (".catch(err)", "orange", None), ("then", "blue", "continues")]
    x = 8
    for i, (t, kind, note) in enumerate(row):
        dash = "5 4" if note == "skipped" else None
        s.box(x, 124, 100, 40, title=t, kind=kind, tsize=10.8, mono_title=True, rx=8, dash=dash)
        if note:
            s.text(x + 50, 180, note, size=9.5, italic=True, color=MUTED)
        if i < len(row) - 1:
            col = "#cbd2dd" if 1 <= i <= 3 else "#475569"
            s.line(x + 101, 144, x + 113, 144, color=col, sw=1.3)
        x += 114
    s.path("M 172 166 L 172 206 L 506 206 L 506 168", color="#dc4c4c", sw=1.8, dash="6 4")
    s.text(339, 224, "the error skips every .then() until it finds a .catch()", size=10, italic=True,
           color="#991b1b")
    s.text(339, 250, "After .catch() handles it, the chain continues normally.", size=10, italic=True,
           color=MUTED)
    return s.render()


@fig
def fetch_flow():
    s = Svg(680, 266, "ff")
    s.box(10, 24, 200, 134, title="Your JavaScript", body=["(in the browser)", "", "p1 = fetch(url)", "p1 is PENDING…"],
          kind="blue", tsize=13, bsize=10.5)
    s.box(470, 24, 200, 134, title="GitHub server", body=["api.github.com", "", "reads the request,", "sends back JSON text"],
          kind="grey", tsize=13, bsize=10.5)
    s.line(212, 64, 466, 64, color="#3f6fd6", sw=1.8)
    s.text(339, 56, "request:  GET /users", size=10.5, mono=True, weight=600, color="#1e3a8a")
    s.line(468, 118, 214, 118, color="#475569", sw=1.8)
    s.text(339, 110, "response:  status 200 + JSON text", size=10.5, mono=True, weight=600, color="#374151")
    s.text(339, 140, "(the internet trip takes time — JS keeps working)", size=9.6, italic=True, color=MUTED)
    s.box(10, 180, 322, 70, title="FULFILLED — the server replied",
          body=["p1 → Response → response.json() → data", "(even a 404 reply counts as “replied”!)"],
          kind="green", tsize=11.5, bsize=10)
    s.box(348, 180, 322, 70, title="REJECTED — no reply at all",
          body=["internet down · DNS failure", "server unreachable"], kind="red", tsize=11.5, bsize=10)
    return s.render()


@fig
def avatars_flow():
    s = Svg(680, 208, "af")
    s.box(6, 30, 96, 44, title="fetch(url)", kind="blue", tsize=10.5, mono_title=True, rx=8)
    s.line(104, 52, 124, 52, color="#475569")
    s.raw('<polygon points="190,20 256,52 190,84 124,52" fill="#fff6c7" stroke="#d9ae00" stroke-width="1.5"/>')
    s.text(190, 49, "response", size=10, mono=True, weight=700, color="#5c4a00")
    s.text(190, 62, ".ok ?", size=10, mono=True, weight=700, color="#5c4a00")
    s.line(256, 52, 290, 52, color="#26a05e")
    s.text(272, 44, "yes", size=9.5, weight=700, color="#14532d")
    s.box(292, 30, 118, 44, title="response.json()", kind="green", tsize=10, mono_title=True, rx=8)
    s.line(412, 52, 430, 52, color="#475569")
    s.box(432, 22, 118, 60, title="for each user:", body=["createElement('img')", "set src + 40px size"],
          kind="green", tsize=10, bsize=9, rx=8)
    s.line(552, 52, 570, 52, color="#475569")
    s.box(572, 30, 102, 44, title="parent.append", body=[], kind="green", tsize=10, mono_title=True, rx=8)
    s.text(623, 96, "30 avatars appear", size=9.8, italic=True, weight=700, color="#14532d")
    s.line(190, 84, 190, 124, color="#dc4c4c")
    s.text(200, 108, "no (404, 500…)", size=9.5, weight=700, color="#991b1b", anchor="start")
    s.box(110, 126, 160, 40, title="throw new Error(…)", kind="red", tsize=10, mono_title=True, rx=8)
    s.line(272, 146, 330, 146, color="#dc4c4c")
    s.box(332, 120, 250, 52, title=".catch(error => …)", body=["parent.textContent = error.message"],
          kind="orange", tsize=10.5, bsize=9.5, mono_title=True, rx=8)
    s.path("M 54 76 L 54 190 L 456 190 L 456 174", color="#dc4c4c", sw=1.5, dash="5 4")
    s.text(160, 202, "network error → fetch itself rejects", size=9.5, italic=True, color="#991b1b")
    return s.render()


# =====================================================================================
# Chapter 6 — JSON
# =====================================================================================
@fig
def json_journey():
    s = Svg(680, 212, "jj")
    s.box(6, 26, 124, 100, title="JS object", body=["(in memory)", "", "{ name: 'Rohit',", "  age: 30 }"],
          kind="blue", tsize=12.5, bsize=9.8)
    s.line(132, 76, 252, 76, color="#475569", sw=1.8)
    s.text(191, 66, "JSON.stringify()", size=9.8, mono=True, weight=700, color="#1e3a8a")
    s.box(256, 40, 186, 72, title="JSON text (a string)", body=['{"name":"Rohit","age":30}'],
          kind="yellow", tsize=12, bsize=9.8, mono_body=True)
    s.line(444, 76, 526, 76, color="#475569", sw=1.8)
    s.text(485, 62, "travels over", size=9.8, italic=True, color=MUTED)
    s.text(485, 96, "the network", size=9.8, italic=True, color=MUTED)
    s.box(530, 16, 144, 120, title="Any language", body=["C++  ·  Python", "Java  ·  Go", "JavaScript", "", "all can read JSON"],
          kind="green", tsize=12.5, bsize=9.8)
    s.path("M 602 138 L 602 168 L 68 168 L 68 130", color="#26a05e", sw=1.6, dash="6 4")
    s.text(338, 186, "the reply comes back as JSON text too", size=10, italic=True, color="#14532d")
    s.rich(338, 204, [("JSON.parse(text)", {"mono": True, "weight": 700}), ("  or  ", {"color": MUTED}),
                      ("await response.json()", {"mono": True, "weight": 700}), ("  →  a JS object again", {"color": MUTED})],
           size=10, anchor="middle")
    return s.render()


# =====================================================================================
# Chapter 7 — async / await
# =====================================================================================
@fig
def await_timeline():
    s = Svg(680, 196, "at")
    s.text(10, 56, "main code", size=11.5, weight=800, color="#1e3a8a", anchor="start")
    s.text(10, 126, "inside demo()", size=11.5, weight=800, color="#5b21b6", anchor="start")
    s.line(100, 30, 100, 150, color="#e2e6ee", sw=1, arrow=False)
    s.chip(112, 40, "1. before", kind="blue", size=10, mono=True, h=22)
    s.chip(222, 40, "demo()", kind="blue", size=10, mono=True, h=22)
    s.chip(350, 40, "3. after", kind="blue", size=10, mono=True, h=22)
    s.line(444, 51, 668, 51, color="#94a3b8", sw=1.5, dash="4 4", arrow=False)
    s.text(556, 36, "main code finished — the thread is free", size=9.5, italic=True, color=MUTED)
    s.line(246, 63, 246, 108, color="#475569", sw=1.4)
    s.text(238, 90, "calls", size=9.5, italic=True, color=MUTED, anchor="end")
    s.chip(200, 110, "2. started", kind="purple", size=10, mono=True, h=22)
    s.line(300, 110, 372, 64, color="#475569", sw=1.4)
    s.text(344, 100, "hits await → returns", size=9.5, italic=True, color=MUTED, anchor="start")
    s.text(344, 88, "", size=9.5)
    s.text(344, 113, "a pending Promise", size=9.5, italic=True, color=MUTED, anchor="start")
    s.rect(456, 110, 128, 22, fill="#f3f4f6", stroke="#9ca3af", sw=1.2, rx=11, dash="4 3")
    s.text(520, 125, "paused (1 s)", size=9.8, color="#374151", weight=600)
    s.chip(592, 110, "4. resumed", kind="green", size=10, mono=True, h=22)
    s.line(110, 168, 668, 168, color="#94a3b8", sw=1.1, arrow=False)
    for x, t in [(150, "0 ms"), (400, "≈ 1 ms"), (630, "1000 ms")]:
        s.line(x, 164, x, 172, color="#94a3b8", sw=1.1, arrow=False)
        s.text(x, 188, t, size=10, weight=600, color="#374151")
    return s.render()


@fig
def seq_vs_par():
    s = Svg(680, 206, "sp")
    x0, pxs = 150, 118

    def bar(y, start, dur, label, kind):
        fill, stroke, tc = KIND[kind]
        s.rect(x0 + start * pxs, y, dur * pxs, 20, fill=fill, stroke=stroke, sw=1.3, rx=6)
        s.text(x0 + (start + dur / 2) * pxs, y + 14, label, size=9.8, mono=True, weight=600, color=tc)

    s.text(8, 18, "Sequential — two awaits", size=11.5, weight=800, color="#7c2d12", anchor="start")
    s.text(140, 42, "await fetchUser()", size=9.8, mono=True, anchor="end")
    bar(28, 0, 2, "2 s", "orange")
    s.text(140, 68, "await fetchPosts()", size=9.8, mono=True, anchor="end")
    bar(54, 2, 2, "2 s", "orange")
    s.text(x0 + 4 * pxs + 8, 72, "≈ 4 s", size=12, weight=800, color="#7c2d12", anchor="start")
    s.text(8, 104, "Parallel — Promise.all([ … ])", size=11.5, weight=800, color="#14532d", anchor="start")
    s.text(140, 128, "fetchUser()", size=9.8, mono=True, anchor="end")
    bar(114, 0, 2, "2 s", "green")
    s.text(140, 154, "fetchPosts()", size=9.8, mono=True, anchor="end")
    bar(140, 0, 2, "2 s", "green")
    s.text(x0 + 2 * pxs + 8, 158, "≈ 2 s — both started together!", size=12, weight=800, color="#14532d", anchor="start")
    s.line(x0, 180, x0 + 4 * pxs, 180, color="#94a3b8", sw=1.1, arrow=False)
    for t in range(5):
        s.line(x0 + t * pxs, 176, x0 + t * pxs, 184, color="#94a3b8", sw=1.1, arrow=False)
        s.text(x0 + t * pxs, 199, f"{t} s", size=10, weight=600, color="#374151")
    return s.render()


@fig
def github_cards():
    s = Svg(680, 262, "gc")
    s.rect(0, 0, 680, 262, fill="#0b0b0b", stroke="#0b0b0b", sw=0, rx=12)
    s.text(340, 40, "Github User", size=22, weight=800, color="#ffffff")
    names = ["mojombo", "defunkt", "pjhyett", "wycats"]
    x = 44
    for i, n in enumerate(names):
        big = i == 3
        s.rect(x, 62, 130, 166, fill="#0b0b0b", stroke="#ffffff", sw=2.2 if big else 1.5, rx=5)
        s.rect(x + 10, 72, 110, 96, fill="#2a2f3a", stroke="#2a2f3a", sw=0, rx=2)
        s.circle(x + 65, 106, 17, fill="#566074", stroke="#566074", sw=0)
        s.path(f"M {x + 33} 168 C {x + 36} 136 {x + 94} 136 {x + 97} 168 Z", color="#566074", sw=0, arrow=False,
               fill="#566074")
        s.text(x + 65, 192, n, size=13, weight=700, color="#ffffff")
        s.text(x + 65, 214, "Visit Profile", size=11.5, weight=600, color="#f59e0b")
        x += 154
    s.text(628, 248, "hover → the card grows 1.2×", size=9.8, italic=True, color="#fde68a", anchor="end")
    s.text(44, 248, "… one card per user (30 in total), wrapping onto new rows", size=9.8, italic=True,
           color="#9ca3af", anchor="start")
    return s.render()


# =====================================================================================
# Chapter 8 — prototypes & classes
# =====================================================================================
@fig
def copies_vs_shared():
    s = Svg(680, 236, "cvs")
    s.rect(4, 4, 330, 228, fill="#fff8f8", stroke="#f1c0c0", sw=1.2, rx=12)
    s.text(169, 26, "Object literals: every object has a COPY", size=11.5, weight=800, color="#7f1d1d")
    for i, (nm, who) in enumerate([("user1", "'Alice'"), ("user2", "'Bob'")]):
        y = 42 + i * 88
        s.box(16, y, 140, 74, title=nm, body=[f"name: {who}", "score: …", "sayHi: ●"], kind="white", tsize=11.5,
              bsize=9.6, mono_body=True)
        s.box(200, y + 16, 122, 40, title=f"sayHi  copy #{i + 1}", kind="red", tsize=10.5, rx=8)
        s.line(140, y + 60, 198, y + 38, color="#dc4c4c", sw=1.4)
    s.text(169, 222, "user1.sayHi === user2.sayHi  →  false", size=10, mono=True, weight=700, color="#7f1d1d")
    s.rect(346, 4, 330, 228, fill="#f4fbf6", stroke="#b5dfc5", sw=1.2, rx=12)
    s.text(511, 26, "Prototype: ONE shared copy", size=11.5, weight=800, color="#14532d")
    for i, (nm, who) in enumerate([("user1", "'Alice'"), ("user2", "'Bob'")]):
        y = 42 + i * 88
        s.box(358, y, 132, 64, title=nm, body=[f"name: {who}", "score: …"], kind="white", tsize=11.5, bsize=9.6,
              mono_body=True)
    s.box(540, 66, 126, 96, title="shared object", body=["sayHi()", "increaseScore()"], kind="green", tsize=11,
          bsize=10, mono_body=True)
    s.line(492, 76, 536, 98, color="#26a05e", sw=1.4, dash="5 4")
    s.line(492, 160, 536, 136, color="#26a05e", sw=1.4, dash="5 4")
    s.text(603, 180, "[[Prototype]] links", size=9.5, mono=True, color="#14532d")
    s.text(511, 222, "user1.sayHi === user2.sayHi  →  true", size=10, mono=True, weight=700, color="#14532d")
    return s.render()


def _chain(s, y, items, h=80):
    """items: list of (x, w, title, body, kind); arrows with [[Prototype]] labels between them."""
    for i, (x, w, t, body, kind) in enumerate(items):
        if t == "null":
            s.chip(x, y + h / 2 - 11, "null", kind="grey", size=10.5, mono=True, h=22)
        else:
            s.box(x, y, w, h, title=t, body=body, kind=kind, tsize=11, bsize=9.6, mono_body=True, mono_title=True)
        if i < len(items) - 1:
            nx = items[i + 1][0]
            s.line(x + w + 3, y + h / 2, nx - 3, y + h / 2, color="#475569", sw=1.5)
            if nx - (x + w) >= 66:
                s.text((x + w + nx) / 2, y + h / 2 - 7, "[[Prototype]]", size=8.6, mono=True, color=MUTED)


@fig
def proto_chain():
    s = Svg(680, 212, "pch")
    _chain(s, 16, [(8, 140, "user1", ["name: 'Alice'", "score: 100"], "blue"),
                   (218, 150, "userFunctions", ["sayHi()", "increaseScore()"], "green"),
                   (438, 150, "Object.prototype", ["toString()", "hasOwnProperty()"], "grey"),
                   (624, 0, "null", [], "grey")])
    rows = [
        [("user1.sayHi()", {"mono": True, "weight": 700}), ("   ① not on user1   →   ② found on userFunctions  ✔", {})],
        [("user1.toString()", {"mono": True, "weight": 700}), ("   → found two steps up, on Object.prototype  ✔", {})],
        [("user1.fly", {"mono": True, "weight": 700}), ("   → not found anywhere, reached null  →  undefined", {})],
    ]
    for i, r in enumerate(rows):
        s.rich(14, 132 + i * 26, r, size=10.5)
    return s.render()


@fig
def builtin_chains():
    s = Svg(680, 196, "bic")
    _chain(s, 8, [(8, 150, "obj", ["name, age, greet"], "blue"),
                  (232, 170, "Object.prototype", ["toString()", "hasOwnProperty()"], "grey"),
                  (470, 0, "null", [], "grey")], h=72)
    _chain(s, 108, [(8, 150, "arr", ["[10, 20, 30]", "length: 3"], "blue"),
                    (232, 150, "Array.prototype", ["push() map()", "filter() …"], "yellow"),
                    (452, 150, "Object.prototype", ["toString() …"], "grey"),
                    (626, 0, "null", [], "grey")], h=72)
    return s.render()


@fig
def new_steps():
    s = Svg(680, 170, "nws")
    s.rich(340, 18, [("new User(\"Alice\", 100)", {"mono": True, "weight": 700}),
                     ("  does four things:", {"color": MUTED})], size=11.5, anchor="middle")
    steps = [("① create", ["a brand-new", "empty object  { }"], "grey"),
             ("② link", ["its [[Prototype]]", "→ User.prototype"], "green"),
             ("③ run User(...)", ["with this = new object", "→ { name: 'Alice',", "     score: 100 }"], "blue"),
             ("④ return it", ["user1 = that", "object"], "yellow")]
    x = 8
    for i, (t, body, kind) in enumerate(steps):
        s.box(x, 34, 152, 104, title=t, body=body, kind=kind, tsize=12, bsize=9.8)
        if i < 3:
            s.line(x + 154, 86, x + 168, 86, color="#475569", sw=1.5)
        x += 170
    s.text(340, 160, "(no magic: it's just an automated recipe)", size=10, italic=True, color=MUTED)
    return s.render()


@fig
def two_prototypes():
    s = Svg(680, 238, "twp")
    s.box(14, 24, 176, 62, title="User", body=["the constructor function", "(or class)"], kind="blue", tsize=13,
          bsize=9.8)
    s.box(414, 16, 254, 104, title="User.prototype", body=["sayHi()", "increaseScore()", "constructor → User"],
          kind="green", tsize=12, bsize=10, mono_title=True, mono_body=True)
    s.line(192, 46, 410, 46, color="#3f6fd6", sw=1.8)
    s.text(300, 38, ".prototype  (a property of the function)", size=9.6, mono=False, color="#1e3a8a", weight=600)
    s.line(410, 96, 192, 72, color="#26a05e", sw=1.3, dash="5 4")
    s.text(300, 104, "constructor  (points back)", size=9.4, color="#14532d", italic=True)
    for i, (nm, x) in enumerate([("user1", 150), ("user2", 330)]):
        s.box(x, 164, 136, 56, title=nm, body=["name, score"], kind="white", tsize=12, bsize=9.8, mono_body=True)
        s.line(x + 100 if i == 0 else x + 110, 162, 470 + i * 70, 122, color="#26a05e", sw=1.6)
    s.text(596, 156, "[[Prototype]]", size=9.6, mono=True, color="#14532d", weight=700)
    s.text(596, 170, "(user1.__proto__)", size=9.2, mono=True, color="#14532d")
    s.line(90, 88, 170, 162, color="#94a3b8", sw=1.3, dash="3 3")
    s.text(96, 136, "new User(…)", size=9.6, mono=True, color=MUTED, anchor="end")
    return s.render()


@fig
def extends_chain():
    s = Svg(680, 196, "exc")
    _chain(s, 14, [(4, 134, "c1", ["name: 'Mohan'", "age: 20", "account: 12", "balance: 540"], "blue"),
                   (162, 150, "Customer.prototype", ["checkBalance()", "constructor"], "orange"),
                   (336, 136, "Person.prototype", ["sayHi()", "constructor"], "green"),
                   (496, 128, "Object.prototype", ["toString() …"], "grey"),
                   (638, 0, "null", [], "grey")], h=96)
    s.rich(14, 150, [("c1.checkBalance()", {"mono": True, "weight": 700}),
                     ("  → found on Customer.prototype  → 540", {})], size=10.5)
    s.rich(14, 176, [("c1.sayHi()", {"mono": True, "weight": 700}),
                     ("  → not on Customer.prototype → found on Person.prototype (inherited!)", {})], size=10.5)
    return s.render()


# =====================================================================================
# Chapter 10 — this
# =====================================================================================
def _card(s, x, y, w, h, title, code, result, kind, result2=None):
    fill, stroke, tc = KIND[kind]
    s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=10)
    s.text(x + w / 2, y + 22, title, size=12, weight=800, color=tc)
    s.text(x + w / 2, y + 46, code, size=11, mono=True, weight=700, color="#1f2937")
    s.text(x + w / 2, y + 72, result, size=10.4, color="#1f2937", weight=600)
    if result2:
        s.text(x + w / 2, y + 88, result2, size=10.4, color="#1f2937", weight=600)


@fig
def this_rules():
    s = Svg(680, 226, "thr")
    _card(s, 4, 6, 162, 100, "1. Method call", "obj.fn()", "this = obj", "blue")
    _card(s, 176, 6, 162, 100, "2. Simple call", "fn()", "strict: undefined", "grey", "sloppy: window")
    _card(s, 348, 6, 162, 100, "3. Explicit", "fn.call(x)", "this = x", "purple", "(also apply, bind)")
    _card(s, 520, 6, 156, 100, "4. Constructor", "new Fn()", "this = the new", "green", "object")
    s.rect(4, 122, 672, 96, fill="#fff0e2", stroke="#e8792a", sw=1.6, rx=10)
    s.text(340, 148, "The exception: arrow functions   () => { … }", size=12.5, weight=800, color="#7c2d12")
    s.text(340, 174, "have NO own this — they use the this of the place where they are WRITTEN", size=11,
           weight=600, color="#1f2937")
    s.text(340, 198, "(the four rules above don't apply to them; call / apply / bind can't change it)", size=10,
           italic=True, color="#7c2d12")
    return s.render()


@fig
def arrow_scope():
    s = Svg(680, 250, "ars")
    s.rect(4, 6, 672, 238, fill="#eef4ff", stroke="#3f6fd6", sw=1.6, rx=14)
    s.rich(20, 32, [("start() ", {"mono": True, "weight": 700}),
                    ("— called as ", {"color": MUTED}), ("myWatch.start()", {"mono": True, "weight": 700}),
                    ("   →   this = myWatch", {"weight": 700, "color": "#1e3a8a"})], size=11.5)
    s.rect(20, 52, 310, 176, fill="#fff3f3", stroke="#dc4c4c", sw=1.5, rx=12)
    s.text(175, 76, "setInterval(function () { … })", size=11, mono=True, weight=700, color="#7f1d1d")
    s.text(175, 104, "a REGULAR function has its OWN this", size=10.5, weight=700, color="#1f2937")
    s.text(175, 124, "(a one-way mirror: it can't see outside)", size=10, italic=True, color=MUTED)
    s.text(175, 156, "setInterval calls it WITHOUT myWatch", size=10.2, color="#1f2937")
    s.text(175, 176, "→ this = window  (not myWatch!)", size=10.2, weight=700, color="#b91c1c")
    s.text(175, 206, "this.seconds++  →  NaN  ✘", size=10.5, mono=True, weight=700, color="#b91c1c")
    s.rect(350, 52, 310, 176, fill="#effcf4", stroke="#26a05e", sw=1.5, rx=12)
    s.text(505, 76, "setInterval(() => { … })", size=11, mono=True, weight=700, color="#14532d")
    s.text(505, 104, "an ARROW function has NO own this", size=10.5, weight=700, color="#1f2937")
    s.text(505, 124, "(transparent glass: it sees the room it's in)", size=10, italic=True, color=MUTED)
    s.text(505, 156, "it looks outward, to start()", size=10.2, color="#1f2937")
    s.text(505, 176, "→ this = myWatch", size=10.2, weight=700, color="#15803d")
    s.text(505, 206, "this.seconds++  →  1, 2, 3 …  ✔", size=10.5, mono=True, weight=700, color="#15803d")
    s.path("M 505 52 C 505 38 470 30 404 30", color="#26a05e", sw=1.6, dash="5 3")
    s.text(516, 44, "looks outward", size=9.6, italic=True, weight=700, color="#15803d", anchor="start")
    return s.render()


@fig
def this_flowchart():
    s = Svg(680, 384, "thf")
    qs = [("Is it an arrow function?", "this = the this of the code around it", "(where it is written)", "orange"),
          ("Called with new?", "this = the brand-new object", "new Person(…)", "green"),
          ("call / apply / bind used?", "this = the object you passed", "fn.call(obj)", "purple"),
          ("Called with a dot?  obj.fn()", "this = obj  (left of the dot)", "person.speak()", "blue")]
    y = 8
    for i, (q, a, ex, kind) in enumerate(qs):
        s.box(8, y, 262, 48, title=q, kind="white", tsize=11.5, rx=10)
        s.line(272, y + 24, 366, y + 24, color="#26a05e", sw=1.6)
        s.text(318, y + 17, "yes", size=10, weight=800, color="#15803d")
        s.box(370, y, 302, 48, title=a, body=[ex], kind=kind, tsize=11, bsize=9.6, mono_body=True, rx=10)
        s.line(139, y + 50, 139, y + 70, color="#dc4c4c", sw=1.5)
        s.text(148, y + 64, "no", size=10, weight=800, color="#b91c1c", anchor="start")
        y += 72
    s.box(8, y, 262, 60, title="None of these:", body=["a plain call  fn()"], kind="grey", tsize=11.5, bsize=10.5,
          rx=10)
    s.line(272, y + 18, 366, y + 8, color="#475569", sw=1.4)
    s.line(272, y + 42, 366, y + 52, color="#475569", sw=1.4)
    s.box(370, y - 12, 302, 38, title="'use strict'  →  undefined", kind="grey", tsize=11, rx=10, mono_title=False)
    s.box(370, y + 34, 302, 38, title="sloppy  →  window / global", kind="grey", tsize=11, rx=10)
    return s.render()


# =====================================================================================
# Chapter 11 — revision
# =====================================================================================
@fig
def big_picture():
    s = Svg(680, 300, "bp")
    s.text(8, 18, "Story 1 — how JavaScript handles waiting", size=12, weight=800, color="#16213e", anchor="start")
    row1 = [("Event loop", "one thread + queues", "Ch 3", "blue"),
            ("Callbacks", "“call me back”", "Ch 4", "yellow"),
            ("Callback hell", "nested pyramid", "Ch 4", "red"),
            ("Promises", "flat .then chain", "Ch 5", "green"),
            ("async / await", "reads like sync", "Ch 7", "purple")]
    x = 4
    for i, (t, b, ch, kind) in enumerate(row1):
        s.box(x, 30, 122, 66, title=t, body=[b, ch], kind=kind, tsize=11.5, bsize=9.6)
        if i < 4:
            s.line(x + 124, 63, x + 136, 63, color="#475569", sw=1.5)
        x += 138
    s.box(418, 112, 160, 44, title="JSON  (Ch 6)", body=["the data fetch brings"], kind="teal", tsize=11,
          bsize=9.4)
    s.line(476, 110, 476, 98, color="#14a39a", sw=1.3, dash="3 3")
    s.text(8, 188, "Story 2 — how objects share behaviour, and how this finds the object", size=12, weight=800,
           color="#16213e", anchor="start")
    row2 = [("Objects", "bags of key: value", "Ch 0–2", "white"),
            ("Prototype chain", "shared methods", "Ch 8", "green"),
            ("Classes", "sugar over prototypes", "Ch 8", "orange"),
            ("this", "decided by the call", "Ch 10", "blue"),
            ("Arrow functions", "borrow outer this", "Ch 10", "purple")]
    x = 4
    for i, (t, b, ch, kind) in enumerate(row2):
        s.box(x, 200, 122, 66, title=t, body=[b, ch], kind=kind, tsize=11.5, bsize=9.6)
        if i < 4:
            s.line(x + 124, 233, x + 136, 233, color="#475569", sw=1.5)
        x += 138
    s.chip(418 - 6, 276, "Strict mode (Ch 9) changes plain-call this", kind="grey", size=9.6, h=20, weight=600)
    s.line(482, 274, 482, 268, color="#94a3b8", sw=1.2, arrow=True)
    return s.render()
