:::chapter 10 | Vectorless RAG | Extra reading: PageIndex and friends · Good to know
- What "vectorless" RAG means, and why people want it
- **"Similarity ≠ relevance"** — the core argument
- **PageIndex**: a tree index + LLM reasoning instead of vectors
- Pros and cons, honestly
- The wider vectorless family: BM25, **text-to-SQL**, graphs, agentic search, long context
- A decision table: which retrieval for which data
- How it connects to PaperRAG and SchemaMind
:::

In 2025 "vectorless RAG" became a hot interview topic, mainly because of an open-source project called **PageIndex**. You don't need to build it — you need to **explain the idea, the trade-offs, and when you'd use it**. That makes you look current.

## 10.1 What problem is it solving? %%GOOD%%

Classic RAG = chunk → embed → nearest-neighbour search. It struggles with **long, structured, professional documents** — a 300-page annual report, a legal contract, a technical manual:

- **Similarity ≠ relevance.** The chunk that *sounds* most like the question is not always the chunk that *answers* it. "What was the operating margin in 2023?" is similar to dozens of passages that mention margins.
- **Chunking destroys structure.** A table, its heading and its footnote end up in different chunks; "see Section 4.2" points nowhere.
- **Hard to explain.** "Retrieved because cosine = 0.83" doesn't tell an auditor *why* that part was chosen.

How does a **human expert** read such a document? They open the **table of contents**, go to the right chapter, then the right section, read it, and maybe jump to an appendix. **Vectorless RAG** copies that.

## 10.2 PageIndex: tree index + reasoning %%GOOD%%

**PageIndex** (open source, by VectifyAI, 2025) works in two steps:

1. **Build a tree index** of the document — a smart "table of contents": each node is a section with its title, page range and a short summary, nested like chapters → sections → subsections. No chunking, no embeddings, no vector database.
2. **Reasoning-based retrieval** — for each question, the LLM reads the tree (not the whole document), decides which node(s) most likely contain the answer, opens them, reads, and either answers or goes deeper / tries another branch — a **tree search guided by reasoning**. The answer cites the exact sections and pages it used.

[[fig:pageindex|Vector RAG compares the question with every chunk; PageIndex lets the LLM navigate a table-of-contents tree like a human expert.]]

The authors report that a financial-QA system built on this idea reached **98.7% accuracy on FinanceBench** (questions over company filings), well above typical vector-RAG results on that benchmark. Treat it as the authors' claim — but it shows why the idea got attention.

:::analogy Library catalogue vs "find similar pages"
Vector RAG is like photocopying every page of every book, shuffling them, and picking the pages whose words look most like your question. PageIndex is like a librarian who reads the table of contents, walks to the right chapter, and reads it properly.
:::

## 10.3 Honest pros and cons %%GOOD%%

| ✅ Strengths | ❌ Weaknesses |
|---|---|
| Keeps the document's **structure**; no chunk boundaries cutting tables in half | **Several LLM calls per question** (navigate, read, maybe backtrack) → slower and costlier |
| **Explainable**: "Section 7.2, pages 45–47, because…" | Needs documents with a meaningful structure (or an LLM-generated one) |
| No embedding model, no vector DB to run | Doesn't scale by itself to **millions of short documents** — you still need a first step to pick the right documents |
| Good for long, professional, high-stakes documents | Building the tree costs LLM calls; errors in reasoning can send it down the wrong branch |

So it's **not** "vectors are dead". It's a strong option for a specific kind of data.

## 10.4 The wider vectorless family %%MUST%%

"Retrieval without embeddings" is older than PageIndex. Interviewers like it when you connect these:

| Approach | How it retrieves | Example |
|---|---|---|
| **Keyword search (BM25)** | Exact word statistics | Elasticsearch, the keyword half of hybrid search (Ch 9) |
| **Structured retrieval (text-to-SQL)** | The LLM writes a query; the database returns exact rows | **Your SchemaMind** |
| **Graph traversal** | Follow relationships with a graph query | Graph RAG with Cypher (Ch 11–12) |
| **Agentic search** | An agent uses tools like list/grep/read to explore files | Lecture 7's code reviewer; coding agents search repos this way instead of embedding them |
| **Tree / TOC navigation** | LLM reasons over a document hierarchy | **PageIndex** |
| **Long context ("just paste it")** | No retrieval: small documents go straight into the prompt, often with caching | A 20-page policy with a 1M-token model |

