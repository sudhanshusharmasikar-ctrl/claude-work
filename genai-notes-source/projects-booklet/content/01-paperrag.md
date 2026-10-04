:::chapter 1 | PaperRAG: Ask Your Research Papers | Retrieval-augmented generation · FAISS · FastAPI
- What problem PaperRAG solves, in plain words
- **The whole pipeline in one picture**
- Building the library: blocks, reading order, chunks, embeddings, the index
- Answering: search, the **"I don't know" guard**, the answer
- How the web page and the server talk to each other
- One question, followed from start to finish
- How it is measured and tested, and what we fixed
- **Questions and answers**: how, why, what if, what more, why not, what we tried
:::

## 1.1 The problem, in plain words

Imagine 40 research papers on your laptop. You want to ask *"Which optimizer did the transformer paper use?"* and get an answer you can **trust**, together with **where** it came from, so you can open the paper and check.

Why not just ask ChatGPT?

- It may never have read your papers: new ones, private ones, your own drafts.
- It can **make things up** in a confident voice. This is called **hallucination**.
- It doesn't tell you the file and page it used.

:::analogy An open-book exam
A normal LLM is a student answering from memory. PaperRAG turns it into an **open-book exam**: first find the right pages in your own books, then answer **only** from those pages, and write down which page you used. If the books don't cover the question, the honest student says *"I don't know"*.
:::

That idea is called **RAG**, retrieval-augmented generation. *Retrieval* means finding the right pieces of text; *augmented generation* means writing the answer from those pieces. PaperRAG adds two things to basic RAG: **page-level citations**, and a **guard** that refuses when your papers don't contain the answer.

## 1.2 The whole pipeline in one picture

[[fig:pb-paperrag-pipeline|PaperRAG has two phases. **A** runs once and builds a searchable library from your PDFs. **B** runs for every question: find the closest chunks, check they are close enough, then answer with citations.]]

Read the picture as two rows:

- **Row A, building the library,** happens **once**, when you run `python -m app.index`. It reads every PDF, cuts the text into small pieces called **chunks**, turns each chunk into **384 numbers** that describe its meaning, and saves everything in the `storage/` folder.
- **Row B, answering,** happens **every time** someone asks. The question is turned into 384 numbers by the same model, the closest chunks are found, a **guard** checks whether the best one is close enough, and the answer comes back with the file and page of every passage.

The rest of this part goes through the numbered boxes one by one.

## 1.3 Building the library, step by step

### A1 · Your PDFs

You copy papers into `data/pdfs/` and run `python -m app.index`, which calls `build()` in `app/index.py`. It goes through the PDFs one by one. A PDF that gives no text at all, usually a **scanned** paper that is really a picture of text, is skipped and listed at the end.

### A2 · Read the text in blocks

A PDF doesn't store paragraphs: it stores letters at positions on a page. **PyMuPDF** (the `pymupdf` library) groups letters into **blocks**, roughly one visual paragraph each, together with the block's position on the page `(x0, y0, x1, y1)`. Two clean-up steps follow, both in `app/chunking.py`:

| Step | What it does | Example |
|---|---|---|
| `clean()` | fixes PDF oddities | the one-character ligature "ﬁ" becomes "fi"; "multi-" at a line end followed by "modal" becomes "multimodal" |
| `_is_noise()` | throws away blocks that aren't prose | page numbers ("12"), short labels ("Table 3"), rows of numbers from tables |

Why bother? Junk text gets turned into numbers too, and it makes the search worse.

### A3 · Put the blocks in reading order

On a two-column paper, sorting blocks from top to bottom mixes the columns: left paragraph, right paragraph, left, right. PaperRAG reads **column by column** instead, in `_reading_order()`:

[[fig:pb-reading-order|Left: the old order mixed the columns. Right: blocks that cross the middle of the page (the title, a wide figure caption) cut the page into **bands**; inside each band the left column is read first, then the right one.]]

How it decides: a block that **crosses the middle** of the page is *wide*: a title, an abstract, a wide caption. Every other block sits in the left or the right column. Wide blocks cut the page into bands, and each band is read left column first, then right column. On a one-column page almost every block crosses the middle, so nothing changes. This was fixed in session 3 (see 1.8).

### A4 · Cut the text into chunks

