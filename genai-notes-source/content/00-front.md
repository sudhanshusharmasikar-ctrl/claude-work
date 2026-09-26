<h1 class="front">How to Use These Notes</h1>

Hello again! 👋 You finished JavaScript. Now we learn **Generative AI** — the way Rohit Negi teaches it in the **STRIKE GenAI** course, in **JavaScript**, from first principles. I am your teacher for the next **45 days**. My job is simple: by Day 45 you should be able to

1. **explain** how LLMs, RAG, vector databases, Graph RAG, vectorless RAG, agents and LangGraph work — in simple words, on a whiteboard;
2. **read and explain** the course code (Lecture 1 – Lecture 30) line by line;
3. **defend your three resume projects** — PaperRAG, SchemaMind and StanceScope — when an interviewer asks *why*, *how*, *what if*, *why not X* and *what next*.

We will **not** learn everything that exists in AI. The field is huge and your time is short. I picked only what AI-role interviews actually ask, and I marked every chapter with a priority tag:

| Tag | Meaning | If you are short on time |
|---|---|---|
| %%MUST%% | Asked in almost every GenAI interview, or needed for your projects | Never skip |
| %%GOOD%% | Makes your answers stronger; interviewers like it | Read once, revise the summary |
| %%OPT%% | Nice extra depth | Skip on the first pass |

### What is inside

| # | Chapter | Source | Priority |
|---|---|---|---|
| 1 | How LLMs really work: tokens, prediction, memory, cost | Lectures 1–3 + code | %%MUST%% |
| 2 | Inside the box: neural networks from C++, transformers in brief | Lectures 27–30 + C++ code | %%GOOD%% |
| 3 | Tools and function calling: your first AI agent | Lectures 4–5 + code | %%MUST%% |
| 4 | Agents that touch your computer: website builder and code reviewer | Lectures 6–7 + code | %%MUST%% |
| 5 | Agent design: patterns, memory, MCP and safety | extra reading | %%MUST%% |
| 6 | Embeddings: meaning as numbers | Lectures 8–9 | %%MUST%% |
| 7 | Vector databases and fast search: IVF, KD-tree, HNSW, PQ | Lectures 9–11 | %%MUST%% |
| 8 | RAG from zero | Lectures 12–13 + code | %%MUST%% |
| 9 | Making RAG good: follow-ups, hybrid search, reranking, chunking, evaluation | Lecture 14 + extra | %%MUST%% |
| 10 | Vectorless RAG (PageIndex and friends) | extra reading | %%GOOD%% |
| 11 | Graph databases and Cypher | Lectures 15–16 | %%GOOD%% |
| 12 | Graph RAG: the movie project | Lectures 17–19 + code | %%MUST%% |
| 13 | Microsoft GraphRAG and choosing the right RAG | extra reading | %%GOOD%% |
| 14 | LangGraph: workflows as state machines | Lectures 20–21 | %%MUST%% |
| 15 | Pause, resume and human-in-the-loop | Lectures 22–26 + docs | %%MUST%% |
| 16 | Multi-agent AI dev team | Lectures 22–26 + code | %%GOOD%% |
| 17 | **Your project: PaperRAG** | your repo | %%MUST%% |
| 18 | **Your project: SchemaMind** | your repo | %%MUST%% |
| 19 | Your project: StanceScope | your repo | %%GOOD%% |
| 20 | Interview question bank + system design | all | %%MUST%% |
| 21 | Final revision on a few pages + resources | all | %%MUST%% |

### How every chapter is organised

1. **Opener** — the dark box tells you what you will learn and which lecture it comes from.
2. **Idea first, code second** — every concept starts from a *problem* (first principles), then the solution, then the code.
3. **Diagrams** — whenever a picture is easier than words.
4. **Code from GitHub** — the course code, explained line by line. JavaScript code has a yellow tag, your Python projects a blue one.
5. **Things to Remember** — read these again before every interview.
6. **Quick Quiz + Answers**, and **Interview Questions** with model answers you can say out loud.

### The coloured boxes you will see

<div class="legend" markdown="1">

:::cpp
Connects the idea to C++ you already know (structs, pointers, `std::map`, function pointers…).
:::

