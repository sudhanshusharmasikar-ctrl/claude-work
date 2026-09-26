:::chapter 13 | Microsoft GraphRAG and Choosing the Right RAG | Extra reading: Microsoft GraphRAG docs · Good to know
- Two different things people call "Graph RAG"
- **Microsoft GraphRAG**: entity graph → **communities** → **community reports**
- **Global**, **local** and **DRIFT** search — which question needs which
- Costs, and cheaper variants
- One table comparing vector RAG, KG Graph RAG, Microsoft GraphRAG, vectorless RAG and text-to-SQL
- A decision flowchart you can draw in an interview
:::

When an interviewer says "Graph RAG", they may mean Rohit's style (a designed knowledge graph you query) or Microsoft's **GraphRAG** project (2024), which is famous for answering "big picture" questions. Know both, and know when to use which — that's a senior-sounding answer.

## 13.1 Two meanings of "Graph RAG" %%GOOD%%

| | **Knowledge-graph RAG** (Rohit's movie project) | **Microsoft GraphRAG** |
|---|---|---|
| Schema | **You design it** (Movie, Actor, DIRECTED…) | **Open** — the LLM extracts whatever entities and relations it finds |
| Retrieval | Graph **queries** (Cypher) built from a plan | Summaries of **communities** + entity neighbourhoods |
| Best for | Precise relational facts, counts, paths | "What are the main themes / how do these things relate across the whole corpus?" |
| Answers | Exact rows | Synthesised, holistic answers |

## 13.2 How Microsoft GraphRAG indexes a corpus %%GOOD%%

1. **Split** the documents into text units (chunks).
2. **Extract** with an LLM: entities (people, organisations, places, concepts), relationships between them, and short descriptions — for **every** chunk.
3. **Build a graph** by merging the same entities across chunks.
4. **Detect communities** with the **Leiden** algorithm — groups of entities that are densely connected — in a **hierarchy** (big communities containing smaller ones).
5. **Summarise** each community with an LLM into a **community report** ("This group is about the 2023 supply-chain disruption involving…").
6. Embed entity descriptions / text units for lookups.

[[fig:ms-graphrag|Microsoft GraphRAG: text → entity graph → hierarchical communities → LLM-written community reports.]]

Why communities? A normal RAG can't answer *"What are the top 5 themes in these 10,000 news articles?"* — no single chunk contains the answer; it's spread over everything. Community reports are **pre-computed summaries of whole regions of the corpus**, so the answer can be assembled from them.

## 13.3 Query modes %%GOOD%%

| Mode | How it works | Use for |
|---|---|---|
| **Global search** | Map-reduce over community reports: each report produces a partial answer with a relevance score; the best partial answers are combined | Corpus-wide, "sensemaking" questions: themes, trends, summaries |
| **Local search** | Start from entities mentioned in the question; gather their neighbours, relationships, source text units and related community reports | Specific questions about particular entities |
| **DRIFT search** | Local search enriched with community information to broaden and refine the answer | Specific questions that benefit from wider context |

**Cost warning.** Indexing runs LLM calls over the **entire** corpus (extraction + summaries), which is expensive for large or fast-changing data. Microsoft later proposed cheaper variants (such as **LazyGraphRAG**, which postpones most LLM work until query time). In an interview: *"GraphRAG buys global understanding with a large indexing cost; I'd use it when those corpus-level questions are the product."*

## 13.4 The big comparison table %%MUST%%

| Approach | Index cost | Best questions | Weak at |
|---|---|---|---|
| **Vector / hybrid RAG** (Ch 8–9) | Low (embed chunks) | Semantic lookups over many documents | Multi-hop, exact aggregates, corpus-wide themes |
| **KG Graph RAG** (Ch 12) | Medium (LLM extraction into a fixed schema) | Relationships, multi-hop, counts, paths | Fuzzy semantic questions; schema design effort |
| **Microsoft GraphRAG** | **High** (LLM over all text + summaries) | Global themes, summaries, "how do these relate" | Cost, fast-changing data, exact numbers |
| **Vectorless / PageIndex** (Ch 10) | Low–medium (build a tree) | Precise sections of long structured documents | Huge collections of short texts; latency |
| **Text-to-SQL** (SchemaMind) | Low (schema description) | Exact numbers, filters, aggregates over tables | Unstructured text |
| **Long context** | None | Small corpora | Cost per call, "lost in the middle" |

## 13.5 A decision flowchart %%MUST%%

[[fig:rag-decision|Pick retrieval by what the question needs. Real products often route between several of these.]]

:::interview The senior answer
"I'd first look at the questions users actually ask and the shape of the data. Exact numbers from tables → text-to-SQL. Relationship chains → a knowledge graph. Semantic lookups over lots of text → hybrid vector search with reranking. Corpus-wide themes → GraphRAG-style community summaries if the budget allows. Long structured reports → section-aware or tree-based retrieval. Then I'd put a router in front and measure each path on an evaluation set."
:::

:::remember
- "Graph RAG" = either a **designed knowledge graph** queried precisely (Rohit) or **Microsoft GraphRAG** (open-schema graph + community summaries).
- Microsoft GraphRAG indexing: chunk → LLM extracts entities/relations → graph → **Leiden communities** (hierarchical) → **community reports**.
- **Global** search (map-reduce over reports) for corpus-wide questions; **local** search around entities for specific ones; **DRIFT** mixes both.
- Big indexing cost; cheaper variants exist (e.g. LazyGraphRAG).
- Choose retrieval by **question type and data shape**; combine with a **router**.
:::

:::quiz
1. Which approach would you pick for "What are the recurring complaints across 50,000 support tickets?" Why?
2. Which for "How many orders from Indore were cancelled last month?"
3. What does a community report contain, and why is it useful?
4. What is the main downside of Microsoft GraphRAG?
:::

:::answer
1. Microsoft-GraphRAG-style global search (or at least clustering + summaries): the answer is spread across the whole corpus, not in any single chunk.
2. Text-to-SQL — it's an exact aggregate over structured data.
3. An LLM-written summary of a densely connected group of entities and their relationships; it pre-computes "what this region of the corpus is about", so global questions can be answered from summaries.
4. Indexing cost (LLM calls over all text) and difficulty keeping it fresh for fast-changing data.
:::

:::qa Interview questions — choosing RAG
Q: What is Microsoft's GraphRAG and how is it different from normal RAG?
It uses an LLM to build an entity–relationship graph from the corpus, clusters it into hierarchical communities with the Leiden algorithm, and writes summaries for each community. Global questions are answered by map-reducing over those summaries; local questions by exploring entity neighbourhoods. Normal RAG retrieves a few similar chunks, so it can't answer corpus-wide "what are the themes" questions.

Q: When would you NOT use GraphRAG?
When questions are simple lookups, when data changes quickly, or when the budget can't cover LLM processing of the whole corpus. Hybrid vector RAG is cheaper and usually good enough; for exact numbers I'd use SQL.

Q: How would you design retrieval for a company assistant that answers HR policy questions, sales numbers and "who worked on project X"?
A router: policy questions → hybrid RAG over documents with citations; sales numbers → text-to-SQL on the warehouse with read-only validation; "who worked on X" → a knowledge graph of people, projects and teams (or SQL joins if it's already relational). Each path evaluated separately, with access control enforced in every retriever.
:::
