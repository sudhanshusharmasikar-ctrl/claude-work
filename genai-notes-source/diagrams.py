"""All diagrams used in the GenAI notes. Each function returns an <svg> string."""
from svg import Svg, KIND, INK, MUTED, text_width

FIGS = {}


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


# ------------------------------------------------------------------ helpers
def hchain(s, x, y, items, w=110, h=46, gap=34, kind="white", tsize=11.5, bsize=10, color="#475569",
           labels=None, lsize=9.5):
    """Draw boxes left→right joined by arrows. items = [(title, [body...], kind?)]."""
    xs = []
    for i, it in enumerate(items):
        title, body = it[0], it[1] if len(it) > 1 else []
        k = it[2] if len(it) > 2 else kind
        bw = it[3] if len(it) > 3 else w
        s.box(x, y, bw, h, title=title, body=body, kind=k, tsize=tsize, bsize=bsize)
        xs.append((x, bw))
        if i < len(items) - 1:
            s.line(x + bw + 4, y + h / 2, x + bw + gap - 4, y + h / 2, color=color)
            if labels and labels[i]:
                s.text(x + bw + gap / 2, y + h / 2 - 7, labels[i], size=lsize, color=MUTED, italic=True)
        x += bw + gap
    return xs


def vchain(s, x, y, items, w=160, h=40, gap=26, kind="white", tsize=11.5, bsize=10, color="#475569",
           labels=None, lsize=9.5):
    ys = []
    for i, it in enumerate(items):
        title, body = it[0], it[1] if len(it) > 1 else []
        k = it[2] if len(it) > 2 else kind
        bh = it[3] if len(it) > 3 else h
        s.box(x, y, w, bh, title=title, body=body, kind=k, tsize=tsize, bsize=bsize)
        ys.append((y, bh))
        if i < len(items) - 1:
            s.line(x + w / 2, y + bh + 3, x + w / 2, y + bh + gap - 3, color=color)
            if labels and labels[i]:
                s.text(x + w / 2 + 8, y + bh + gap / 2 + 4, labels[i], size=lsize, color=MUTED,
                       italic=True, anchor="start")
        y += bh + gap
    return ys


def bar(s, x, y, w, h, frac, fill, bg="#eef1f6"):
    s.rect(x, y, w, h, fill=bg, stroke=bg, sw=0.5, rx=3)
    if frac > 0:
        s.rect(x, y, max(2, w * frac), h, fill=fill, stroke=fill, sw=0.5, rx=3)


def panel(s, x, y, w, h, title, kind="grey", tsize=12):
    fill, stroke, tcol = KIND[kind]
    s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, rx=12)
    if title:
        s.text(x + w / 2, y + 20, title, size=tsize, weight=700, color=tcol)


# =====================================================================================
# Chapter 1 — how LLMs work
# =====================================================================================
@fig
def next_token():
    s = Svg(680, 250, "ntok")
    # input sentence
    s.text(16, 26, "Step 1: the model reads all tokens so far", size=11, weight=700, anchor="start", color="#1e3a8a")
    toks = ["The", " capital", " of", " France", " is"]
    x = 16
    for t in toks:
        w = text_width(t, 11.5, mono=True) + 14
        s.box(x, 38, w, 30, title=t, kind="blue", tsize=11.5, mono_title=True, rx=6)
        x += w + 5
    s.line(x + 4, 53, x + 40, 53)
    s.box(x + 44, 30, 96, 46, title="LLM", body=["billions of", "weights"], kind="navy", tsize=13, bsize=9.5)
    mx = x + 44 + 96
    # probabilities
    s.text(mx + 20, 26, "Step 2: a probability for every token", size=11, weight=700, anchor="start",
           color="#1e3a8a")
    probs = [(" Paris", 0.92), (" Lyon", 0.03), (" a", 0.02), (" the", 0.01)]
    py = 40
    for t, p in probs:
        s.text(mx + 20, py + 10, t, size=10.5, mono=True, anchor="start")
        bar(s, mx + 78, py + 1, 110, 12, p, "#8b5cf6" if p > 0.5 else "#c4b5fd")
        s.text(mx + 196, py + 11, f"{p:.2f}", size=10, mono=True, anchor="start", color=MUTED)
        py += 18
    s.line(mx + 4, 53, mx + 16, 53, arrow=False)
    # step 3 pick + append
    s.text(16, 132, "Step 3: pick one token (usually a likely one), APPEND it, and repeat", size=11, weight=700,
           anchor="start", color="#1e3a8a")
    x = 16
    for t in toks + [" Paris"]:
        w = text_width(t, 11.5, mono=True) + 14
        s.box(x, 144, w, 30, title=t, kind="green" if t == " Paris" else "blue", tsize=11.5, mono_title=True,
              rx=6)
        x += w + 5
    s.text(x + 8, 164, "→ predict again → \".\" → predict again → <end>", size=11, anchor="start", color=INK,
           mono=True)
    # loop arrow
    s.path("M 600 178 C 640 215, 470 232, 330 222", color="#8b5cf6", dash="5 4")
    s.text(470, 244, "one token at a time — this loop IS text generation", size=10, italic=True, color="#5b21b6")
    return s.render()


@fig
def stateless():
    s = Svg(680, 262, "stls")
    s.text(340, 18, "The API remembers NOTHING between calls — your code sends the whole history each time",
           size=11, weight=700, color="#1e3a8a")
    calls = [
        ("Call 1", [("user", "My name is Rohit")]),
        ("Call 2", [("user", "My name is Rohit"), ("model", "Nice to meet you, Rohit!"), ("user", "What is my name?")]),
    ]
    # left: without history
    panel(s, 8, 32, 318, 222, "Without history ❌", "red", 12)
    s.box(22, 62, 200, 30, title="user: What is my name?", kind="white", tsize=10.5, mono_title=True, rx=6)
    s.line(226, 77, 262, 77)
    s.box(266, 58, 50, 38, title="LLM", kind="navy", tsize=12)
    s.box(22, 118, 290, 34, title='model: "I don\'t know your name."', kind="white", tsize=10.5, mono_title=True,
          rx=6)
    s.lines(167, 180, ["Each call is a fresh start.", "The model never saw", "\"My name is Rohit\"."],
            size=10.5, color="#7f1d1d", italic=True)
    # right: with history
    panel(s, 346, 32, 326, 222, "With history ✅ (Lecture 2 idea)", "green", 12)
    rows = [("user", "My name is Rohit"), ("model", "Nice to meet you, Rohit!"), ("user", "What is my name?")]
    y = 68
    for role, t in rows:
        kind = "blue" if role == "user" else "purple"
        s.box(358, y, 218, 26, title=f"{role}: {t}", kind=kind, tsize=10, mono_title=True, rx=6, align="start")
        y += 31
    s.rect(352, 63, 230, 98, fill="none", stroke="#26a05e", sw=1.3, rx=8, dash="5 4")
    s.text(467, 175, "whole array = contents", size=9.5, italic=True, color="#14532d")
    s.line(586, 112, 606, 112)
    s.box(610, 93, 52, 38, title="LLM", kind="navy", tsize=12)
    s.box(358, 188, 304, 30, title='model: "Your name is Rohit!"', kind="white", tsize=10.5, mono_title=True,
          rx=6)
    s.text(510, 240, "then push this answer into the array too", size=9.5, italic=True, color="#14532d")
    return s.render()


@fig
def token_growth():
    s = Svg(680, 250, "tokg")
    s.text(340, 18, "Input tokens you pay for on each call of a chat (example numbers)", size=11.5, weight=700,
           color="#1e3a8a")
    calls = [("Call 1", 100, 0, 2, 20), ("Call 2", 100, 22, 3, 50), ("Call 3", 100, 75, 5, 60),
             ("Call 4", 100, 140, 4, 55)]
    colors = {"sys": "#8b5cf6", "hist": "#60a5fa", "msg": "#34d399", "out": "#fbbf24"}
    base_y, scale, bw = 214, 0.62, 70
    x = 70
    for name, sys, hist, msg, out in calls:
        y = base_y
        for val, key in ((sys, "sys"), (hist, "hist"), (msg, "msg")):
            h = val * scale
            if h > 0:
                s.rect(x, y - h, bw, h, fill=colors[key], stroke="#ffffff", sw=1, rx=2)
            y -= h
        s.text(x + bw / 2, y - 6, f"{sys + hist + msg} in", size=10.5, weight=700, mono=True)
        # output bar beside
        h = out * scale
        s.rect(x + bw + 6, base_y - h, 26, h, fill=colors["out"], stroke="#fff", sw=1, rx=2)
        s.text(x + bw + 19, base_y - h - 5, f"{out}", size=9, mono=True, color="#92400e")
        s.text(x + bw / 2 + 16, base_y + 16, name, size=10.5, weight=600)
        x += 140
    s.line(56, base_y, 640, base_y, arrow=False, color="#9ca3af", sw=1)
    ly = 36
    for label, key in (("system instruction (sent EVERY call)", "sys"), ("old history (grows)", "hist"),
                       ("new message", "msg"), ("output tokens (often priced higher)", "out")):
        s.rect(62, ly, 12, 12, fill=colors[key], stroke=colors[key], sw=1, rx=2)
        s.text(80, ly + 10, label, size=9.5, anchor="start", color=INK)
        ly += 17
    return s.render()


# =====================================================================================
# Chapter 2 — neural networks
# =====================================================================================
@fig
def neuron():
    s = Svg(680, 190, "neur")
    s.box(20, 30, 120, 42, title="study = 3", kind="blue", tsize=12, mono_title=True)
    s.box(20, 110, 120, 42, title="sleep = 2", kind="blue", tsize=12, mono_title=True)
    s.circle(330, 91, 44, fill="#f1eaff", stroke="#8b5cf6", sw=2)
    s.text(330, 88, "Σ + b", size=15, weight=700, color="#4c1d95")
    s.text(330, 106, "b = 1", size=10.5, mono=True, color="#4c1d95")
    s.line(144, 51, 288, 80, color="#475569")
    s.line(144, 131, 288, 102, color="#475569")
    s.chip(196, 44, "× w1 = 15", kind="yellow", size=10.5, mono=True)
    s.chip(196, 118, "× w2 = 2", kind="yellow", size=10.5, mono=True)
    s.line(376, 91, 460, 91, color="#475569")
    s.box(464, 66, 196, 50, title="predicted = 50", body=["15×3 + 2×2 + 1"], kind="green", tsize=12.5,
          bsize=10.5, mono_title=True)
    s.text(562, 140, "actual marks = 25  →  error = −25", size=11, weight=600, color="#b91c1c")
    s.text(562, 160, "so all weights get nudged down", size=10, italic=True, color=MUTED)
    s.text(330, 176, "marks = w1·study + w2·sleep + b", size=11.5, mono=True, color="#1e3a8a", weight=600)
    return s.render()


def _plot_axes(s, x0, y0, w, h, xmax, ymax, xt, yt, xlabel="x", ylabel="y"):
    s.line(x0, y0, x0 + w + 8, y0, color="#6b7280", sw=1.2)
    s.line(x0, y0, x0, y0 - h - 8, color="#6b7280", sw=1.2)
    for v in xt:
        px = x0 + v / xmax * w
        s.line(px, y0, px, y0 + 4, arrow=False, color="#6b7280", sw=1)
        s.text(px, y0 + 15, str(v), size=9, color=MUTED)
    for v in yt:
        py = y0 - v / ymax * h
        s.line(x0 - 4, py, x0, py, arrow=False, color="#6b7280", sw=1)
        s.text(x0 - 7, py + 3, str(v), size=9, color=MUTED, anchor="end")
    s.text(x0 + w + 12, y0 + 4, xlabel, size=10, color=MUTED, anchor="start", italic=True)
    s.text(x0, y0 - h - 14, ylabel, size=10, color=MUTED, italic=True)

    def P(xv, yv):
        return x0 + xv / xmax * w, y0 - yv / ymax * h
    return P


