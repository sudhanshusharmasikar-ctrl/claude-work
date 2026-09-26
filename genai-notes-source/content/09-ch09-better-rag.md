:::chapter 9 | Making RAG Good | Lecture 14 + extra reading · Must-know
- **Follow-up questions**: query rewriting (Rohit's homework)
- **Multi-hop questions** and **agentic RAG** (Lecture 14)
- **Hybrid search**: BM25 + vectors, fused with **RRF**
- **Reranking**: bi-encoders vs cross-encoders
- Better **chunking**: layout-aware, semantic, parent–child, **contextual retrieval**
- Query tricks: multi-query, **HyDE**, decomposition, filters
- **Lost in the middle** and how to assemble context
- **Evaluating** RAG: recall@k, MRR, faithfulness, RAGAS, abstention
- A failure-mode → fix table for interviews
:::

Chapter 8's RAG works for simple questions. Real users ask follow-ups, use exact product codes, ask questions that need several facts joined together, and ask things your documents don't contain. This chapter is the toolbox interviewers expect you to know — the difference between "I followed a tutorial" and "I can make RAG work".

## 9.1 Follow-up questions: rewrite the query %%MUST%%

Rohit's whiteboard: the user asks *"What is Node.js?"*, then *"Explain **it** in detail"*. Basic RAG embeds *"Explain it in detail"* — which is about nothing — and retrieves garbage. (His `query.js` even has the comment *"intent model ko introduce: Homework"*.)

Fix: keep the chat history, and **before retrieval**, ask the LLM to rewrite the last question into a **standalone** question.

```js title="query rewriting before retrieval (my version of the homework)" lines
const History = [];   // the real conversation: [{ role, parts }]

async function rewriteQuery(question) {
  if (History.length === 0) return question;   // first question: nothing to resolve
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: [...History, { role: "user", parts: [{ text: question }] }],
    config: {
      systemInstruction:
        "Rewrite the user's LAST question as a complete, standalone question, "
        + "replacing words like 'it' or 'that' with what they refer to. "
        + "Return only the rewritten question.",
      temperature: 0,
      thinkingConfig: { thinkingBudget: 0 },   // a quick, cheap call
    },
  });
  return response.text.trim();
}

// in chatting(question):
//   const standalone = await rewriteQuery(question);
//         // e.g. "Explain the V8 engine in Node.js in detail"
//   const queryVector = await embeddings.embedQuery(standalone);
//   ... retrieve, answer, then push the user question and the answer into History
```

I tested it with a scripted fake model: the first question passes through unchanged; for "Explain it in detail" the rewriter receives the 2 earlier messages + the new one, and the rewritten text is what gets embedded. The answer step can still use the history too, so the final reply sounds conversational.

## 9.2 Multi-hop questions and agentic RAG (Lecture 14) %%MUST%%

Rohit's Lecture 14 whiteboard is full of questions where normal RAG **fails**:

- **Shopping logs**: "What should we recommend to Anjali?" → *first* find what Anjali bought → *then* who else bought those items → *then* what else those people bought.
- **Family facts**: "A is father of B … C is son of B … K is daughter of C. What is the relationship between A and K?" → you must **chain** facts: A → B → C → K = great-granddaughter.
- **Bank fraud**: "Is Vedant's account a fraud?" → Vedant → sent money to Priya → Priya's phone device → used by a company → that company is flagged as fraud.
- **"Who are all the friends of Elon Musk and what do they do?"** → facts spread across a long biography.

Why normal RAG fails: similarity search returns the chunks **closest to the question text**. But the answer needs a **chain** of facts, and the later links (Priya's device, the company) are **not similar** to the question at all — you only know to look for them after reading the earlier links.

Two solutions:

1. **Agentic RAG** — give an agent a `search` tool and let it retrieve **several times**, deciding what to look up next from what it found (ReAct, Chapter 5). It can decompose the question, search, read, and search again until it can answer.
2. **Graph RAG** — store the facts as a **graph** of entities and relationships, so "follow the links" is a cheap database query (Chapters 11–12). Best when your data is naturally about **relationships**.

[[fig:agentic-rag|Agentic RAG: instead of one retrieval, the agent keeps searching based on what it has learned so far, until it can answer.]]

Trade-off: agentic RAG is more capable but slower and more expensive (several LLM calls per question), and needs a step limit.

## 9.3 Hybrid search: keywords + meaning %%MUST%%

Embeddings are great at **meaning** but weak at **exact tokens**: error codes (`ERR_4102`), product ids, rare names, version numbers. The classic keyword algorithm **BM25** is the opposite: it scores documents by how often the query's **exact words** appear (term frequency), how **rare** those words are across all documents (inverse document frequency), adjusted for document length.

**Hybrid search** runs **both** searches and **fuses** the two ranked lists. The simplest robust fusion is **Reciprocal Rank Fusion (RRF)**:

`RRF score(d) = Σ over the lists of  1 / (k + rank(d))`, with **k = 60** by convention.

Example: a chunk is **3rd** in the BM25 list and **7th** in the vector list → 1/63 + 1/67 ≈ 0.0159 + 0.0149 = **0.0308**. A chunk that appears in only one list gets only one term. RRF uses **ranks**, not raw scores, so you don't have to make BM25 scores and cosine scores comparable.

[[fig:hybrid|Hybrid retrieval with rank fusion, followed by a reranker that keeps only the best few chunks for the prompt.]]

## 9.4 Reranking: a second, smarter look %%MUST%%

Two kinds of models score (query, chunk) relevance:

| | **Bi-encoder** (embedding model) | **Cross-encoder** (reranker) |
|---|---|---|
| How | Query and chunk are embedded **separately**; compare vectors | Reads query **and** chunk **together** in one model pass |
| Speed | Very fast; chunk vectors are precomputed | Slow; must run once per (query, chunk) pair |
| Accuracy | Good for finding candidates | Better at judging "does this passage answer this question?" |
| Use | First stage: search millions → top 50 | Second stage: rerank top 50 → keep top 5 |

So the standard pipeline is **retrieve wide, rerank narrow**. Examples: open-source cross-encoders (like the MS-MARCO MiniLM rerankers or BGE rerankers) or hosted rerank APIs. An LLM can also act as a reranker — Rohit's Graph RAG similarity handler takes 50 candidates and asks Gemini to pick the best 10 (Chapter 12).

## 9.5 Better chunking %%MUST%%

| Strategy | Idea | Good for |
|---|---|---|
| **Fixed / recursive** (course) | ~N characters, cut at paragraph/line breaks, with overlap | Quick start, plain text |
| **Layout-aware** | Use the document's own structure: PDF blocks, pages, headings, sections | PDFs and papers — **your PaperRAG** (never crosses a page → page citations) |
| **Semantic** | Embed sentences; start a new chunk where the meaning shifts (similarity drops) | Long unstructured text |
| **Parent–child** (small-to-big) | Search on **small** chunks for precision, but send the **bigger parent** section to the LLM for context | Precise matching + enough context |
| **Contextual retrieval** | Before embedding, prepend a short LLM-written note that situates the chunk ("This chunk is from ACME's Q2 2023 report, revenue section…") | Chunks that make no sense alone |

**Contextual retrieval** (published by Anthropic in 2024): in their tests, adding context to chunks before both embedding and BM25 indexing reduced failed retrievals by **49%**, and by **67%** when combined with reranking (top-20 failure rate 5.7% → 2.9% → 1.9%). The cost is one cheap LLM call per chunk at indexing time.

Also add **metadata** to every chunk (title, section path, page, date) — it helps filtering, citations, and even retrieval if you embed the title with the text.

## 9.6 Query-side tricks %%GOOD%%

- **Query rewriting** (9.1) — standalone questions for follow-ups.
- **Multi-query** — ask the LLM for 3–5 different phrasings, retrieve for each, merge (RRF). Helps when users phrase things differently from the documents.
- **HyDE** (Hypothetical Document Embeddings) — ask the LLM to write a **fake answer** first and embed **that**. A fake answer "looks like" the real document more than a short question does, so retrieval improves. (The fake answer is never shown to the user.)
- **Decomposition** — split a complex question into sub-questions; retrieve for each.
- **Metadata filters / self-query** — the LLM extracts structured filters ("2024", "HR department") and the vector DB applies them.
- **Routing** — send the question to the right index or tool (product docs vs HR policies vs SQL database).

## 9.7 Assembling the context: "lost in the middle" %%MUST%%

Research on long prompts ("Lost in the Middle", 2023) found a **U-shaped** pattern: models use information at the **beginning** and **end** of the context best, and are noticeably worse when the key passage is in the **middle** — even for models with long context windows.

Practical rules:

- Keep the final context **small**: retrieve wide, rerank, send the **best 3–8** chunks, not 50.
- Put the most relevant chunk **first** (or first and last).
- **Deduplicate** overlapping chunks.
- Number the chunks `[1]`, `[2]`… and ask the model to **cite** them — PaperRAG's prompt does exactly this.
- Tell the model what to do when the context is insufficient.

## 9.8 Evaluating RAG %%MUST%%

"It seems to work" is not an answer. Build a **labelled evaluation set**: 40–100 realistic questions with the expected answer and/or the expected source (file + page) — and include **unanswerable** questions (the answer is not in your documents).

**Retrieval metrics** (did we find the right chunks?)

| Metric | Meaning |
|---|---|
| **Hit rate / recall@k** | Fraction of questions where a correct chunk is in the top k |
| **Precision@k** | Fraction of the top k that are relevant |
| **MRR** (mean reciprocal rank) | Average of 1 / (rank of the first correct chunk). Ranks 1, 3, not found → (1 + 1/3 + 0) / 3 ≈ **0.444** |

**Generation metrics** (is the answer good?) — the **RAGAS** framework's four core metrics:

| Metric | Question it answers |
|---|---|
| **Faithfulness** | Are all claims in the answer supported by the retrieved context? (hallucination check) |
| **Answer relevancy** | Does the answer actually address the question? |
| **Context precision** | Are the relevant chunks ranked near the top? |
| **Context recall** | Did retrieval find everything needed to answer? (needs a reference answer) |

These often use an **LLM as a judge** — fast and scalable, but judges have biases, so spot-check by hand.

**Abstention metrics** (your PaperRAG story):

- **Unsupported-answer rate** — how often the system answers an unanswerable question.
- **False-refusal rate** — how often it refuses a question it could have answered.
- Moving the similarity threshold trades one against the other; **sweeping** it and plotting the curve is a strong, honest result.

Also track **latency** (p50/p95) and **cost per question**, and re-run the whole set after every change (a regression test for RAG).

## 9.9 Failure modes → fixes (memorise this table) %%MUST%%

| Symptom | Likely cause | Fix |
|---|---|---|
| Right passage exists but isn't retrieved | Bad chunking; embeddings miss exact terms | Better chunking, hybrid BM25 + vectors, contextual retrieval |
| Right passage retrieved, answer still wrong | Too many distractors; weak prompt | Rerank, fewer chunks, best chunk first, clearer prompt |
| Confident answer to an unanswerable question | No abstention path | Similarity threshold + "I don't know" instruction + second check |
| Follow-up questions fail | No history in retrieval | Query rewriting |
| Questions needing several linked facts fail | Single-shot retrieval | Agentic RAG or Graph RAG |
| Numbers in tables are never found | Parser dropped tables / scanned PDF | Table-aware parsing, OCR |
| Answers are out of date | Index not refreshed | Incremental re-indexing with stable ids (upsert) |
| User A sees user B's documents | No access filter in retrieval | Metadata filter by owner/tenant, enforced server-side |
| Slow or expensive | Large k, many LLM calls | Smaller k after rerank, caching, cheaper model for sub-steps |

:::remember
- Follow-ups → **rewrite the query** into a standalone question before retrieval.
- Multi-hop → **agentic RAG** (search repeatedly) or **Graph RAG** (follow relationships).
- **Hybrid** = BM25 (exact words) + vectors (meaning), fused with **RRF**: Σ 1/(60 + rank).
- **Retrieve wide, rerank narrow**: bi-encoder for candidates, cross-encoder (or LLM) to rerank.
- Chunking: layout-aware, semantic, parent–child, **contextual retrieval** (−49% failed retrievals, −67% with reranking in Anthropic's tests).
- Query tricks: multi-query, **HyDE**, decomposition, filters, routing.
- **Lost in the middle**: keep context small, best chunks first, cite `[n]`.
- Evaluate: recall@k, MRR; RAGAS faithfulness / answer relevancy / context precision / context recall; unsupported-answer vs false-refusal rates.
:::

:::quiz
1. What text should be embedded for the follow-up "What about its disadvantages?"
2. Why does normal RAG fail on "Is Vedant's account a fraud?" in Rohit's example?
3. A chunk is ranked 1st by BM25 and not returned by vector search. What is its RRF score (k = 60)?
4. Why is a cross-encoder not used for the first retrieval stage?
5. What does HyDE embed instead of the question?
:::

:::answer
1. A rewritten standalone question, e.g. "What are the disadvantages of the V8 engine in Node.js?" (with "its" resolved from history).
2. The evidence is a chain (Vedant → Priya → device → company → fraud); the later links aren't textually similar to the question, so one similarity search can't find them.
3. 1 / (60 + 1) ≈ 0.0164 (only one list contributes).
4. It must run once per (query, chunk) pair — far too slow over millions of chunks. It's used on a short candidate list.
5. A hypothetical answer written by the LLM, which resembles the real documents more than the short question does.
:::

:::qa Interview questions — advanced RAG
Q: How do you handle follow-up questions in a RAG chatbot?
Keep the conversation history and add a query-rewriting step: an LLM call that turns the latest message into a standalone question using the history; embed and retrieve with that. The answer generation can still see the history. It costs one small LLM call per turn.

Q: What is hybrid search and why use it?
Running keyword search (BM25) and vector search together and fusing the results, usually with Reciprocal Rank Fusion. BM25 catches exact identifiers, names and codes that embeddings miss; vectors catch paraphrases. Together they improve recall, especially on technical or ID-heavy content.

Q: Explain reranking.
A two-stage retrieval: a fast bi-encoder or hybrid search gets the top 20–50 candidates, then a slower cross-encoder (or an LLM) scores each candidate together with the query and keeps the best few. It improves precision and helps with "lost in the middle" because the prompt contains fewer, better chunks.

Q: What is agentic RAG? When is it worth it?
An agent that uses retrieval as a tool and can search multiple times, decompose questions and decide what to look up next. It's worth it for multi-hop or research-style questions; for simple FAQ-style questions a single retrieval is cheaper and faster.

Q: How do you evaluate a RAG system?
With a labelled question set including unanswerable questions. Retrieval: recall@k, MRR. Answers: faithfulness, answer relevancy, context precision/recall (RAGAS-style, often LLM-judged and spot-checked). Plus abstention metrics — unsupported-answer rate and false-refusal rate — and latency and cost. I rerun it after every change.

Q: What is "lost in the middle"?
A finding that LLMs use information at the start and end of a long context better than information in the middle. So I keep the context small after reranking, put the strongest chunks first, and remove duplicates.

Q: What is contextual retrieval?
Before indexing, each chunk gets a short LLM-generated description of where it sits in the document, prepended to the chunk for both embedding and BM25. It fixes chunks that are ambiguous on their own; Anthropic reported roughly half the retrieval failures, and about two-thirds fewer with reranking.

Q: Your RAG answers confidently when the answer isn't in the documents. What do you do?
Add an abstention path: a similarity threshold on the best match (tuned on labelled data), a prompt instruction to answer "I don't know" or a sentinel like INSUFFICIENT_CONTEXT, and measure both unsupported-answer and false-refusal rates to pick the threshold — exactly what I built in PaperRAG.
:::