:::remember
The must-not-forget points. Perfect for the last hour before an interview.
:::

:::mistake
A bug or misunderstanding that almost everyone has once.
:::

:::analogy
A real-life story (open-book exam, restaurant menu, library shelves…) that makes the idea obvious.
:::

:::interview
How an interviewer asks about this topic — and what a strong answer sounds like.
:::

:::honest
Where your project is not finished yet, and exactly how to say that without losing marks.
:::

:::build
A change to make in your project later, when we build it. Not now!
:::

:::security
Something that can hurt real users (leaked keys, deleted files, injected prompts).
:::

</div>

### How to run the course code

All course code is **Node.js with ES modules** (`"type": "module"` in `package.json`, so `import` works and top-level `await` is allowed).

```bash title="one-time setup for any lecture folder"
npm install                     # installs @google/genai, dotenv, readline-sync ...
echo "GEMINI_API_KEY=your_key_here" > .env
node index.js                   # or app.js / agent.js (the lecture's file)
```

:::security Keys belong in `.env`, never in code
Some course files (and one Notion page) had real-looking API keys typed straight into the code or the notes. In these notes **every key is replaced** by `process.env.SOMETHING`. Rules for your own projects: keep keys in `.env`, add `.env` to `.gitignore`, and if a key was ever pushed to GitHub, treat it as stolen — **revoke it and make a new one**. Deleting the line later does not help, because Git keeps history.
:::

:::note Model names change fast
The course uses `gemini-2.5-flash` for chat and `text-embedding-004` for embeddings. Google **shut down `text-embedding-004` on 14 January 2026**; the replacement is `gemini-embedding-001` (3072 numbers per vector by default). The later course lectures already use the new model. If a model name in any tutorial fails, check the provider's model list first — the idea stays the same even when the name changes.
:::

[[pagebreak]]

<h1 class="front">Your 45-Day Plan</h1>

About **3 hours a day** for this book, on top of your DSA practice. Every seventh day is revision. If a day goes badly, do not panic — skip the %%OPT%% parts and keep going.

