:::chapter Part 1 | Embeddings, Vector Search, RAG and Graph Databases | Lectures 8–16 · 31 questions
- **A.** Embeddings (Q1–Q3)
- **B.** Vector databases and search algorithms (Q4–Q14)
- **C.** RAG (Q15–Q19)
- **D.** Advanced RAG, Lecture 14 (Q20–Q24)
- **E.** Graph databases (Q25–Q29)
- **F.** Linking it to your project (Q30–Q31)
:::

## A. Embeddings: the base for everything

:::qa -
Q: What is an embedding? {{p:66–68}}
A list of numbers that represents the meaning of a text: similar meanings give nearby vectors. It comes from a trained model, and the dimensions aren't human-readable. Documents and questions must use the **same model**, because vectors from different models can't be compared.

Q: Cosine similarity or Euclidean distance: which for text, and why? {{p:68}}
Cosine, because it measures the **angle** (the direction of meaning) and ignores length. A short text and a long article on the same topic point the same way but have different lengths, so Euclidean would wrongly call them far apart.

Q: What does normalising do? {{p:70}}
It scales every vector to length 1. Then the dot product equals cosine similarity, and Euclidean distance gives the same ranking as cosine. Vector databases like it because a dot product is the fastest calculation. PaperRAG normalises for exactly this reason.
:::

## B. Vector databases and search algorithms

:::qa -
Q: Why can't a normal database do similarity search? {{p:74}}
Normal indexes (B-trees, hashes) need an order or an exact key. Vectors have no natural order, and "find the 10 closest" isn't an exact match, so we need special nearest-neighbour structures.

Q: What is brute-force (exact) search, and when is it the right choice? {{p:74}}
Compare the query with every stored vector and keep the top k. The cost is N × d per query: 1 million vectors × 768 dimensions = 768 million operations. It's slow but **perfect**. It's the right choice for small data, which is why PaperRAG uses FAISS `IndexFlatIP`.

Q: What is approximate search (ANN), and what is recall@k? {{p:75}}
ANN gives up a tiny bit of accuracy for a huge speed-up, often 100× or more. Recall@k measures what you lost: of the true top-k, how many did the index return? Recall@10 = 0.95 means 95% of the real top 10 were found.

Q: Explain IVF and its four drawbacks. {{p:75–76}}
**Indexing:** k-means finds, say, 1,000 cluster centres, and each vector goes into its nearest centre's list. **Searching:** compare the query with the 1,000 centres, then search inside the closest cluster. That's about 2,000 comparisons instead of 1,000,000. The four drawbacks:

1. **Training cost:** k-means over all the data.
2. **Border problem:** the true neighbour may sit just over the edge, in another cluster. The fix is searching more clusters (nprobe), which is slower.
3. **Changing data:** clusters go stale as new data arrives.
4. **Choosing K:** the number of clusters has to be tuned.

Q: Why don't we use KD-trees for text embeddings? {{p:76–77}}
A KD-tree splits space in halves, alternating dimensions, and backtracks across a split line when a closer point might be on the other side. In 2–3 dimensions it skips most branches. In 768 dimensions the search crosses almost every split line, so it backtracks everywhere and becomes brute force. That's the **curse of dimensionality**.

Q: Explain HNSW. {{p:77}}
- **Structure:** layer 0 holds every vector, each linked to about M (e.g. 16) of its nearest neighbours. Upper layers hold fewer and fewer nodes, giving long-distance "highway" links, like a skip list.
- **Search:** start at the top layer, hop greedily to whichever neighbour is closer, drop a layer and repeat. At layer 0, run a beam search that keeps the best **efSearch** candidates.
- **Analogy:** a fast train to the right area, then a slow train for the last stops.

Q: HNSW's settings, advantages and disadvantages? {{p:77–78}}
- **Settings:** **M** (links per node: better accuracy, more memory), **efConstruction** (build quality), **efSearch** (accuracy vs speed per query).
- **Advantages:** no training, no border problem, cheap inserts, the best speed/accuracy balance.
- **Disadvantages:** **the most memory** (full vectors plus links), awkward deletes, and it's still approximate.

Q: Explain product quantization (PQ). {{p:78–79}}
- **The problem:** one 1536-dimension vector in 32-bit floats takes 6,144 bytes, so a billion vectors need 6.1 TB of RAM.
- **Compression:** split each vector into chunks, learn a 256-entry codebook per chunk position, and store each chunk as a 1-byte id. A 16-number vector becomes 4 bytes instead of 64.
- **Search:** compute 4 small lookup tables once per query. The distance to any stored vector is then 4 table lookups added together.
- **Cost:** some accuracy is lost, so you **re-rank** the top candidates with their full vectors. **IVF-PQ** is the standard choice at billion scale.

Q: Which search method would you pick, and when? {{p:79–81}}
- **Small data:** exact flat search.
- **Best speed and accuracy, and memory is fine:** HNSW.
- **Billions of vectors with tight memory:** IVF-PQ with re-ranking.
- **Already on Postgres:** pgvector.
- **No servers to run:** Pinecone.

Q: What does a vector database store, and why does metadata matter? {{p:80}}
Each record has an **id**, the **vector** and **metadata** (chunk text, file, page, user id, date). Metadata enables filtering, like "only this user's documents", which is essential for security in multi-user apps.

Q: FAISS vs a vector database? {{p:80}}
FAISS is a library that lives in your program's memory and stores only vectors; you save and load it yourself. That's why PaperRAG keeps the chunk text in a separate `chunks.jsonl`. A vector database is a server: metadata, filtering, many users, persistence.
:::

## C. RAG