@fig
def relu_sum():
    s = Svg(680, 250, "relu")
    # left plot: ramp
    s.text(165, 18, "ReLU(x − 10) − ReLU(x − 30)", size=11.5, weight=700, mono=True, color="#4c1d95")
    P = _plot_axes(s, 40, 210, 250, 150, 40, 25, [0, 10, 20, 30, 40], [0, 10, 20])
    relu = lambda v: max(0.0, v)
    pts = [P(x, relu(x - 10)) for x in (0, 10, 40)]
    s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in [P(x, min(relu(x - 10), 25)) for x in (0, 10, 35)]),
           color="#93c5fd", dash="4 3", arrow=False, sw=1.4)
    s.text(P(24, 20)[0] - 4, P(24, 20)[1] - 6, "ReLU(x−10) alone", size=9, color="#2563eb", anchor="end")
    ramp = [P(x, relu(x - 10) - relu(x - 30)) for x in (0, 10, 30, 40)]
    s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in ramp), color="#7c3aed", sw=2.6, arrow=False)
    s.text(P(20, 14)[0] - 6, P(20, 14)[1], "rises 10→30", size=9.5, color="#4c1d95", anchor="end")
    s.text(P(35, 20)[0], P(35, 20)[1] + 16, "then flat at 20", size=9.5, color="#4c1d95")
    # right plot: x^2 via relus
    s.text(505, 18, "y = x² built from ReLUs", size=11.5, weight=700, color="#14532d")
    P2 = _plot_axes(s, 380, 210, 250, 150, 5, 25, [0, 1, 2, 3, 4, 5], [0, 5, 10, 15, 20, 25])
    curve = [P2(x / 10, (x / 10) ** 2) for x in range(0, 51)]
    s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in curve), color="#9ca3af", sw=1.4, arrow=False,
           dash="3 3")
    poly = [P2(x, x * x) for x in range(0, 6)]
    s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in poly), color="#059669", sw=2.4, arrow=False)
    for (a, b), x in zip(poly, range(6)):
        s.circle(a, b, 3.2, fill="#059669", stroke="#fff", sw=1)
    slopes = ["slope 1", "3", "5", "7", "9"]
    for i in range(5):
        (a1, b1), (a2, b2) = poly[i], poly[i + 1]
        dy = -8 if i == 0 else 12
        s.text((a1 + a2) / 2 + 10, (b1 + b2) / 2 + dy, slopes[i], size=9, color="#065f46", anchor="start")
    s.text(505, 240, "each new ReLU adds +2 to the slope → the kinks follow the curve", size=9.5, italic=True,
           color=MUTED)
    return s.render()


@fig
def transformer_mini():
    s = Svg(680, 268, "trf")
    toks = ["The", " cat", " sat", " because", " it"]
    x = 22
    for t in toks:
        w = text_width(t, 11, mono=True) + 14
        s.box(x, 22, w, 28, title=t, kind="blue", tsize=11, mono_title=True, rx=6)
        x += w + 5
    s.text(x + 6, 41, "token ids", size=10, italic=True, color=MUTED, anchor="start")
    s.line(150, 54, 150, 74)
    s.box(20, 78, 260, 36, title="Embedding + position", body=[], kind="purple", tsize=11.5)
    s.line(150, 118, 150, 136)
    s.rect(20, 140, 260, 88, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=10, dash="5 4")
    s.box(34, 150, 232, 30, title="Self-attention (look back at earlier tokens)", kind="green", tsize=10.5)
    s.box(34, 188, 232, 30, title="Feed-forward network (per token)", kind="orange", tsize=10.5)
    s.text(292, 188, "× N blocks", size=11, weight=700, color="#334155", anchor="start")
    s.line(150, 232, 150, 246)
    s.box(20, 248 - 0, 260, 18, title="", kind="white")
    s.text(150, 261, "scores → softmax → next-token probabilities", size=10, weight=600, color="#1e3a8a")
    # attention illustration
    s.text(500, 30, "Attention for the token \"it\"", size=11.5, weight=700, color="#14532d")
    words = ["The", "cat", "sat", "because", "it"]
    ws = [0.05, 0.62, 0.08, 0.10, 0.15]
    y = 50
    for wd, wt in zip(words, ws):
        s.text(430, y + 11, wd, size=11, mono=True, anchor="end")
        bar(s, 440, y + 1, 170, 13, wt / 0.62 * 0.95, "#10b981" if wt > 0.5 else "#a7f3d0")
        s.text(618, y + 12, f"{wt:.2f}", size=10, mono=True, color=MUTED, anchor="start")
        y += 24
    s.lines(500, 188, ["\"it\" attends mostly to \"cat\",", "so its new vector carries", "the meaning \"the cat\"."],
            size=10.5, italic=True, color="#14532d")
    return s.render()


# =====================================================================================
# Chapter 3 — function calling
# =====================================================================================
def seq(s, lanes, top, bottom, msgs, row_h=34, start_y=None, lsize=10):
    """Sequence diagram. lanes = [(x, title, kind)], msgs = [(from_i, to_i, label, color)]."""
    for x, title, kind in lanes:
        s.box(x - 62, top, 124, 34, title=title, kind=kind, tsize=11.5)
        s.line(x, top + 36, x, bottom, arrow=False, color="#cbd5e1", sw=1.4, dash="4 4")
    y = start_y or top + 62
    ys = []
    for i, (a, b, label, color) in enumerate(msgs):
        xa, xb = lanes[a][0], lanes[b][0]
        d = 1 if xb > xa else -1
        s.line(xa + 5 * d, y, xb - 7 * d, y, color=color, sw=1.7)
        cx = xa + 14 * d
        s.circle(cx, y - 11, 8, fill=color, stroke=color, sw=1)
        s.text(cx, y - 7.5, str(i + 1), size=9, weight=700, color="#ffffff")
        tw = text_width(label, lsize, mono=True)
        mid = (xa + xb) / 2
        if d > 0:
            left = max(mid - tw / 2, cx + 12)
        else:
            left = min(mid - tw / 2, cx - 12 - tw)
        s.text(left, y - 6, label, size=lsize, color=INK, mono=True, anchor="start")
        ys.append(y)
        y += row_h
    return ys


@fig
def fc_sequence():
    s = Svg(680, 330, "fcs")
    lanes = [(70, "User", "grey"), (250, "Your code", "blue"), (450, "Gemini", "navy"), (610, "Tool (API)", "orange")]
    msgs = [
        (0, 1, '"bitcoin price?"', "#6b7280"),
        (1, 2, "history + tools", "#2563eb"),
        (2, 1, "functionCall", "#7c3aed"),
        (1, 3, "fetch(CoinGecko)", "#ea580c"),
        (3, 1, "JSON { price }", "#ea580c"),
        (1, 2, "+ functionResponse", "#2563eb"),
        (2, 1, 'text answer', "#7c3aed"),
        (1, 0, "print answer", "#6b7280"),
    ]
    ys = seq(s, lanes, 8, 322, msgs, row_h=34, start_y=74)
    # loop bracket between the User and Your-code lanes
    x = 176
    s.path(f"M {x + 8} {ys[1] - 14} L {x} {ys[1] - 14} L {x} {ys[5] + 4} L {x + 8} {ys[5] + 4}", color="#8b5cf6",
           sw=1.6, arrow=False)
    s.lines(x - 6, (ys[1] + ys[5]) / 2 - 10, ["agent loop:", "repeat until", "the model", "answers in text"],
            size=9.5, italic=True, color="#5b21b6", anchor="end")
    return s.render()


# =====================================================================================
# Chapter 4 — computer-using agents
# =====================================================================================
@fig
def reviewer_flow():
    s = Svg(680, 170, "revf")
    items = [
        ("list_files", ["(\"../tester\")"], "blue", 112),
        ("read_file", ["one file"], "blue", 104),
        ("model thinks", ["bugs? security?", "bad practice?"], "purple", 124),
        ("write_file", ["fixed content"], "orange", 112),
        ("final text", ["📊 report"], "green", 104),
    ]
    xs = hchain(s, 12, 40, items, h=58, gap=24, tsize=12, bsize=10)
    # loop back from write_file to read_file
    wx, ww = xs[3]
    rx, rw = xs[1]
    s.path(f"M {wx + ww / 2} 102 C {wx + ww / 2} 146, {rx + rw / 2} 146, {rx + rw / 2} 104", color="#7c3aed",
           dash="5 4")
    s.text((wx + rx + ww / 2 + rw / 2) / 2, 160, "next file (one tool call per loop round)", size=10,
           italic=True, color="#5b21b6")
    s.text(340, 22, "Every arrow = one round of the agent loop: model asks → our code runs the tool → result goes back",
           size=10.5, weight=600, color="#1e3a8a")
    return s.render()


# =====================================================================================
# Chapter 5 — agent design
# =====================================================================================
def _mini(s, x, y, w, h, title, t, kind="blue"):
    s.box(x, y, w, h, title=t, kind=kind, tsize=10, rx=7)


@fig
def patterns():
    s = Svg(680, 322, "pat")
    # panel frames
    P = [(6, 6, 220, 150, "1 · Prompt chaining"), (232, 6, 220, 150, "2 · Routing"),
         (458, 6, 216, 150, "3 · Parallelisation"), (6, 164, 334, 152, "4 · Orchestrator–workers"),
         (346, 164, 328, 152, "5 · Evaluator–optimiser")]
    for x, y, w, h, t in P:
        s.rect(x, y, w, h, fill="#fbfcfe", stroke="#d7dce6", sw=1.1, rx=10)
        s.text(x + 10, y + 19, t, size=11, weight=700, anchor="start", color="#1e3a8a")
    # 1 chaining
    _mini(s, 16, 60, 54, 30, "", "LLM 1")
    s.line(72, 75, 92, 75)
    s.circle(104, 75, 11, fill="#e2f7ea", stroke="#26a05e")
    s.text(104, 79, "✓", size=11, weight=700, color="#14532d")
    s.line(116, 75, 136, 75)
    _mini(s, 138, 60, 54, 30, "", "LLM 2")
    s.text(104, 110, "gate: code checks the output", size=9, italic=True, color=MUTED)
    s.text(104, 124, "before the next call", size=9, italic=True, color=MUTED)
    s.line(193, 75, 214, 75)
    # 2 routing
    _mini(s, 242, 64, 66, 30, "", "Router", "purple")
    for i, (lbl, yy) in enumerate((("graph", 40), ("similar", 84), ("other", 128))):
        s.line(310, 79, 360, yy + 13)
        _mini(s, 362, yy, 80, 26, "", f"handler {lbl}")
    # 3 parallel
    for i, yy in enumerate((34, 72, 110)):
        s.line(476, 87, 496, yy + 13)
        _mini(s, 498, yy, 60, 26, "", f"LLM {'abc'[i]}")
        s.line(560, yy + 13, 590, 87)
    s.circle(470, 87, 5, fill="#475569", stroke="#475569")
    _mini(s, 592, 72, 74, 30, "", "combine", "green")
    s.text(566, 150, "sectioning or voting", size=9, italic=True, color=MUTED)
    # 4 orchestrator
    _mini(s, 16, 214, 100, 36, "", "Orchestrator", "purple")
    for i, yy in enumerate((190, 230, 270)):
        s.line(118, 232, 150, yy + 13)
        _mini(s, 152, yy, 74, 26, "", f"worker {i + 1}")
        s.line(228, yy + 13, 250, 232)
    _mini(s, 252, 216, 80, 32, "", "synthesise", "green")
    s.text(74, 296, "tasks decided at run time", size=9, italic=True, color=MUTED)
    # 5 evaluator-optimiser
    _mini(s, 366, 206, 96, 34, "", "Generator", "blue")
    _mini(s, 548, 206, 96, 34, "", "Evaluator", "orange")
    s.path("M 464 216 C 500 196, 512 196, 546 216", color="#2563eb")
    s.text(505, 196, "draft", size=9.5, color="#1e3a8a")
    s.path("M 546 234 C 512 256, 500 256, 464 234", color="#ea580c")
    s.text(505, 266, "feedback", size=9.5, color="#9a3412")
    s.line(596, 242, 596, 280)
    s.text(596, 296, "accepted → output", size=9.5, color="#14532d", weight=600)
    return s.render()