<table class="plan">
<thead><tr><th>Day</th><th>Study</th><th>Do (hands-on / speaking)</th></tr></thead>
<tbody>
<tr><td colspan="3" class="week">Week 1 — LLM basics and your first agents</td></tr>
<tr><td>1</td><td>Front matter · the <b>Survival Kit</b> (next page) · Ch 1.1–1.4</td><td>Memorise the three 30-second project pitches — placements may start early</td></tr>
<tr><td>2</td><td>Ch 1.5–end (history, system instructions, thinking, tokens, cost)</td><td>Run Lecture 2 and Lecture 3 code</td></tr>
<tr><td>3</td><td>Ch 2 (neurons in C++, ReLU, transformers in brief)</td><td>Compile and run <code>first.cpp</code>; change the learning rate and watch</td></tr>
<tr><td>4</td><td>Ch 3 (function calling)</td><td>Run Lecture 5; add a third tool of your own</td></tr>
<tr><td>5</td><td>Ch 4 (website builder, code reviewer)</td><td>Run the code reviewer on a copy of an old project folder</td></tr>
<tr><td>6</td><td>Ch 5 (patterns, memory, MCP, security)</td><td>Say the OWASP top 3 risks out loud without looking</td></tr>
<tr><td>7</td><td><b>Revision</b>: Things to Remember + quizzes of Ch 1–5</td><td>Answer all Ch 1–5 interview questions aloud (record yourself)</td></tr>
<tr><td colspan="3" class="week">Week 2 — Embeddings, vector search, RAG</td></tr>
<tr><td>8</td><td>Ch 6 (embeddings, cosine vs Euclidean)</td><td>Compute one cosine similarity by hand</td></tr>
<tr><td>9</td><td>Ch 7.1–7.4 (brute force, IVF, KD-tree)</td><td>Draw IVF clusters from memory</td></tr>
<tr><td>10</td><td>Ch 7.5–end (HNSW, PQ, which vector DB)</td><td>Explain HNSW to a friend in 2 minutes</td></tr>
<tr><td>11</td><td>Ch 8 (RAG from zero)</td><td>Run Lecture 12–13 with <code>gemini-embedding-001</code></td></tr>
<tr><td>12</td><td>Ch 9.1–9.4 (follow-ups, multi-hop, hybrid search, reranking)</td><td>Write the RRF formula from memory</td></tr>
<tr><td>13</td><td>Ch 9.5–end (chunking, evaluation) · Ch 10 (vectorless RAG)</td><td>List 5 RAG failure modes + fixes</td></tr>
<tr><td>14</td><td><b>Revision</b> week 2 · first read of Ch 17 (PaperRAG pitch + architecture)</td><td>Explain PaperRAG's architecture on paper</td></tr>
<tr><td colspan="3" class="week">Week 3 — PaperRAG deep dive, graphs</td></tr>
<tr><td>15</td><td>Ch 17 (PaperRAG: design decisions)</td><td>Open your repo next to the chapter</td></tr>
<tr><td>16</td><td>Ch 17 (PaperRAG: why-not / what-if questions)</td><td>Answer 15 PaperRAG questions aloud</td></tr>
<tr><td>17</td><td>Ch 11 (graph databases, Cypher)</td><td>Write 5 Cypher queries for the movie graph on paper</td></tr>
<tr><td>18</td><td>Ch 12.1–12.5 (Graph RAG design, indexing)</td><td>Trace one movie from PDF to Neo4j</td></tr>
<tr><td>19</td><td>Ch 12.6–end (query pipeline, safe Cypher)</td><td>Trace "Movies like Inception" through the code</td></tr>
<tr><td>20</td><td>Ch 13 (Microsoft GraphRAG, which RAG when)</td><td>Draw the RAG decision flowchart from memory</td></tr>
<tr><td>21</td><td><b>Revision</b> week 3 · mock: PaperRAG in 2 minutes</td><td>Record it; listen; improve</td></tr>
<tr><td colspan="3" class="week">Week 4 — SchemaMind, LangGraph</td></tr>
<tr><td>22</td><td>Ch 18 (SchemaMind: pipeline, safety layers)</td><td>Open your repo next to the chapter</td></tr>
<tr><td>23</td><td>Ch 18 (SchemaMind: why-not / what-if questions)</td><td>Answer 15 SchemaMind questions aloud</td></tr>
<tr><td>24</td><td>Ch 14.1–14.4 (why LangGraph, nodes, edges, state, reducers)</td><td>Draw the PDF pipeline graph</td></tr>
<tr><td>25</td><td>Ch 14.5–end (batching, checkpointers, resume)</td><td>Explain thread_id and checkpoints to a friend</td></tr>
<tr><td>26</td><td>Ch 15 (interrupts, human-in-the-loop)</td><td>Write the interrupt/resume code from memory</td></tr>
<tr><td>27</td><td>Ch 16.1–16.4 (AI dev team architecture)</td><td>Draw the dev loop</td></tr>
<tr><td>28</td><td>Ch 16.5–end · <b>Revision</b> week 4</td><td>Answer all LangGraph interview questions aloud</td></tr>
<tr><td colspan="3" class="week">Week 5 — StanceScope and the question bank</td></tr>
<tr><td>29</td><td>Ch 19 (StanceScope)</td><td>30-second + 2-minute pitch, honest version</td></tr>
<tr><td>30</td><td>Ch 20.1–20.2 (LLM + prompting questions)</td><td>Rapid-fire: answer each in under 45 seconds</td></tr>
<tr><td>31</td><td>Ch 20.3–20.4 (RAG + vector DB questions)</td><td>Rapid-fire</td></tr>
<tr><td>32</td><td>Ch 20.5–20.6 (agents, LangGraph, evaluation, security)</td><td>Rapid-fire</td></tr>
<tr><td>33</td><td>Ch 20.7 (system design questions)</td><td>Design "customer-support RAG bot" on paper</td></tr>
<tr><td>34</td><td>Ch 20.7 again (text-to-SQL at company scale)</td><td>Design it on paper, 20 minutes</td></tr>
<tr><td>35</td><td><b>Mock interview 1</b> — your three projects</td><td>Ask a friend to use the project question lists</td></tr>
<tr><td colspan="3" class="week">Week 6 — Make it stick</td></tr>
<tr><td>36–37</td><td>Re-read every %%MUST%% section you marked as weak</td><td>Redo all quizzes</td></tr>
<tr><td>38</td><td>Course code tour: re-read the Code-from-GitHub boxes</td><td>Explain the Lecture 5 agent loop line by line</td></tr>
<tr><td>39–40</td><td>System design practice (3 designs in Ch 20)</td><td>Time yourself: 25 minutes each</td></tr>
<tr><td>41</td><td><b>Mock interview 2</b> — theory rapid-fire</td><td>50 questions from Ch 20</td></tr>
<tr><td>42</td><td><b>Mock interview 3</b> — projects, "what if" and "why not"</td><td>Focus on the questions you fumbled</td></tr>
<tr><td>43–44</td><td>Ch 21 revision sheets</td><td>One page per topic, from memory</td></tr>
<tr><td>45</td><td>Light revision, sleep early</td><td>Prepare 2 smart questions to ask the interviewer</td></tr>
</tbody>
</table>

