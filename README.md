# JavaScript — Explained Simply

**[JavaScript-Explained-Simply.pdf](JavaScript-Explained-Simply.pdf)** is a 166-page set of study notes for a student who
already knows C++ and is learning JavaScript. It covers Lectures 12 and 17–22 of the MERN course, plus the course code
for Day 17 to Day 22 from
[coderarmy-notes/mern-stack-course/03JS](https://github.com/coderarmy-notes/mern-stack-course/tree/main/03JS).

| Ch | Topic | Lecture | Code explained |
|---|---|---|---|
| 0 | JavaScript warm-up for a C++ brain | — | — |
| 1 | Array methods: `forEach`, `map`, `filter`, `reduce`, `find`, `some`, `every` | 12 | — |
| 2 | `Set` and `Map` | 12 | — |
| 3 | The event loop (call stack, Web APIs, microtasks and macrotasks) | 17 | Day 17 |
| 4 | Callbacks and callback hell (the Zomato order app) | 18 | Day 18 |
| 5 | Promises, `fetch`, chaining, `.finally` | 19 | Day 19 |
| 6 | JSON vs JavaScript objects | 19 | Day 19 |
| 7 | `async` / `await`, `Promise.all` | 20 | Day 20 |
| 8 | Prototypes and classes | 21 | Day 21 |
| 9 | Strict mode | 22 | Day 22 |
| 10 | `this`, `call` / `apply` / `bind`, arrow functions | 22 | Day 22 |
| 11 | Final revision: cheat sheets, rapid-fire questions, practice puzzles | all | all |

Each chapter has step-by-step explanations, C++ comparisons, diagrams, the real output of every example,
"Things to Remember" boxes and a quiz with answers. I ran the examples in Node.js and headless Chromium to get
the outputs shown in the notes.

## Rebuilding the PDF

The PDF is generated from the Markdown chapters in `notes-source/content/`.

Requirements: Python 3 with `markdown pygments pypdf reportlab pikepdf`, and Node.js with `playwright` and Chromium.

```bash
cd notes-source
./fonts/get_fonts.sh     # downloads Inter + JetBrains Mono (OFL) from Google Fonts
./make.sh ../JavaScript-Explained-Simply.pdf
```

`make.sh` renders the HTML with Chromium three times so that the page numbers in the table of contents are
correct. It then adds the running headers and page numbers. The diagrams are inline SVG, drawn in `diagrams.py`.
`tools/layout_check.py` scans a built PDF for text that overlaps other text or crosses the page margins.
