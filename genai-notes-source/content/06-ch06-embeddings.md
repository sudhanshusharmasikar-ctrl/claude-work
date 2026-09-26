:::chapter 6 | Embeddings: Meaning as Numbers | Lectures 8–9 · whiteboards + Lecture19 config · Must-know
- The recommendation problem, solved four ways (first principles)
- Why **one number** per item fails, and **vectors** work
- What an **embedding** is and which models make them
- **Euclidean distance** vs **cosine similarity**, with C++ you can run
- **Normalisation** and why it makes cosine = dot product
- Making embeddings in JavaScript (`gemini-embedding-001`)
- Where embeddings are used — and where they fail
:::

RAG, vector databases, semantic search, recommendations, your PaperRAG and SchemaMind retrieval — all stand on one idea: **turn meaning into a list of numbers, then compare the lists.** Rohit spends a whole lecture reaching that idea from first principles. Let's walk the same road.

## 6.1 The problem: "what should we recommend?" %%MUST%%

You run an online store with **1 million products**. A customer buys **protein powder**. What do you show next?

**Solution 1 — categories by hand.** Put items in groups (fitness, fruits, vegetables, clothes, electronics) and recommend from the same group.

- ❌ **Not scalable** — someone must label a million products.
- ❌ **Rigid boundaries** — a **banana** is a fruit, but gym people eat it with protein. A **blender** is an appliance, but it's how you make shakes.
- ❌ **Can't discover new relationships** — the famous "beer and diapers" story: data found that people buying diapers often bought beer. No human category would put them together.

**Solution 2 — "bought together" counts.** Keep a matrix: how often product *i* and product *j* were bought together; recommend the highest counts.

- ❌ The matrix is **N × N** — for a million products, a trillion cells.
- ❌ For every request you must scan and sort a huge row.
- ❌ **Cold start** — a brand-new product has no purchases, so it's never recommended.
- ❌ Only **co-occurrence**, not **content** — "On Whey" and "MyProtein Whey" are basically the same thing but are rarely bought together, so the matrix never links them.

**Solution 3 — give every item one number** (apple = 1, banana = 2, …, protein = 101, BCAA = 102, creatine = 103, …, blender = 151) and recommend items with nearby numbers.

- ❌ **Single-meaning problem** — a number sits on one line; banana can't be near both "fruits" and "gym food".
- ❌ **Boundary problem** — 150 (fish oil) and 151 (blender) are neighbours but unrelated.
- ❌ **Insertion problem** — where does a new product go between 102 and 103?

**Solution 4 — give every item *several* numbers.** Each number describes one aspect. Now an item can be close to others in **one** aspect and far in another. That list of numbers is a **vector**.

## 6.2 From two numbers to many: the movie map %%MUST%%

Rohit's Bollywood example: describe each movie with **two** numbers — **action** (−10 peaceful … +10 full action) and **comedy** (−10 serious … +10 comedy).

[[fig:movie-map|Movies as 2-D vectors. Similar movies land close together — but two numbers are too few: Lagaan and Taare Zameen Par look almost identical here.]]

It works — comedies cluster, action films cluster. But look at the **serious-drama blob**: Lagaan (historical sports epic), Swades (social drama), Dangal (sports biopic) and Taare Zameen Par (childhood, dyslexia) are squashed together, just because all are "not action, not comedy". Someone who loved Lagaan's historical scale may not want Taare Zameen Par.

Fix: **add dimensions** — emotional intensity, romance, realism… With **5 numbers**, those four movies separate. Real embedding models use **hundreds or thousands** of dimensions (384, 768, 1536, 3072).

:::def Embedding
An **embedding** is a vector (a list of numbers) produced by a trained neural network so that **things with similar meaning get vectors that are close together**. "How much does a car cost?" and "What is the price of an automobile?" share almost no words, yet their embeddings are very close.
:::

Two important differences from the movie map:

1. Nobody hand-labels the dimensions. The **embedding model learns them** from huge amounts of text, so a single dimension usually has **no human meaning** — meaning lives in the **direction** of the whole vector.
2. Relationships show up as **directions**: the classic result `vector("king") − vector("man") + vector("woman") ≈ vector("queen")`.

## 6.3 Embedding models you should know %%MUST%%

| Model | Dimensions | Where you meet it |
|---|---|---|
| `text-embedding-004` (Google) | 768 | Lectures 12–13 — **shut down on 14 Jan 2026** |
| `gemini-embedding-001` (Google) | 3072 by default; can output 768 or 1536 | Lecture 19 onwards |
| `all-MiniLM-L6-v2` (open source, sentence-transformers) | 384 | **PaperRAG, SchemaMind, StanceScope** — small, runs on a CPU |
| OpenAI `text-embedding-3-small` / `-large` | 1536 / 3072 | Common in industry tutorials |

Rules that interviewers check:

- Use the **same model** for documents and queries — vectors from different models live in different "maps" and can't be compared.
- **Dimensions must match** the vector index (a 3072-d vector can't go into a 768-d Pinecone index).
- Changing the model means **re-embedding everything**.
- Models have an **input limit**. MiniLM reads about 256 word-pieces; longer text is silently cut — PaperRAG's config explains that chunk sizes above ~1200 characters would be wasted.

## 6.4 How close are two vectors? Euclidean vs cosine %%MUST%%

**Euclidean distance** — the straight-line "ruler" distance between two points. It cares about **magnitude**.

`d(A, B) = √[(a₁ − b₁)² + (a₂ − b₂)² + … + (aₙ − bₙ)²]`

Example: A = [4, 5], B = [6, 7] → √((6−4)² + (7−5)²) = √8 ≈ **2.83**.

**Cosine similarity** — the **angle** between two vectors. It cares about **direction**, not length.

`cos(A, B) = (A · B) / (‖A‖ × ‖B‖)`, where `A · B = a₁b₁ + a₂b₂ + …` and `‖A‖ = √(a₁² + a₂² + …)`.

Result is between **−1 and 1**: **1** = same direction (most similar), **0** = perpendicular (unrelated), **−1** = opposite.

[[fig:cos-vs-euc|A short text and a long article about the same topic point the same way (cosine = 1) but are far apart by ruler distance. Cosine asks "same topic?", Euclidean asks "same point?".]]

Rohit's example: *"I love cat, cat is cat, cat is good"* — a longer text about cats can produce a longer vector, but it's still **about cats**, so the direction is the same. Let's prove it in C++:

```cpp title="similarity.cpp — cosine vs Euclidean (my test program; #includes omitted)" lines
double dot(const vector<double>& a, const vector<double>& b) {
    double s = 0;
    for (size_t i = 0; i < a.size(); i++) s += a[i] * b[i];
    return s;
}
double norm(const vector<double>& a) { return sqrt(dot(a, a)); }

double cosine(const vector<double>& a, const vector<double>& b) {
    return dot(a, b) / (norm(a) * norm(b));
}
double euclidean(const vector<double>& a, const vector<double>& b) {
    double s = 0;
    for (size_t i = 0; i < a.size(); i++) s += (a[i] - b[i]) * (a[i] - b[i]);
    return sqrt(s);
}

int main() {
    vector<double> shortCat = {10, 20, 30, 40};      // "I love cat"
    vector<double> longCat  = {100, 200, 300, 400};  // a long article about cats
    vector<double> dogs     = {12, 18, 33, 35};      // a short text about dogs

    cout << "cosine(shortCat, longCat) = " << cosine(shortCat, longCat) << "\n";
    cout << "cosine(shortCat, dogs)    = " << cosine(shortCat, dogs) << "\n";
    cout << "euclid(shortCat, longCat) = " << euclidean(shortCat, longCat) << "\n";
    cout << "euclid(shortCat, dogs)    = " << euclidean(shortCat, dogs) << "\n";
}
```

```output title="g++ similarity.cpp -o similarity && ./similarity"
cosine(shortCat, longCat) = 1          #> same direction → most similar
cosine(shortCat, dogs)    = 0.993442
euclid(shortCat, longCat) = 492.95     #> far away by ruler distance
euclid(shortCat, dogs)    = 6.48074    #> Euclidean says "dogs" is closer!
```

Cosine says the long cat article is the best match; Euclidean says the dog text is. For **meaning**, cosine is right.

| Use **cosine** (direction matters) | Use **Euclidean** (actual values matter) |
|---|---|
| Text, image, audio **embeddings** | GPS coordinates (latitude, longitude) |
| Semantic search, RAG, recommendations | Physical measurements (height, weight, temperature) |
| Document clustering, deduplication | Pixel colour values, sensor readings, prices |

## 6.5 Normalisation: the trick every vector DB uses %%MUST%%

**Normalise** = divide a vector by its length so its length becomes 1 (a **unit vector**):

`[3, 4]` → length √(9 + 16) = 5 → `[3/5, 4/5] = [0.6, 0.8]` → length √(0.36 + 0.64) = 1 ✓

After normalising both vectors:

- **cosine similarity = dot product** (the division by lengths becomes division by 1×1),
- and ranking by Euclidean distance gives the **same order** as ranking by cosine, because for unit vectors ‖A − B‖² = 2 − 2·cos(A, B).

That's why your **PaperRAG** uses FAISS `IndexFlatIP` (inner product = dot product) **with normalised MiniLM vectors**: inner product on unit vectors *is* cosine similarity. Many vector databases do the same internally.

:::cpp Why dot product is fast
A dot product is one loop of multiply-adds — exactly what CPUs (SIMD) and GPUs are built for. Normalise once when you store a vector, and every future comparison is a single `dot()`. Libraries like FAISS are basically very optimised versions of your `dot()` function.
:::

:::note Normalising Gemini embeddings
Google's docs say `gemini-embedding-001`'s full 3072-dimension output is already normalised; if you ask for a smaller size (768 or 1536) you should normalise it yourself before comparing.
:::

## 6.6 Making embeddings in JavaScript %%MUST%%

The Graph RAG code (Lecture 19) embeds with the official SDK:

```js title="Lecture19/2_config.js — embedding helpers" lines
// text-embedding-004 → SHUT DOWN Jan 14, 2026.
// gemini-embedding-001 → 3072 dimensions by default.
async function embedText(text) {
  const response = await genai.models.embedContent({
    model: "gemini-embedding-001",
    contents: text,
  });
  // response.embeddings is an ARRAY (even for single text)
  return response.embeddings[0].values;          // number[3072]
}

async function embedTexts(texts) {               // many texts in one request
  const response = await genai.models.embedContent({
    model: "gemini-embedding-001",
    contents: texts,
  });
  return response.embeddings.map((e) => e.values);
}
```

- **Lines 4–7** — `embedContent` sends text to the embedding model (not the chat model).
- **Line 9** — the result is an **array of embeddings**; for one text we take `[0].values`.
- **Lines 12–18** — **batching**: many texts in one request is faster and hits rate limits less often.

Optional settings: `config: { outputDimensionality: 768 }` for smaller vectors, and `taskType: "RETRIEVAL_DOCUMENT"` when embedding stored chunks vs `"RETRIEVAL_QUERY"` when embedding the user's question (the model optimises each side for search).

## 6.7 Where embeddings are used — and where they fail %%GOOD%%

Used for: **semantic search**, **RAG retrieval** (Chapter 8), **recommendations**, **clustering** similar tickets, **deduplication**, **classification** (nearest labelled example), **anomaly detection**, and picking relevant tables (**SchemaMind**) or evidence (**StanceScope**).

Where they fail — say these in interviews:

- **Similar topic ≠ correct answer.** "Is aspirin safe for kids?" is close to a passage saying "aspirin is **not** safe for kids" *and* to one about adult dosage. Embeddings capture topic better than **negation** or exact facts. That's why PaperRAG has a **second** guard, and why systems use **rerankers** (Chapter 9).
- **Exact terms**: product codes, error numbers, rare names (`ERR_4102`) — keyword search (BM25) often beats embeddings → **hybrid search** (Chapter 9).
- **Domain words**: a general model may not know your company's jargon.
- **Long text**: one vector for a whole book blurs everything; that's why we **chunk** (Chapter 8).

:::remember
- Hand categories, co-occurrence matrices and single numbers all fail; **vectors** (many numbers) capture many aspects at once.
- **Embedding** = vector from a trained model; similar meaning → nearby vectors. Dimensions are learned, not human-readable.
- Same model for docs and queries; index dimension must match; new model = re-embed everything.
- **Cosine** (angle, −1…1) for meaning; **Euclidean** (ruler) when magnitudes matter.
- **Normalise** → cosine = dot product, and Euclidean ranks the same. PaperRAG: `IndexFlatIP` + normalised vectors = exact cosine.
- `gemini-embedding-001` (3072), MiniLM (384) in your projects; `text-embedding-004` is dead.
- Embeddings match **topic**, not truth — rerankers, hybrid search and abstention guards cover the gaps.
:::

:::quiz
1. Give two reasons why "one number per product" fails.
2. A = [1, 0], B = [0, 5]. What is their cosine similarity? What does that mean?
3. Why does PaperRAG normalise vectors before using `IndexFlatIP`?
4. You switch from `text-embedding-004` (768-d) to `gemini-embedding-001` (3072-d). What must you do with your Pinecone index?
5. Why might a search for "error ERR_4102" work badly with embeddings alone?
:::

:::answer
1. Any two of: an item can't be close to two different groups (single meaning), unrelated neighbours at group boundaries, no room to insert new items.
2. Dot product = 0 → cosine = 0: perpendicular, unrelated.
3. For unit vectors, inner product equals cosine similarity, so the index does exact cosine search.
4. Create a new 3072-d index (or configure 768-d output and normalise) and **re-embed all documents** with the new model — old and new vectors can't be mixed.
5. Embeddings capture general meaning; a rare exact code may be tokenised oddly and has little "meaning". Keyword search (BM25) matches it exactly — use hybrid search.
:::

:::qa Interview questions — embeddings
Q: What is an embedding?
A dense vector produced by a trained model such that semantically similar inputs map to nearby vectors. It lets us compare meaning with simple maths (cosine similarity) instead of matching exact words.

Q: Cosine similarity vs Euclidean distance — which do you use for text embeddings and why?
Cosine, because meaning is encoded in the direction of the vector; length can vary with things like text length. Euclidean is for data where magnitudes matter, like coordinates or measurements. If vectors are normalised, both give the same ranking and cosine becomes a plain dot product.

Q: What does normalising a vector do, and why do vector databases like it?
Scales it to length 1. Then cosine similarity is just the dot product, which is very fast and lets indexes use inner-product search. In PaperRAG I normalise MiniLM embeddings and use FAISS IndexFlatIP to get exact cosine similarity.

Q: How do you choose an embedding model?
Quality on my domain (test retrieval on a small labelled set), dimensions (storage and speed), cost and latency, input length limit, language support, and whether it must run locally. For PaperRAG I chose all-MiniLM-L6-v2 (384-d) because it runs on CPU and deploys on a free tier; a larger model would likely improve recall.

Q: Can you mix embeddings from two different models in one index?
No. Each model defines its own vector space; distances between spaces are meaningless (and dimensions often differ). Switching models requires re-embedding the whole corpus.

Q: What are the limitations of embedding-based retrieval?
It finds topically similar text, not necessarily text that answers the question; it's weak on exact identifiers, negation and numbers; it depends on the model knowing the domain; and one vector can't represent a long document well. Fixes: chunking, hybrid search with BM25, rerankers, metadata filters and abstention checks.
:::
