# Study notes — Explained Simply

Study guides for a student who already knows C++:

| PDF | What it covers | Pages |
|---|---|---|
| **[GenAI-RAG-Agents-Explained-Simply.pdf](GenAI-RAG-Agents-Explained-Simply.pdf)** | Generative AI, agents, RAG, vector databases, vectorless RAG, Graph RAG and LangGraph (STRIKE GenAI Lectures 1–30), interview prep for the PaperRAG, SchemaMind and StanceScope projects, and a 45-day plan | 218 |
| **[Projects-Explained-PaperRAG-SchemaMind.pdf](Projects-Explained-PaperRAG-SchemaMind.pdf)** | A beginner's picture guide to the PaperRAG and SchemaMind projects as they are after build sessions 1–7: 13 pipeline diagrams, each step tied to its file in the code, PaperRAG's real evaluation results, and 74 how / why / what-if / why-not questions with answers | 36 |
| **[Lecture-QA-Interview-Practice.pdf](Lecture-QA-Interview-Practice.pdf)** | 52 interview questions with answers for the STRIKE GenAI lectures finished so far: Lectures 8–16 (embeddings, vector search, RAG, advanced RAG, graph databases) and 20–21 (LangGraph) | 12 |
| **[JavaScript-Explained-Simply.pdf](JavaScript-Explained-Simply.pdf)** | JavaScript Lectures 12 and 17–22 of the MERN course, plus the Day 17–22 code | 166 |

## GenAI, RAG & Agents — Explained Simply

