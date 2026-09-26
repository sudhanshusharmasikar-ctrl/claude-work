:::chapter 17 | Your Project: PaperRAG | github.com/sudhanshusharmasikar-ctrl/paperrag · Most important
- Your **30-second and 2-minute** pitches
- The architecture, file by file, with the key code
- Every **design decision** and what you rejected
- An honest **resume-bullet check** (what's true today, what needs a fix)
- The **two-column bug** — tested, with a tested fix
- What to do **when we build** (priority list)
- 31 interview questions: **why, how, what if, why not, what next**
:::

This is your strongest project for AI roles: it's small enough to explain fully, and every part has a **reason**. Read this chapter with your repo open. By the end you should be able to defend every line.

## 17.1 Your pitch %%MUST%%

:::pitch 30 seconds
"PaperRAG answers questions over a folder of research papers and cites the **file and page** for every answer. I chunk PDFs along PyMuPDF's **text blocks**, never crossing a page, so every chunk carries one page number — that's what makes page-level citation possible. It **refuses to answer** when the best match is too weak, with a second check for passages that are on-topic but don't contain the answer, and the similarity cut-off is a setting I can sweep on a labelled question set."
:::

:::pitch 2 minutes (problem → approach → decisions → evaluation → next) !break
**Problem.** Generic RAG demos answer everything confidently and can't tell you *where* in a paper the answer is. For research papers you need page-level citations and honest "I don't know"s.

**Approach.** Indexing: PyMuPDF extracts text **blocks** per page; I clean ligatures and hyphenation, drop noise like page numbers and table rows, and pack whole blocks into chunks of up to ~900 characters that **never cross a page**. Each chunk is embedded with all-MiniLM-L6-v2 (384-d, normalised) into a FAISS `IndexFlatIP` — exact cosine search. Query: embed the question, take the top-5, and apply **two guards**: if the top-1 similarity is below a threshold, abstain; otherwise generate — either **extractive** (return passages verbatim, no key needed) or with **Mistral**, whose prompt forces `[n]` citations and allows `INSUFFICIENT_CONTEXT`.

**Decisions.** Exact search because the corpus is small; threshold on top-1 because the mean of top-k drifts with k; extractive default so the demo is free and gives a 100%-faithful baseline.

**Evaluation.** An eval script measures unsupported-answer rate with and without the guard, false-refusal rate and citation hit rate, and sweeps the threshold. *(Say honestly whether you've run it on your labelled set yet.)*

**Next.** Hybrid BM25 + vectors, a cross-encoder reranker, OCR/table handling.
:::

## 17.2 Architecture %%MUST%%

[[fig:paperrag-arch|PaperRAG: layout-aware indexing, exact cosine retrieval, and two independent abstention guards.]]

| File | Job |
|---|---|
| `app/config.py` | Every tunable number, with a comment explaining **why** (env-var overridable) |
| `app/chunking.py` | PDF → cleaned text blocks → page-bounded chunks |
| `app/index.py` | Embed chunks, build/save/load the FAISS index + `chunks.jsonl` |
| `app/retrieve.py` | Search + the **retrieval-side guard** (top-1 threshold) |
| `app/generate.py` | Extractive or Mistral answers + the **generation-side guard** |
| `app/api.py` | FastAPI: `/health`, `/ask` (validated input, latency) |
| `ui/streamlit_app.py` | UI that talks to the **API** over HTTP (proves the API works) |
| `eval/run_eval.py` | Labelled evaluation + threshold sweep |

## 17.3 The code, file by file %%MUST%%

### `config.py` — numbers you must know

```python title="app/config.py (key lines)"
CHUNK_CHARS = int(os.getenv("PAPERRAG_CHUNK_CHARS", 900))
CHUNK_OVERLAP = int(os.getenv("PAPERRAG_CHUNK_OVERLAP", 150))
MIN_CHUNK_CHARS = 120        # drop headers, page numbers, stray figure labels
EMBED_MODEL = os.getenv("PAPERRAG_EMBED_MODEL",
                        "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = 384
TOP_K = int(os.getenv("PAPERRAG_TOP_K", 5))
SIM_THRESHOLD = float(os.getenv("PAPERRAG_SIM_THRESHOLD", 0.35))  # sweep it!
GEN_MODE = os.getenv("PAPERRAG_GEN_MODE", "extractive")           # or "mistral"
```

Why 900 characters? The config comment: chunk size is in **characters** so ingestion doesn't depend on a tokenizer, and **MiniLM truncates at 256 word-pieces (~1000 characters of English)** — anything much above that would be silently cut off before embedding.

### `chunking.py` — the heart of the project

```python title="app/chunking.py — cleaning and noise filtering"
_LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "’": "'", "–": "-", ...}

def clean(text: str) -> str:
    for bad, good in _LIGATURES.items():
        text = text.replace(bad, good)
    text = re.sub(r"-\n(?=[a-z])", "", text)     # "multi-\nmodal" -> "multimodal"
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def _is_noise(block_text: str) -> bool:
    t = block_text.strip()
    if len(t) < 25:                                  # tiny fragments
        return True
    if re.fullmatch(r"[\d\s\-–.ivxlIVXL]+", t):      # page numbers, roman numerals
        return True
    alpha = sum(c.isalpha() for c in t)
    return alpha / max(len(t), 1) < 0.45             # mostly digits = a table row
```

- **Ligatures** (`ﬁ` as one character) and **hyphenated line breaks** corrupt words; fixing them improves embedding quality ("multi-\nmodal" would otherwise be two odd tokens).
- The noise filter drops running headers, page numbers and **table rows** (under 45% letters). Trade-off: numeric questions answered only inside tables will fail — a documented limitation.

```python title="app/chunking.py — blocks per page, packed into chunks (condensed)"
def page_blocks(page) -> list[str]:
    raw = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
    text_blocks = [b for b in raw if len(b) > 6 and b[6] == 0]   # 0 = text block
    # sort top-to-bottom, then left-to-right; handles two-column papers
    text_blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))
    out = []
    for b in text_blocks:
        t = clean(b[4])
        if t and not _is_noise(t):
            out.append(t)
    return out

def chunk_pdf(path: Path) -> list[Chunk]:
    chunks = []
    with fitz.open(path) as doc:
        for page_no, page in enumerate(doc, start=1):
            blocks = page_blocks(page)
            if not blocks:
                continue  # scanned page with no text layer; see README on OCR
            for i, text in enumerate(_pack(blocks)):      # packing is PER PAGE
                if len(text) < MIN_CHUNK_CHARS:
                    continue
                chunks.append(Chunk(chunk_id=f"{path.stem}::p{page_no}::c{i}",
                                    doc_id=path.stem, source=path.name,
                                    page=page_no, text=text))
    return chunks
```

- A PyMuPDF **block** is roughly a visual paragraph with its bounding box.
- `_pack(blocks)` greedily joins **whole blocks** up to `CHUNK_CHARS`, carrying the last `CHUNK_OVERLAP` characters into the next chunk; a single huge block is split on **sentence** boundaries.
- Because `_pack` runs **per page**, a chunk can never span two pages → **every chunk has exactly one page number**. Chunk ids look like `tmpt::p7::c2`.
- The sort line is where a real bug lives: its comment says it "handles two-column papers", but it doesn't — Section 17.5 proves it.

### `index.py` — exact cosine search

```python title="app/index.py (key lines)"
def get_model():
    """Load once per process. Loading MiniLM takes ~2s; doing it per request
    is the single most common performance bug in a RAG demo."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def embed(texts):
    vecs = get_model().encode(texts, batch_size=EMBED_BATCH, convert_to_numpy=True,
                              normalize_embeddings=True)   # required: IP == cosine
    return vecs.astype("float32")

index = faiss.IndexFlatIP(vecs.shape[1])     # exact inner-product search
index.add(vecs)
faiss.write_index(index, str(INDEX_PATH))    # + chunks.jsonl, one row per vector
```

On load, it checks `index.ntotal == len(chunks)` — if the vector file and the chunk file are out of sync, row *i* would point to the wrong text, so it refuses to start.

### `retrieve.py` — the first guard

```python title="app/retrieve.py — Retriever.__call__ (condensed)"
if not query.strip():
    return Retrieval(query, [], 0.0, True, threshold)       # empty → abstain
qv = embed([query])
scores, idxs = self.index.search(qv, min(top_k, self.index.ntotal))
hits = []
for score, i in zip(scores[0], idxs[0]):
    if i < 0:
        continue                  # FAISS pads with -1 when it has < k results
    c = self.chunks[int(i)]       # row i of chunks.jsonl ↔ vector i
    hits.append(Hit(chunk_id=c["chunk_id"], source=c["source"],
                    page=int(c["page"]), text=c["text"], score=float(score)))
top = hits[0].score if hits else 0.0          # results come sorted: best first
return Retrieval(query=query, hits=hits, top_score=top,
                 abstain=top < threshold, threshold=threshold)
```

The guard uses the **top-1** score. Why not the average of the top-k? Because the average **drops as k grows**, so the right threshold would silently depend on k — impossible to sweep cleanly.

### `generate.py` — the second guard

```prompt title="SYSTEM_PROMPT in app/generate.py"
You answer questions strictly from the numbered context passages provided.
Rules:
- Use only the passages. Never add facts from your own knowledge.
- Cite the passage number in square brackets after each claim, like [2].
- If the passages do not contain the answer, reply exactly:
  INSUFFICIENT_CONTEXT
- Be concise. Three sentences unless the question demands more.
```

- **Extractive mode** (default): return the top passages verbatim with `file p.N (similarity 0.xxx)` — no key, no cost, **100% faithful by construction**, and a baseline to compare the LLM against.
- **Mistral mode**: passages numbered `[1] (paper.pdf p.7) …`, `temperature 0.0`, and if the reply contains `INSUFFICIENT_CONTEXT` the system abstains — this catches questions whose passages are **on-topic but don't contain the answer**, which a similarity threshold can't detect.

### `api.py` and the UI

- FastAPI **lifespan** loads the model and index **once** at startup; `/health` reports chunks, mode and threshold; `/ask` validates input with Pydantic (question 3–1000 chars, `top_k` 1–20, threshold −1…1, mode `extractive|mistral`) and returns latency.
- The Streamlit UI calls the API over HTTP with sliders for top-k and threshold — so the demo **proves the API works**, and lets you show the threshold trade-off live.

### `eval/run_eval.py` — how the numbers are made

- You write `questions.jsonl`: **answerable** questions (with expected file + page) and **unanswerable** ones (on-topic but not in your papers) — aim for 40–60, at least a third unanswerable.
- Metrics: **unsupported answers before** the guard (every unanswerable question is answered), **after** the guard, **false-refusal rate**, **citation hit rate** (does any retrieved hit match the expected page?).
- `--sweep` runs thresholds from 0.20 to 0.66 in steps of 0.02 — the curve **is** the finding.

## 17.4 Design decisions (memorise this table) %%MUST%%

| Choice | Why | Rejected |
|---|---|---|
| `IndexFlatIP` (exact) | Tens of thousands of vectors search in milliseconds; perfect recall; no tuning | IVF/HNSW — recall loss and knobs for a speed problem I don't have |
| MiniLM-L6-v2 (384-d) | ~80 MB, fast on CPU, deploys on a free tier | Bigger embedders — better recall, heavier deployment |
| Normalised vectors | Inner product = cosine | Raw vectors (length would affect scores) |
| Block-level, page-bounded chunks | Keeps page numbers and paragraphs intact | Fixed-size split over the whole document — destroys citability |
| Threshold on **top-1** | Independent of k; sweepable | Mean/median of top-k |
| Extractive default | Free, always works, faithful baseline | LLM-only — nothing to compare faithfulness against |
| Two independent guards | Catch different failures (off-topic vs on-topic-but-missing) | Only a prompt instruction |
| No framework (no LangChain) | Every step is visible and explainable | Faster to start, harder to explain and debug |
| API + separate UI | The UI exercises the real API | UI importing the pipeline directly |

## 17.5 The two-column bug (tested) and its fix %%MUST%%

The README and your resume say two-column papers "stay in reading order". The code sorts blocks by **(top y, then left x)**:

```python title="the current sort in page_blocks()"
text_blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))   # y first, then x
```

On a two-column page this **interleaves** the columns — left paragraph, right paragraph, left, right — whenever the right column's paragraphs start at different heights. I generated a two-column PDF and ran your real `page_blocks()`:

```output title="python twocol_test.py  (your chunking.py vs a column-aware sort)"
PaperRAG order : ['TITLE:', 'L1', 'R1', 'L2', 'R2', 'L3', 'R3']  #> interleaved
Column-aware   : ['TITLE:', 'L1', 'L2', 'L3', 'R1', 'R2', 'R3']  #> reading order
```

Why it matters: `_pack` joins blocks **in this order**, so chunks mix sentences from both columns, a paragraph that continues from the bottom of the left column to the top of the right column gets split in the wrong place, and embeddings get noisier. The fix (tested on the same PDF):

```python title="column-aware reading order (drop-in replacement for the sort)"
def reading_order(page, blocks):
    mid = page.rect.width / 2
    def key(b):
        x0, y0, x1 = b[0], b[1], b[2]
        if x0 < mid - 20 and x1 > mid + 20:
            col = 0            # spans both columns: title, wide figure caption
        elif x1 <= mid + 20:
            col = 1            # left column
        else:
            col = 2            # right column
        return (col, y0, x0)
    return sorted(blocks, key=key)
```

Known limits of this simple fix: a full-width block **in the middle** of a page (a wide figure) is moved to the top; three-column layouts need a more general method. For harder PDFs, layout-analysis tools exist (e.g. `pymupdf4llm` or layout models). In an interview, this is a **great** story: *"I found that my sort interleaved columns, wrote a test PDF to prove it, and fixed it with a column-aware key."*

## 17.6 Honest resume-bullet check %%MUST%%

| Resume bullet | True today? | What to say |
|---|---|---|
| "Answer that tells you which file and which page it came from" | ✅ Yes — every hit carries `source` + `page` | "Citations come from chunk metadata, not from the LLM." |
| "Splits each PDF along its visual paragraphs … so no chunk spans two pages" | ✅ Mostly — chunks are packed from **whole** blocks up to ~900 chars, per page | "Chunks are built from whole PyMuPDF blocks, packed up to ~900 characters, never across a page." |
| "…and two-column papers stay in reading order" | ❌ **Not yet** — the sort interleaves columns (17.5) | Fix it before interviews, or drop this phrase. |
| "Says 'I don't know' … with a second check for on-topic passages that don't contain the answer" | ✅ Yes — but the second check runs **only in Mistral mode** | "The second guard needs generation mode; extractive mode relies on the threshold." |
| "Exposes the similarity cut-off … measured on a labelled question set" | ✅ The **capability** exists (env var, API, UI slider, sweep script) | Don't quote numbers until you've run your labelled set. |

:::honest If they ask for results before you've run the evaluation
"The evaluation harness is built — it measures unsupported-answer rate with and without the guard, false refusals and citation hit rate, and sweeps the threshold. I haven't finalised my labelled question set yet, so I don't want to quote numbers I haven't measured. The design expectation is a clear trade-off curve: raising the threshold cuts unsupported answers but increases false refusals." — Honest, specific, and shows you know **how** it will be measured.
:::

## 17.7 When we build: the priority list %%MUST%%

:::build Do these in this order (later, when we build together)
1. **Fix the two-column sort** (17.5) + add the test PDF as a unit test.
2. **Write 40–60 labelled questions** (≥ ⅓ unanswerable, with expected pages), run `--sweep`, pick a threshold, fill the README table. Only then put numbers on the resume.
3. **Cite only what the model cited**: in Mistral mode, parse the `[n]` markers and return only those citations (today all top-k hits are listed).
4. **Hybrid search**: add BM25 (e.g. `rank_bm25`) and fuse with RRF; measure citation hit rate before/after.
5. **Reranker**: retrieve 20, rerank with a cross-encoder, keep 5; measure again.
6. **Tables and scanned PDFs**: PyMuPDF's table detection and an OCR fallback for pages without a text layer.
:::

## 17.8 Interview questions — the "why" questions %%MUST%%

:::qa Why did you build it this way?
Q: Why did you build PaperRAG?
Because generic RAG demos answer everything confidently and can't point to the source page. For research papers you need verifiable, page-level citations and an honest "I don't know". I wanted a system where every design choice is explainable and measurable.

Q: Why chunk by PDF blocks instead of fixed character counts?
Fixed-size splitting over the whole document crosses page boundaries and cuts paragraphs in half, so you can't cite a page and embeddings mix topics. Blocks follow the visual paragraphs; packing whole blocks per page keeps one page number per chunk.

Q: Why 900 characters with 150 overlap?
MiniLM reads about 256 word-pieces (~1000 characters); longer text is truncated before embedding, so bigger chunks would waste text. 900 leaves margin. The 150-character overlap keeps a sentence that falls on a chunk edge retrievable from at least one side. Both are env-configurable to tune on the eval set.

Q: Why FAISS IndexFlatIP and not HNSW or a vector database?
The corpus is small — tens of thousands of vectors — so exact search takes milliseconds on a CPU with perfect recall and no tuning. HNSW would add approximation and parameters to solve a speed problem I don't have. A vector database adds a server; FAISS plus a JSONL file is enough. At millions of chunks I'd switch and measure recall against the flat index.

Q: Why normalise embeddings?
With unit-length vectors, inner product equals cosine similarity, so IndexFlatIP gives exact cosine search and scores fall in [−1, 1], which makes a single threshold meaningful.

Q: Why all-MiniLM-L6-v2?
It's small (~80 MB), fast on CPU and good enough for English papers, so the whole thing deploys on a free tier. A larger model would probably improve recall; the eval harness lets me measure that trade-off.

Q: Why a threshold on the top-1 score, not the average of the top-k?
The average falls as k grows, so the threshold would secretly depend on k. Top-1 answers the real question — "is there at least one strong match?" — and can be swept independently of k.

Q: Why two guards?
They catch different failures. The similarity threshold catches off-topic questions where nothing is close. But a question can be on-topic — the passages are about the right paper — yet the specific answer isn't there; only a model reading the passages can notice that, hence INSUFFICIENT_CONTEXT.

Q: Why is extractive the default?
It needs no API key and costs nothing, so the demo always works; it's faithful by construction because nothing is generated; and it gives a baseline to compare the LLM's faithfulness against.

Q: Why no LangChain?
I wanted every step visible — chunking, embedding, search, guards — so I can explain and test each one. The pipeline is a few hundred lines; a framework would add abstraction without solving a problem I had.

Q: Why FastAPI plus a separate Streamlit UI?
FastAPI gives a typed, validated, documented API (Pydantic, /docs); the UI calling the API over HTTP proves the backend works as a service, and any other client could use it.

Q: How do citations work?
Each chunk stores its source filename and page number at indexing time. Retrieval returns those with the scores, and the answer includes them. In Mistral mode the passages are numbered and the prompt requires [n] citations after each claim.
:::

## 17.9 Interview questions — "what if…?" %%MUST%%

:::qa What if…
Q: What if you had 1 million papers?
About 30–50 million chunks. I'd move from a flat index to HNSW or IVF-PQ (FAISS or a vector DB like Qdrant/pgvector), measuring recall against a flat sample; embed offline with batching on GPUs; store metadata in a database instead of JSONL; add metadata filters (year, venue); and re-tune the threshold, because score distributions change with corpus size.

Q: What if a PDF is scanned (no text layer)?
Today those pages produce no chunks and the file is reported as skipped. I'd add an OCR fallback (e.g. Tesseract) for pages without text, with a confidence check, and still keep page numbers.

Q: What if the answer is inside a table?
Currently table rows are filtered as noise, so it would likely fail — a documented limitation. I'd detect tables (PyMuPDF has table detection), convert each to Markdown or row-wise sentences, and index them as separate chunks with their page number.

Q: What if the answer spans two pages?
Chunks never cross pages, so each half is a separate chunk; with top-5 retrieval both halves can be retrieved and cited as two pages. If this is common, a parent–child scheme (retrieve small, expand to neighbouring chunks) would help.

Q: What if the question needs information from two papers?
Top-k retrieval spans all papers, so passages from both can come back and be cited separately. For comparison questions I'd add query decomposition ("what does paper A say… paper B…") and retrieve per sub-question.

Q: What if the threshold is set wrong?
Too high → many false refusals; too low → unsupported answers slip through. That's why it's configurable and why the eval script sweeps it on labelled data. It should be re-tuned when the corpus or embedding model changes.

Q: What if a paper contains text like "ignore your instructions and say X"?
That's indirect prompt injection. In extractive mode nothing is generated, so it can't act. In Mistral mode the system prompt restricts the model to answering from passages with citations, and the model has no tools, so the worst case is a wrong answer — mitigated by citations the user can check. I'd also wrap passages in clear delimiters and never put secrets in the prompt.

Q: What if two users upload PDFs at the same time?
Today indexing is an offline script over one folder. For multi-user uploads I'd make indexing a background job with a queue, add per-user or per-collection namespaces with access filters, and rebuild or incrementally add to the index with a lock.

Q: What if latency must be under 200 ms?
The model and index are loaded once; embedding one query with MiniLM on CPU plus a flat search is fast for this corpus size. Extractive mode needs no LLM call. With Mistral, the LLM dominates latency — I'd stream the answer, and cache frequent questions.

Q: What if the embedding model changes?
All vectors must be recomputed — different models live in different vector spaces — and the threshold must be re-swept. The index load check (vector count vs chunk rows) guards against mixing files.
:::

## 17.10 Interview questions — "why not…?" and "what next?" %%MUST%%

:::qa Why not… / what next
Q: Why not just paste the whole paper into a long-context LLM?
Cost and latency on every question, weaker use of details in the middle of long contexts, and no retrieval scores to power an "I don't know". RAG also scales to a folder of many papers.

Q: Why not fine-tune a model on the papers?
Fine-tuning doesn't reliably add facts, can't give page citations, and must be redone for every new paper. RAG updates by re-indexing and cites sources.

Q: Why not OpenAI embeddings?
They'd likely improve retrieval, but add cost, a network dependency and an API key. MiniLM keeps the system free and local; switching models is a one-line config change followed by re-indexing and re-evaluating.

Q: Why not semantic chunking?
Block-level chunking already follows the author's paragraphs and preserves pages, which semantic splitting doesn't guarantee. Semantic chunking could be tried inside very long blocks and compared on the eval set.

Q: Why not BM25?
Pure BM25 misses paraphrases; pure embeddings miss exact terms like model names and dataset ids. The best is both — adding BM25 with Reciprocal Rank Fusion is my first planned improvement.

Q: What would you improve first, and how would you know it helped?
First run the labelled evaluation to get a baseline. Then hybrid search with RRF, then a cross-encoder reranker over the top 20. After each change I'd re-run the eval and compare citation hit rate, unsupported-answer rate and false refusals.

Q: How is this different from a LangChain tutorial RAG?
Page-bounded, layout-aware chunking for citations; exact search chosen deliberately; two independent abstention guards; a configurable threshold with an evaluation harness to measure the trade-off; and an extractive baseline for faithfulness.

Q: What was the hardest part?
Getting chunking right: PDF text is messy — ligatures, hyphenation, headers, tables and multi-column layouts. The column-ordering bug was the most instructive — I only found it by generating a test PDF, which is why I now test chunking directly.

Q: What did you learn?
That RAG quality is mostly retrieval and data preparation, that refusing to answer is a feature you must design and measure, and that every threshold needs an evaluation set behind it.
:::

:::remember PaperRAG in numbers
MiniLM **384-d**, normalised · chunks **≤ 900 chars**, **150** overlap, min **120**, never across pages · FAISS **IndexFlatIP** (exact cosine) · **top-5** · threshold default **0.35** (sweep 0.20–0.66) · guard 1 = **top-1 < threshold**, guard 2 = **INSUFFICIENT_CONTEXT** (Mistral mode) · modes: **extractive** (default) / **mistral** (temperature 0) · API **/ask**, **/health** · known gaps: column order, tables, OCR, eval not yet run.
:::