@fig
def mcp_arch():
    s = Svg(680, 262, "mcp")
    s.rect(8, 10, 218, 222, fill="#f1eaff", stroke="#8b5cf6", sw=1.4, rx=12)
    s.text(117, 32, "HOST (AI app)", size=12, weight=700, color="#4c1d95")
    s.text(117, 48, "IDE · desktop assistant · your agent", size=9, color="#4c1d95", italic=True)
    s.box(24, 58, 186, 34, title="LLM + app logic", kind="navy", tsize=11)
    servers = [("GitHub server", "GitHub API"), ("Postgres server", "Database"), ("Files server", "Your disk")]
    for i, (srv, ext) in enumerate(servers):
        y = 108 + i * 42
        s.box(34, y, 150, 32, title=f"MCP client {i + 1}", kind="white", tsize=10.5)
        s.line(186, y + 16, 300, y + 16, start_arrow=True, color="#475569")
        s.box(304, y - 5, 170, 42, title=srv, body=["tools · resources · prompts"], kind="blue", tsize=10.5,
              bsize=9)
        s.line(476, y + 16, 530, y + 16, start_arrow=True, color="#94a3b8")
        s.box(534, y, 130, 32, title=ext, kind="grey", tsize=10.5)
    s.text(263, 98, "JSON-RPC 2.0", size=9.5, weight=700, color="#334155")
    s.text(340, 254, "messages: JSON-RPC 2.0  ·  transport: stdio (local) or HTTP (remote)  ·  one server per system",
           size=9.5, italic=True, color=MUTED)
    return s.render()


# =====================================================================================
# Chapter 6 — embeddings
# =====================================================================================
@fig
def movie_map():
    s = Svg(680, 300, "mmap")
    cx, cy, sx, sy = 250, 150, 17, 11.5
    s.line(cx - 10.6 * sx, cy, cx + 10.8 * sx, cy, color="#94a3b8", sw=1.2)
    s.line(cx, cy + 10.8 * sy, cx, cy - 10.8 * sy, color="#94a3b8", sw=1.2)
    s.text(cx + 10.8 * sx - 2, cy + 18, "more ACTION →", size=10, color=MUTED, anchor="end", italic=True)
    s.text(cx - 10.6 * sx + 2, cy + 18, "← peaceful", size=10, color=MUTED, anchor="start", italic=True)
    s.text(cx + 8, cy - 10.8 * sy + 8, "more COMEDY ↑", size=10, color=MUTED, anchor="start", italic=True)
    s.text(cx + 8, cy + 10.8 * sy - 2, "serious ↓", size=10, color=MUTED, anchor="start", italic=True)
    P = lambda x, y: (cx + x * sx, cy - y * sy)
    pts = [
        ("Dhamaal", 2.2, 8.8, "#f59e0b", (9, 4, "start")),
        ("Hera Pheri", -1.4, 7.0, "#f59e0b", (-9, 4, "end")),
        ("Jab We Met", -6.4, 8.6, "#f59e0b", (-9, 4, "end")),
        ("3 Idiots", -4.6, 4.8, "#f59e0b", (-9, 4, "end")),
        ("Lagaan", -2.0, -4.6, "#8b5cf6", (9, 0, "start")),
        ("Taare Zameen Par", -3.4, -6.0, "#8b5cf6", (-9, 6, "end")),
        ("Dangal", -1.0, -7.8, "#8b5cf6", (9, 5, "start")),
        ("Swades", -7.4, -3.6, "#8b5cf6", (-9, 4, "end")),
        ("Sholay", 8.0, 5.0, "#ef4444", (-9, 4, "end")),
        ("Pathaan", 9.6, -2.4, "#ef4444", (-9, 4, "end")),
        ("War", 10.0, -5.2, "#ef4444", (-9, 4, "end")),
    ]
    for name, x, y, col, (dx, dy, anc) in pts:
        px, py = P(x, y)
        s.circle(px, py, 5.5, fill=col, stroke="#ffffff", sw=1.4)
        s.text(px + dx, py + dy, name, size=10.5, weight=600, anchor=anc)
    lx, ly = P(-2.7, -5.3)
    s.circle(lx, ly, 22, fill="none", stroke="#7c3aed", sw=1.5)
    s.path(f"M {lx + 12} {ly + 19} C {lx + 60} {ly + 70}, {cx + 230} {cy + 120}, {cx + 236} {cy + 92}",
           color="#7c3aed", dash="4 3")
    s.lines(cx + 200, cy + 60, ["Lagaan and Taare Zameen Par", "look almost the same in 2-D", "→ add more dimensions"],
            size=10, italic=True, color="#5b21b6", anchor="start")
    s.text(P(-4, 11.3)[0], P(-4, 11.3)[1], "comedy blob", size=10, weight=700, color="#b45309")
    s.text(P(8.5, 8.8)[0], P(8.5, 8.8)[1], "action", size=10, weight=700, color="#b91c1c")
    s.text(P(-5, -10.2)[0], P(-5, -10.2)[1], "serious-drama blob", size=10, weight=700, color="#5b21b6")
    s.lines(560, 40, ["Each movie =", "[action, comedy]", "", "Dhamaal ≈ [2, 9]", "War ≈ [10, −5]"],
            size=10.5, color="#334155", anchor="start", mono=False)
    return s.render()


@fig
def cos_vs_euc():
    s = Svg(680, 250, "cve")
    ox, oy = 70, 226
    import math
    def pt(angle, length):
        a = math.radians(angle)
        return ox + length * math.cos(a), oy - length * math.sin(a)
    A = pt(34, 110)
    B = pt(34, 285)
    C = pt(47, 120)
    s.line(ox, oy, ox + 360, oy, arrow=False, color="#cbd5e1", sw=1)
    s.line(ox, oy, ox, oy - 210, arrow=False, color="#cbd5e1", sw=1)
    s.line(ox, oy, *B, color="#2563eb", sw=2.2)
    s.line(ox, oy, *A, color="#7c3aed", sw=3)
    s.line(ox, oy, *C, color="#ea580c", sw=2.2)
    s.text(B[0] - 4, B[1] - 10, "B: long article about cats", size=10.5, weight=600, color="#1e3a8a", anchor="middle")
    s.text(A[0] + 10, A[1] + 14, "A: \"I love cat\"", size=10.5, weight=600, color="#5b21b6", anchor="start")
    s.text(C[0] - 8, C[1] - 6, "C: short text about dogs", size=10.5, weight=600, color="#9a3412", anchor="end")
    s.line(A[0], A[1], C[0], C[1], arrow=False, color="#ea580c", dash="3 3", sw=1.4)
    s.circle(ox, oy, 3, fill="#475569", stroke="#475569")
    # right side explanation
    x = 440
    s.box(x, 26, 228, 72, title="Cosine (angle)", body=["A vs B: angle 0 → similarity 1 ✓", "A vs C: small angle → 0.99"],
          kind="green", tsize=11.5, bsize=10)
    s.box(x, 112, 228, 72, title="Euclidean (ruler)", body=["A vs B: 493 (very far) ✗", "A vs C: 6.5 (near)"],
          kind="red", tsize=11.5, bsize=10)
    s.text(x + 114, 206, "For meaning, direction matters", size=10, italic=True, color=MUTED)
    s.text(x + 114, 220, "→ use cosine for embeddings", size=10, italic=True, color=MUTED)
    return s.render()


# =====================================================================================
# Chapter 7 — vector search
# =====================================================================================
import random as _random


@fig
def ivf():
    s = Svg(680, 270, "ivf")
    rnd = _random.Random(7)
    x0, y0, w, h = 10, 12, 400, 250
    s.rect(x0, y0, w, h, fill="#fbfcfe", stroke="#d7dce6", sw=1.1, rx=10)
    cents = [(110, 80, "#3b82f6"), (300, 72, "#10b981"), (120, 200, "#f59e0b"), (305, 196, "#ef4444")]
    # borders (simple 2x2 split)
    s.line(208, y0 + 4, 208, y0 + h - 4, arrow=False, color="#94a3b8", sw=1.2, dash="5 4")
    s.line(x0 + 4, 138, x0 + w - 4, 138, arrow=False, color="#94a3b8", sw=1.2, dash="5 4")
    for cx, cy, col in cents:
        for _ in range(14):
            px = min(max(cx + rnd.gauss(0, 34), x0 + 10), x0 + w - 10)
            py = min(max(cy + rnd.gauss(0, 24), y0 + 10), y0 + h - 10)
            if (px < 208) != (cx < 208) or (py < 138) != (cy < 138):
                continue
            s.circle(px, py, 3.6, fill=col, stroke="#ffffff", sw=0.8)
        s.text(cx, cy + 6, "✕", size=17, weight=700, color="#111827")
    # query near the border and its true neighbour just across
    qx, qy = 200, 128
    s.circle(216, 124, 4.2, fill="#10b981", stroke="#065f46", sw=1.4)
    s.text(qx - 2, qy + 5, "★", size=16, color="#7c3aed")
    s.text(qx - 12, qy - 10, "Q", size=11, weight=700, color="#5b21b6", anchor="end")
    s.text(214, 152, "↑ true nearest neighbour", size=9.5, color="#065f46", anchor="start", weight=700)
    s.text(214, 164, "   (in the green cluster!)", size=9.5, color="#065f46", anchor="start")
    # right side steps
    x = 424
    s.box(x, 14, 246, 58, title="1. Compare Q with the centroids ✕",
          body=["4 comparisons instead of all points"], kind="blue", tsize=10.5, bsize=9.5)
    s.box(x, 84, 246, 58, title="2. Search only the nearest cluster",
          body=["Q is closest to the blue centroid"], kind="purple", tsize=10.5, bsize=9.5)
    s.box(x, 154, 246, 58, title="3. Border problem",
          body=["the true neighbour is across the line →", "search 2+ clusters (nprobe)"], kind="red",
          tsize=10.5, bsize=9.5)
    s.text(x + 123, 236, "✕ = centroid found by k-means", size=9.5, italic=True, color=MUTED)
    s.text(x + 123, 252, "dashed lines = cluster borders", size=9.5, italic=True, color=MUTED)
    return s.render()


