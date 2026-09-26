:::chapter 20 | Interview Question Bank + System Design | All chapters · Must-know
- How to answer any question in **four moves** (and how to say "I don't know")
- **Rapid-fire** banks: LLMs, prompting, RAG, vector search, agents, LangGraph, evaluation, security
- A **seven-step** method for system design questions
- Three full designs: **support RAG bot**, **company text-to-SQL**, **QA over 10 million documents**
:::

This chapter is for **practice**, not first-time learning. Every answer is short enough to say in **under 45 seconds**. Cover the answer with a piece of paper, say yours **out loud**, then compare. The chapters already have deeper Q&A at their ends — this bank adds new questions and short versions, with pointers back.

## 20.0 How to answer %%MUST%%

:::tip The four-move answer
1. **Define** it in one line. *"Reranking is a second, more accurate scoring pass over the retrieved chunks."*
2. **Why** it exists — the problem. *"Vector search is fast but rough; the right chunk is often at rank 15."*
3. **How** it works, in 2–3 steps. *"Retrieve 50 cheaply, score each (query, chunk) pair with a cross-encoder, keep the best 5."*
4. **Trade-off or example**, ideally from your project. *"It adds 100–300 ms; in PaperRAG it's my planned second improvement, measured by citation hit rate."*
:::

:::honest When you don't know
Never bluff. Say: *"I haven't used that directly. Here's how I'd reason about it…"* and reason from first principles (what problem, what trade-off). Interviewers hire people who think clearly under uncertainty — and they catch bluffing within one follow-up.
:::

## 20.1 LLM fundamentals %%MUST%%

:::qa Rapid-fire — LLMs (also revise the Q&A in Chapters 1–2)
Q: What is a large language model?
A transformer network trained to predict the next token on a huge amount of text. Generation is just that prediction repeated: pick a token, append it, predict again.

Q: What are pre-training, instruction tuning and preference tuning?
Pre-training teaches language and facts by next-token prediction on internet-scale text. Instruction tuning (SFT) trains on prompt–good-answer pairs so it follows instructions. Preference tuning (RLHF or DPO) makes it prefer answers people rate as helpful and safe.

Q: Encoder, decoder and encoder–decoder models?
Encoders like BERT read the whole text in both directions — good for classification and embeddings. Decoders like GPT or Gemini generate left to right. Encoder–decoders like T5 read an input, then generate an output (translation, summarisation).

Q: What are temperature, top-k and top-p?
Temperature sharpens (low) or flattens (high) the probability distribution. Top-k samples only from the k most likely tokens; top-p from the smallest set whose probabilities add up to p. For SQL or JSON use temperature near 0.

Q: What is the KV cache?
While generating, the model stores the attention keys and values of earlier tokens so it doesn't recompute them for every new token. It makes generation fast, and it's why long contexts use lots of GPU memory.

Q: Can hallucination be eliminated?
No — the model always produces its most likely continuation, even without knowledge. You reduce it: ground answers in retrieved context, allow and design abstention, require citations, verify with a second check, and measure faithfulness.

Q: What are TTFT and tokens per second?
Time to first token — how long before the answer starts (queueing plus reading the prompt) — and generation speed after that. Streaming hides total latency; long prompts hurt TTFT.

Q: How do you choose a model for a product?
Run your own eval set and compare quality, latency, cost per request, context size, tool and JSON support, and data-privacy requirements. Start with a strong model to prove the task works, then test smaller, cheaper ones against the same eval.

Q: API model or open-weight model?
APIs: best quality, no infrastructure, pay per token, data leaves your servers. Open-weight: control, privacy and lower cost at high volume, but you run GPUs and serving. Data sensitivity and volume usually decide.

Q: What is quantization?
Storing weights with fewer bits — 8-bit or 4-bit instead of 16 — so the model is smaller and faster with a small quality loss. It lets big models run on smaller GPUs.

