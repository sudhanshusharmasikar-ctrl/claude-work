:::chapter 21 | Final Revision on a Few Pages | All chapters · Days 43–45
- **Seven revision sheets** — one per topic — to rewrite from memory
- **Code you must be able to write** on a whiteboard (tested)
- A **short** list of trusted resources — only if you have spare time
- The **last-week checklist**, and what to do on the day
:::

Days 43–44: for each sheet, **cover it**, write everything you remember on a blank page, then compare and fill the gaps in a different colour. The gaps are your final revision list. Day 45: read the sheets once, then rest.

## 21.1 Sheet 1 — LLMs and prompting %%MUST%%

| Topic | The line to say |
|---|---|
| **What an LLM does** | Predicts the next token, appends it, repeats. Plausible ≠ true → hallucination. |
| **Tokens** | ~4 English characters; the unit of reading, writing and **billing**. |
| **Temperature** | Low for SQL, JSON, RAG; higher for creative text. Top-k / top-p limit the candidates. |
| **Memory** | The API is **stateless** — memory is the history **you** resend (`ai.chats.create` manages it). |
| **System instruction** | Goes in `config`, sent every call, **not** a security control. |
| **Thinking** | Hidden reasoning tokens, billed as output; turn on for hard questions only. |
| **Training** | Pre-training → instruction tuning (SFT) → preference tuning (RLHF / DPO). |
| **RAG or fine-tune?** | Prompt first, **RAG for knowledge**, **fine-tune (LoRA) for behaviour**. |
| **Reliable JSON** | JSON mode + schema + validate + strip fences + retry with the error. |
| **Cost** | system + history + new message + output (+ thinking); 429 → exponential backoff. |
| **Prompt shape** | ROLE → GOAL → RULES → OUTPUT FORMAT; give a legal "I can't answer" path. |

## 21.2 Sheet 2 — Agents and safety %%MUST%%

| Topic | The line to say |
|---|---|
| **Function calling** | The model returns `functionCall {name, args}`; **your code** runs it and sends back a `functionResponse`. |
| **Agent** | LLM + tools + loop; stops when it answers in text — or at the **step limit**. |
| **Workflow vs agent** | Code fixes the path vs the LLM chooses the next step. Start with the simplest. |
| **Five patterns** | Chaining, routing, parallelisation, orchestrator–workers, evaluator–optimiser. |
| **ReAct** | Thought → Action → Observation, repeated. |
| **Memory** | Short-term = state/history; long-term = stored facts; summaries. Choosing it = **context engineering**. |
| **MCP** | Host ↔ client ↔ server; servers expose **tools, resources, prompts**. Function calling is how the model uses them. |
| **Dangerous tools** | A shell tool = your full permissions. Specific tools, allow-lists, path jail, sandbox, approvals, logs. |
| **Prompt injection** | Untrusted text carrying instructions — defend in **code and permissions**, not prompt wording. |
| **OWASP to name** | LLM01 injection · LLM02 sensitive info · LLM05 output handling · LLM06 excessive agency · LLM10 unbounded consumption. |

## 21.3 Sheet 3 — Embeddings and vector search %%MUST%%

| Topic | The line to say |
|---|---|
| **Embedding** | A vector of meaning; similar meaning → nearby vectors. Same model for documents and queries. |
| **Cosine vs Euclidean** | Angle vs straight-line distance. Normalise → same ranking, and inner product = cosine. |
| **Models** | `gemini-embedding-001` (3072), MiniLM (384). `text-embedding-004` is shut down. Change model → re-embed all. |
| **Brute force** | Exact, O(N·d) per query — right for small data (PaperRAG, SchemaMind). |
| **IVF** | k-means clusters, search `nprobe` of them; border problem; needs training. |
| **KD-tree** | Median splits + backtracking; fails in high dimensions. |
| **HNSW** | Layered graph; greedy on top, `efSearch` beam at the bottom; fast, accurate, **memory-hungry**. |
| **PQ** | Split the vector, 256-centroid codebook per piece, 1 byte per piece; IVF-PQ for billions. |
| **ANN quality** | recall@k against exact search, plus p95 latency and memory. |
| **Security** | id + vector + **metadata**; filter by user/tenant **inside** the search. |
| **Memory math** | N × dimensions × 4 bytes: 10M × 768 × 4 ≈ **30.7 GB**. |