## 10.5 Which retrieval for which data? %%MUST%%

| Your data looks like… | Best starting point |
|---|---|
| Many short, independent texts (FAQs, tickets, chat logs, product descriptions) | **Vector or hybrid RAG** |
| A few long, structured documents where exact sections matter (annual reports, contracts, manuals, research papers) | **Tree/TOC navigation** (PageIndex-style), or layout-aware chunking + hybrid |
| Tables and numbers in a database | **Text-to-SQL** |
| Questions about relationships and multi-hop chains | **Graph RAG** |
| A codebase | **Agentic search** (grep, read files, run tests) |
| A small corpus that fits comfortably in the context window | **Long context** + prompt caching |

Real systems often **combine** them: a router sends each question to the right retriever (Chapter 5's routing pattern).

## 10.6 Connecting to your projects %%GOOD%%

- **PaperRAG** already respects document structure (text blocks, pages). A natural extension is a **section tree**: research PDFs often have an outline (PyMuPDF's `doc.get_toc()` returns `[level, title, page]` entries), so questions like "what does the Method section say about X?" could navigate sections first, then use vector search inside them — a hybrid of both worlds.
- **SchemaMind** is a hybrid too: it uses **vectors to pick tables**, then **vectorless SQL** to fetch exact answers. If asked "is SchemaMind RAG?", say: *"Yes — retrieval-augmented generation where the retrieval step is a SQL query, not a similarity search. Embeddings only select which tables go into the prompt."*

:::remember
- **Vectorless RAG** = retrieval without embeddings; the famous 2025 example is **PageIndex**.
- PageIndex: build a **tree index** (TOC with summaries) → the LLM **reasons** its way down the tree → answers with section/page references.
- Argument: **similarity ≠ relevance**; chunking breaks structure; experts navigate by structure.
- Costs: more LLM calls, latency; needs structure; not for millions of tiny docs alone.
- Family: BM25, **text-to-SQL**, graph traversal, agentic file search, TOC navigation, long context.
- Choose by data shape; combine with a router.
:::

:::quiz
1. What does "similarity ≠ relevance" mean? Give an example.
2. What are PageIndex's two steps?
3. Why is PageIndex alone not a good fit for a million customer-support tickets?
4. Is SchemaMind vector RAG, vectorless RAG, or both? Explain.
5. For a 15-page HR policy and a 1M-token model, what is the simplest approach?
:::

:::answer
1. The most similar-sounding text may not answer the question — "operating margin in 2023?" matches every passage that mentions margins, but only one gives the 2023 figure.
2. Build a hierarchical tree index (sections with summaries); then let the LLM reason over the tree to pick and read the right sections.
3. Tickets are many short, independent texts without a useful hierarchy; navigating by reasoning would be slow and costly. Vector/hybrid search is the right first stage.
4. Both: embeddings select relevant tables; the answer itself is retrieved with SQL (vectorless).
5. Put the whole policy in the prompt (long context), ideally with prompt caching — no retrieval pipeline needed.
:::

:::qa Interview questions — vectorless RAG
Q: What is vectorless RAG?
Retrieval-augmented generation where the retrieval step doesn't use embeddings or a vector database. Examples: PageIndex-style navigation of a document's table-of-contents tree by an LLM, BM25 keyword search, text-to-SQL over databases, graph traversal, or agents searching files with tools.

Q: How does PageIndex work, and when would you use it?
It builds a hierarchical index of a document — sections with titles, page ranges and summaries — and lets the LLM reason over that tree to choose which sections to read, like a human expert using a table of contents. I'd use it for long, structured, high-stakes documents like financial filings or contracts, where exact sections matter and explainability is important. For huge collections of short texts I'd stay with vector or hybrid search.

Q: Is vector search becoming obsolete?
No. It's cheap, fast and scales to millions of documents. Vectorless methods trade cost and latency for precision and structure awareness. The practical answer is to pick retrieval by data shape and often combine them behind a router.

Q: What are the downsides of LLM-driven (reasoning-based) retrieval?
More LLM calls per question, so higher latency and cost; dependence on good document structure; the model can reason itself into the wrong branch; and it still needs a first step to choose documents when the corpus is large. It should be evaluated like any retriever — accuracy, latency, cost.
:::