[[pagebreak]]

<h1 class="front">Survival Kit: Before Your First Interview</h1>

Placements can start before you finish this book. Learn this page on **Day 1**. It lets you survive an early interview while the rest of the book makes you strong.

### Your three 30-second pitches

:::pitch PaperRAG — question answering over research papers
"PaperRAG answers questions about a folder of research papers and tells you **which file and which page** each answer came from. The key design choice is the chunking: I split PDFs along their **visual text blocks**, and a chunk never crosses a page, so every chunk carries exactly one page number — that is what makes page-level citation possible. It also **refuses to answer** when the best match is too weak, and that similarity cut-off is a setting I can sweep on a labelled question set to trade wrong answers against unnecessary refusals. Stack: Python, PyMuPDF, sentence-transformers, FAISS, FastAPI, Streamlit."
:::

:::pitch SchemaMind — plain English to SQL
"SchemaMind lets you ask a database a question in normal English and shows the answer **next to the SQL** that produced it. Instead of pasting the whole schema into the prompt, it **retrieves only the relevant tables** using embeddings, so the prompt stays small as the database grows. Safety is two independent layers: the SQL is **parsed into a syntax tree** with sqlglot and rejected unless it is a read, and the connection is opened **read-only**. If a query fails, the real database error goes back to the model, with a limit on retries."
:::

:::pitch StanceScope — claim analysis agent
"StanceScope takes a claim and a batch of social-media posts and reports how many **support, oppose or are neutral**, with the news evidence and the exact posts behind every number. It is a **LangGraph** pipeline with separate nodes for evidence retrieval, classification, human review and the report. When the classifier is unsure about a post, the graph **really pauses** with `interrupt()`, a person decides, and it resumes exactly where it stopped. Every prediction is stored with whether it came from the model or a human, so any number in the report can be audited. The classifier slot is built for my thesis **BERT + ViT** model; today a keyword placeholder runs there so the workflow can be tested end to end."
:::

### Five definitions you must say perfectly

| Term | One-line answer |
|---|---|
| **LLM** | A neural network trained to predict the next token; it generates text by repeating that prediction one token at a time. |
| **Token** | A small piece of text (a word, part of a word, or a symbol) — the unit the model reads, writes and bills you for. |
| **Embedding** | A list of numbers that represents the meaning of a text, so similar meanings give nearby vectors. |
| **RAG** | Retrieve relevant chunks from your own data, put them into the prompt, and let the LLM answer from them — an open-book exam. |
| **Agent** | An LLM in a loop that can call tools, look at the results, and decide the next step until the task is done. |

### Three honesty rules (they protect you)

1. **Never claim a number you did not measure.** "I built the evaluation script; I haven't run the full labelled set yet" is a strong answer. A made-up 92% is a trap — the next question will be "how did you measure it?".
2. **Know what is a placeholder.** StanceScope's classifier is currently a keyword stub, and SchemaMind's no-key "template mode" is not real text-to-SQL. Say so before they find it.
3. **"I don't know, but here is how I would find out"** beats guessing. Interviewers test *how you think*.

[[pagebreak]]

<h1 class="toc-title notoc">Contents</h1>

[[toc]]