A whole paper is far too long to search as one piece, and the embedding model reads only about 1,000 characters at a time. So the blocks of each page are packed into **chunks** by `_pack()`:

[[fig:pb-chunking|Whole blocks are packed into chunks of at most 900 characters. The end of one chunk is repeated at the start of the next (the overlap), and a chunk never contains text from two pages.]]

| Rule | Value | Why |
|---|---|---|
| Maximum size | 900 characters | the model reads only about 256 word pieces (≈ 1,000 characters); anything longer would be cut off without a warning |
| Overlap | 150 characters | a sentence that falls on the edge is still complete in one of the two chunks; the overlap shrinks when the next paragraph is long, so the 900 limit holds |
| One page per chunk | always | every chunk has exactly **one page number**, which is what makes page citations possible |

Chunks shorter than 120 characters are dropped (usually headers or stray labels). A single paragraph longer than 900 characters is split at sentence ends. Each chunk becomes one line of `storage/chunks.jsonl`; this one is **real**, made by the current code from a small test PDF (the text is shortened here):

```json title="one line of storage/chunks.jsonl, spread over several lines"
{
  "chunk_id": "transformers::p2::c0",
  "doc_id": "transformers",
  "source": "transformers.pdf",
  "page": 2,
  "text": "We train with the Adam optimizer, a learning rate warmup of …"
}
```

Read the `chunk_id` as: file `transformers`, page 2, chunk 0 of that page.

### A5 · Turn every chunk into numbers

[[fig:pb-embedding-space|An embedding model turns text into a list of numbers. Texts with similar meaning get numbers that point in a similar direction, so the question lands next to the chunk that answers it.]]

An **embedding model** reads a piece of text and outputs a list of numbers, called a **vector**, that describes its meaning. PaperRAG uses **all-MiniLM-L6-v2** ("MiniLM"): every chunk becomes **384 numbers**. Texts about the same idea get similar numbers even when they use different words.

Every vector is **normalised**, which means scaled to length 1. Comparing two such vectors is then one multiplication, the **dot product**, and its result is the **cosine similarity**: close to 1 means the same meaning, close to 0 means unrelated.

Why MiniLM: it is small (about 80 MB), fast on a laptop's processor, free, and works offline. A bigger model might match meaning a little better, but this project has to run on a free server.

### A6 · Save the library

| File | What is in it | Why |
|---|---|---|
| `storage/faiss.index` | the 384 numbers of every chunk | **FAISS** is a library built for searching vectors fast; it stores **only numbers** |
| `storage/chunks.jsonl` | the text, file name and page of every chunk, one per line | so a search result ("row 17") can be turned back into text and a page |

Row 17 in the index is line 17 in the file. When the server loads them, `load()` checks that the counts match, and refuses to start if they don't ("out of sync — rebuild").

PaperRAG uses the index type **IndexFlatIP**. *Flat* means the question is compared with **every** chunk, an exact search; *IP* means inner product, which is the dot product above.

## 1.4 Answering a question, step by step

### B1 · The question arrives

You type into the Streamlit page, which sends the question to the server's `/ask` **endpoint** as **JSON** (a simple text format for data):

```json title="what the web page sends to POST /ask"
{"question": "Which optimizer did they use?", "top_k": 5,
 "threshold": 0.35, "mode": "extractive"}
```

The server checks the input first: 3 to 1,000 characters, `top_k` between 1 and 20, `mode` either `extractive` or `mistral`. Anything else is rejected with an error (HTTP 422) before any work starts.

### B2 · The question becomes numbers

The question goes through the **same** MiniLM model and becomes 384 numbers. It has to be the same model: numbers from two different models are like coordinates from two different maps.

### B3 · Find the closest chunks

FAISS compares the question's vector with every chunk's vector and returns the **top 5** with their scores (cosine similarity). With a few hundred papers that is tens of thousands of comparisons, which takes milliseconds.

### B4 · The guard

[[fig:pb-guard|The guard compares only the best score with the threshold. Below 0.35 PaperRAG refuses; at 0.35 or above it answers.]]

If even the best chunk scores below the **threshold**, your papers probably don't cover the question, so PaperRAG refuses instead of guessing. The refusal shows both numbers (the format is **real**; the score is an example):