@fig
def kdtree():
    s = Svg(680, 300, "kdt")
    pts = {"A": (2, 7), "B": (3, 16), "C": (4, 4), "D": (5, 11), "E": (7, 14), "F": (9, 4), "G": (10, 19),
           "H": (11, 3), "I": (12, 13), "J": (19, 10), "K": (14, 15), "L": (15, 3), "M": (17, 11), "N": (18, 5),
           "O": (19, 9)}
    ox, oy, sc = 64, 290, 13
    P = lambda x, y: (ox + x * sc, oy - y * sc)
    s.rect(ox, oy - 20.5 * sc, 21 * sc, 20.5 * sc, fill="#fbfcfe", stroke="#d7dce6", sw=1.1, rx=4)
    s.line(*P(11, 0), *P(11, 20.5), arrow=False, color="#2563eb", sw=2)
    s.line(*P(0, 11), *P(11, 11), arrow=False, color="#7c3aed", sw=1.6)
    s.line(*P(11, 10), *P(21, 10), arrow=False, color="#7c3aed", sw=1.6)
    s.text(P(11, 20.5)[0], P(11, 20.5)[1] - 6, "x = 11 (H)", size=9.5, color="#1d4ed8", weight=700)
    s.text(ox - 5, P(0, 11)[1] + 3, "y = 11", size=9.5, color="#6d28d9", anchor="end", weight=700)
    s.text(ox - 5, P(0, 11)[1] + 15, "(D)", size=9, color="#6d28d9", anchor="end")
    s.text(ox + 21 * sc + 5, P(21, 10)[1] + 3, "y = 10", size=9.5, color="#6d28d9", anchor="start", weight=700)
    s.text(ox + 21 * sc + 5, P(21, 10)[1] + 15, "(J)", size=9, color="#6d28d9", anchor="start")
    q = P(13, 8)
    s.circle(q[0], q[1], 5.39 * sc, fill="none", stroke="#f59e0b", sw=1.4)
    off = {"J": (-7, -6, "end"), "O": (7, 11, "start"), "M": (-7, -6, "end"), "G": (-7, 4, "end"),
           "H": (7, 4, "start"), "I": (7, -4, "start")}
    for k, (x, y) in pts.items():
        px, py = P(x, y)
        col = "#10b981" if k == "M" else ("#d97706" if k == "L" else "#475569")
        s.circle(px, py, 4.2, fill=col, stroke="#ffffff", sw=1)
        dx, dy, anc = off.get(k, (7, -4, "start"))
        s.text(px + dx, py + dy, k, size=10, weight=700, anchor=anc, color=col)
    s.text(q[0], q[1] + 5, "★", size=16, color="#7c3aed")
    s.text(q[0] - 8, q[1] + 16, "Q", size=10.5, weight=700, color="#5b21b6", anchor="end")
    x, w = 392, 282
    s.box(x, 22, w, 52, title="1. Walk down → lower-right box", body=["best of {L, N, O}: L at 5.39",
          "(orange circle = current search radius)"], kind="orange", tsize=10.5, bsize=9.5)
    s.box(x, 84, w, 52, title="2. Line y = 10 is only 2 away (< 5.39)",
          body=["→ must check upper-right box", "→ M at 5.00 ✓ closer!"], kind="green", tsize=10.5, bsize=9.5)
    s.box(x, 146, w, 52, title="3. Line x = 11 is 2 away (< 5.00)",
          body=["→ check the left half too", "→ best there F at 5.66, no gain. Answer: M"], kind="blue",
          tsize=10.5, bsize=9.5)
    s.box(x, 208, w, 52, title="In 768-D every split line is \"close\"",
          body=["→ backtracking everywhere", "→ no better than brute force"], kind="red", tsize=10.5, bsize=9.5)
    return s.render()


