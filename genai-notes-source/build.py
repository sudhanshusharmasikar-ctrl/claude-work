#!/usr/bin/env python3
"""Build notes.html from content/*.md.

Mini-syntax on top of Markdown:
  ```js title="..." lines start=5 hl=2,4-6 break   -> highlighted code block
  ```output title="..."                             -> dark console block ("#>" starts a note)
  :::type Optional title  ...  :::                   -> callout box
      types: remember cpp mistake analogy tip deep quiz answer day def cols
  :::chapter N | Title | kicker   (bullet list)  ::: -> chapter opener
  [[fig:name|Caption]]                               -> SVG diagram from diagrams.py
  [[toc]]  [[pagebreak]]
"""
import html
import json
import pathlib
import re
import sys

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

import diagrams

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content"

LANG = {  # fence language -> (pygments lexer, label, css class)
    "js": ("javascript", "JavaScript", "js"),
    "cpp": ("cpp", "C++", "cpp"),
    "html": ("html", "HTML", "html"),
    "css": ("css", "CSS", "css"),
    "json": ("json", "JSON", "json"),
    "bash": ("bash", "Terminal", "bash"),
    "text": ("text", "Text", "text"),
    "pseudo": ("cpp", "Pseudo-code", "pseudo"),
    "py": ("python", "Python", "py"),
    "python": ("python", "Python", "py"),
    "sql": ("sql", "SQL", "sql"),
    "cypher": ("cypher", "Cypher (Neo4j)", "cypher"),
    "prompt": ("text", "Prompt", "prompt"),
    "env": ("bash", ".env file", "bash"),
}

BOX = {  # type -> (default title, icon)
    "remember": ("Things to Remember", "📌"),
    "cpp": ("C++ Corner", "🧠"),
    "mistake": ("Common Mistake", "⚠️"),
    "analogy": ("Real-Life Analogy", "💡"),
    "tip": ("Tip", "✅"),
    "deep": ("Deep Dive (optional)", "🔍"),
    "quiz": ("Quick Quiz", "🎯"),
    "answer": ("Answers", "✔️"),
    "day": ("Code from GitHub", "💻"),
    "def": ("Definition", "📖"),
    "note": ("Note", "📝"),
    "interview": ("Interview Angle", "🎤"),
    "honest": ("Say It Honestly", "🧭"),
    "build": ("When We Build the Project", "🛠️"),
    "security": ("Security Alert", "🔒"),
    "pitch": ("Your Pitch", "🗣️"),
}

PRIO = {"%%MUST%%": '<span class="prio must">must</span>',
        "%%GOOD%%": '<span class="prio good">good to know</span>',
        "%%OPT%%": '<span class="prio opt">optional</span>'}

stash = {}


def put(fragment):
    key = f"XSTASHX{len(stash)}X"
    stash[key] = fragment
    return key


def unstash(text):
    pat = re.compile(r"(?:<p>)?(XSTASHX\d+X)(?:</p>)?")
    for _ in range(10):
        new = pat.sub(lambda m: stash[m.group(1)], text)
        if new == text:
            break
        text = new
    if "XSTASHX" in text:
        raise SystemExit("unresolved stash key left in output")
    return text


def md(text):
    return markdown.markdown(
        text,
        extensions=["tables", "attr_list", "sane_lists", "smarty", "md_in_html"],
        output_format="html5",
    )


# ---------------------------------------------------------------- code blocks
def parse_info(info):
    parts = re.findall(r'([\w-]+)(?:=(?:"([^"]*)"|([^\s"]+)))?', info)
    lang = parts[0][0] if parts else "text"
    return lang, {k: (q or u) for k, q, u in parts[1:]}


def parse_hl(spec):
    out = []
    for piece in filter(None, spec.split(",")):
        if "-" in piece:
            a, b = piece.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(piece))
    return out


LONG = []


