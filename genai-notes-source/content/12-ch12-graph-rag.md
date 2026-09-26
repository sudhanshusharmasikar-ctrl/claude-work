:::chapter 12 | Graph RAG: The Movie Project | Lectures 17–19 · Lecture19 code (13 files) · Must-know
- The problem: **relational** movie questions without hallucination
- From documents to a **knowledge graph** (6 node types, 5 relationships)
- Why **two databases**: Neo4j for facts, Pinecone for similarity
- Rohit's **query templates**: traversal, property, filter, set logic, projection
- The **indexing pipeline**: Gemini extracts JSON → `MERGE` into Neo4j → embed into Pinecone
- The **query pipeline**: extract → **resolve entities** → classify → graph or similarity handler
- **Safe Cypher**: the LLM writes a JSON plan, code validates and builds the query
- A security review of the validator (with a tested fix)
- Limits, improvements and interview questions
:::

This is the course's most "senior-engineer" project. It combines everything so far: LLM calls, JSON output, retries, embeddings, a vector DB, a graph DB, routing, and security thinking. Even if Graph RAG is not on your resume, interviewers love hearing **how** you'd build it.

## 12.1 The problem (Lecture 17) %%MUST%%

We have documents about ~1000 movies and want to answer questions like:

- Movies directed by Christopher Nolan.
- Actors who worked in Nolan movies that won an Oscar.
- Actors who won an Oscar in a **different** movie and genre.
- Movies **similar** to Inception.

Constraints from Rohit's notes: the data is **static facts**, the questions are **relational**, we must **avoid hallucination**, and it must **scale**. His key sentence:

> The problem is NOT "generate an answer". The problem IS **retrieve the correct facts and present them clearly**.