@fig
def hnsw():
    s = Svg(680, 300, "hnsw")
    rnd = _random.Random(3)
    layers = [("Layer 2 (few nodes, long jumps)", 42, 3), ("Layer 1", 132, 7), ("Layer 0 (ALL vectors)", 228, 15)]
    xs_all = [60 + i * 38 for i in range(15)]
    chosen = {0: [1, 7, 13], 1: [1, 3, 5, 7, 9, 11, 13], 2: list(range(15))}
    ys = {}
    for li, (title, y, n) in enumerate(layers):
        s.path(f"M 30 {y - 22} L 610 {y - 22} L 650 {y + 22} L 70 {y + 22} Z", color="#cbd5e1", arrow=False,
               fill="#f8fafc", sw=1.1)
        s.text(24, y - 26, title, size=10, weight=700, anchor="start", color="#334155")
        idx = chosen[li]
        pts = [(xs_all[i] + 20, y + (8 if i % 2 else -6)) for i in idx]
        for a in range(len(pts) - 1):
            s.line(pts[a][0], pts[a][1], pts[a + 1][0], pts[a + 1][1], arrow=False, color="#94a3b8", sw=1.1)
        if li == 2:
            for a in range(len(pts) - 2):
                if a % 3 == 0:
                    s.line(pts[a][0], pts[a][1], pts[a + 2][0], pts[a + 2][1], arrow=False, color="#cbd5e1", sw=1)
        for i, (px, py) in zip(idx, pts):
            ys[(li, i)] = (px, py)
            s.circle(px, py, 5.5, fill="#e0e7ff", stroke="#4f46e5", sw=1.3)
    # vertical links
    for i in chosen[0]:
        a, b = ys[(0, i)], ys[(1, i)]
        s.line(a[0], a[1] + 6, b[0], b[1] - 6, arrow=False, color="#c7d2fe", sw=1, dash="3 3")
    for i in chosen[1]:
        a, b = ys[(1, i)], ys[(2, i)]
        s.line(a[0], a[1] + 6, b[0], b[1] - 6, arrow=False, color="#c7d2fe", sw=1, dash="3 3")
    # search path
    path = [ys[(0, 1)], ys[(0, 7)], ys[(1, 7)], ys[(1, 9)], ys[(2, 9)], ys[(2, 10)]]
    s.path("M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in path), color="#7c3aed", sw=2.4)
    s.circle(*ys[(0, 1)], 7, fill="#7c3aed", stroke="#fff", sw=1.4)
    s.text(ys[(0, 1)][0], ys[(0, 1)][1] - 11, "entry point", size=9.5, weight=700, color="#5b21b6")
    tx, ty = ys[(2, 10)]
    s.text(tx + 4, ty + 44, "★ query's neighbours found by beam search (efSearch)", size=9.5, weight=600,
           color="#5b21b6", anchor="middle")
    s.text(ys[(0, 7)][0] + 10, ys[(0, 7)][1] - 10, "greedy hop", size=9.5, italic=True, color="#5b21b6",
           anchor="start")
    s.text(ys[(1, 7)][0] - 8, ys[(1, 7)][1] - 30, "drop down", size=9.5, italic=True, color="#5b21b6", anchor="end")
    return s.render()


@fig
def pq():
    s = Svg(680, 250, "pq")
    vals = [1.1, 2.3, 0.9, 3.4, 8.8, 7.6, 9.1, 6.5, 4.2, 5.5, 3.9, 5.1, 9.9, 8.1, 7.7, 9.3]
    cols = ["#dbeafe", "#dcfce7", "#fef3c7", "#fce7f3"]
    strokes = ["#3b82f6", "#16a34a", "#d97706", "#db2777"]
    ids = [10, 23, 123, 16]
    s.text(14, 22, "Original vector: 16 floats × 4 bytes = 64 bytes", size=11, weight=700, anchor="start",
           color="#1e3a8a")
    x = 14
    for c in range(4):
        for j in range(4):
            v = vals[c * 4 + j]
            s.rect(x, 32, 38, 26, fill=cols[c], stroke=strokes[c], sw=1, rx=4)
            s.text(x + 19, 50, f"{v}", size=10.5, mono=True)
            x += 40
        x += 6
    for c in range(4):
        cx = 14 + c * 166 + 80
        s.line(cx, 62, cx, 88, color=strokes[c])
        s.box(cx - 76, 90, 152, 46, title=f"codebook {c + 1}", body=["256 centroids (k-means)"], kind="white",
              tsize=10.5, bsize=9)
        s.line(cx, 138, cx, 160, color=strokes[c])
        s.rect(cx - 26, 162, 52, 30, fill=cols[c], stroke=strokes[c], sw=1.4, rx=5)
        s.text(cx, 182, str(ids[c]), size=13, weight=700, mono=True)
    s.text(340, 212, "Stored: [10, 23, 123, 16] → 4 bytes (16× smaller). Each id = nearest centroid of that chunk.",
           size=10.5, weight=600, color="#14532d")
    s.text(340, 236, "Query time: distance ≈ table1[10] + table2[23] + table3[123] + table4[16]  (4 lookups)",
           size=10.5, mono=False, color="#5b21b6")
    return s.render()


# =====================================================================================
# Chapter 8 — RAG
# =====================================================================================
@fig
def rag_phases():
    s = Svg(680, 270, "ragp")
    s.rect(4, 8, 672, 104, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=12)
    s.text(16, 28, "PHASE A — INDEXING (offline, once per document)", size=11, weight=700, anchor="start",
           color="#4c1d95")
    items = [("Load", ["PDFs, pages, docs"], "white", 120), ("Chunk", ["~1000 chars,", "200 overlap"], "white", 120),
             ("Embed", ["each chunk → vector"], "white", 124), ("Vector DB", ["vector + text +", "metadata"], "navy", 130)]
    hchain(s, 22, 42, items, h=56, gap=34, tsize=12, bsize=9.5)
    s.rect(4, 128, 672, 136, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=12)
    s.text(16, 148, "PHASE B — QUERY (every question)", size=11, weight=700, anchor="start", color="#1e3a8a")
    items2 = [("Question", ["from the user"], "white", 92), ("Embed", ["SAME model"], "white", 92),
              ("Search", ["top-k similar", "chunks"], "white", 96), ("Augment", ["rules + chunks", "+ question"], "white", 100),
              ("LLM", ["generates"], "navy", 80), ("Answer", ["+ citations"], "green", 88)]
    xs = hchain(s, 14, 170, items2, h=56, gap=18, tsize=11.5, bsize=9.2)
    # search reads from vector db
    sx, sw_ = xs[2]
    s.path(f"M {sx + sw_ / 2} 168 C {sx + sw_ / 2} 140, 560 140, 560 102", color="#7c3aed", dash="4 3",
           start_arrow=True)
    s.text(470, 122, "nearest-neighbour search", size=9.5, italic=True, color="#5b21b6")
    return s.render()


@fig
def chunk_overlap():
    s = Svg(680, 150, "chov")
    x0, w, total = 30, 620, 2600
    X = lambda c: x0 + c / total * w
    s.rect(x0, 22, w, 22, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4)
    s.text(x0 + w / 2, 37, "the PDF's text (characters 1 … 2600)", size=10.5, color="#334155")
    chunks = [(0, 1000, "#dbeafe", "#3b82f6", "chunk 1: 1–1000"), (800, 1800, "#dcfce7", "#16a34a", "chunk 2: 801–1800"),
              (1600, 2600, "#fef3c7", "#d97706", "chunk 3: 1601–2600")]
    y = 60
    for a, b, fill, stroke, label in chunks:
        s.rect(X(a), y, X(b) - X(a), 22, fill=fill, stroke=stroke, sw=1.3, rx=4)
        s.text((X(a) + X(b)) / 2, y + 15, label, size=10.5, weight=600, mono=True)
        y += 28
    for a in (800, 1600):
        s.rect(X(a), 54, X(a + 200) - X(a), 90, fill="#f472b6", stroke="none", sw=0, rx=2, opacity=0.18)
        s.text((X(a) + X(a + 200)) / 2, 146, "overlap 200", size=9.5, weight=700, color="#be185d")
    return s.render()


# =====================================================================================
# Chapter 9 — better RAG
# =====================================================================================
@fig
def agentic_rag():
    s = Svg(680, 236, "agrag")
    s.box(14, 90, 104, 46, title="Question", body=["\"What to recommend", "to Anjali?\""], kind="white", tsize=11,
          bsize=9)
    s.line(120, 113, 150, 113)
    s.box(154, 80, 120, 66, title="Agent (LLM)", body=["decides the next", "search"], kind="navy", tsize=12,
          bsize=9.5)
    s.box(154, 190, 120, 38, title="Answer", kind="green", tsize=11.5)
    s.line(214, 148, 214, 186)
    s.text(222, 172, "enough info", size=9.5, italic=True, color="#14532d", anchor="start")
    s.box(154, 8, 120, 42, title="search tool", body=["vector DB / SQL / web"], kind="purple", tsize=11, bsize=9)
    s.path("M 196 78 C 188 66, 188 62, 196 52", color="#7c3aed")
    s.path("M 232 52 C 240 62, 240 66, 232 78", color="#7c3aed")
    s.text(176, 68, "query", size=9, color="#5b21b6", anchor="end")
    s.text(252, 68, "results", size=9, color="#5b21b6", anchor="start")
    # trace
    x = 300
    steps = [("1", "search: \"Anjali's purchases\"", "→ Surf Excel, Micromax phone, bread"),
             ("2", "search: \"who else bought these?\"", "→ Priya, Rohan, Aman"),
             ("3", "search: \"what else did they buy?\"", "→ Vim bar, earphones, butter"),
             ("4", "enough → answer", "recommend Vim bar, earphones, butter")]
    y = 14
    for n, a, b in steps:
        s.circle(x + 10, y + 16, 10, fill="#7c3aed" if n != "4" else "#16a34a", stroke="#fff", sw=1)
        s.text(x + 10, y + 20, n, size=10, weight=700, color="#ffffff")
        s.text(x + 28, y + 13, a, size=10.5, weight=600, anchor="start", mono=True)
        s.text(x + 28, y + 29, b, size=10, anchor="start", color=MUTED)
        y += 52
    return s.render()


@fig
def hybrid():
    s = Svg(680, 200, "hyb")
    s.box(8, 76, 84, 44, title="Query", kind="white", tsize=11.5)
    s.box(126, 20, 150, 50, title="BM25 keyword search", body=["exact words, codes, names"], kind="orange",
          tsize=10.5, bsize=9)
    s.box(126, 126, 150, 50, title="Vector search", body=["meaning, paraphrases"], kind="blue", tsize=10.5,
          bsize=9)
    s.line(94, 92, 122, 50)
    s.line(94, 104, 122, 146)
    s.box(310, 72, 108, 52, title="RRF fusion", body=["Σ 1/(60 + rank)"], kind="purple", tsize=11, bsize=9.5)
    s.line(278, 45, 306, 88)
    s.line(278, 151, 306, 108)
    s.text(322, 62, "ranked list A", size=9, italic=True, color=MUTED, anchor="start")
    s.text(322, 142, "ranked list B", size=9, italic=True, color=MUTED, anchor="start")
    s.line(420, 98, 446, 98)
    s.text(433, 90, "top 50", size=9, italic=True, color=MUTED)
    s.box(450, 72, 110, 52, title="Reranker", body=["cross-encoder / LLM"], kind="green", tsize=11, bsize=9)
    s.line(562, 98, 588, 98)
    s.text(575, 90, "top 5", size=9, italic=True, color=MUTED)
    s.box(592, 72, 80, 52, title="LLM", body=["prompt"], kind="navy", tsize=11.5, bsize=9)
    return s.render()


# =====================================================================================
# Chapter 10 — vectorless RAG
# =====================================================================================
@fig
def pageindex():
    s = Svg(680, 268, "pgi")
    panel(s, 6, 6, 250, 256, "Vector RAG", "blue", 12)
    rnd = _random.Random(11)
    q = (130, 60)
    s.box(q[0] - 40, 34, 80, 26, title="query vector", kind="white", tsize=9.5)
    cells_ = []
    for r in range(5):
        for c in range(6):
            x = 22 + c * 37 + rnd.randint(-3, 3)
            y = 96 + r * 30 + rnd.randint(-2, 2)
            cells_.append((x, y))
    top = {3, 9, 16, 22}
    for i, (x, y) in enumerate(cells_):
        s.line(q[0], 62, x + 14, y, arrow=False, color="#bfdbfe" if i not in top else "#2563eb",
               sw=0.6 if i not in top else 1.3)
    for i, (x, y) in enumerate(cells_):
        s.rect(x, y, 28, 18, fill="#dbeafe" if i not in top else "#2563eb", stroke="#60a5fa", sw=0.8, rx=3)
    s.text(131, 252, "compare with EVERY chunk → top-k by similarity", size=9.5, italic=True, color="#1e3a8a")
    # right: tree
    panel(s, 266, 6, 408, 256, "PageIndex (tree + reasoning)", "purple", 12)
    s.box(400, 34, 150, 30, title="Annual Report 2023", kind="white", tsize=10.5)
    kids = [("1 Business", 292), ("2 Risk factors", 404), ("7 Financials", 536)]
    for name, x in kids:
        hi = name.startswith("7")
        s.line(475, 66, x + 50, 92, arrow=False, color="#7c3aed" if hi else "#c4b5fd", sw=2 if hi else 1.2)
        s.box(x, 94, 100, 28, title=name, kind="purple" if hi else "white", tsize=10)
    subs = [("7.1 Income stmt", 470, True), ("7.2 Balance sheet", 580, False)]
    for name, x, hi in subs:
        s.line(586, 124, x + 45, 150, arrow=False, color="#7c3aed" if hi else "#c4b5fd", sw=2 if hi else 1.2)
        s.box(x, 152, 92, 34, title=name, body=["p. 45–47"] if hi else ["p. 48–50"],
              kind="green" if hi else "white", tsize=9.5, bsize=8.5)
    s.lines(282, 140, ["Q: \"operating margin", "in 2023?\"", "", "LLM: margins are in the", "income statement →",
                       "open 7 → 7.1 → read"], size=9.5, italic=True, color="#4c1d95", anchor="start")
    s.text(560, 212, "answer + citation: \"Section 7.1, p. 46\"", size=10, weight=700, color="#14532d")
    s.text(470, 238, "no chunks, no embeddings — the LLM navigates the document like an expert", size=9.5,
           italic=True, color=MUTED)
    return s.render()


# =====================================================================================
# Chapter 11 — graph databases
# =====================================================================================
@fig
def sql_vs_graph():
    s = Svg(680, 250, "svg11")
    panel(s, 6, 6, 330, 238, "SQL: every hop = index lookup", "red", 11.5)
    # friendships table
    s.rect(24, 40, 138, 150, fill="#ffffff", stroke="#e5a3a3", sw=1.2, rx=6)
    s.text(93, 56, "friendships", size=10.5, weight=700, color="#7f1d1d")
    rows = [("rohit", "mohit"), ("rohit", "aman"), ("mohit", "sohan"), ("aman", "tulsi"), ("…", "…"),
            ("(N rows)", "")]
    for i, (a, b) in enumerate(rows):
        y = 74 + i * 19
        s.text(36, y, a, size=9.5, mono=True, anchor="start")
        s.text(104, y, b, size=9.5, mono=True, anchor="start")
    s.box(186, 44, 136, 40, title="hop 1: B-tree", body=["O(log N)"], kind="white", tsize=10, bsize=9.5)
    s.box(186, 94, 136, 40, title="hop 2: 500 lookups", body=["500 × O(log N)"], kind="white", tsize=10,
          bsize=9.5)
    s.box(186, 144, 136, 40, title="hop 3: 2.5 lakh", body=["2.5 lakh × O(log N)"], kind="white", tsize=10,
          bsize=9.5)
    s.text(171, 214, "N = the WHOLE network — it keeps growing", size=9.5, italic=True, color="#7f1d1d")
    panel(s, 346, 6, 328, 238, "Graph: every hop = pointer jump", "green", 11.5)
    nodes = {"Rohit": (420, 124), "Mohit": (520, 60), "Aman": (520, 124), "Anjali": (520, 188),
             "Sohan": (626, 44), "Tulsi": (626, 104), "Google": (626, 176)}
    edges = [("Rohit", "Mohit"), ("Rohit", "Aman"), ("Rohit", "Anjali"), ("Mohit", "Sohan"), ("Aman", "Tulsi"),
             ("Anjali", "Google")]
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        s.line(x1 + 26, y1, x2 - 28, y2, color="#16a34a", sw=1.5)
    for n, (x, y) in nodes.items():
        kind = "navy" if n == "Rohit" else ("orange" if n == "Google" else "white")
        s.box(x - 27, y - 13, 54, 26, title=n, kind=kind, tsize=10, rx=13)
    s.text(573, 170, "WORKS_AT", size=8.5, color="#9a3412")
    s.text(510, 230, "cost ∝ nodes you touch, not database size", size=9.5, italic=True, color="#14532d")
    return s.render()


@fig
def neo4j_records():
    s = Svg(680, 250, "n4j")
    s.text(14, 20, "Node store: fixed 15-byte records → address = 1000 + id × 15", size=11, weight=700,
           anchor="start", color="#1e3a8a")
    names = ["Rohit", "Mohit", "Aman", "Anjali", "Suraj"]
    for i, n in enumerate(names):
        x = 14 + i * 130
        s.rect(x, 30, 122, 56, fill="#eef2ff" if i else "#e0e7ff", stroke="#6366f1", sw=1.3, rx=6)
        s.text(x + 8, 46, f"id {i} · @{1000 + i * 15}", size=9.5, mono=True, anchor="start", color="#3730a3")
        s.text(x + 8, 63, n, size=11, weight=700, anchor="start")
        s.text(x + 8, 79, "firstRel →" if i == 0 else "firstRel, firstProp", size=9, mono=True, anchor="start",
               color=MUTED)
    s.text(150, 118, "Relationship store: fixed 34-byte records, chained per node", size=11, weight=700,
           anchor="start", color="#14532d")
    rels = [("@2000", "Rohit → Mohit", "FRIEND"), ("@2034", "Rohit → Aman", "FRIEND"),
            ("@2068", "Rohit → Anjali", "FRIEND")]
    for i, (addr, txt, typ) in enumerate(rels):
        x = 60 + i * 200
        s.rect(x, 130, 160, 58, fill="#ecfdf5", stroke="#10b981", sw=1.3, rx=6)
        s.text(x + 8, 146, addr, size=9.5, mono=True, anchor="start", color="#065f46")
        s.text(x + 8, 163, txt, size=10.5, weight=700, anchor="start")
        s.text(x + 8, 180, f"type {typ} · next →", size=9, mono=True, anchor="start", color=MUTED)
        if i < 2:
            s.line(x + 162, 159, x + 198, 159, color="#10b981")
    s.text(662, 163, "null", size=9.5, mono=True, color=MUTED)
    s.line(622, 159, 646, 159, color="#94a3b8")
    s.path("M 90 88 C 90 110, 110 118, 120 128", color="#6366f1")
    s.text(340, 220, "\"All of Rohit's friends\" = start at nodes[0].firstRel and follow next pointers —",
           size=10, italic=True, color="#334155")
    s.text(340, 236, "no join, no index search per hop", size=10, italic=True, color="#334155")
    return s.render()


# =====================================================================================
# Chapter 12 — Graph RAG
# =====================================================================================
@fig
def movie_schema():
    s = Svg(680, 250, "msch")
    cx, cy = 340, 128
    s.circle(cx, cy, 44, fill="#16213e", stroke="#16213e", sw=1)
    s.text(cx, cy - 2, "Movie", size=13, weight=700, color="#ffffff")
    s.text(cx, cy + 14, "{title, year}", size=9, mono=True, color="#c7d2fe")
    nodes = [("Director", 110, 70, "{name}", "DIRECTED", "in"), ("Actor", 110, 190, "{name}", "ACTED_IN", "in"),
             ("Genre", 570, 50, "{name}", "BELONGS_TO", "out"), ("Theme", 590, 128, "{name}", "EXPLORES", "out"),
             ("Award", 570, 206, "{name, category}", "WON", "out")]
    for name, x, y, props, rel, d in nodes:
        s.circle(x, y, 32, fill="#ede9fe", stroke="#7c3aed", sw=1.6)
        s.text(x, y + 1, name, size=11.5, weight=700, color="#4c1d95")
        if len(props) > 8:
            s.text(x, y + 13, "{name,", size=8, mono=True, color="#6d28d9")
            s.text(x, y + 22, "category}", size=8, mono=True, color="#6d28d9")
        else:
            s.text(x, y + 14, props, size=8, mono=True, color="#6d28d9")
        # edge between (x,y) and movie
        import math
        ang = math.atan2(cy - y, cx - x)
        x1, y1 = x + 33 * math.cos(ang), y + 33 * math.sin(ang)
        x2, y2 = cx - 46 * math.cos(ang), cy - 46 * math.sin(ang)
        if d == "in":
            s.line(x1, y1, x2, y2, color="#475569", sw=1.6)
        else:
            s.line(x2, y2, x1, y1, color="#475569", sw=1.6)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        s.chip(mx, my - 10, rel, kind="yellow", size=9, mono=True, anchor="middle")
    s.text(340, 242, "label = class · relationship = fact · property = data", size=10, italic=True, color=MUTED)
    return s.render()


@fig
def graphrag_indexing():
    s = Svg(680, 214, "gri")
    s.box(8, 84, 96, 46, title="movies.pdf", body=["~1000 movies"], kind="white", tsize=11, bsize=9)
    s.line(106, 98, 136, 52)
    s.line(106, 116, 136, 162)
    s.text(12, 20, "facts →", size=10, weight=700, anchor="start", color="#4c1d95")
    s.text(12, 206, "meaning →", size=10, weight=700, anchor="start", color="#1e3a8a")
    xs = hchain(s, 140, 26, [("Gemini extracts", ["batches of 50 · 5 parallel", "retries · JSON only"], "purple", 150),
                             ("JSON entities", ["movie, director, actors,", "genres, themes, awards"], "white", 146),
                             ("Neo4j", ["MERGE in transactions", "+ indexes"], "navy", 138)],
                h=54, gap=26, tsize=11, bsize=9)
    hchain(s, 140, 136, [("Split by ----", ["one chunk per movie"], "white", 150),
                          ("gemini-embedding-001", ["3072-d · 5 at a time"], "blue", 146),
                          ("Pinecone", ["upsert batches of 100", "{id, values, text}"], "navy", 138)],
           h=54, gap=26, tsize=11, bsize=9)
    return s.render()


@fig
def graphrag_query():
    s = Svg(680, 402, "grq")
    ys = vchain(s, 200, 6, [("Question", ["\"Movies like Inception\" / \"Nolan's films\""], "white", 40),
                            ("1 · Extract names (LLM)", ["[\"Inception\"], [\"Nolan\"]"], "purple", 40),
                            ("2 · Resolve in Neo4j", ["exact, then CONTAINS · all 6 labels"], "blue", 40),
                            ("3 · Classify (LLM)", ["graph or similarity?"], "purple", 40)],
                w=280, gap=18, tsize=11, bsize=9)
    y0 = ys[-1][0] + ys[-1][1]
    s.line(300, y0 + 2, 170, y0 + 30)
    s.line(380, y0 + 2, 510, y0 + 30)
    s.text(200, y0 + 18, "graph", size=10, weight=700, color="#1e3a8a", anchor="end")
    s.text(480, y0 + 18, "similarity", size=10, weight=700, color="#9a3412", anchor="start")
    vchain(s, 30, y0 + 32, [("LLM → JSON plan", [], "white", 26), ("validate + build Cypher", ["whitelists · $params"], "green", 36),
                            ("Neo4j (READ session)", [], "navy", 26), ("LLM writes plain English", [], "white", 26)],
           w=270, gap=10, tsize=10.5, bsize=9)
    vchain(s, 380, y0 + 32, [("Pinecone top 50", ["embed the movie name"], "orange", 36),
                             ("Neo4j genre filter", ["keep shared genres"], "navy", 36),
                             ("LLM picks best 10", ["with reasons (a reranker)"], "white", 36)],
           w=270, gap=10, tsize=10.5, bsize=9)
    return s.render()


# =====================================================================================
# Chapter 13 — Microsoft GraphRAG / choosing RAG
# =====================================================================================
@fig
def ms_graphrag():
    s = Svg(680, 262, "msg")
    hchain(s, 10, 10, [("Documents", ["any text corpus"], "white", 120), ("Text units", ["chunks"], "white", 110),
                       ("LLM extraction", ["entities · relations", "descriptions"], "purple", 150),
                       ("Entity graph", ["same entities merged"], "blue", 150)], h=50, gap=26, tsize=11, bsize=9)
    rnd = _random.Random(5)
    comms = [((110, 170), "#3b82f6"), ((230, 190), "#10b981"), ((340, 160), "#f59e0b")]
    pts = []
    for (cx, cy), col in comms:
        s.circle(cx, cy, 46, fill="none", stroke=col, sw=1.4)
        for _ in range(6):
            px, py = cx + rnd.uniform(-28, 28), cy + rnd.uniform(-28, 28)
            pts.append((px, py, col))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if pts[i][2] == pts[j][2] and rnd.random() < 0.45:
                s.line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], arrow=False, color="#cbd5e1", sw=1)
    s.line(pts[2][0], pts[2][1], pts[8][0], pts[8][1], arrow=False, color="#94a3b8", sw=1)
    s.line(pts[9][0], pts[9][1], pts[14][0], pts[14][1], arrow=False, color="#94a3b8", sw=1)
    for px, py, col in pts:
        s.circle(px, py, 4.5, fill=col, stroke="#fff", sw=1)
    s.text(225, 252, "Leiden algorithm → hierarchical communities", size=10, weight=600, color="#334155")
    s.line(400, 176, 440, 176)
    for i, (t, col) in enumerate((("Report: community A", "#3b82f6"), ("Report: community B", "#10b981"),
                                  ("Report: community C", "#f59e0b"))):
        y = 108 + i * 46
        s.rect(446, y, 222, 38, fill="#ffffff", stroke=col, sw=1.4, rx=6)
        s.text(456, y + 16, t, size=10.5, weight=700, anchor="start", color="#1f2937")
        s.text(456, y + 30, "LLM-written summary of the group", size=9, anchor="start", color=MUTED)
    s.text(557, 252, "global search = map-reduce over reports", size=10, weight=600, color="#5b21b6")
    return s.render()