def render_code(lang, code, opts):
    title = opts.get("title", "")
    for ln in code.split("\n"):
        if len(ln) > 84:
            LONG.append(ln)
    classes = ["code"]
    if "break" in opts or code.count("\n") >= 34:
        classes.append("can-break")
    if lang == "output":
        body = []
        for line in code.split("\n"):
            esc = html.escape(line)
            m = re.search(r"\s*#&gt;\s?(.*)$", esc)
            if m:
                esc = esc[: m.start()] + f'<span class="ann">← {m.group(1)}</span>'
            body.append(esc if esc else " ")
        label = opts.get("label", "Output")
        head = f'<div class="code-head"><span class="chip">{label}</span>'
        head += f'<span class="title">{html.escape(title)}</span></div>' if title else "</div>"
        return (f'<div class="{" ".join(classes)} output">{head}'
                f'<pre>{chr(10).join(body)}</pre></div>')
    lexer_name, label, css = LANG[lang]
    fmt = HtmlFormatter(
        linenos="inline" if "lines" in opts else False,
        linenostart=int(opts.get("start", 1)),
        hl_lines=parse_hl(opts.get("hl", "")),
        cssclass="hl",
    )
    body = highlight(code, get_lexer_by_name(lexer_name), fmt)
    classes.append(css)
    head = f'<div class="code-head"><span class="chip">{label}</span>'
    head += f'<span class="title">{html.escape(title)}</span>' if title else ""
    head += "</div>"
    return f'<div class="{" ".join(classes)}">{head}{body}</div>'


FENCE = re.compile(r"^([ \t]*)```([^\n]*)\n(.*?)\n\1```[ \t]*$", re.M | re.S)


def stash_code(text):
    def repl(m):
        indent = m.group(1)
        lang, opts = parse_info(m.group(2).strip())
        code = "\n".join(l[len(indent):] if l.startswith(indent) else l.lstrip()
                         for l in m.group(3).split("\n"))
        return "\n\n" + indent + put(render_code(lang, code, opts)) + "\n\n"
    return FENCE.sub(repl, text)


# ----------------------------------------------------------------- directives
CHAPTER = re.compile(r"^:::chapter[ \t]+(.*?)\n(.*?)\n:::[ \t]*$", re.M | re.S)
BOXRE = re.compile(r"^:::(\w+)(?:[ \t]+([^\n]*))?\n(.*?)\n:::[ \t]*$", re.M | re.S)
FIG = re.compile(r"^\[\[fig:([\w-]+)(?:\|(.*?))?\]\][ \t]*$", re.M)

state = {"chapter": "0", "fig": 0, "q": 0}


def chapter_block(m):
    num, title, kicker = [s.strip() for s in m.group(1).split("|")]
    state["chapter"], state["fig"], state["q"] = num, 0, 0
    learn = md(m.group(2))
    label = f"Chapter {num}" if num.isdigit() else num
    return "\n\n" + put(
        f'<section class="opener">'
        f'<div class="kicker"><span class="num">{html.escape(label)}</span>'
        f'<span class="src">{html.escape(kicker)}</span></div>'
        f'<h1 class="chapter" data-label="{html.escape(label)}">{html.escape(title)}</h1>'
        f'<div class="learn"><div class="learn-title">In this chapter you will learn</div>{learn}</div>'
        f"</section>"
    ) + "\n\n"


QLINE = re.compile(r"^Q:[ \t]*(.*)$", re.M)


def qa_block(title, body):
    parts = QLINE.split(body)
    items = []
    for i in range(1, len(parts), 2):
        q, a = parts[i].strip(), parts[i + 1].strip()
        state["q"] += 1
        long = len(a) > 1100 or "XSTASHX" in a
        items.append(
            f'<div class="qa{" long" if long else ""}"><div class="q"><span class="qn">Q{state["q"]}</span>'
            f'<span>{md(q)[3:-4]}</span></div><div class="a">{md(a)}</div></div>')
    head = f'<div class="qa-head">{md(title)[3:-4]}</div>' if title else ""
    return "\n\n" + put(f'<div class="qa-set">{head}{"".join(items)}</div>') + "\n\n"


def box_block(m):
    kind, title, body = m.group(1), (m.group(2) or "").strip(), m.group(3)
    if kind == "qa":
        return qa_block(title or "Interview Questions", body)
    if kind == "cols":
        cols = re.split(r"^\|\|\|[ \t]*$", body, flags=re.M)
        inner = "".join(f'<div class="col">{md(c)}</div>' for c in cols)
        return "\n\n" + put(f'<div class="cols">{inner}</div>') + "\n\n"
    default, icon = BOX[kind]
    title = title or default
    can_break = " can-break" if title.endswith("!break") else ""
    title = title.replace("!break", "").strip()
    return "\n\n" + put(
        f'<div class="box {kind}{can_break}"><div class="box-title">'
        f'<span class="icon">{icon}</span>{md(title)[3:-4]}</div>'
        f'<div class="box-body">{md(body)}</div></div>'
    ) + "\n\n"


