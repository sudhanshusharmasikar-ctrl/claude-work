:::chapter 7 | Vector Databases and Fast Search | Lectures 9–11 · whiteboards · Must-know
- Why SQL indexes can't answer "find similar"
- **Exact** search (brute force) vs **approximate** search (ANN), and **recall**
- **IVF**: clustering with k-means — and its four drawbacks
- **KD-trees**: great in 2-D, useless in 768-D
- **HNSW**: the layered graph behind most vector databases
- **Product Quantization**: fitting a billion vectors in memory
- What a vector DB stores, and how to choose one
:::

You now have embeddings. RAG needs to answer, in milliseconds: *"which of my million chunk vectors are closest to this question vector?"* Rohit spends three lectures on how databases do this. Interviewers love this topic because it mixes **DSA** (trees, graphs, clustering, heaps) with AI — your C++ background is a big advantage here.

## 7.1 Why a normal database can't do it %%MUST%%

SQL and NoSQL databases are built for **exact matches** and **ranges**: `WHERE id = 42` (hash index, O(1)) or `WHERE price BETWEEN 10 AND 20` (B-tree, O(log n)). They work because numbers have an **order**.

Vectors have **no single order**. Sorting a million 768-number vectors by their first number tells you nothing about which ones point in the same direction as your query. "Find the 10 most similar" is a different problem — **nearest-neighbour search** — and needs different data structures.

## 7.2 Exact search: brute force (ENN) %%MUST%%

The simplest correct method: compare the query with **every** stored vector, keep the top k (a heap, just like "k closest points" in DSA).

- Cost per query: **N × d** multiply-adds. 1 million vectors × 768 dims = **768 million** operations.
- It's slow **because it's perfect** — it guarantees the true closest vectors. This is **Exact Nearest Neighbour (ENN)**.

For small collections, exact is the **right** choice. Your **PaperRAG** uses FAISS `IndexFlatIP` (brute force) on purpose: a few hundred papers = tens of thousands of vectors, searched in milliseconds, with **no accuracy loss and no tuning**.

## 7.3 Approximate search (ANN) and recall %%MUST%%

**Approximate Nearest Neighbour (ANN)** algorithms give up a **tiny** bit of accuracy for a **huge** speed-up (often 100× or more). They might return 9 of the true top-10 plus the 11th-best.

We measure that accuracy with **recall@k**: of the true top-k neighbours, how many did the index return? Recall@10 = 0.95 means 95% of the real top-10 were found. Every ANN index has knobs that trade **recall** against **speed** and **memory**.

## 7.4 Method 1 — IVF: cluster first, search one cluster %%MUST%%

**IVF (Inverted File index)** works like a library with section signs.

**Indexing (one-time):**

1. Run **k-means** to find, say, 1000 **centroids** (centre points). k-means: pick random centres → assign every vector to its nearest centre → move each centre to the average of its vectors → repeat until stable.
2. Put each vector into the **list** of its nearest centroid (the "inverted file").

**Searching:**

1. Compare the query with the **1000 centroids** only.
2. Search **inside the closest cluster** (~1000 vectors if clusters are even).

About 1000 + 1000 comparisons instead of 1,000,000.

[[fig:ivf|IVF: the query is compared with the centroids, then only the vectors inside the nearest cluster(s) are checked. A query near a border can miss its true neighbour in the next cluster.]]

Rohit's four **drawbacks** of IVF (interview favourite):

| Drawback | Meaning | Usual fix |
|---|---|---|
| **Training cost** | k-means must run over the dataset before indexing; for 100M vectors that takes hours | Train on a sample |
| **Border problem** | The true nearest neighbour may sit just across the border, in another cluster | Search several clusters (**nprobe** > 1) — slower |
| **Dynamic data** | New vectors change the data distribution; clusters become unbalanced and stale | Periodically re-train |
| **Choosing K** | Too few clusters → each is huge (slow); too many → more border misses | Tune on your data |

## 7.5 Method 2 — KD-tree: split the space in halves %%GOOD%%

A **KD-tree** is a binary search tree for points. Split all points at the **median x** (vertical line); split each half at its **median y** (horizontal line); keep alternating dimensions until each box has only a few points.