@fig
def rag_decision():
    s = Svg(680, 336, "rdec")
    s.box(210, 4, 260, 36, title="What does the question need?", kind="navy", tsize=12)
    rows = [("exact numbers from tables", "Text-to-SQL", "SchemaMind", "green"),
            ("relationship chains, multi-hop", "Knowledge-graph RAG", "Rohit's movie project", "purple"),
            ("corpus-wide themes / summaries", "GraphRAG (global search)", "community reports", "orange"),
            ("precise sections of long reports", "Tree / section-aware (PageIndex)", "vectorless", "pink"),
            ("semantic lookup over many docs", "Hybrid vector RAG + rerank", "PaperRAG-style", "blue"),
            ("a small corpus", "Long context (+ caching)", "no retrieval", "grey")]
    s.line(340, 42, 340, 54, arrow=False)
    s.line(120, 54, 560, 54, arrow=False, color="#94a3b8")
    y = 62
    for cond, appr, ex, kind in rows:
        s.box(20, y, 250, 36, title=cond, kind="white", tsize=10.5)
        s.line(274, y + 18, 336, y + 18)
        s.box(340, y, 220, 36, title=appr, kind=kind, tsize=10.5)
        s.text(570, y + 22, ex, size=9.5, italic=True, color=MUTED, anchor="start")
        y += 42
    s.text(340, 330, "In real products: a router sends each question to the right path", size=10, italic=True,
           color="#334155")
    return s.render()


# =====================================================================================
# Chapter 14 — LangGraph
# =====================================================================================
@fig
def lg_pipeline():
    s = Svg(680, 262, "lgp")
    s.box(6, 34, 58, 34, title="START", kind="grey", tsize=10, rx=17)
    xs = hchain(s, 84, 30, [("loadPDF", [], "blue", 88), ("createChunks", [], "blue", 108),
                            ("embedChunk", [], "purple", 100), ("storeEmbedding", [], "purple", 118)],
                h=42, gap=22, tsize=11)
    s.line(66, 51, 80, 51)
    ex, ew = xs[-1]
    s.line(ex + ew + 4, 51, ex + ew + 32, 51)
    s.box(ex + ew + 36, 34, 58, 34, title="END", kind="green", tsize=10, rx=17)
    # loop back
    (ax, aw), (bx, bw) = xs[2], xs[3]
    s.path(f"M {bx + bw / 2} 74 C {bx + bw / 2} 110, {ax + aw / 2} 110, {ax + aw / 2} 76", color="#7c3aed",
           sw=1.8)
    s.text((ax + bx + aw / 2 + bw / 2) / 2, 118, "currentIndex < chunks.length ? loop", size=9.5, weight=600,
           color="#5b21b6")
    s.text(ex + ew + 18, 26, "done", size=9.5, weight=600, color="#14532d")
    # checkpoints
    s.rect(90, 150, 488, 44, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8, dash="5 4")
    s.text(334, 168, "Checkpointer: after EVERY node → save (state, next node) for thread_id \"pdf-001\"", size=10.5,
           weight=600, color="#334155")
    s.text(334, 185, "MemorySaver (RAM) · SqliteSaver (file) · Postgres / Redis (production)", size=9.5,
           italic=True, color=MUTED)
    for x, w in xs:
        s.line(x + w / 2, 74, x + w / 2, 148, color="#cbd5e1", sw=1, dash="3 3")
    s.box(90, 206, 488, 50, title="State = { pdfText, chunks, currentIndex: 237, currentEmbedding }",
          body=["crash at chunk 237? → invoke(null, config) continues from here"], kind="yellow", tsize=10.5,
          bsize=9.5, mono_title=True)
    return s.render()