Q: What is prompt caching?
The provider reuses the processed form of a prompt prefix it saw recently, so calls sharing a long, identical beginning (system prompt, big document) are cheaper and faster. Put stable content first, changing content last.

Q: What is a multimodal model?
One that takes more than text — images, audio, video. Gemini reads images directly; my thesis model is a small multimodal classifier combining BERT for text and ViT for images.
:::

## 20.2 Prompting and structured output %%MUST%%

:::qa Rapid-fire — prompting (also revise Chapter 5.7)
Q: What makes a good prompt?
A clear role, the task, the context it needs, constraints, the exact output format and, if needed, examples. The course's agents follow ROLE → GOAL → RULES → OUTPUT FORMAT. Specific beats clever.

Q: Zero-shot vs few-shot?
Zero-shot gives only instructions; few-shot adds a few input–output examples to show format and style. Choose diverse examples — or retrieve the most similar ones per question (dynamic few-shot).

Q: What is chain-of-thought, and when does it help?
Asking the model to reason step by step before answering; it helps multi-step problems like maths or planning. It costs tokens and latency, and reasoning models already do it internally.

Q: How do you get reliable JSON out of an LLM?
Use the API's JSON mode or response schema, validate the output against a schema (zod, Pydantic), strip stray markdown fences, and retry on a parse failure with the error message — exactly what the dev team's `callGemini` does.

Q: How do you stop the model from making up an answer?
Give it only the context it should use, give it a legal way out ("reply INSUFFICIENT_CONTEXT"), require citations, and add a retrieval-score threshold before generation — PaperRAG's two guards.

Q: Prompt injection vs jailbreak?
A jailbreak is the user trying to bypass the model's own safety rules. Prompt injection is untrusted content — a web page, PDF or email — carrying instructions the app didn't intend. Defend injection with least privilege and checks in code, not with prompt wording.

Q: System message vs user message?
The system message sets persistent rules and persona; user messages are the inputs. Models follow system instructions more strongly, but it's not a security boundary — never put secrets in it.

Q: How do you test and version prompts?
Keep prompts in files under version control, run them against a fixed eval set on every change, and log the prompt version with each response so you can trace regressions.

Q: What is self-consistency?
Generate several answers (with some randomness) and take the majority. It improves reasoning accuracy at several times the cost; for SQL you can compare the **results** of several candidate queries.