```output title="the refusal message, wrapped onto two lines here"
I don't have enough supporting material in the indexed papers to answer
that. The closest passage scored 0.123, below the 0.350 threshold.
```

Two details matter:

- It uses the **best (top-1)** score, not the average of the top 5. The average drops as you ask for more results, so the cut-off would quietly depend on `top_k`.
- 0.35 is only a **starting value**. The right value depends on your papers; once you add them, a later session sets it from your own test questions.

### B5 · Write the answer

| Mode | How the answer is made | Good | Not so good |
|---|---|---|---|
| `extractive` (default) | the passages are returned word for word, numbered, with file, page and score | invents nothing; no API key; free | you read passages, not a short answer |
| `mistral` | the passages and the question go to the Mistral LLM with strict rules: use only the passages, cite them as [1], [2], and reply `INSUFFICIENT_CONTEXT` if they don't contain the answer | a short, readable answer | needs an API key; the model could still slip |

In mistral mode there is a **second guard**: if the model replies `INSUFFICIENT_CONTEXT` (the passages were on topic but didn't contain the answer), PaperRAG turns that into a refusal too. The **temperature** is 0, so the same question gives the same answer.

### B6 · The reply

```json title="what /ask sends back (the shape is real, the values are an example)"
{"question": "Which optimizer did they use?",
 "answer": "Extractive mode -- passages returned verbatim ...",
 "abstained": false, "top_score": 0.712, "threshold": 0.35,
 "mode": "extractive",
 "citations": [{"n": 1, "source": "transformers.pdf", "page": 2,
                "score": 0.712, "chunk_id": "transformers::p2::c0"}],
 "latency_ms": 41.3}
```

The citations come from the chunks' saved file and page, **not** from the LLM, so the model can't invent a page number.

## 1.5 How the parts talk to each other

[[fig:pb-paperrag-components|You use the Streamlit page; the page talks to the FastAPI server over HTTP; the server keeps the model and the library in memory and calls Mistral only in mistral mode. The library is built beforehand by the indexing script.]]

- **The FastAPI server** (`app/api.py`) is a Python web server. It loads the model and the library **once**, when it starts (the `lifespan` function), then answers requests at its endpoints: `/ask` for questions, `/health` to check that the library is loaded and how many chunks it has, and `/docs`, an automatic page where you can try the API in the browser.
- **The Streamlit page** (`ui/streamlit_app.py`) is what you use. It contains no search code: it sends HTTP requests to the server and shows the reply. Its sliders change `top_k`, the threshold and the mode.
- **Why two programs?** The page proves the API works on its own, and any other program, a mobile app or a script, could use the same API.

You have already seen `/health` working: `{"status":"index_missing","chunks":0,...}` means the server runs but no library has been built yet.

## 1.6 One question, from start to finish

Question: *"Which optimizer did the transformer paper use?"* The scores are an **example**.

| # | What happens | Where in the code | Result |
|---|---|---|---|
| 1 | The page sends the question to `/ask` | `ui/streamlit_app.py` | a JSON request |
| 2 | The input is checked (length, `top_k`, mode) | `AskRequest` in `app/api.py` | OK |
| 3 | The question becomes 384 numbers | `embed()` in `app/index.py` | one vector |
| 4 | FAISS finds the 5 closest chunks | `Retriever.__call__` in `app/retrieve.py` | best: `transformers.pdf p.2`, score 0.71 |
| 5 | The guard compares 0.71 with 0.35 | the same function | answer allowed |
| 6 | The extractive answer is built | `answer()` in `app/generate.py` | passages starting `[1] transformers.pdf p.2` |
| 7 | The reply goes back with citations and timing | `ask()` in `app/api.py` | shown on the page |

Now ask *"What is a good chocolate cake recipe?"*. Step 4 finds nothing close (best score perhaps 0.12), the guard stops the question at step 5, and the page shows the refusal message with both numbers.

## 1.7 How it is measured and tested

**Tests** check that the code does what it promises. There are 37, run with `pytest`, offline, in about a second. They don't download MiniLM: a tiny stand-in that counts words replaces it, so the tests are fast and give the same result every time. They cover cleaning, reading order, chunk sizes and overlap, the saved files, the guard, the answer format, the API, and the evaluation's arithmetic. Since session 6, GitHub runs them after every push, on Python 3.11 and 3.14 (see 3.3).

**Evaluation** measures how *good* the answers are, which tests can't do. `eval/run_eval.py` needs a file of your own questions of two kinds: **answerable** (with the page where the answer is) and **unanswerable** (on topic, but not in your papers). It reports:

| Number | Meaning |
|---|---|
| Unsupported answers, no guard | % of questions answered without support in the papers when nothing ever refuses |
| Unsupported answers, with guard | the same with the guard switched on |
| False refusals | answerable questions that were refused |
| Citation hit rate | how often the right page is among the cited ones |

`--sweep` then tries thresholds from 0.20 to 0.66:

[[fig:pb-tradeoff|A stricter guard gives fewer wrong answers but more false refusals. The evaluation finds the threshold where wrong answers have dropped and refusals are still rare.]]

## 1.8 What we changed, and what we tried

| Session | Change | Why it matters |
|---|---|---|
| 1 | Every library fixed to a tested version | the project installs the same way everywhere, including Python 3.14 on your Mac |
| 2 | 34 tests with a stand-in embedder | writing them uncovered two bugs, fixed in session 3 (37 tests now) |
| 3 | Two-column pages read column by column | chunks no longer mix sentences from two columns |
| 3 | The overlap can't push a chunk past 900 characters | no chunk is longer than the model can read, except a single sentence over 900 characters |
| 3 | An overlap of 0 no longer repeats whole chunks | in Python, `text[-0:]` is the whole string, so chunks had snowballed to 1,877 characters |
| 6 | The tests run on GitHub after every push (CI) | a change that breaks something shows a red cross before it is merged |

**What we tried for the two-column fix.** The first idea, from your notes, gave every block a single sort key: wide blocks first, then the left column, then the right. A test showed it breaks normal pages: a short line on a one-column page moved to the end, and a wide caption in the middle jumped to the top. The band method passed all three layout tests and read a realistic five-page two-column paper in the right order, while one-column documents came out exactly as before.

:::honest Still missing
No real evaluation numbers yet: they need your papers and your own test questions (a later session). No keyword search (BM25) and no reranker. Tables and scanned pages are skipped.
:::

## 1.9 Questions and answers

:::qa How does it work?
Q: How does PaperRAG know which page an answer came from?
Every chunk is built from one page only, and its page number is saved next to its text in `chunks.jsonl`. When a chunk is found, its page comes with it. The LLM never chooses the page, so it can't invent one.

Q: How does it decide to say "I don't know"?
It compares the best similarity score between the question and any chunk with a threshold, 0.35 by default. Below it, the papers probably don't cover the question, so it refuses. In mistral mode a second check also refuses when the model replies `INSUFFICIENT_CONTEXT`.

Q: How does it read a two-column paper in the right order?
Blocks that cross the middle of the page (title, abstract, wide captions) cut the page into bands. Inside each band it reads the left column from top to bottom, then the right column. One-column pages are unchanged, because almost every block there crosses the middle.

Q: How is text turned into numbers, and how are they compared?
MiniLM turns each chunk, and later the question, into 384 numbers scaled to length 1. The dot product of two such vectors is their cosine similarity: close to 1 means similar meaning. FAISS computes it for every chunk and keeps the top 5.

Q: How do the web page and the server work together?
The Streamlit page sends the question to the FastAPI server as JSON, with an HTTP POST to `/ask`. The server, which loaded the model and the library once at startup, runs the search, the guard and the answer step, and sends JSON back for the page to display.
:::

:::qa Why was it built this way?
Q: Why cut papers into chunks instead of searching whole papers?
A whole paper's meaning blurs into one vector, and the model reads only about 1,000 characters anyway. Small chunks give precise matches and precise page citations.

Q: Why 900 characters with 150 overlap?
900 stays under what MiniLM can read (about 256 word pieces), so nothing is silently cut off. The overlap keeps a sentence that falls on a chunk edge complete in one of the chunks. Both are starting values that the evaluation can compare against others.

Q: Why exact search (FAISS IndexFlatIP) and not HNSW?
A few hundred papers give tens of thousands of chunks, and checking all of them takes milliseconds with perfect accuracy. HNSW is approximate and has settings to tune; it solves a speed problem this project doesn't have yet.

Q: Why MiniLM and not a bigger embedding model?
It's small (about 80 MB), fast on a laptop, free, and works offline, so the project runs on a free server. A bigger model might find slightly better matches, and the evaluation would show whether that's worth the cost.

Q: Why is extractive mode the default?
It needs no API key, costs nothing, and can't invent anything, because it only quotes. It's also a fair baseline to compare the LLM mode against.

Q: Why use the best score, not the average of the top 5?
The average drops as you ask for more results, so the cut-off would quietly change whenever `top_k` changes. The best score doesn't depend on `top_k`.
:::

:::qa What if…?
Q: What if the answer isn't in any of the papers?
The best score is usually low, so the guard refuses and shows the score and the threshold. If a chunk is on topic but doesn't hold the answer, extractive mode will still show it, because it can't tell; mistral mode's second guard catches that case.

Q: What if a PDF is scanned, a picture of text?
PyMuPDF finds no text, the PDF produces no chunks, and `build()` lists it as skipped. Fixing that needs OCR (reading text from images), which isn't built yet.

Q: What if the answer is only in a table?
The noise filter drops blocks that are mostly numbers, so table contents are usually missing, and such a question will likely be refused. Table extraction is on the to-do list.

Q: What if you had 10,000 papers?
That's roughly 300,000 to 500,000 chunks. Exact search still works but gets slower, so I'd switch to an approximate index (HNSW, or IVF-PQ to save memory), measure its accuracy against exact search, build the index in batches, and keep the text in a database.

Q: What if two chunks disagree?
Extractive mode shows both with their pages, so you see the disagreement. Mistral mode is told to use only the passages and may mention both. Nothing resolves conflicts automatically.
:::

:::qa What more could you add?
Q: What would you add next?
1) The evaluation with your own questions, and a threshold set from it. 2) Keyword search (BM25) next to vector search, merged with RRF, for exact names and numbers. 3) A reranker that rescores the top 20 chunks. 4) In mistral mode, citing only the passages the model actually used. 5) Tables and OCR.