# =====================================================================================
# Chapter 15 — human in the loop
# =====================================================================================
@fig
def interrupt_flow():
    s = Svg(680, 418, "intf")
    lanes = [(70, "Human", "grey"), (240, "Your app / API", "blue"), (420, "LangGraph", "navy"),
             (600, "Checkpoint DB", "orange")]
    msgs = [
        (1, 2, "invoke(input, thread_id)", "#2563eb"),
        (2, 3, "save: waiting at humanReview", "#ea580c"),
        (2, 1, "returns { __interrupt__ }", "#7c3aed"),
        (1, 0, "show plan: approve?", "#6b7280"),
        (0, 1, "\"approve\"", "#6b7280"),
        (1, 2, "invoke(Command({resume}))", "#2563eb"),
        (3, 2, "load saved state", "#ea580c"),
        (2, 1, "final result", "#7c3aed"),
    ]
    ys = seq(s, lanes, 8, 368, msgs[:4], row_h=36, start_y=74)
    y_gap = ys[-1] + 26
    s.line(20, y_gap, 660, y_gap, arrow=False, color="#94a3b8", sw=1.2, dash="6 5")
    s.text(340, y_gap + 16, "…minutes or days later — the process may have restarted, any server can continue…",
           size=10, italic=True, color="#475569")
    # draw remaining messages manually continuing numbering
    y = y_gap + 44
    for i, (a, b, label, color) in enumerate(msgs[4:], start=5):
        xa, xb = lanes[a][0], lanes[b][0]
        d = 1 if xb > xa else -1
        s.line(xa + 5 * d, y, xb - 7 * d, y, color=color, sw=1.7)
        cx = xa + 14 * d
        s.circle(cx, y - 11, 8, fill=color, stroke=color, sw=1)
        s.text(cx, y - 7.5, str(i), size=9, weight=700, color="#ffffff")
        tw = text_width(label, 10, mono=True)
        mid = (xa + xb) / 2
        left = max(mid - tw / 2, cx + 12) if d > 0 else min(mid - tw / 2, cx - 12 - tw)
        s.text(left, y - 6, label, size=10, color=INK, mono=True, anchor="start")
        y += 36
    s.box(430, y - 18, 244, 40, title="humanReview re-runs from line 1;",
          body=["interrupt() now RETURNS \"approve\""], kind="purple", tsize=9.5, bsize=9.5)
    return s.render()


# =====================================================================================
# Chapter 16 — AI dev team
# =====================================================================================
@fig
def dev_team():
    s = Svg(680, 470, "devt")
    def band(y, h, title):
        s.rect(4, y, 672, h, fill="#fbfcfe", stroke="#d7dce6", sw=1.1, rx=10)
        s.text(14, y + 16, title, size=10.5, weight=700, anchor="start", color="#4c1d95")
    band(4, 58, "Phase 1 · Spec")
    s.box(140, 18, 110, 34, title="pmAgent", kind="purple", tsize=11)
    s.box(330, 18, 110, 34, title="humanInput", kind="orange", tsize=11)
    s.path("M 252 28 C 280 20, 300 20, 328 28", color="#475569")
    s.path("M 328 44 C 300 52, 280 52, 252 44", color="#475569")
    s.text(290, 16, "questions", size=8.5, italic=True, color=MUTED)
    s.text(470, 38, "→ spec_ready", size=10, weight=600, color="#14532d", anchor="start")
    band(68, 78, "Phase 2 · Blueprint")
    xs = hchain(s, 120, 88, [("arch 1", [], "blue", 64), ("arch 2", [], "blue", 64), ("arch 3", [], "blue", 64),
                             ("arch 4", [], "blue", 64), ("arch 5", [], "blue", 64),
                             ("validator", [], "green", 90)], h=30, gap=16, tsize=10)
    vx, vw = xs[5]
    s.path(f"M {vx + vw / 2} 120 C {vx + vw / 2} 132, {xs[2][0] + 32} 132, {xs[2][0] + 32} 122", color="#dc2626",
           dash="4 3")
    s.text(xs[3][0] + 32, 141, "errors → back to steps 2–4 (max 2 cycles)", size=8.5, italic=True, color="#b91c1c")
    band(152, 58, "Phase 3 · Plan + sandbox")
    hchain(s, 160, 168, [("planner", ["task queue"], "blue", 110), ("setupSandbox", ["Docker + git"], "grey", 120),
                         ("healthCheck", [], "grey", 104)], h=34, gap=24, tsize=10, bsize=8.5)
    band(216, 250, "Phase 4 · Dev loop (per task)")
    Y1, Y2, Y3 = 254, 318, 392
    top = [("selectNextTask", "white", 104), ("contextBuilder", "white", 100), ("coderAgent", "purple", 90),
           ("updateRegistry", "white", 104), ("reviewerAgent", "orange", 100)]
    hchain(s, 24, Y1, [(t, [], k, w) for t, k, w in top], h=32, gap=26, tsize=10)
    # rejected -> coder (over the top)
    s.path(f"M 556 {Y1 - 2} C 540 {Y1 - 22}, 360 {Y1 - 22}, 344 {Y1 - 2}", color="#dc2626", dash="4 3")
    s.text(450, Y1 - 20, "rejected ≤ 2 → retry with feedback", size=8.5, color="#b91c1c")
    # row 2
    s.box(24, Y2, 104, 32, title="snapshotManager", kind="green", tsize=9.5)
    s.box(280, Y2, 104, 32, title="simplifyTask", kind="red", tsize=10)
    s.box(526, Y2, 100, 32, title="executorAgent", kind="blue", tsize=10)
    s.line(576, Y1 + 34, 576, Y2 - 2)
    s.text(582, Y1 + 50, "approved", size=8.5, color="#14532d", anchor="start")
    s.line(536, Y1 + 34, 388, Y2 + 10, color="#dc2626")
    s.text(470, Y2 - 19, "3rd reject", size=8.5, color="#b91c1c")
    s.path(f"M 280 {Y2 + 16} C 200 {Y2 + 16}, 150 {Y1 + 50}, 116 {Y1 + 34}", color="#94a3b8")
    # pass corridor
    s.path(f"M 540 {Y2 + 34} L 540 {Y2 + 52} L 76 {Y2 + 52} L 76 {Y2 + 34}", color="#16a34a")
    s.text(300, Y2 + 47, "pass → commit + git tag", size=8.5, color="#14532d")
    s.line(76, Y2 - 2, 76, Y1 + 34, color="#16a34a")
    # row 3
    s.box(526, Y3, 100, 30, title="debuggerAgent", kind="red", tsize=10)
    s.line(606, Y2 + 34, 606, Y3 - 2)
    s.text(612, Y2 + 62, "fail", size=8.5, color="#b91c1c", anchor="start")
    s.path(f"M 540 {Y3 - 2} C 520 {Y3 - 40}, 380 {Y2 - 10}, 352 {Y1 + 34}", color="#dc2626", dash="4 3")
    s.text(522, Y3 - 7, "fix → coder", size=8.5, color="#b91c1c", anchor="end")
    s.box(154, Y3, 130, 30, title="humanEscalation", kind="orange", tsize=9.5)
    s.line(524, Y3 + 20, 286, Y3 + 20, color="#ea580c")
    s.text(405, Y3 + 15, "tier 3: skip / guide / simplify", size=8.5, color="#9a3412")
    s.text(24, Y3 + 48, "phase done → phaseVerification → patternExtractor → stateCompactor → next task",
           size=8.8, anchor="start", color="#334155")
    s.text(24, Y3 + 63, "all done → deploymentVerifier → presentToUser → END", size=8.8, anchor="start",
           color="#334155")
    return s.render()


@fig
def escalation():
    s = Svg(680, 214, "esc")
    steps = [("Tier 1", "targeted fix", "error + failing files · 3 tries", "orange"),
             ("Tier 2", "wider context", "+ up to 10 project files · 2 tries", "orange"),
             ("Tier 2.5", "rollback", "reset sandbox to last good git tag", "red"),
             ("Tier 3", "human", "skip · give guidance · simplify", "purple")]
    for i, (t, a, b, kind) in enumerate(steps):
        x = 12 + i * 166
        y = 150 - i * 40
        s.box(x, y, 156, 56, title=f"{t}: {a}", body=[b], kind=kind, tsize=11, bsize=8.8)
        if i < 3:
            s.line(x + 158, y + 28, x + 170, y - 12 + 28)
    s.text(14, 22, "each step costs more — but tries something DIFFERENT, instead of looping forever",
           size=10.5, weight=600, anchor="start", color="#334155")
    return s.render()


# =====================================================================================
# Chapter 17 — PaperRAG
# =====================================================================================
@fig
def paperrag_arch():
    s = Svg(680, 376, "prag")
    s.rect(4, 6, 672, 110, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=12)
    s.text(16, 25, "PHASE A — INDEXING (offline script, once per folder of PDFs)", size=11, weight=700,
           anchor="start", color="#4c1d95")
    items = [("PyMuPDF", ["PDF → text blocks", "(text + box) per page"], "white", 118),
             ("Clean + de-noise", ["ligatures, hyphens,", "page nos, table rows"], "white", 122),
             ("Pack per page", ["whole blocks ≤ 900 ch,", "150 overlap, 1 page"], "white", 132),
             ("MiniLM embed", ["384-d, normalised"], "white", 98),
             ("FAISS index", ["IndexFlatIP +", "chunks.jsonl"], "navy", 98)]
    xa = hchain(s, 16, 40, items, h=62, gap=20, tsize=11, bsize=9)
    s.rect(4, 126, 672, 186, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=12)
    s.text(16, 145, "PHASE B — QUERY (each /ask)", size=11, weight=700, anchor="start", color="#1e3a8a")
    Y = 166
    q = [("Question", ["3–1000 chars"], "white", 70), ("Embed", ["same MiniLM"], "white", 78),
         ("Search", ["exact cosine,", "top-5 hits"], "white", 88), ("Guard 1", ["top-1 score", "< threshold?"],
                                                                     "orange", 92),
         ("Generate", ["extractive or", "Mistral (temp 0)"], "purple", 100)]
    xs = hchain(s, 16, Y, q, h=56, gap=20, tsize=11, bsize=9, labels=[None, None, None, "no", None], lsize=9)
    g2x = xs[-1][0] + xs[-1][1] + 20
    s.line(g2x - 16, Y + 28, g2x - 4, Y + 28)
    s.box(g2x, Y, 124, 56, kind="orange")
    s.text(g2x + 62, Y + 17, "Guard 2", size=11, weight=700, color=KIND["orange"][2])
    s.text(g2x + 62, Y + 31, "reply contains", size=9, color=INK)
    s.text(g2x + 62, Y + 45, "INSUFFICIENT_CONTEXT?", size=8, mono=True, color=INK)
    # search reads the index built in phase A
    fx, fw = xa[-1]
    sx, sw_ = xs[2]
    s.path(f"M {fx + fw / 2} 104 C {fx + fw / 2} 138, {sx + sw_ - 14} 132, {sx + sw_ - 14} {Y - 3}",
           color="#7c3aed", dash="4 3")
    s.text(470, 158, "index loaded once at startup", size=9, italic=True, color="#5b21b6")
    # abstain + answer
    Y2 = 254
    g1x, g1w = xs[3]
    s.box(250, Y2, 250, 48, title="Abstain", body=["abstained = true, no citations"], kind="red", tsize=11,
          bsize=9)
    s.line(g1x + g1w / 2, Y + 58, g1x + g1w / 2, Y2 - 3, color="#dc2626")
    s.text(g1x + g1w / 2 + 6, Y + 76, "yes", size=9, weight=600, color="#b91c1c", anchor="start")
    s.line(g2x + 18, Y + 58, 504, Y2 + 12, color="#dc2626")
    s.text(g2x + 4, Y + 80, "yes", size=9, weight=600, color="#b91c1c", anchor="end")
    s.box(g2x, Y2, 124, 48, title="Answer", body=["+ file & page citations"], kind="green", tsize=11, bsize=9)
    s.line(g2x + 92, Y + 58, g2x + 92, Y2 - 3, color="#16a34a")
    s.text(g2x + 98, Y + 76, "no", size=9, weight=600, color="#14532d", anchor="start")
    s.text(24, Y2 + 20, "guard 1: nothing close", size=9, italic=True, color="#7f1d1d", anchor="start")
    s.text(24, Y2 + 34, "guard 2: close but no answer", size=9, italic=True, color="#7f1d1d", anchor="start")
    # around it
    for i, t in enumerate(["FastAPI: /ask, /health", "Streamlit UI → HTTP → API",
                           "eval: threshold sweep 0.20–0.66"]):
        s.box(16 + i * 220, 326, 208, 32, title=t, kind="grey", tsize=10)
    return s.render()