Rohit's 15-point example (A–O). The first split is at H (x = 11); the left half splits at D (y = 11), the right half at J (y = 10). Now find the nearest neighbour of **Q = [13, 8]**:

[[fig:kdtree|KD-tree search for Q = [13, 8]. Q falls in the lower-right box, but the true nearest point M lies across the y = 10 line — the search must backtrack.]]

1. Walk down: x = 13 ≥ 11 → right; y = 8 < 10 → lower-right box {L, N, O}. Best so far: **L at 5.39**.
2. **Backtrack**: the split line y = 10 is only 2 away from Q, and 2 < 5.39 — the circle of radius 5.39 crosses the line, so a closer point **might** be on the other side. Check the upper-right box → **M at 5.00** (better!), I at 5.10.
3. The x = 11 line is also only 2 away → check the left half → best there is F at 5.66 → no improvement. Answer: **M**. (Top 3: M 5.00, I 5.10, then H or L at 5.39 — I verified these distances.)

In 2 or 3 dimensions, most branches are skipped → about **O(log n)**. In **768 dimensions**, the search ball crosses almost **every** split line, so you backtrack everywhere and it becomes brute force. This is the **curse of dimensionality** — why KD-trees are not used for text embeddings.

:::cpp It's a BST with a twist
A KD-tree node is `struct Node { Point p; int axis; Node *left, *right; };` — the same pruning idea as branch-and-bound. You prune a subtree only when the distance to its splitting line is larger than your best distance so far.
:::

## 7.6 Method 3 — HNSW: a skip list made of graphs %%MUST%%

**HNSW (Hierarchical Navigable Small World)** is the index used by most vector databases (Qdrant, Weaviate, pgvector, Elasticsearch, Redis, Milvus…).

**Structure:**

- **Layer 0** contains **all** vectors. Each vector is a node connected to about **M** (e.g. 16) of its nearest neighbours — a "small world" graph where any node can be reached in a few hops.
- **Upper layers** contain exponentially **fewer** nodes (each node is promoted to the next layer with some probability — Rohit uses 1/2). The top layer has only a handful: long "highway" jumps.

**Search:**

1. Start at the **entry point** on the top layer.
2. **Greedy**: jump to whichever neighbour is closer to the query; repeat until no neighbour is closer.
3. **Drop down** one layer and continue from there.
4. At **layer 0**, do a **beam search**: keep a list of the best **efSearch** candidates (e.g. 50–100), keep expanding the closest unexplored one, and finally return the top-k.

[[fig:hnsw|HNSW: long jumps on sparse upper layers, then a careful beam search on the dense bottom layer.]]

:::analogy Mumbai local trains
To travel across Mumbai you take a **fast train** (few stops, big jumps) to the right area, then switch to a **slow train** (every stop) for the last part. HNSW's top layers are the fast trains; layer 0 is the slow train. In C++ terms, it's the same idea as a **skip list**.
:::