Q: How would hybrid search help?
Vector search finds meaning; keyword search finds exact terms such as a model name or "Table 3". Running both and merging their rankings with Reciprocal Rank Fusion catches questions that either one alone would miss.

Q: How would you know that an improvement really helped?
Run the same evaluation before and after and compare the numbers: citation hit rate, false refusals and unsupported answers. If they don't move, the change isn't worth its extra complexity.
:::

:::qa Why not something else?
Q: Why not paste all the papers into the LLM's prompt?
They don't fit: dozens of papers are millions of characters. It would also be slow and expensive on every question, and models answer worse when the useful part is buried in a huge prompt.

Q: Why not fine-tune a model on the papers?
Fine-tuning teaches style and behaviour, not reliable facts, and it can't point to a page. Adding a paper would mean training again; with RAG you just rebuild the index.

Q: Why not use LangChain or LlamaIndex?
I wanted to understand and control every step, keep the dependencies few, and make each part easy to test. A framework would hide the chunking and the guard, which are the most interesting parts.

Q: Why not a vector database like Pinecone?
At this size, a FAISS file is faster, free and simpler. A vector database pays off with many users, frequent updates, or filtering by metadata such as the user or the year.
:::

:::qa What did you try, and what did you learn?
Q: What went wrong with two-column papers, and how did you fix it?
A test showed that blocks were sorted top to bottom, which mixed the columns. The simple fix of one sort key per block broke one-column pages, so I chose bands: wide blocks split the page, and each band is read left column first. Tests cover one-column, two-column and wide-caption pages.

Q: What other bugs did the tests find?
The overlap carried into a new chunk wasn't counted, so chunks could reach about 1,050 characters, more than the model reads. And an overlap of 0 made every chunk repeat the whole previous one, because `text[-0:]` is the whole string. Both are fixed and tested.

Q: Why do the tests use a fake embedder?
Unit tests should be fast, offline and give the same result every time. A word-counting stand-in keeps all three, while the real model's quality is measured separately by the evaluation.

Q: What did you learn from building it?
The hard parts of RAG aren't the LLM call: they're reading PDFs correctly, chunking, knowing when to refuse, and measuring. And tests find real bugs: two of the three chunking bugs appeared only because a test was written.
:::