# =====================================================================================
# Chapter 18 — SchemaMind
# =====================================================================================
@fig
def schemamind_arch():
    s = Svg(680, 392, "smind")
    X, W, H = 236, 206, 44
    rows = [(8, "Question", ["\"Top 3 customers by spend?\""], "white"),
            (70, "Schema retriever", ["top-3 tables by cosine similarity"], "blue"),
            (132, "SQL generator", ["template  |  Mistral (temperature 0)"], "purple"),
            (194, "Validator — layer 1", ["sqlglot AST: one SELECT, no writes"], "orange"),
            (256, "Executor — layer 2", ["read-only file (mode=ro), ≤ 200 rows"], "orange"),
            (330, "Result", ["rows + the SQL that produced them"], "green")]
    for y, t, b, k in rows:
        s.box(X, y, W, H, title=t, body=b, kind=k, tsize=11.5, bsize=9.5)
    for (y1, *_), (y2, *_) in zip(rows, rows[1:]):
        s.line(X + W / 2, y1 + H + 3, X + W / 2, y2 - 3)
    s.text(X + W / 2 + 8, 318, "ok", size=9, weight=600, color="#14532d", anchor="start")
    # startup: introspection feeds the retriever
    s.box(474, 44, 198, 96, kind="grey", rx=10)
    s.text(573, 62, "At startup (once)", size=10.5, weight=700, color="#374151")
    s.lines(484, 80, ["introspect: sqlite_master, PRAGMA", "describe() each table: columns,",
                      "PK, FK →, 2 sample rows", "embed descriptions (MiniLM)"], size=9, lh=13,
            anchor="start", color=INK)
    s.line(472, 92, X + W + 4, 92, color="#64748b")
    # annotations for the two layers
    s.text(454, 212, "parse, don't pattern-match", size=9.5, italic=True, color="#9a3412", anchor="start")
    s.text(454, 226, "blocks DROP / DELETE / UPDATE …", size=9, color=MUTED, anchor="start")
    s.text(454, 274, "the database itself refuses", size=9.5, italic=True, color="#9a3412", anchor="start")
    s.text(454, 288, "writes if layer 1 is fooled", size=9, color=MUTED, anchor="start")
    # repair loop on the left
    rx = 184
    s.line(X - 3, 216, rx, 216, arrow=False, color="#dc2626")
    s.line(X - 3, 278, rx, 278, arrow=False, color="#dc2626")
    s.line(rx, 278, rx, 158, arrow=False, color="#dc2626")
    s.line(rx, 158, X - 4, 158, color="#dc2626")
    s.text(rx + 5, 211, "invalid", size=8.5, color="#b91c1c", anchor="start")
    s.text(rx + 5, 273, "DB error", size=8.5, color="#b91c1c", anchor="start")
    s.box(6, 128, 164, 92, kind="red", rx=10)
    s.text(88, 146, "Repair loop", size=10.5, weight=700, color="#7f1d1d")
    s.lines(15, 163, ["the real error + the failed SQL", "go back to the generator", "max 2 repairs = 3 attempts,",
                      "then ok = false + error"], size=9, lh=13, anchor="start", color=INK)
    s.line(172, 170, rx - 3, 170, arrow=False, color="#dc2626", dash="3 3")
    return s.render()


# =====================================================================================
# Chapter 19 — StanceScope
# =====================================================================================
@fig
def stance_graph():
    s = Svg(680, 318, "stg")
    s.box(8, 30, 52, 30, title="START", kind="grey", tsize=9.5, rx=15)
    xs = hchain(s, 84, 22, [("retrieve_evidence", [], "blue", 128), ("classify_posts", [], "purple", 112),
                            ("human_review", [], "orange", 112), ("aggregate", [], "green", 92)],
                h=46, gap=24, tsize=10.5)
    s.line(62, 45, 80, 45)
    ex, ew = xs[-1]
    s.line(ex + ew + 4, 45, ex + ew + 20, 45)
    s.box(ex + ew + 24, 30, 46, 30, title="END", kind="grey", tsize=9.5, rx=15)
    notes = [["MiniLM: top-3 news", "snippets for the claim"], ["stance + confidence", "per post; < 0.6 →",
                                                                 "low_confidence"],
             ["none flagged → skip;", "else interrupt() →", "graph PAUSES"], ["counts, %, evidence,", "per-post detail"]]
    for (x, w), lines in zip(xs, notes):
        s.lines(x + w / 2, 88, lines, size=9, lh=12.5, color="#334155")
    # API band
    s.rect(4, 142, 672, 104, fill="#fff7ed", stroke="#fdba74", sw=1.1, rx=10)
    s.text(14, 160, "The API around the pause", size=10.5, weight=700, anchor="start", color="#9a3412")
    hchain(s, 14, 172, [("POST /claims/{id}/run", ["→ status \"awaiting_review\"", "+ the flagged posts"], "white", 196),
                        ("A human decides", ["e.g. post 3 → neutral"], "white", 146),
                        ("POST /runs/{id}/review", ["Command(resume={\"3\": \"neutral\"})", "same thread_id run-{id}"],
                         "white", 256)], h=60, gap=28, tsize=10.5, bsize=9)
    s.path(f"M 560 170 C 560 152, {xs[2][0] + 56} 150, {xs[2][0] + 56} 126", color="#ea580c", dash="4 3")
    s.text(596, 150, "resumes at human_review", size=9, italic=True, color="#9a3412", anchor="middle")
    # storage band
    s.box(4, 258, 330, 52, title="MemorySaver (in RAM)", body=["checkpoint after every node, per thread run-{id}",
                                                                "⚠ lost on restart → use SqliteSaver"],
          kind="grey", tsize=10.5, bsize=9)
    s.box(346, 258, 330, 52, title="SQLite (the app's own tables)", body=["claims · posts · runs (classifier, status)",
                                                                          "predictions: stance, confidence, model/human"],
          kind="grey", tsize=10.5, bsize=9)
    return s.render()


# =====================================================================================
# Chapter 20 — system design
# =====================================================================================
@fig
def sd_support():
    s = Svg(680, 356, "sdsup")
    s.rect(4, 4, 672, 66, fill="#f5f3ff", stroke="#c4b5fd", sw=1.1, rx=10)
    s.text(14, 21, "OFFLINE — re-run for an article whenever it changes", size=10, weight=700, anchor="start",
           color="#4c1d95")
    hchain(s, 14, 28, [("Help articles", [], "white", 104), ("Clean + split by section", [], "white", 164),
                       ("+ title, product, locale, date", [], "white", 188), ("Vector + BM25 index", [], "navy", 128)],
           h=32, gap=18, tsize=10)
    Y = 150
    xs = hchain(s, 10, Y, [("User", ["chat"], "white", 58), ("API", ["login →", "user_id"], "white", 70),
                           ("Rewrite", ["follow-up →", "standalone"], "white", 80),
                           ("Router", ["small, cheap", "model"], "purple", 78)], h=52, gap=18, tsize=10.5, bsize=8.8)
    rx, rw = xs[-1]
    bx, bw = 390, 178
    paths = [(84, "How-to / policy", ["hybrid search + rerank →", "answer with citations"], "blue"),
             (150, "\"Where is my order?\"", ["tool: order API, scoped to", "the logged-in user_id"], "green"),
             (216, "Refund fight / unsure", ["hand off to a human", "with a short summary"], "orange")]
    for y, t, b, k in paths:
        s.box(bx, y, bw, 52, title=t, body=b, kind=k, tsize=10.5, bsize=8.8)
        s.path(f"M {rx + rw + 3} {Y + 26} C {rx + rw + 20} {Y + 26}, {bx - 20} {y + 26}, {bx - 4} {y + 26}")
    s.box(592, 118, 82, 116, kind="red")
    s.text(633, 140, "Guardrails", size=10, weight=700, color="#7f1d1d")
    s.lines(633, 160, ["abstain if", "weak match,", "PII check,", "policy check"], size=9, lh=14,
            color="#7f1d1d")
    for y, *_ in paths:
        s.line(bx + bw + 3, y + 26, 588, min(max(y + 26, 128), 224), color="#94a3b8")
    s.text(633, 250, "streamed reply", size=9, weight=600, color="#334155")
    s.line(453, 72, 453, 82, color="#7c3aed", dash="3 3")
    s.rect(4, 272, 672, 78, fill="#f8fafc", stroke="#cbd5e1", sw=1.1, rx=10)
    s.text(14, 290, "ALWAYS ON — measure it", size=10, weight=700, anchor="start", color="#334155")
    s.lines(14, 308, ["Log every turn (PII redacted): question, retrieved articles, answer, route, latency, cost.",
                      "Metrics: solved without a human (containment), CSAT, faithfulness, correct hand-offs.",
                      "Questions with no good article = content gaps → the docs team writes them."],
            size=9.5, lh=14, anchor="start", color=INK)
    return s.render()


@fig
def sd_scale():
    s = Svg(680, 306, "sdscale")
    s.rect(4, 4, 672, 104, fill="#f5f3ff", stroke="#c4b5fd", sw=1.1, rx=10)
    s.text(14, 21, "INGESTION — batch + incremental, checkpointed (a crash resumes, never restarts)", size=10,
           weight=700, anchor="start", color="#4c1d95")
    hchain(s, 12, 32, [("10M docs", ["queue of", "doc ids"], "white", 76), ("Parse", ["OCR for scans,", "dedup by hash"], "white", 96),
                       ("Chunk", ["+ tenant, date,", "access list"], "white", 96),
                       ("Embed on GPUs", ["batched; skip", "unchanged docs"], "white", 110),
                       ("Sharded index", ["ANN (IVF-PQ / HNSW)", "+ BM25 per shard"], "navy", 142)],
           h=62, gap=20, tsize=10.5, bsize=8.8)
    s.rect(4, 120, 672, 104, fill="#eff6ff", stroke="#93c5fd", sw=1.1, rx=10)
    s.text(14, 137, "QUERY — budget ≈ 1–2 s before the first answer token", size=10, weight=700, anchor="start",
           color="#1e3a8a")
    hchain(s, 12, 150, [("Query", ["+ user's", "permissions"], "white", 72),
                        ("Rewrite", ["standalone,", "maybe 2–3 variants"], "white", 100),
                        ("Fan-out", ["hybrid top-100", "per shard, filtered"], "white", 104),
                        ("Merge (RRF)", ["→ rerank top-50", "(cross-encoder)"], "purple", 106),
                        ("LLM", ["top-8 chunks", "+ citations"], "navy", 82),
                        ("Answer", ["or abstain"], "green", 66)],
           h=62, gap=17, tsize=10.5, bsize=8.8)
    s.box(4, 236, 330, 64, title="Sizing (say it out loud)", body=["10M docs × ~10 chunks = 100M vectors",
                                                                    "× 768 × 4 bytes ≈ 307 GB as float32",
                                                                    "PQ at 64 bytes/vector ≈ 6.4 GB"],
          kind="yellow", tsize=10.5, bsize=9)
    s.box(346, 236, 330, 64, title="Keep it correct", body=["access filters inside the search, not after",
                                                             "deletes by doc id on every shard",
                                                             "recall@k checked against exact search"],
          kind="grey", tsize=10.5, bsize=9)
    return s.render()