:::qa -
Q: What is RAG, and why use it instead of fine-tuning? {{p:84–86}}
Retrieve the relevant chunks from your data, put them in the prompt, and let the LLM answer from them: an open-book exam. It fixes the knowledge cutoff, gives access to private data, reduces hallucinations and enables citations. You update it by re-indexing, not retraining. Fine-tuning is for changing **behaviour or style**, not for adding facts.

Q: Walk me through a RAG pipeline end to end. {{p:85}}
- **Indexing:** load → chunk → embed → store (vector + text + metadata).
- **Query:** embed the question with the **same model** → search the top-k → build the prompt (rules + chunks + question) → the LLM answers.

Q: How do you choose chunk size and overlap? {{p:86–87}}
The course uses 1,000 characters with 200 overlap. Too small loses context; too big mixes topics and blurs the embedding. Overlap keeps a sentence that falls on a boundary whole in at least one chunk. RecursiveCharacterTextSplitter cuts at paragraphs first, then lines, then words. Final values come from testing on an evaluation set.

Q: How do you reduce hallucinations in RAG? {{p:90}}
- Tell the model to answer **only** from the context, and give it an escape sentence ("I don't have enough information").
- Use a low temperature.
- Use a similarity threshold, so weak retrievals refuse before the LLM is called (PaperRAG's first guard).
- Require citations.

Q: What can't basic RAG do? {{p:91}}
- Handle follow-up questions.
- Answer multi-hop questions.
- Match exact terms, like error codes or names.
- Refuse when retrieval is weak (no cut-off), or cite its sources.
- Measure itself (no evaluation).

These are exactly what advanced RAG fixes.
:::

## D. Advanced RAG (Lecture 14)

:::qa -
Q: How do you handle follow-up questions like "Explain it in detail"? {{p:94–95}}
Before retrieving, ask the LLM to rewrite the last question into a **standalone** question using the chat history. After "What is Node.js?", the follow-up "Explain it in detail" becomes "Explain Node.js in detail". Then embed and search with that rewritten question.

Q: What are multi-hop questions, and why does normal RAG fail on them? {{p:95}}
Questions that need a **chain** of facts. Example: "Is Vedant's account a fraud?" → Vedant sent money to Priya → Priya's phone → used by a company → that company is flagged. Similarity search only finds chunks close to the question, and the later links aren't similar to it at all.

Q: Agentic RAG vs Graph RAG? {{p:95–96}}
- **Agentic RAG:** an agent with a search tool retrieves several times, deciding what to look up next. Flexible, but several LLM calls per question, slower and more expensive, and it needs a step limit.
- **Graph RAG:** stores facts as entities and relationships, so following links is a cheap database query. Best when the data is about relationships.

Q: What is hybrid search? <span class="qnote">extra reading, not in the lecture</span> {{p:96–97}}
Run keyword search (BM25, good at exact names and codes) and vector search (good at meaning), then merge the two ranked lists with Reciprocal Rank Fusion: score = Σ 1/(60 + rank).

Q: What is reranking? <span class="qnote">extra reading, not in the lecture</span> {{p:97}}
Retrieve wide (say the top 50) with fast vector search, then score each (question, chunk) pair with a more accurate cross-encoder and keep the best 5. The rule: retrieve wide, rerank narrow.
:::

## E. Graph databases

:::qa -
Q: When would you use a graph database instead of SQL? {{p:112}}
When the questions are about **relationships**: friends of friends, fraud chains, recommendations, "how is A connected to K?". SQL is better for aggregates over rows (totals, reports) and simple tables.

Q: Why is SQL slow for "friends of friends of friends"? {{p:108–109}}
Each hop is a self-join, and every lookup goes through an index over the **whole** friendships table, costing about log N. With 500 connections each: log N + 500·log N + 2.5 lakh·log N lookups. It grows fast, even though you only care about your own neighbourhood.

Q: What is index-free adjacency? {{p:109}}
Each node stores direct references to its relationships, so following a link is a pointer jump: about O(1) per hop. The cost depends on how much of the graph you touch, not on the size of the whole database. It's the adjacency list from DSA, made permanent.

Q: How does Neo4j store this? {{p:110}}
- **Fixed-size records:** 15 bytes per node, 34 bytes per relationship. Record i lives at base + i × size, an O(1) jump like an array.
- **Linked relationships:** a node points to its first relationship, and each relationship points to the next one for both of its nodes, forming linked lists.
- **The starting node** still needs an index (hash or B+ tree).

Q: Explain the graph data model and Cypher basics. {{p:110–111}}
- **Nodes** are things, and their **labels** are like classes.
- **Relationships** are typed, directed facts, like DIRECTED or ACTED_IN.
- **Properties** hold the data.
- **Cypher** follows MATCH (a pattern) → WHERE (filter) → RETURN. **MERGE** avoids duplicates, and values always go in as `$parameters` to prevent injection.
:::

## F. Linking it to your project

:::qa -
Q: Why does PaperRAG use exact search and not HNSW? {{p:164}}
A few hundred papers is only tens of thousands of vectors, which exact search handles in milliseconds with perfect recall and no tuning. HNSW would add approximation and settings to solve a speed problem I don't have. At millions of chunks I'd switch, and measure its recall against exact search.

Q: What would change if PaperRAG had 1 million papers? {{p:167}}
About 30–50 million chunks. I'd move to HNSW or IVF-PQ in a vector database, measure recall against exact search on a sample, embed offline in batches, keep metadata in a database, add metadata filters, and re-tune the refusal threshold.
:::

:::tip How to practise Part 1
Answer in batches of 10 a day, out loud and without looking, and mark the ones where you get stuck. The ones asked most often are **Q5, Q6, Q9, Q11, Q15, Q16, Q17, Q21 and Q27**.
:::