**Knobs:** **M** (links per node: more = better recall, more memory), **efConstruction** (effort while building), **efSearch** (effort per query: higher = more accurate, slower).

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| No training phase (unlike IVF's k-means) | **Memory-hungry**: stores full vectors **plus** the graph links |
| No border problem — navigation is smooth | Deletes are awkward (usually "mark deleted" + rebuild later) |
| Inserts are cheap (~O(log N)) → good for changing data | Building a big index takes time |
| Best speed/recall trade-off in practice | Still approximate |

Insert, briefly: pick a random top level for the new vector; search down to find its nearest neighbours on each layer; connect it to the **M** closest, both directions; if a neighbour now has too many links, keep only its closest M.

## 7.7 Method 4 — Product Quantization: compress the vectors %%GOOD%%

The **memory** problem: one 1536-dim vector of 32-bit floats = 1536 × 4 = **6,144 bytes**. A **billion** vectors = **6.1 TB** of RAM. Too expensive.

**Product Quantization (PQ)** compresses each vector (Rohit's colour analogy: store a palette **index** instead of the full RGB value):

1. **Split** the vector into chunks, e.g. a 16-number vector → 4 chunks of 4.
2. For each chunk position, run k-means with **256 centroids** → a **codebook** (256 entries fit in one byte: 0–255).
3. Store each chunk as the **id** of its nearest codebook entry. The vector becomes `[10, 23, 123, 16]` — **4 bytes instead of 64** (16× smaller).

[[fig:pq|Product Quantization: each chunk of the vector is replaced by the id of its nearest centroid in that chunk's codebook.]]

**Searching with PQ:** split the query into the same 4 chunks; for each chunk compute its distance to all 256 centroids of that codebook → 4 small **lookup tables** (4 × 256 = 1024 distances, computed once). The distance to **any** stored vector is now just **4 table lookups added up** — e.g. `1.3 + 6.1 + 1.5 + 9.1 = 18`. Very fast.

Cost: compression loses detail, so results are rougher. Common fix: **re-rank** the top candidates using their original full vectors. **IVF-PQ** (IVF clustering + PQ compression) is the classic billion-scale combination.

## 7.8 Which method is best? %%MUST%%

Rohit's comparison:

| Method | Speed (latency) | Accuracy (recall) | Memory |
|---|---|---|---|
| **HNSW** | Highest | Highest | **Highest** |
| **IVF-PQ** (hybrid) | High | High (with re-ranking) | **Lowest by far** |
| **IVF** (flat lists) | Medium | Medium | Low |
| **KD-tree** | Low in high dimensions | Low | Medium |
| **Brute force (flat)** | Slow at scale | **Perfect** | Full vectors |

And the vector-database landscape (from the lecture, lightly updated):

| Database / library | Type | Known for |
|---|---|---|
| **Pinecone** | Managed service (SaaS) | Zero-ops, easy API — used in the course (internals are proprietary) |
| **Qdrant** | Open source (Rust) | Speed, strong metadata filtering |
| **Weaviate** | Open source | Built-in hybrid (keyword + vector) search, modules |
| **Milvus** | Open source | Huge scale, many index types (HNSW, IVF-PQ, …) |
| **pgvector** | Postgres extension | Vectors **next to your SQL data**; HNSW and IVFFlat |
| **Elasticsearch / OpenSearch** | Search engines | Keyword (BM25) + vector in one query |
| **Redis** | In-memory store | Very low latency |
| **FAISS** (Meta) | **Library**, not a database | The reference toolkit (flat, IVF, PQ, HNSW); used in **PaperRAG** |
| **Chroma** | Lightweight open source | Quick local prototypes |

## 7.9 What does a vector database actually store? %%MUST%%

Each record has three parts:

```json title="one record in a vector DB"
{
  "id": "product_456",
  "values": [0.98, 0.23, -0.11, "... 3072 numbers ..."],
  "metadata": {
    "product_name": "Red Running Shoes",
    "price": 89.99,
    "link": "https://..."
  }
}
```

- **id** — unique key (upsert with the same id **replaces** the record — useful for re-indexing).
- **values** — the vector.
- **metadata** — anything you want back or want to **filter** on: the chunk text, source file, page, user id, date.

Features that matter in production:

- **Metadata filtering** — "similar chunks **where** `user_id = 7` and `year ≥ 2024`". Essential for multi-user apps (never let user A retrieve user B's documents — OWASP LLM08).
- **Namespaces / collections** — separate indexes per tenant or per document set.
- **Upsert / delete**, persistence, backups, replication, access control.

:::cpp Library vs database
**FAISS** is like `std::vector` + an algorithm: it lives **inside** your program's memory, you save/load it yourself, and it stores only vectors with integer positions. PaperRAG therefore keeps the chunk text and page numbers in a separate `chunks.jsonl` file, row *i* matching vector *i*. A **vector database** is a server: it stores metadata, filters, handles many users, and survives restarts.
:::

## 7.10 How to choose (interview-ready answer) %%MUST%%

- **Small data (< ~1M vectors)**: exact flat search (FAISS flat, or pgvector) — no recall loss, no tuning. *(PaperRAG's choice.)*
- **Already on Postgres / need joins and SQL filters**: **pgvector**.
- **Don't want to run servers**: **Pinecone** (managed).
- **Self-hosted, open source, heavy filtering**: **Qdrant**, **Weaviate**, **Milvus**.
- **Need keyword + vector together**: Elasticsearch / OpenSearch / Weaviate (hybrid — Chapter 9).
- **Billions of vectors, tight memory**: IVF-PQ with re-ranking.

:::remember
- Normal indexes need an **order**; vectors don't have one → special nearest-neighbour structures.
- **Brute force** = exact, O(N·d) per query; perfect for small data (PaperRAG uses it on purpose).
- **ANN** trades a little **recall** for a lot of **speed**; recall@k measures what you lost.
- **IVF**: k-means clusters; drawbacks = training cost, **border problem** (nprobe), dynamic data, choosing K.
- **KD-tree**: median splits + backtracking; dies in high dimensions (**curse of dimensionality**).
- **HNSW**: layered small-world graphs, greedy on top + **efSearch** beam at layer 0; best speed/recall; **most memory**.
- **PQ**: split into chunks, 256-centroid codebooks, 1 byte per chunk, lookup-table distances; **IVF-PQ** for billions.
- A record = **id + vector + metadata**; use **metadata filters** for per-user security.
:::

:::quiz
1. Why is brute force the right choice for PaperRAG?
2. What is the "border problem" in IVF, and how is it reduced?
3. In the KD-tree example, why does the search leave the lower-right box?
4. What does efSearch control in HNSW?
5. A 16-dimension float vector is PQ-encoded with 4 chunks and 256 centroids per codebook. How many bytes before and after?
:::

:::answer
1. The corpus is small (tens of thousands of vectors), so exact search is fast enough, gives perfect recall and needs no tuning.
2. The true nearest neighbour lies just across a cluster boundary, so searching only the nearest cluster misses it. Search several nearest clusters (nprobe > 1), at some speed cost.
3. The distance from Q to the y = 10 split line (2) is smaller than the best distance found (5.39), so a closer point could be on the other side — and M (5.00) is.
4. How many candidates the beam search keeps at layer 0 — higher means better recall but slower queries.
5. Before: 16 × 4 = 64 bytes. After: 4 chunks × 1 byte = 4 bytes.
:::

:::qa Interview questions — vector search
Q: Why do we need vector databases? Can't we use SQL?
SQL indexes (hash, B-tree) rely on exact values or a sort order. Similarity search in hundreds of dimensions has no useful order, so we need nearest-neighbour structures (HNSW, IVF, PQ) plus features like metadata filtering and upserts. pgvector shows the two can live together in Postgres.

Q: Explain HNSW.
A multi-layer proximity graph. Every vector is in layer 0, linked to about M nearest neighbours; higher layers hold exponentially fewer nodes for long jumps. A query starts at the top, greedily moves closer, drops layer by layer, and at layer 0 runs a beam search keeping efSearch candidates. It gives excellent recall and speed and supports inserts, at the cost of high memory.

Q: What's the difference between exact and approximate nearest neighbour search?
Exact (brute force) compares against every vector and guarantees the true top-k, costing O(N·d). ANN uses an index to check only a small part of the data, returning almost the same results much faster; its accuracy is measured by recall@k and tuned with parameters like nprobe or efSearch.

Q: What is product quantization and when would you use it?
A compression method: split each vector into sub-vectors, replace each with the id of its nearest centroid from a 256-entry codebook (1 byte), and compute distances with precomputed lookup tables. Use it when memory is the bottleneck — hundreds of millions to billions of vectors — usually combined with IVF and a re-ranking step.

Q: Why did you use a flat (brute-force) FAISS index in PaperRAG instead of HNSW?
Because the corpus is small — tens of thousands of chunk vectors — and exact search runs in milliseconds on a CPU. An ANN index would add recall loss and tuning knobs to solve a speed problem I don't have. If the corpus grew to millions of chunks, I'd switch to HNSW or IVF and measure recall against the flat index.

Q: How do you keep one user from retrieving another user's documents?
Store the owner (user/tenant id) in each vector's metadata or use separate namespaces, and always apply a filter on it in the query — enforced server-side, not left to the LLM. This is the OWASP "vector and embedding weaknesses" risk.
:::