## 21.4 Sheet 4 — RAG, basic to good %%MUST%%

| Topic | The line to say |
|---|---|
| **Why RAG** | Knowledge cutoff, hallucination, private data → an **open-book exam**. |
| **Two phases** | Indexing: load → chunk → embed → store. Query: embed → top-k → augment → generate. |
| **Chunking** | Course: 1000 chars / 200 overlap. PaperRAG: whole PDF blocks, ≤ 900 / 150, never across a page. |
| **Follow-ups** | Rewrite into a standalone question before retrieving. |
| **Hybrid** | BM25 + vectors fused with **RRF: Σ 1/(60 + rank)**. |
| **Rerank** | Retrieve wide with a bi-encoder, rerank narrow with a cross-encoder. |
| **Contextual retrieval** | Add chunk context before embedding: −49% failed retrievals, −67% with reranking (Anthropic). |
| **Lost in the middle** | Few, best chunks; best first; cite `[n]`. |
| **Abstain** | Similarity threshold before the LLM + `INSUFFICIENT_CONTEXT` after (PaperRAG's two guards). |
| **Evaluate** | recall@k, MRR; faithfulness, answer relevancy, context precision / recall; unsupported vs false-refusal. |
| **Debug** | Was the right chunk **retrieved**? If yes, was it **used faithfully**? |

## 21.5 Sheet 5 — Graphs, GraphRAG, vectorless %%MUST%%

| Topic | The line to say |
|---|---|
| **Graph DB** | Index-free adjacency: O(1) per hop. Neo4j: 15-byte node, 34-byte relationship records. |
| **Cypher** | `MATCH` pattern → `WHERE` → `RETURN`; `MERGE` avoids duplicates; always `$parameters`. |
| **Rohit's Graph RAG** | Neo4j for facts + Pinecone for meaning; 6 labels, 5 relationship types. |
| **Query pipeline** | Extract → resolve entities → classify → handler. |
| **Safety** | The LLM writes a **JSON plan, never Cypher**; code whitelists and binds parameters; READ session. |
| **Microsoft GraphRAG** | LLM extracts entities → **Leiden communities** → **community reports**; global / local / DRIFT search. |
| **Its cost** | Indexing runs the LLM over everything; cheaper variants like LazyGraphRAG. |
| **Vectorless (PageIndex)** | A tree of sections with summaries; the LLM **reasons** down it; cites sections and pages. |
| **Why vectorless** | Similarity ≠ relevance; chunking breaks structure. Cost: more LLM calls, latency. |
| **Choosing** | Tables → SQL · relationships → graph · themes → GraphRAG · long reports → tree · semantic → hybrid vectors · small → long context — plus a **router**. |

## 21.6 Sheet 6 — LangGraph and human-in-the-loop %%MUST%%

| Topic | The line to say |
|---|---|
| **Why LangGraph** | Plain functions can't pause, resume or retry safely; a graph with saved state can. |
| **Parts** | **State** + **nodes** (work) + **edges** (control, incl. conditional) + runtime. |
| **Reducers** | Default: last value wins; lists append. Return **deltas** into additive reducers. |
| **Checkpointer** | Saves state + next node after every node, per **thread_id**; `invoke(null, config)` resumes. |
| **Idempotency** | After a crash only the failed node re-runs → stable ids / upserts. |
| **MemorySaver** | RAM only — lost on restart (StanceScope: `KeyError` on resume). Use SQLite / Postgres. |
| **interrupt()** | Saves and returns `__interrupt__`; resume with `Command({ resume })` + the same thread_id. |
| **Its rules** | The node **re-runs from its start**; no side effects before `interrupt()`; don't swallow it in `try/catch`; plain-JSON resume values with **string keys**. |
| **API pattern** | Run → "awaiting_review" + items → review endpoint validates, resumes, logs model vs human. |
| **Multi-agent** | State is the only channel; every loop has an exit: caps, escalation tiers, budget, recursion limit (25). |

## 21.7 Sheet 7 — Your three projects %%MUST%%

:::remember PaperRAG — the numbers and the honest lines
**Say:** block-level, page-bounded chunks → page citations from metadata; exact cosine (FAISS `IndexFlatIP`, normalised MiniLM 384-d); top-5; **two guards** (top-1 < threshold 0.35 → abstain; `INSUFFICIENT_CONTEXT` in Mistral mode); extractive default = free, faithful baseline; sweep 0.20–0.66 on labelled questions. Chunks ≤ 900 chars, 150 overlap, min 120.

**Honest:** the sort **interleaves two-column pages** (tested; fix in 17.5); the second guard is Mistral-mode only; the eval isn't run yet — no numbers.

**Story:** "My sort's comment said it handled two columns. I built a test PDF, proved it didn't, and wrote a column-aware key."
:::

:::remember SchemaMind — the numbers and the honest lines
**Say:** table descriptions (columns, PK, FK →, 2 sample rows) embedded with MiniLM; top-3 tables; generate → **AST validate** (only Select/Union, `walk()` for nested writes) → **read-only** execute (`mode=ro`, 200 rows) → repair with the real error (2 repairs = 3 attempts); SQL always shown; execution accuracy, retrieved vs full schema.

**Honest:** template mode is **not** text-to-SQL; eval not run; the hidden-second-statement check depends on the sqlglot version (≥ 29 blocks it; the executor blocks it anyway); `timeout=10` is a lock wait — a recursive query runs forever without a progress handler.

**Story:** "Safe isn't correct: 'orders from Pune' returned 150 instead of 22, and my two revenue templates disagree — 5,422,800 vs 4,791,200."
:::

:::remember StanceScope — the numbers and the honest lines
**Say:** 4 nodes (retrieve_evidence → classify_posts → human_review → aggregate); confidence < 0.6 → real `interrupt()`; API returns `awaiting_review`; resume with `Command(resume=…)` on thread `run-{id}`; every prediction stored with source = model or human.

**Honest:** the classifier is a **keyword stub** (BERT + ViT slot not wired); MemorySaver loses paused runs on restart; evidence isn't used by the classifier; 0.6 is uncalibrated.

**Story:** "Three bugs I only found by running it: `hash()` randomisation, integer resume keys, and a broken INSERT — plus the restart test."
:::

## 21.8 Code you must be able to write %%MUST%%

On a whiteboard nobody expects perfect syntax — they expect the **right structure**. Practise these until they're automatic.

```js title="1 · The agent loop (Chapter 3) — skeleton"
for (let step = 1; step <= MAX_STEPS; step++) {
  const result = await ai.models.generateContent({ model, contents: history,
                                                   config: { tools } });
  const calls = result.functionCalls ?? [];
  history.push(result.candidates[0].content);        // the model's own turn
  if (calls.length === 0) return result.text;         // final answer
  const responses = [];
  for (const { name, args } of calls) {               // EVERY call
    let output;
    try { output = await toolFunctions[name](args); }
    catch (err) { output = { error: err.message }; }  // failure = data
    responses.push({ functionResponse: { name, response: { result: output } } });
  }
  history.push({ role: "user", parts: responses });
}
```

```js title="2 · Cosine similarity and 3 · RRF (Chapters 6 and 9)"
function cosine(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

function rrf(lists, k = 60) {                 // each list: ids, best first
  const score = new Map();
  for (const list of lists)
    list.forEach((id, i) => score.set(id, (score.get(id) ?? 0) + 1 / (k + i + 1)));
  return [...score]
    .sort((a, b) => b[1] - a[1])                  // highest score first
    .map(([id, s]) => `${id}:${s.toFixed(4)}`);
}

console.log(cosine([1, 2, 3], [2, 4, 6]).toFixed(3),     // same direction
            cosine([1, 0], [0, 1]).toFixed(3));           // at right angles
console.log(rrf([["a", "b", "c"], ["c", "a", "d"]]));
```

```output title="node memory.mjs"
1.000 0.000                                          #> 1 = same, 0 = unrelated
[ 'a:0.0325', 'c:0.0323', 'b:0.0161', 'd:0.0159' ]   #> in both lists → on top
```

```js title="4 · Pause and resume with LangGraph (Chapter 15) — skeleton"
async function humanReview(state) {
  const answer = interrupt({ question: "Approve?", plan: state.plan });
  return { approved: answer.approved };        // runs only after resume
}
const app = graph.compile({ checkpointer: new MemorySaver() });
const config = { configurable: { thread_id: "job-42" } };
const first = await app.invoke({ request: "blog API" }, config);   // pauses
// first.__interrupt__[0].value → show it to a human ... later:
await app.invoke(new Command({ resume: { approved: true } }), config);
```

Also be ready to write: a Cypher `MATCH` with a `$parameter` (Chapter 11), the RAG query function — embed, search, build the prompt (Chapter 8) — and a `StateGraph` with one conditional edge (Chapter 14).

## 21.9 Trusted resources (only if you have spare time) %%OPT%%

This book is enough for interviews. If you have extra time, these are the **primary sources** behind it — read the one that matches your weakest sheet.

| Resource | Where to find it | Read it for |
|---|---|---|
| Rohit Negi's lectures | YouTube: **Coder Army** (@CoderArmy9) and the STRIKE GenAI course | Re-watching a lecture you found hard |
| *Building Effective Agents* | Anthropic engineering blog | Workflows vs agents, the five patterns (Ch 5) |
| *Introducing Contextual Retrieval* | Anthropic blog | Contextual chunks, hybrid search, reranking (Ch 9) |
| *Lost in the Middle* | Liu et al., 2023 (arXiv) | Why position in the context matters (Ch 9) |
| RAGAS documentation | docs.ragas.io | RAG metrics (Ch 9, 17) |
| PageIndex | GitHub: VectifyAI/PageIndex | Vectorless, tree-based retrieval (Ch 10) |
| Microsoft GraphRAG | microsoft.github.io/graphrag | Communities, global/local search (Ch 13) |
| LangGraph docs | search "LangGraph interrupts" and "LangGraph persistence" | Checkpoints, interrupts (Ch 14–15) |
| Model Context Protocol | modelcontextprotocol.io | MCP architecture (Ch 5) |
| OWASP Top 10 for LLM Apps (2025) | genai.owasp.org | Security vocabulary (Ch 5, 18) |
| FAISS wiki | GitHub: facebookresearch/faiss | Index types, IVF/HNSW/PQ settings (Ch 7) |

## 21.10 The last-week checklist %%MUST%%

:::build Your repos (links on a resume get clicked)
- Each README says honestly what is **tested**, what is a **placeholder**, and what is **not measured yet**.
- No secrets anywhere: `.env` in `.gitignore`; any key that was ever pushed is **revoked**.
- If we've done the "when we build" work (17.7, 18.9, 19.7) by then, update the README and resume lines to match. If not, use the honest lines from 17.6, 18.8 and 19.1 — they're strong answers too.
- The `stance-detection` repository: add the thesis code and results, or don't link it.
- Run each project once, end to end, the day before — demos fail when they haven't been run in weeks.
:::

:::tip The day before and the day of
- Say the three **30-second pitches** and one **2-minute pitch** out loud.
- Read Sheets 1–7 once. Don't start anything new.
- Keep two questions ready for the interviewer, e.g. *"How do you evaluate LLM features before they ship?"* and *"What has been the hardest production failure with your AI systems?"*
- In the room: ask clarifying questions, think out loud, use **define → why → how → trade-off**, and say "I don't know, but here's how I'd find out" when you need to.
- Sleep. A rested brain answers better than one more hour of reading.
:::

You started this book knowing a little JavaScript. You now know how LLMs work, how to give them tools, how to make them search your data, how to keep them safe, and how to defend three real projects line by line. **You're ready. Go and get that offer.** 🚀