Q: What is context engineering?
Deciding exactly what goes into the context window at each step — instructions, retrieved documents, tool results, summaries of old history — and nothing else. Less but relevant context gives better answers at lower cost (the dev team's context builder).
:::

## 20.3 RAG %%MUST%%

:::qa Rapid-fire — RAG (also revise Chapters 8–10)
Q: Where can a RAG system fail?
Parsing and chunking (text broken or mixed), retrieval (the right chunk isn't found), ranking (found but too low), context (too much, lost in the middle), generation (unfaithful answer), or the question isn't a retrieval question at all (an aggregate that needs SQL).

Q: A RAG answer is wrong. How do you find out whether retrieval or generation is to blame?
Check whether the chunk containing the answer was retrieved. If not, it's retrieval — fix chunking, embeddings, hybrid search or reranking. If it was, it's generation — fix the prompt, context order or model.

Q: Which retrieval metrics do you know?
Recall@k (was a relevant chunk in the top k?), precision@k, MRR (how high the first relevant result ranks) and nDCG (graded relevance, position-weighted).

Q: What does RAGAS measure?
Faithfulness (claims supported by the context), answer relevancy (does it answer the question), context precision (are retrieved chunks relevant) and context recall (did we retrieve everything needed). Several of these use an LLM as a judge.

Q: What is small-to-big (parent–child) retrieval?
Embed small chunks for precise matching, but give the LLM the larger parent section they came from. Precise search plus enough context.

Q: What are HyDE and multi-query retrieval?
HyDE asks the LLM to write a hypothetical answer and searches with its embedding — answers look more like documents than questions do. Multi-query writes several paraphrases, searches with each and merges the results. Both raise recall at extra cost.

Q: How do you handle tables and multi-column PDFs?
Parse layout first: keep tables as Markdown or one sentence per row, and put columns in reading order. My PaperRAG two-column bug is the proof that this step matters.

Q: How do you keep a RAG index fresh?
Ingest incrementally: key chunks by document id plus a content hash, re-embed only changed documents, delete old chunks of updated or removed documents, and run it on a schedule or on change events.

Q: How many chunks should go into the prompt?
Enough for recall, few enough not to distract — typically 3–10 after reranking. Measure it on the eval set; more context isn't free (cost, latency, lost in the middle).

Q: How do you make citations trustworthy?
Attach source and page from chunk metadata — not from the model's memory — and check that each cited chunk supports its claim (an entailment check or an LLM judge on a sample).

Q: How do you reduce RAG latency?
Load models once, use an ANN index, run keyword and vector search in parallel, use a small reranker on few candidates, cache frequent questions, and stream the answer.

Q: What is a semantic cache?
Store answers keyed by the question's embedding and reuse them when a new question is very similar. Risks: wrong reuse — keep a strict threshold and clear the cache when documents change.

Q: When is RAG the wrong tool?
Exact numbers over tables (use SQL), a tiny corpus (just use long context), changing tone or format (fine-tuning), corpus-wide themes (GraphRAG-style summaries).
:::

## 20.4 Embeddings and vector databases %%MUST%%

:::qa Rapid-fire — vectors (also revise Chapters 6–7)
Q: How are sentence-embedding models trained?
With contrastive learning: pairs that belong together (question and answer, paraphrases) are pulled close; other pairs in the batch are pushed apart.

Q: Bi-encoder vs cross-encoder?
A bi-encoder embeds query and document separately — fast and indexable, used for search. A cross-encoder reads both together and outputs one score — more accurate but too slow for millions, so it reranks a short list.

Q: How do you pick the embedding dimension?
The model decides it (MiniLM 384, gemini-embedding-001 up to 3072). Some models allow shorter vectors (Matryoshka-style) — `outputDimensionality` in the Gemini API — trading a little quality for memory and speed.

Q: What do HNSW's M, efConstruction and efSearch control?
M: links per node (memory versus recall). efConstruction: how carefully the graph is built. efSearch: how many candidates a query explores — the main recall-versus-latency knob at query time.

Q: What do IVF's nlist and nprobe control?
nlist is the number of clusters; nprobe is how many clusters each query searches. More probes → higher recall, slower search.

Q: How do you evaluate an ANN index?
Run a sample of queries through exact (flat) search and the ANN index; recall@k is the overlap. Also measure p95 latency, memory and build time.

Q: Pre-filtering vs post-filtering by metadata?
Post-filtering removes results after the search, so you can end up with far fewer than k. Filtering during the search keeps k valid results — important for per-user access control.

Q: FAISS vs pgvector vs a managed vector database?
FAISS is a library inside your process — great for small or static data (PaperRAG). pgvector puts vectors in Postgres next to your relational data. Managed or dedicated servers (Pinecone, Qdrant, Weaviate, Milvus) handle scale, replication and filtering for you.

Q: How much memory do 10 million 768-dimensional float32 vectors need?
10M × 768 × 4 bytes ≈ 30.7 GB, plus index overhead. Product quantization or int8 storage cuts that several times, at some recall cost.

Q: Sparse vs dense retrieval?
Sparse (BM25) matches exact words — great for names, codes, ids. Dense (embeddings) matches meaning — great for paraphrases. Hybrid with rank fusion gets both.

Q: You upgrade the embedding model. What happens?
Every vector must be recomputed — vectors from different models aren't comparable — and thresholds re-tuned. Build the new index alongside the old one and switch when it's evaluated.
:::

## 20.5 Agents, tools and MCP %%MUST%%

:::qa Rapid-fire — agents (also revise Chapters 3–5)
Q: What is an AI agent?
An LLM in a loop that chooses actions — tool calls — based on what it observes, until the goal is met or a limit is hit. A workflow has fixed steps; an agent decides its own next step.

Q: How do you design a good tool for an agent?
A clear name and description, typed parameters (enums where possible), one focused job, safe to retry, helpful error messages, and compact results. The model only knows your tool through its description.

Q: How do you stop an agent from looping forever?
A maximum number of steps, a token or cost budget, detection of repeated identical actions, and escalation — try something different, then ask a human (the dev team's tiers).

Q: How do agents remember things?
Short-term: the message history or graph state for this task. Long-term: facts or summaries stored outside (a database or vector store) and retrieved when relevant. Summarise old history to save tokens.

Q: MCP vs function calling?
Function calling is the model-API feature: the model asks your code to run a named function. MCP is an open protocol for packaging tools, resources and prompts in servers any MCP-aware app can connect to — those tools still reach the model through function calling.

Q: Plan-and-execute vs ReAct?
ReAct decides one step at a time from observations — flexible. Plan-and-execute writes a plan first and then runs the steps — fewer LLM calls and easier to review, but it must re-plan when reality differs.

Q: When do you use multiple agents?
When the work splits into parts that need different instructions, tools or context — like PM, architect, coder and reviewer. It costs more tokens and coordination, so start with one agent and split only when it struggles.

Q: How do you make an agent safe?
Least privilege (only the tools and permissions the task needs), a sandbox, allow-lists, validation of tool inputs in code, human approval for irreversible actions, budgets, and an audit log of every action.

Q: How do you debug an agent?
Tracing: record every LLM call, tool call, input, output, token count and latency, then replay the run. With LangGraph checkpoints you can inspect the state at any step.

Q: How do you evaluate an agent?
A set of realistic tasks with success checks: task success rate, steps and cost per task, correct tool use, safety violations — plus reading full trajectories, not just final answers.
:::

## 20.6 LangGraph, evaluation, security, production %%MUST%%

:::qa Rapid-fire — LangGraph (also revise Chapters 14–16)
Q: LangGraph in one sentence?
A library for building stateful LLM workflows and agents as graphs of nodes over a shared state, with checkpoints, human-in-the-loop interrupts and streaming built in.

Q: Conditional edge vs Command?
A conditional edge is a function that reads the state after a node and returns the next node's name. A node can instead return a `Command` with both a state update and `goto` — routing decided inside the node.

Q: What are the streaming modes?
"values" streams the full state after each step, "updates" only what each node changed, "messages" the LLM's tokens as they're generated, and "custom" your own events.

Q: What is time travel?
With a checkpointer you can list a thread's past checkpoints, inspect the state at any step, and resume or fork from an earlier one — useful for debugging and "undo".

Q: What is a subgraph?
A compiled graph used as a node inside another graph — a way to build big systems from tested pieces, like the phases of the dev team.

Q: What is the recursion limit?
A cap on the number of steps in one run (25 by default in the JS version used in this book), so a buggy loop fails loudly instead of running forever. Raise it in the config for long pipelines.
:::

:::qa Rapid-fire — evaluation, security, production
Q: How do you evaluate an LLM application?
A fixed eval set of real questions with expected answers or checks; component metrics (retrieval recall, faithfulness, task success); LLM-as-judge with a rubric, checked against human labels; run on every change. In production: user feedback, monitoring and A/B tests.

Q: What are the pitfalls of LLM-as-a-judge?
It favours longer answers, the first option shown (position bias), and its own style. Use clear rubrics, swap the order in pairwise comparisons, and measure its agreement with human labels.

Q: What are guardrails?
Checks around the model: on input (topic, PII, known injection patterns) and on output (schema, groundedness, PII, policy). The important rules are enforced in code — SchemaMind's AST check is a guardrail.

Q: Which OWASP LLM risks do your projects handle?
SchemaMind: improper output handling (AST validation) and excessive agency (read-only connection) — and I found an unbounded-consumption gap (runaway queries). PaperRAG: misinformation (abstains, cites pages). The dev team: unbounded consumption (token budget).

Q: What do you monitor in production?
Latency (p50/p95, time to first token), tokens and cost per request, error and retry rates, retrieval scores, abstention rate, user feedback — with PII redacted from logs and alerts on changes.

Q: How do you handle rate limits and API failures?
Retry 429 and 5xx errors with exponential backoff plus jitter, set timeouts, cap retries, fall back to another model or a clear message, and queue non-urgent work.

Q: How do you cut LLM cost at scale?
Cache (prompt caching, semantic cache), route easy requests to smaller models, trim prompts and history, limit output length, batch offline work, and compute embeddings once.

Q: How do you protect user data?
Send the model only what it needs, redact PII before external APIs, isolate tenants in retrieval, enforce permissions in the data layer, set retention rules, and keep audit logs.

Q: How do you deploy an LLM-backed API?
An async API (FastAPI or Express) that loads models once at startup, health checks, horizontal scaling behind a load balancer, streaming responses, timeouts, and secrets from environment variables — never in code.
:::

## 20.7 System design %%MUST%%

In a system design round you **drive**. Use the same seven steps every time — interviewers mostly judge the **structure** and the **trade-offs**, not whether you name the fanciest tool.

| Step | Say… |
|---|---|
| 1. **Requirements** | Who uses it? What questions? How many per day? Latency target? How wrong is acceptable? How sensitive is the data? |
| 2. **Data** | Where does it come from, how big, how often does it change, who may see what? |
| 3. **Ingestion** | Parse → clean → chunk/describe → embed → index, incremental and restartable |
| 4. **Serving** | The request path: rewrite → route → retrieve/tool → generate |
| 5. **Safety** | Permissions, validation, abstention, PII, prompt injection |
| 6. **Evaluation** | Offline eval set + metrics; online feedback and monitoring |
| 7. **Scale and cost** | Numbers, caching, model sizes, bottlenecks, what breaks first |

### Design 1 — A customer-support bot for an e-commerce company

**Requirements (state your assumptions).** 50,000 chats a day in English and Hindi; answer from ~2,000 help-center articles; answer "where is my order?"; hand hard cases to humans; first words within ~2 seconds; never invent policy.

[[fig:sd-support|Support bot: offline indexing, a router with three paths, guardrails, and measurement on every turn.]]

- **Ingestion**: split articles by **section**, keep title, product, language and last-updated date as metadata; hybrid index (vector + BM25); re-index an article when it changes.
- **Serving**: rewrite follow-ups into standalone questions (Chapter 9) → a small **router** model picks the path → policy questions use hybrid search + reranking and answer **with citations**; order questions call the **order API** — with the user id taken from the **login session**, never from the model's text; disputes, anger or low confidence go to a **human** with a summary.
- **Safety**: abstain when retrieval is weak (PaperRAG's guard); the model can't reveal another customer's order because the tool itself is scoped; PII redacted in logs.
- **Evaluation**: 300 real past tickets with the right article and answer; measure faithfulness, correct routing, and **containment** (solved without a human) — online, CSAT and thumbs up/down.
- **Scale and cost**: cheap model for routing, stronger one for answers; cache frequent questions; stream replies. Questions with no good article are **content gaps** — send them to the docs team.

:::interview Follow-ups to expect
*"How do you stop it promising a refund?"* — policy answers only from retrieved text, a guardrail that blocks commitments not in the policy, human hand-off for refunds. *"New policy published — how fast is the bot updated?"* — re-index on the change event, minutes. *"How do you know it's working?"* — containment and CSAT, plus a weekly sample reviewed by support leads.
:::

### Design 2 — Text-to-SQL for a whole company

**Requirements.** Business users ask questions over a warehouse with **800 tables**; answers in under 20 seconds; users may only see data they're allowed to; wrong numbers are expensive. This is **SchemaMind grown up** — use Figure 18.1 as the core and add:

1. **Better metadata** — table and column descriptions, documentation, masked example values, and the **query log** (which tables are joined together in practice) → embed and retrieve at **column** level too.
2. **A semantic layer** — business metrics defined once ("revenue = payments on non-cancelled orders"). The LLM uses the definitions instead of guessing (SchemaMind's two "revenue" numbers).
3. **Retrieval** — pick the business area, then tables and columns, then **expand along foreign keys**; retrieve similar past question→SQL pairs as few-shot examples.
4. **Clarify** — ask one question back when a term is ambiguous ("revenue gross or net?").
5. **Validate** — one read-only statement, only tables this user may see, `LIMIT` added, and an **estimated cost** check before running (many warehouses offer dry runs or EXPLAIN).
6. **Execute** — as a **read-only role with the user's permissions** (row-level security in the database, not in the prompt), with a statement timeout.
7. **Answer** — rows, a chart and **the SQL**, with a "was this right?" button that feeds the eval set.

**Evaluation**: a gold set built from analysts' real queries, execution accuracy, table recall, and a weekly review of failures by category (wrong table, wrong join, wrong filter, ambiguous metric).

:::interview Follow-ups to expect
*"How do you stop someone seeing salaries?"* — the database role and row-level security decide, so even a perfect prompt injection can't widen access. *"A query scans 5 TB."* — dry-run cost check, a limit per query, and cached results. *"The model keeps choosing the wrong table."* — improve descriptions, add query-log signals, few-shot examples, and measure table recall.
:::

### Design 3 — Question answering over 10 million documents

**Requirements.** An enterprise with 10M documents (PDFs, emails, wikis), many teams with different permissions, answers with citations in a few seconds, daily updates.

[[fig:sd-scale|Large-scale RAG: checkpointed ingestion into a sharded hybrid index; fan-out, fuse, rerank, answer.]]

- **Sizing first**: ~10 chunks per document → 100M vectors; at 768 dimensions in float32 that's ≈ 307 GB — too much for one machine's RAM, so **shard** it and **compress** (PQ ≈ 64 bytes per vector ≈ 6.4 GB). Check recall against exact search on a sample.
- **Ingestion**: a queue of document ids; workers parse (OCR for scans), **deduplicate** by hash, chunk with metadata (tenant, date, access list), embed on GPUs in batches. Make it **checkpointed and idempotent** — the Chapter 14 LangGraph lesson: a crash resumes, it never re-embeds everything or writes duplicates.
- **Serving**: rewrite → fan out to all shards (hybrid search with **permission filters inside the search**) → merge with RRF → cross-encoder rerank of the top ~50 → the LLM gets ~8 chunks → answer with citations or abstain.
- **Freshness and deletion**: daily incremental updates by content hash; deleting a document removes its chunks from **every** shard (legal "right to be forgotten").
- **Latency budget**: retrieval ~100–200 ms, reranking ~100–300 ms, then stream the answer.
- **Evaluation**: a sampled question set with labelled relevant documents; recall@k per stage, faithfulness of answers, and monitoring of abstention rate.

:::interview Follow-ups to expect
*"Why not just a bigger context window?"* — 10M documents never fit; cost per question would be enormous. *"Corpus-wide questions like 'main risks this year'?"* — add a GraphRAG-style summary layer or offline clustering for those (Chapter 13). *"Reranking is too slow."* — fewer candidates, a smaller cross-encoder, or cache.
:::

:::remember
- Answer shape: **define → why → how → trade-off/example** — under 45 seconds.
- Debug RAG by stage: was the right chunk **retrieved**? then was it **used faithfully**?
- Numbers to have ready: 10M × 768 × 4 B ≈ **30.7 GB**; 100M vectors ≈ **307 GB** float32; RRF **k = 60**; LangGraph JS recursion limit **25**.
- System design = **seven steps**: requirements, data, ingestion, serving, safety, evaluation, scale/cost.
- Permissions live in the **data layer** (scoped tools, DB roles, filtered search), never in the prompt.
:::