def fig_block(m):
    name, caption = m.group(1), (m.group(2) or "").strip()
    svg = diagrams.FIGS[name]()
    state["fig"] += 1
    cap = ""
    if caption:
        cap = (f'<figcaption><b>Figure {state["chapter"]}.{state["fig"]}</b> '
               f'{md(caption)[3:-4]}</figcaption>')
    return "\n\n" + put(f'<figure class="diagram" id="fig-{name}">{svg}{cap}</figure>') + "\n\n"


def convert_file(text):
    text = stash_code(text)
    text = CHAPTER.sub(chapter_block, text)
    text = FIG.sub(fig_block, text)
    text = BOXRE.sub(box_block, text)
    text = text.replace("[[pagebreak]]", put('<div class="pagebreak"></div>'))
    text = text.replace("[[toc]]", put("@@TOC@@"))
    out = md(text)
    for k, v in PRIO.items():
        out = out.replace(k, v)
    return out


# ------------------------------------------------------------------------ TOC
def number_headings(doc):
    counter = {"n": 0}
    heads = []

    def repl(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        counter["n"] += 1
        hid = f"h{counter['n']}"
        cls = re.search(r'class="([^"]*)"', attrs or "")
        label = re.search(r'data-label="([^"]*)"', attrs or "")
        heads.append({
            "id": hid, "level": int(level),
            "text": html.unescape(re.sub(r"<[^>]+>", "", re.sub(r'<span class="prio[^"]*">.*?</span>', "", inner))).strip(),
            "html": inner.strip(),
            "cls": cls.group(1) if cls else "",
            "label": label.group(1) if label else "",
        })
        attrs = re.sub(r'\s*id="[^"]*"', "", attrs or "")
        return f'<h{level} id="{hid}"{attrs}>{inner}</h{level}>'

    doc = re.sub(r"<h([123])([^>]*)>(.*?)</h\1>", repl, doc, flags=re.S)
    return doc, heads


def build_toc(heads, pages):
    rows = []
    for h in heads:
        if "notoc" in h["cls"] or h["level"] == 3:
            continue
        pg = pages.get(h["id"], "")
        if h["level"] == 1:
            label = f'<span class="toc-num">{html.escape(h["label"])}</span>' if h["label"] else ""
            rows.append(
                f'<a class="toc-row toc-ch" href="#{h["id"]}">{label}'
                f'<span class="toc-text">{h["html"]}</span><span class="toc-dots"></span>'
                f'<span class="toc-pg">{pg}</span></a>')
        else:
            rows.append(
                f'<a class="toc-row toc-sec" href="#{h["id"]}"><span class="toc-text">{h["html"]}</span>'
                f'<span class="toc-dots"></span><span class="toc-pg">{pg}</span></a>')
    return '<div class="toc">' + "\n".join(rows) + "</div>"


def main():
    pages = {}
    if len(sys.argv) > 1 and pathlib.Path(sys.argv[1]).exists():
        pages = json.loads(pathlib.Path(sys.argv[1]).read_text())
    parts = []
    for f in sorted(CONTENT.glob("*.md")):
        parts.append(f'<div class="file" data-src="{f.name}">' + convert_file(f.read_text()) + "</div>")
    doc = unstash("\n".join(parts))
    doc = re.sub(r"<table>(.*?)</table>",
                 lambda m: ('<table class="keep">' if m.group(1).count("<tr") <= 12 else "<table>")
                 + m.group(1) + "</table>", doc, flags=re.S)
    for ln in LONG:
        print("LONG CODE LINE:", len(ln), ln)
    doc, heads = number_headings(doc)
    doc = doc.replace("@@TOC@@", build_toc(heads, pages))
    cover = (ROOT / "cover.html").read_text()
    tpl = (ROOT / "template.html").read_text()
    out = tpl.replace("{{COVER}}", cover).replace("{{BODY}}", doc)
    (ROOT / "notes.html").write_text(out)
    (ROOT / "headings.json").write_text(json.dumps(heads, indent=1, ensure_ascii=False))
    print(f"built notes.html: {len(heads)} headings, {len(stash)} blocks")


if __name__ == "__main__":
    main()