Placement preparation for AI roles, planned as 45 days of about 3 hours a day. It explains the course code from
[Rohitnegi9/STRIKEGenAI](https://github.com/Rohitnegi9/STRIKEGenAI) (Lectures 1–30, JavaScript) line by line, then
walks through three resume projects and the interview questions they invite: *why*, *how*, *what if*, *why not* and
*what next*.

| Ch | Topic | Source |
|---|---|---|
| — | How to use the notes, the 45-day plan, a Day-1 survival kit (three 30-second pitches) | — |
| 1 | How LLMs work: tokens, prediction, memory, cost | Lectures 1–3 + code |
| 2 | Neural networks from C++, transformers in brief | Lectures 27–30 + C++ code |
| 3 | Tools and function calling: the first agent | Lectures 4–5 + code |
| 4 | Agents that touch your computer: website builder and code reviewer | Lectures 6–7 + code |
| 5 | Agent design: patterns, memory, MCP, OWASP LLM Top 10 | extra reading |
| 6 | Embeddings; cosine vs Euclidean | Lectures 8–9 |
| 7 | Vector databases: brute force, IVF, KD-tree, HNSW, PQ | Lectures 9–11 |
| 8 | RAG from zero | Lectures 12–13 + code |
| 9 | Making RAG good: query rewriting, hybrid search, reranking, chunking, evaluation | Lecture 14 + extra |
| 10 | Vectorless RAG (PageIndex) | extra reading |
| 11 | Graph databases and Cypher | Lectures 15–16 |
| 12 | Graph RAG: the movie project | Lectures 17–19 + code |
| 13 | Microsoft GraphRAG and choosing the right retrieval | extra reading |
| 14 | LangGraph: workflows as state machines | Lectures 20–21 + code |
| 15 | Pause, resume and human-in-the-loop | Lectures 22–26 + docs |
| 16 | The multi-agent AI dev team | Lectures 22–26 + code |
| 17 | **PaperRAG**: pitches, code walkthrough, design decisions, a tested two-column bug and its fix, 31 questions | your repo |
| 18 | **SchemaMind**: text-to-SQL, both safety layers attacked and tested, silent wrong answers, 38 questions | your repo |
| 19 | **StanceScope**: LangGraph interrupt, bugs found by running it, BERT + ViT in one page, 18 questions | your repo |
| 20 | Interview bank (71 rapid-fire questions) and three system designs | all |
| 21 | Seven one-page revision sheets, code to write from memory, resources, last-week checklist | all |

**What was checked.** The outputs printed in the notes come from running the code:
- the course's JavaScript, with model calls mocked where they needed an API key;
- the C++ programs;
- LangGraph JS 1.4.18 and LangGraph Python 1.2.12;
- the scripts in [`genai-notes-source/verify/`](genai-notes-source/verify/), run against the three project repos (the SchemaMind validator was tested on sqlglot 26, 28, 29 and 30.19).

The project chapters describe the code as it is today, including what is still a placeholder or not yet measured. Every API key that appeared in the course material is replaced by a `process.env` name.

### Rebuilding the GenAI PDF

Requirements: Python 3 with `markdown pygments pypdf reportlab pikepdf` (plus `pymupdf pillow` for the tools in
`tools/`), and Node.js with `playwright` and Chromium.

```bash
cd genai-notes-source
./fonts/get_fonts.sh     # downloads Inter + JetBrains Mono (OFL) from Google Fonts
./make.sh ../GenAI-RAG-Agents-Explained-Simply.pdf
python3 tools/layout_check.py ../GenAI-RAG-Agents-Explained-Simply.pdf   # overlaps / margins
python3 tools/svg_bounds.py                                              # diagram clipping
```

## Projects Explained — PaperRAG & SchemaMind

**[Projects-Explained-PaperRAG-SchemaMind.pdf](Projects-Explained-PaperRAG-SchemaMind.pdf)** explains the two main
resume projects from zero, for someone seeing them for the first time. It describes the code in
[paperrag](https://github.com/sudhanshusharmasikar-ctrl/paperrag) and
[schemamind](https://github.com/sudhanshusharmasikar-ctrl/schemamind) after build sessions 1–7, so where it differs
from Chapters 17–18 of the GenAI PDF (written earlier), this guide is the current one.

| Part | Topic | Figures | Questions |
|---|---|---|---|
| 1 | **PaperRAG**: the pipeline in one picture, then each step: text blocks, two-column reading order, chunks and overlap, embeddings, the FAISS index, the "I don't know" guard, the answer; how the web page and server talk; tests, the real evaluation (51 questions, the threshold sweep, what went wrong) and what each session fixed | 7 | 33 |
| 2 | **SchemaMind**: the shop database, the pipeline, table cards, picking tables, template and Mistral SQL, the sqlglot validator, the three safety layers, the repair loop; tests, evaluation and what each session fixed | 5 | 30 |
| 3 | Both projects side by side, one-minute explanations, questions about both (including the CI that tests them), and a glossary | 1 | 11 |

Outputs marked "real" were produced by running the project code (the SchemaMind answers come from the seeded
`data/shop.db`); scores marked "example" are illustrations, because the real ones depend on the papers you index.

The guide uses the GenAI toolchain. Its Markdown is in `genai-notes-source/projects-booklet/content/` and its
diagrams are in `projects-booklet/figures.py`. To rebuild it:

```bash
cd genai-notes-source
./fonts/get_fonts.sh     # once
./projects-booklet/make.sh ../Projects-Explained-PaperRAG-SchemaMind.pdf
```

## Lecture Q&A — Interview Practice

**[Lecture-QA-Interview-Practice.pdf](Lecture-QA-Interview-Practice.pdf)** collects the interview questions and answers
from the study sessions, for the lectures finished so far:

| Part | Lectures | Topics | Questions |
|---|---|---|---|
| 1 | 8–16 | Embeddings, vector search (brute force, IVF, KD-tree, HNSW, PQ), RAG, advanced RAG, graph databases | 31 |
| 2 | 20–21 | LangGraph: state, reducers, checkpointers, resuming after a crash, the three pipeline designs, StanceScope | 21 |

Each question has a page tag that points to the page of the GenAI PDF where the topic is explained. The answers
that say "I tested it" were checked by running LangGraph JS 1.4.18.

The booklet uses the GenAI toolchain. Its Markdown is in `genai-notes-source/qa-booklet/content/`, and
`qa-booklet/book.json` sets its header, footer and PDF metadata. To rebuild it:

```bash
cd genai-notes-source
./fonts/get_fonts.sh     # once
./qa-booklet/make.sh ../Lecture-QA-Interview-Practice.pdf
```

## JavaScript — Explained Simply

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

### Rebuilding the JavaScript PDF

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