Normal chunk-RAG struggles here: "actors in Nolan's Oscar-winning movies" needs facts from **many** documents joined together (Chapter 9's multi-hop problem).

## 12.2 From documents to a graph %%MUST%%

Each movie document looks like this:

```text title="one movie document (Lecture 17 notes)"
Movie Title: Inception
Release Year: 2010
Director: Christopher Nolan
Actors: - Leonardo DiCaprio - Joseph Gordon-Levitt - Ellen Page
Genre: - Sci-Fi - Psychological Thriller
Themes: - Time - Dreams - Reality
Awards: - Oscar (Best Cinematography) - Oscar (Best Sound Mixing)
```

Documents are repetitive and **hard to connect**. Humans think in links: *Nolan → movies → actors → awards → other movies → genre*. So we model the data as a graph:

[[fig:movie-schema|The movie knowledge graph: 6 node labels (classes) and 5 relationship types (facts).]]

- **Node labels (classes)**: `Movie`, `Director`, `Actor`, `Genre`, `Theme`, `Award`.
- **Relationships (facts)**: `(Director)-[:DIRECTED]->(Movie)`, `(Actor)-[:ACTED_IN]->(Movie)`, `(Movie)-[:BELONGS_TO]->(Genre)`, `(Movie)-[:EXPLORES]->(Theme)`, `(Movie)-[:WON]->(Award)`.
- **Properties (data)**: `Movie {title, year}`, `Award {name, category}`, others `{name}`.

## 12.3 Two databases, two jobs %%MUST%%

| | **Neo4j (graph DB)** | **Pinecone (vector DB)** |
|---|---|---|
| Stores | **Facts** as nodes + relationships | The **meaning** of each whole movie document (one vector per movie) |
| Answers | "Who directed…", "which actors…", counts, paths | "Movies **like** Inception", "mind-bending sci-fi" |
| Does NOT know | Vague taste/similarity | Directors, actors, awards as facts |

Rohit's rule: the vector DB "only **reduces the search space**" — it finds candidates; the graph checks facts. So the first question for every query is: **factual or similarity?**

- **Factual** ("movies directed by Nolan", "actors who won an Oscar") → **graph only**.
- **Similarity** ("movies like Inception") → **vector DB → shortlist → graph filter**.

## 12.4 Query templates: thinking steps, not question-specific queries %%GOOD%%

Rohit's Lecture 17 notes make a sharp point: don't write one query per question. Write **templates per thinking step**, and **compose** them:

| Template | First-thought meaning | Cypher shape |
|---|---|---|
| **1. Traversal (pattern)** | "Some things are connected to other things." | `(a:Label)-[:REL]->(b:Label)` |
| **2. Property access** | "Tell me something **about** this thing." | `RETURN n.property` |
| **3. Filter** | "From what I have, remove what I don't want." | `WHERE cond AND/OR/NOT cond` |
| **4. Set combination** | All conditions (AND), either (OR / `UNION`), exclusion (NOT / `<>`) | inside `WHERE`, or `UNION` |
| **5. Projection** | "What exactly should I show?" | `RETURN DISTINCT …`, `count(…)` |

> Every graph query is: **Pattern → Filter → Filter → … → Return.** No exception.

Example — *"Actors who worked in Nolan movies that won an Oscar"*: Director→Movie (traversal), Movie→Award (traversal), Actor→Movie (traversal), keep Nolan AND Oscar (filters), return distinct actor names (projection). This composability is exactly what makes the **JSON plan** in Section 12.6 possible.

## 12.5 The indexing pipeline (Lecture 19) %%MUST%%

```bash title="run it"
npm run test     # 1_testConnection.js: Neo4j, Pinecone, Gemini, embeddings OK?
npm run index    # 7_runIndexing.js: extract → graph → vectors
npm run query    # 13_runQuery.js: interactive questions
```

[[fig:graphrag-indexing|Indexing: one PDF feeds two stores. An LLM turns text into structured JSON for the graph; each movie's text becomes one vector.]]

### Step 1 — Gemini extracts entities as JSON (`4_entityExtractor.js`)

Instead of parsing text with regexes, the whole PDF is **uploaded once** to the Gemini Files API, and Gemini is asked for movies in **batches of 50** (1000 movies → 20 requests), **5 batches in parallel**:

```js title="4_entityExtractor.js — one batch, with retries (excerpt)"
const EXTRACTION_PROMPT = `You are a precise entity extractor for a movie
knowledge graph. From the attached PDF, extract movies {START} through {END}
(by their order in the document). For EACH movie, output this EXACT JSON:
{ "movie": {"title": "string", "year": number}, "director": {"name": "string"},
  "actors": ["string"], "genres": ["string"], "themes": ["string"],
  "awards": ["string"] }
Rules: If awards say "None", return []. Keep exact names. Year is a number.
Return ONLY valid JSON. No markdown, no backticks, no explanation.`;

async function extractBatch(fileInfo, start, end, attempt = 1) {
  const maxRetries = 3;
  const prompt = EXTRACTION_PROMPT.replace("{START}", start).replace("{END}", end);
  try {
    const response = await genai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: [{ role: "user", parts: [
        createPartFromUri(fileInfo.uri, fileInfo.mimeType),   // the uploaded PDF
        { text: prompt },
      ]}],
    });
    let raw = response.text.trim();
    raw = raw.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim(); // fences
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch (err) {
    if (attempt < maxRetries) {
      const is429 = err.message?.includes("429");
      const wait = is429 ? attempt * 30 : attempt * 10;  // 429 → wait longer
      await new Promise((r) => setTimeout(r, wait * 1000));
      return extractBatch(fileInfo, start, end, attempt + 1);
    }
    return [];                                     // counted as a failed batch
  }
}
```

- The **prompt is a schema**: exact JSON shape, rules for edge cases ("None" → `[]`), and "ONLY valid JSON".
- `createPartFromUri` attaches the uploaded PDF, so Gemini reads it with its long context — no local text parsing needed for extraction.
- Code still **defends** against the model: strip ```` ```json ```` fences, `JSON.parse` inside `try`.
- **Retries on any error**, with longer waits for `429` rate limits (30 s, 60 s) than for other errors (10 s, 20 s). After pass 1, a **second pass** retries every failed batch one by one, and the final log reports exactly which movies were lost.

### Step 2 — build the graph with `MERGE` (`5_graphBuilder.js`)

```js title="5_graphBuilder.js — insert one movie (excerpt)"
async function insertMovieGraph(entity) {
  const session = driver.session();
  try {
    await session.executeWrite(async (tx) => {   // one transaction: all or nothing
      await tx.run(`MERGE (m:Movie {title: $title}) SET m.year = $year`,
                   { title: entity.movie.title, year: entity.movie.year });
      await tx.run(`MERGE (d:Director {name: $name})
                    MERGE (m:Movie {title: $title})
                    MERGE (d)-[:DIRECTED]->(m)`,
                   { name: entity.director.name, title: entity.movie.title });
      for (const actorName of entity.actors) {
        await tx.run(`MERGE (a:Actor {name: $name})
                      MERGE (m:Movie {title: $title})
                      MERGE (a)-[:ACTED_IN]->(m)`,
                     { name: actorName, title: entity.movie.title });
      }
      // ... same for genres (BELONGS_TO) and themes (EXPLORES) ...
      for (const awardName of entity.awards) {
        // "Oscar (Best Sound Mixing)" → type "Oscar", category "Best Sound Mixing"
        const match = awardName.match(/^(.+?)\s*\((.+)\)$/);
        if (match) {
          await tx.run(`MERGE (aw:Award {name: $awardType, category: $category})
                        MERGE (m:Movie {title: $title})
                        MERGE (m)-[:WON]->(aw)`,
                       { awardType: match[1].trim(), category: match[2].trim(),
                         title: entity.movie.title });
        }
      }
    });
  } finally {
    await session.close();
  }
}
// before inserting (one per label):
//   CREATE INDEX IF NOT EXISTS FOR (m:Movie) ON (m.title)
```

- **`MERGE` everywhere** → "Leonardo DiCaprio" in 10 movies is **one** node with 10 `ACTED_IN` relationships.
- **`executeWrite`** wraps one movie in a **transaction**: if anything fails, nothing half-written remains.
- **Parameters** (`$title`, `$name`) — values are never pasted into the query text.
- The regex splits `"Oscar (Best Sound Mixing)"` into `name = "Oscar"`, `category = "Best Sound Mixing"`, so "which movies won an Oscar?" is a simple filter.
- **Indexes first**: without an index on `Movie.title`, every `MERGE` would scan all movies.

### Step 3 — vectors for similarity (`6_vectorStore.js`)

The PDF text is split on the `----------` separators into **one chunk per movie**, each chunk embedded with `gemini-embedding-001` (5 at a time, with retries), and upserted to Pinecone in batches of 100 as `{ id: "chunk-17", values: [...3072 numbers], metadata: { text } }`. The code calls the Pinecone SDK directly because the LangChain Pinecone package conflicted with the newer LangChain core version — a real-world lesson in dependency pain.

## 12.6 The query pipeline %%MUST%%

[[fig:graphrag-query|Every question goes through entity resolution first; a classifier then routes it to the graph handler or the similarity handler.]]

### Step 1 — extract and **resolve** entities (`9_entityResolver.js`)

The LLM first lists the names in the question ("Action movies with Tom Hardy" → `["Action", "Tom Hardy"]`). But what **is** "Nolan"? A director? An actor? Only the graph knows. So each name is searched in **all six labels**:

```js title="9_entityResolver.js — resolveEntity (excerpt)"
for (const { label, property } of NODE_TYPES) {    // Movie.title, Director.name…
  const exact = await session.run(
    `MATCH (n:${label}) WHERE toLower(n.${property}) = toLower($name)
     RETURN n.${property} AS nodeName, labels(n)[0] AS label LIMIT 5`,
    { name: entityName });
  if (exact.records.length > 0) { /* keep as "exact" */ continue; }

  const partial = await session.run(                // "Nolan" → "Christopher Nolan"
    `MATCH (n:${label}) WHERE toLower(n.${property}) CONTAINS toLower($name)
     RETURN n.${property} AS nodeName, labels(n)[0] AS label LIMIT 5`,
    { name: entityName });
  // keep as "partial"
}
// prefer exact matches over partial ones
```

- **Exact match first** (case-insensitive), then **`CONTAINS`** for partial names ("Nolan" → "Christopher Nolan").
- `${label}` and `${property}` come from the code's own fixed `NODE_TYPES` list — safe. The user's text is only ever `$name`, a parameter.
- The session is opened with `defaultAccessMode: "READ"` — the query path never needs to write.

Why this step matters: every later LLM call is told *"Nolan = Director, exact name 'Christopher Nolan'"*, so it doesn't guess.

### Step 2 — classify: graph or similarity? (`10_queryClassifier.js`)

An LLM call with the resolved entities returns `{"type": "graph" | "similarity", "reasoning": "…"}`. Only two classes: factual, descriptive and relationship questions are all "traverse the graph"; only "like / similar / recommend" needs vectors. If the JSON can't be parsed, it **defaults to graph** (a safe fallback).

### Step 3a — the graph handler: LLM plans, code builds Cypher (`11_graphHandler.js`, `8_cypherTemplates.js`)

The most important design decision in the project:

> **The LLM never writes raw Cypher.** It writes a small **JSON plan** made of Rohit's templates. Code **validates every step against whitelists** and **builds** a read-only query with parameters.

The planner prompt gives the schema, the allowed step types (`traversal`, `filter`, `projection`, `aggregation`, `sort`, `limit`, plus `describe` for "tell me about X" and `path` for "how are X and Y related"), and worked examples. Then:

```js title="8_cypherTemplates.js — whitelists and validation (excerpt, re-wrapped)"
const ALLOWED_LABELS = new Set(
  ["Movie", "Director", "Actor", "Genre", "Theme", "Award"]);
const ALLOWED_RELATIONSHIPS = new Set(
  ["DIRECTED", "ACTED_IN", "BELONGS_TO", "EXPLORES", "WON"]);
const ALLOWED_PROPERTIES = {
  Movie: ["title", "year"], Director: ["name"], Actor: ["name"],
  Genre: ["name"], Theme: ["name"], Award: ["name", "category"] };
const ALLOWED_OPERATORS = new Set(
  ["=", "<>", ">", "<", ">=", "<=", "CONTAINS", "STARTS WITH"]);
const LABEL_VAR_MAP = {
  Movie: "m", Director: "d", Actor: "a", Genre: "g", Theme: "t", Award: "aw" };

function validateStep(step) {
  switch (step.type) {
    case "traversal":
      if (!ALLOWED_LABELS.has(step.from)) throw new Error(`Invalid: ${step.from}`);
      if (!ALLOWED_LABELS.has(step.to)) throw new Error(`Invalid: ${step.to}`);
      if (!ALLOWED_RELATIONSHIPS.has(step.rel))
        throw new Error(`Invalid relationship: ${step.rel}`);
      break;
    case "filter": {
      const [label, prop] = step.field.split(".");
      if (!ALLOWED_PROPERTIES[label]?.includes(prop))
        throw new Error(`Invalid property: ${step.field}`);
      if (!ALLOWED_OPERATORS.has(step.op))
        throw new Error(`Invalid operator: ${step.op}`);
      break;
    }
    // projection, aggregation, sort, limit ... (limit must be a number 1–100)
    default:
      throw new Error(`Unknown step type: ${step.type}`);
  }
}
// buildCypher(plan): validate ALL steps, then turn traversals into MATCH lines,
// filters into "var.prop op $pN" (the value goes into params), projection into
// RETURN, and so on.
```

I ran `buildCypher` from the course file on the planner's own example plans and on a malicious one:

```output title="node test_cypher.mjs  (course's 8_cypherTemplates.js)"
--- Movies directed by Christopher Nolan
MATCH (d:Director)-[:DIRECTED]->(m:Movie)
WHERE d.name = $p0
RETURN DISTINCT m.title, m.year
params: {"p0":"Christopher Nolan"}
--- Action movies with Tom Hardy
MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
MATCH (m:Movie)-[:BELONGS_TO]->(g:Genre)
WHERE a.name = $p0 AND g.name = $p1
RETURN DISTINCT m.title, m.year
params: {"p0":"Tom Hardy","p1":"Action"}
--- Blocked: unknown relationship
REJECTED: Invalid relationship: DELETE_ALL
--- Blocked: value injection is harmless (it is a parameter)
MATCH (d:Director)-[:DIRECTED]->(m:Movie)
WHERE d.name = $p0                    #> the text stays DATA, never code
RETURN m.title
params: {"p0":"x' OR 1=1 //"}
```

Why this is strong:

1. **No DELETE/SET/CREATE can ever be produced** — the builder only knows how to emit `MATCH … WHERE … RETURN`.
2. Labels, relationships, properties and operators come from **whitelists**; values are **parameters**.
3. The Neo4j session is **READ** mode — a second layer.

`describe` ("Tell me about Inception") runs a fixed `OPTIONAL MATCH` query per label that collects directors, actors, genres, themes and awards; `path` runs `shortestPath((a)-[*..6]-(b))`. Finally, an LLM turns the result rows into plain English (with "don't mention databases or JSON").

### Step 3b — the similarity handler (`12_similarityHandler.js`)

For *"Movies like Inception"*:

1. The resolver already knows Inception is a `Movie`.
2. **Pinecone**: embed the name, fetch the **top 50** similar movie chunks.
3. **Neo4j**: get Inception's genres and themes.
4. **Neo4j filter**: keep only candidates that share at least one genre:

```cypher title="keep candidates that share a genre"
MATCH (m:Movie)-[:BELONGS_TO]->(g:Genre)
WHERE m.title IN $titles
WITH m, collect(g.name) AS genres
WHERE any(genre IN genres WHERE genre IN $sourceGenres)
RETURN m.title AS title, genres
```

5. **LLM rerank**: give Gemini the genre-matched list (with each movie's text) and ask for the **10 best** with a one-line reason each.

If no movie entity was resolved ("mind-bending sci-fi"), it falls back to **pure vector search** (top 20) + LLM ranking. This is the "vector DB reduces the search space, the graph checks facts" rule in action — and the LLM step is a **reranker** (Chapter 9).

## 12.7 Security review: two gaps in the validator (and a tested fix) %%GOOD%%

The design is right, but two step types let model-written text reach the query **string**:

- `sort` checks the label and the direction, but **not the property name**.
- `aggregation` doesn't check the **alias** (the name after `AS`) or `groupBy`.

```output title="same test, crafted plans against the course validator"
--- GAP 1: sort property is not whitelisted
MATCH (d:Director)-[:DIRECTED]->(m:Movie)
RETURN m.title
ORDER BY m.title DESC LIMIT 1 // ASC    #> model text changed the query
params: {}
--- GAP 2: aggregation alias is not checked
MATCH (m:Movie)-[:BELONGS_TO]->(g:Genre)
RETURN count(m) AS n, 1 AS anything_else
params: {}
```

Here the damage is limited (read-only session, no write clauses), but the principle matters: **every piece of model text that becomes query syntax must be whitelisted**. The fix is a few lines:

```js title="the fix — tested: gaps rejected, normal plans unchanged"
const SAFE_IDENT = /^[A-Za-z_][A-Za-z0-9_]*$/;    // letters, digits, _ only

// in case "aggregation":
if (step.alias !== undefined && !SAFE_IDENT.test(step.alias))
  throw new Error(`Invalid alias: ${step.alias}`);
if (step.groupBy) {
  const [gl, gp] = step.groupBy.split(".");
  if (!ALLOWED_PROPERTIES[gl]?.includes(gp))
    throw new Error(`Invalid groupBy: ${step.groupBy}`);
}

// in case "sort":
if (!ALLOWED_PROPERTIES[sLabel].includes(sProp) && !SAFE_IDENT.test(sProp))
  throw new Error(`Invalid sort field: ${step.field}`);
```

```output title="node test_fixed.mjs"
--- GAP 1: sort property is not whitelisted
REJECTED: Invalid sort field: Movie.title DESC LIMIT 1 //
--- GAP 2: aggregation alias is not checked
REJECTED: Invalid alias: n, 1 AS anything_else
```

Same idea for `path`: `executePath` puts `fromLabel`/`toLabel` into the query text, so check them with `ALLOWED_LABELS.has(...)` first. (`describe` is already safe: it only accepts labels through a fixed `switch`.)

:::interview How to use this in an interview
"In the Graph RAG project from my course, the model never writes Cypher: it writes a JSON plan, and code validates each step against whitelists and binds values as parameters. When I studied the validator, I noticed the sort field and aggregation alias weren't whitelisted, so model text could reach the query string — I added identifier checks and tested that normal plans still compile." That's the same philosophy as SchemaMind's AST validator — a great bridge to your own project. (Make the story true: apply and test this fix yourself on Day 19 — the test plans are in this section.)
:::

## 12.8 Limitations and improvements %%GOOD%%

| Limitation | Improvement |
|---|---|
| One variable per label (`m` for every Movie) → can't express "an actor in **two different** movies" | Let traversal steps name their own variables (`m1`, `m2`), still validated |
| Entity resolution uses exact / `CONTAINS` → typos ("Nolen") fail; "Jordan" may match several people | Fuzzy or full-text index, embeddings over entity names, ask the user to disambiguate |
| `MERGE` relies on indexes but no **uniqueness constraints** | `CREATE CONSTRAINT … REQUIRE m.title IS UNIQUE` (also guards concurrent writes); titles aren't unique in real life → use ids |
| Similarity query embeds just the **title** ("Inception") | Embed or look up the **movie's own document vector** ("more like this") |
| 3–4 LLM calls per question (extract, classify, plan, answer) | Cache resolutions, merge extract+classify, use a small model for routing |
| Two databases to operate | Neo4j also supports **vector indexes** — one store for both jobs |
| No evaluation | A question set with expected answers for factual and similarity queries |

:::remember
- Graph RAG = **facts in a graph** (Neo4j) + **meaning in vectors** (Pinecone); vectors shortlist, the graph verifies.
- Model: 6 labels (Movie, Director, Actor, Genre, Theme, Award), 5 relationships (DIRECTED, ACTED_IN, BELONGS_TO, EXPLORES, WON).
- Templates: **traversal, property, filter, set logic, projection**; every query = pattern → filters → return.
- Indexing: upload PDF once → LLM extracts **JSON in batches** (parallel + retries) → **MERGE** in transactions with indexes → one vector per movie.
- Query: **extract → resolve (exact, then CONTAINS, across all labels) → classify → handler**.
- **The LLM writes a JSON plan, never Cypher**; code whitelists labels/relationships/properties/operators, binds values as **parameters**, READ session.
- Review found `sort` property and `aggregation` alias not whitelisted → fixed with an identifier check.
:::

:::quiz
1. Why does every query start with entity resolution?
2. Which questions go to the similarity handler, and what does Neo4j add there?
3. Why is `x' OR 1=1 //` harmless in a filter value?
4. What stops the planner from producing a `DELETE`?
5. Name one question the current plan format can't express.
:::

:::answer
1. Because a name like "Nolan" could be a director, actor or even a movie; only the graph knows. Resolving first gives later LLM calls exact labels and full names.
2. "Movies like / similar to / recommend" questions. Neo4j filters the vector candidates to those sharing the source movie's genres (fact check), before the LLM ranks them.
3. Values are bound as parameters (`$p0`), so they are treated as data, never parsed as Cypher.
4. The builder can only emit MATCH/WHERE/RETURN/ORDER BY/LIMIT from whitelisted pieces; there is no step type that produces write clauses (and the session is read-only).
5. Anything needing two different nodes of the same label, e.g. "actors who acted in two different Nolan movies" (every Movie gets the same variable `m`).
:::

:::qa Interview questions — Graph RAG
Q: What is Graph RAG and when does it beat vector RAG?
RAG where retrieval queries a knowledge graph of entities and relationships instead of (or in addition to) similarity search over chunks. It wins on relational and multi-hop questions — "actors in Nolan's Oscar-winning films", counts, paths — where facts from many documents must be joined exactly. Vector RAG is better for fuzzy, semantic questions.

Q: How do you build the graph from unstructured text?
Use an LLM for entity and relationship extraction into a fixed JSON schema, in batches with retries and validation; then insert with MERGE (and indexes or uniqueness constraints) inside transactions, parsing composite values like "Oscar (Best Cinematography)" into properties. Log and retry failed batches.

Q: How do you let an LLM query a graph database safely?
Don't let it write the query language. Have it output a structured plan from a small set of templates; validate every label, relationship, property, operator and identifier against whitelists; bind all values as parameters; run in a read-only session with a read-only user; add limits and timeouts.

Q: How does the similarity path work in the movie project?
Resolve the source movie, embed it, take the top 50 vector matches from Pinecone, filter them in Neo4j to those sharing a genre, then let the LLM pick and explain the best 10 — vector search for recall, graph for factual filtering, LLM for final ranking.

Q: What would you improve?
Uniqueness constraints and stable ids, fuzzy entity resolution with disambiguation, embedding the movie's own document for "more like this", per-step variable names for richer plans, caching and fewer LLM calls, possibly Neo4j's native vector index instead of a second database, and an evaluation set.
:::
