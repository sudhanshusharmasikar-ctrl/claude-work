:::chapter 14 | LangGraph: Workflows as State Machines | Lectures 20–21 · LangGraph notes · Must-know
- Why a plain `async` function is a bad home for long AI workflows
- The mental shift: **execution = current step + state**
- **Nodes, edges, state, reducers, conditional edges**
- The PDF → vector DB pipeline as a graph (tested code)
- **Checkpointers**, `thread_id`, and **resuming after a crash** (tested)
- Three pipeline designs: one-by-one, **batches**, **streaming batches**
- Idempotency, `recursionLimit`, streaming and state inspection
:::

Rohit introduces LangGraph with a question: *what happens when your AI workflow crashes halfway?* This chapter is the foundation for human-in-the-loop (Chapter 15), the multi-agent dev team (Chapter 16) and your **StanceScope** project.

## 14.1 Why not just write a function? %%MUST%%

What most people build first:

```js title="a workflow as one big function"
async function runAgent() {
  const plan = await planner();
  const data = await fetchData(plan);
  const result = await analyze(data);
  return result;
}
```

It works — until real life happens. Rohit's list of problems:

1. **Crash in the middle** — planner done, financial data fetched, news fetch in progress… the server dies. You must start again from the beginning, and you don't even know where it stopped.
2. **You can't pause** — "get human approval before the final answer" or "wait 2 hours" is hard, because the execution lives in **stack memory**.
3. **Parallel is messy** — fetch financial data and news **in parallel**, then merge: you hand-write `Promise` logic, merging, and race-condition handling.
4. **Retry is dangerous** — if one branch fails you must retry only that part, without corrupting state or re-running the parts that already succeeded.

> The core problem: **execution is trapped inside a function call.** It is temporary, not checkpointed, not resumable, not replayable, and hard to debug.

## 14.2 The mental shift: a state machine %%MUST%%

LangGraph treats execution as **data**: *where am I (current step) + what do I know (state)*.

| Piece | Role | Analogy |
|---|---|---|
| **State** | The shared memory — a structured object every step reads and updates | The "save file" of a game |
| **Node** | A unit of **work** — a function `(state) → partial update` | One level of the game |
| **Edge** | **Control** — which node runs next (fixed or decided by a function) | The door to the next level |
| **Runtime** | The engine that runs nodes, merges updates, and saves checkpoints | The game console |

Rohit's summary: *"LLMs are non-deterministic. Production systems must be deterministic. LangGraph gives deterministic control over non-deterministic intelligence."* The LLM can be creative **inside** a node; the **flow** between nodes is controlled by your graph.

:::cpp A `switch` over a saved struct
Picture `struct State { int currentIndex; vector<string> chunks; … };` saved to disk after every step, plus a loop `while (step != END) { switch (step) { case LOAD: …; case EMBED: …; } save(state, step); }`. If the program crashes, you reload the file and continue from `step`. LangGraph gives you exactly this — the struct, the switch, and the save — without writing the plumbing.
:::

## 14.3 The example: PDF → vector DB without losing progress %%MUST%%

Remember Lecture 12's indexing: chunk a PDF, embed each chunk, store it. Now imagine **1000 chunks** and a crash at chunk **237**:

- ❌ You don't know where it stopped. ❌ You may create duplicates. ❌ You restart from 0.

**Where is the progress stored? Nowhere** — it lived in the loop variable. The fix: break the loop into **nodes**, keep `currentIndex` in the **state**, and save the state after every node. Then a crash at 237 isn't scary: resume from 237.

[[fig:lg-pipeline|The loop lives in the graph's structure (a conditional edge), not in a while-loop. After every node, the state is checkpointed.]]

## 14.4 The code: state, nodes, edges (tested) %%MUST%%

The Notion notes sketch this with pseudo-helpers. Below is a **runnable** version for LangGraph JS v1: I replaced the PDF, embedding API and vector DB with tiny fakes (so it runs without keys) and ran it, including a simulated crash.

```js title="pdf_pipeline.mjs — state and nodes" lines
import { StateGraph, Annotation, START, END, MemorySaver }
  from "@langchain/langgraph";

// 1. STATE: every field, and how updates are merged
const State = Annotation.Root({
  pdfText: Annotation(),                               // default: last value wins
  chunks: Annotation(),
  currentIndex: Annotation({ reducer: (_, next) => next, default: () => 0 }),
  currentEmbedding: Annotation(),
  log: Annotation({ reducer: (old, add) => old.concat(add), default: () => [] }),
});

// 2. NODES: (state) => a PARTIAL update
async function loadPDF(state) {
  return { pdfText: await readPdfText("file.pdf"), log: ["loadPDF"] };
}
async function createChunks(state) {
  const chunks = splitIntoChunks(state.pdfText);    // e.g. 1000 chars, 200 overlap
  return { chunks, log: [`createChunks → ${chunks.length} chunks`] };
}
async function embedChunk(state) {
  const embedding = await embed(state.chunks[state.currentIndex]);
  return { currentEmbedding: embedding };
}
async function storeEmbedding(state) {
  await vectorDB.upsert({ id: String(state.currentIndex),    // same id → overwrite
                          values: state.currentEmbedding });
  return { currentIndex: state.currentIndex + 1, currentEmbedding: null,
           log: [`stored chunk ${state.currentIndex}`] };
}
```

- **Lines 5–11** — `Annotation.Root` declares the state. A plain `Annotation()` keeps the **last value written**. A field with a **reducer** decides how a new value is combined with the old one: `currentIndex` just takes the new value; `log` **appends**.
- **Lines 14–30** — nodes are normal `async` functions (`readPdfText`, `splitIntoChunks`, `embed` and `vectorDB` stand for your real helpers — in my test they were tiny fakes). They **read** the state and **return only what changed** — LangGraph merges it in using the reducers. Nodes never call each other; **state is the only way nodes communicate**.
- **Lines 26–27** — the chunk index is the vector id. Writing the same id twice just overwrites it — the write is **idempotent** (important for Section 14.6).

```js title="pdf_pipeline.mjs — the graph" lines start=32
// 3. GRAPH: nodes + edges + a conditional loop
const graph = new StateGraph(State)
  .addNode("loadPDF", loadPDF)
  .addNode("createChunks", createChunks)
  .addNode("embedChunk", embedChunk)
  .addNode("storeEmbedding", storeEmbedding)
  .addEdge(START, "loadPDF")
  .addEdge("loadPDF", "createChunks")
  .addEdge("createChunks", "embedChunk")
  .addEdge("embedChunk", "storeEmbedding")
  .addConditionalEdges("storeEmbedding",
    (state) => (state.currentIndex >= state.chunks.length ? END : "embedChunk"));

const app = graph.compile({ checkpointer: new MemorySaver() });
const config = { configurable: { thread_id: "pdf-001" }, recursionLimit: 5000 };
await app.invoke({}, config);
```

- **Lines 34–37** — register nodes by name.
- **Lines 38–41** — fixed edges. `START` is the entry (older code uses `graph.setEntryPoint("loadPDF")`).
- **Lines 42–43** — the **conditional edge** is the loop: after storing, a small **router function** looks at the state and returns the next node's name, or `END` (the string `"__end__"` in the notes) when all chunks are done.
- **Line 45** — `compile()` checks the graph and attaches a **checkpointer**.
- **Line 46** — `thread_id` names this run; `recursionLimit` caps the number of steps (default 25 — a 1000-chunk loop needs a much higher limit, or LangGraph stops it with a recursion error).

## 14.5 Checkpointers and resuming after a crash (tested) %%MUST%%

A **checkpointer** saves `(state, next node)` after every step, keyed by `thread_id`:

| Checkpointer | Where state lives | Use |
|---|---|---|
| `MemorySaver` | RAM of the current process | Learning and tests — **lost if the process dies** |
| `SqliteSaver` (`@langchain/langgraph-checkpoint-sqlite`) | A SQLite file | Single-machine apps |
| Postgres / Redis savers | A database server | Production, many processes (the AI dev team uses Redis) |

To test resuming, I made `storeEmbedding` throw an error the first time it reached chunk 2, then called `invoke` again with **`null` input** and the **same `thread_id`**:

```js title="crash and resume"
try {
  await app.invoke({}, config);
} catch (err) {
  console.log("CRASH:", err.message);
  const snap = await app.getState(config);           // what was saved?
  console.log("saved state → currentIndex =", snap.values.currentIndex,
              "| next node =", snap.next);
}
const final = await app.invoke(null, config);   // null = "continue this thread"
console.log("resumed and finished:", final.log.join(" | "));
```

```output title="node pdf_pipeline.mjs  (LangGraph JS 1.4, fake PDF with 4 chunks)"
CRASH: network died while storing chunk 2
saved state → currentIndex = 2 | next node = [ 'storeEmbedding' ]
resumed and finished: loadPDF | createChunks → 4 chunks | stored chunk 0 |
                      stored chunk 1 | stored chunk 2 | stored chunk 3
vectors in DB: 4 chunks: 4
```

Read this carefully — it's the whole point of LangGraph:

- The crash didn't lose anything: the checkpoint says **currentIndex = 2** and the next node is **storeEmbedding**.
- Resuming re-ran **only the node that failed**. `loadPDF`, `createChunks` and the embedding of chunk 2 were **not** repeated.
- Result: exactly 4 vectors — **no duplicates, no restart**.

With `MemorySaver` this only works while the process is alive. To survive a **real** crash (the server restarts), use a persistent checkpointer:

```js title="persistent checkpoints (from the notes)"
import { SqliteSaver } from "@langchain/langgraph-checkpoint-sqlite";
const checkpointer = SqliteSaver.fromConnString("checkpoints.db");
const app = graph.compile({ checkpointer });
await app.invoke({}, { configurable: { thread_id: "pdf-processing-1" } });
// after a restart:
//   await app.invoke(null, { configurable: { thread_id: "pdf-processing-1" } });
```

:::remember `thread_id` is critical
Checkpoints are stored **per thread**. Same `thread_id` → continue that workflow. New `thread_id` → a fresh run. In a web app, a thread is usually one conversation, one job, or one user request (StanceScope uses `run-<id>`).
:::

## 14.6 Idempotency: the detail that makes resume safe %%GOOD%%

A checkpoint is written **after** a node finishes. If the process dies **inside** `storeEmbedding` — after the database write but before the checkpoint — LangGraph will run `storeEmbedding` **again** on resume. That's safe only if running it twice has the same effect as once: **idempotent**.

- ✅ `upsert` with a **deterministic id** (`String(currentIndex)`): the second write overwrites the first.
- ❌ `insert` with a random id, "send email", "charge card": the second run duplicates the effect.

Rule: make node side effects **idempotent** (stable ids, "check before do"), or put them after a human checkpoint. (Chapter 15 shows the same rule for `interrupt()`.)

## 14.7 Three designs for the pipeline (Lecture 21) %%GOOD%%

| Design | Graph | Good | Bad |
|---|---|---|---|
| **1. One by one** | loadPDF → createChunks → embedChunk → store → loop | Simplest; fine-grained resume | One API call + one DB write **per chunk** → slow |
| **2. Batches** | createBatch → embedBatch → storeBatch → loop | `Promise.all` inside the node + **bulk upsert** → much faster | All chunks still kept in memory |
| **3. Streaming batches** | loadPDF → createChunkBatch → embedBatch → storeBatch → loop | Creates only the **next** batch from a `textCursor` → low memory | Slightly more state to manage |

The streaming version's key node — it makes the next few chunks and moves the cursor:

```js title="design 3 — createChunkBatch and embedBatch (tested)"
async function createChunkBatch(state) {
  const chunks = [];
  let cursor = state.textCursor;
  for (let i = 0; i < state.batchSize; i++) {
    if (cursor >= state.pdfText.length) break;
    chunks.push({ id: cursor,
                  content: state.pdfText.slice(cursor, cursor + state.chunkSize) });
    cursor += state.chunkSize - state.overlap;      // step forward, keep overlap
  }
  return { currentChunkBatch: chunks, textCursor: cursor };
}

async function embedBatch(state) {                     // parallel INSIDE one node
  const embeddings = await Promise.all(
    state.currentChunkBatch.map((c) => embed(c.content)));
  return { currentEmbeddings: embeddings };
}
// storeBatch: one bulk upsert (ids = chunk start positions), then clear the batch.
// Loop edge after storeBatch:
//   textCursor >= pdfText.length ? END : "createChunkBatch"
```

With a 250-character fake text, `chunkSize` 100, `overlap` 20 and `batchSize` 2, my run made two bulk upserts with chunk ids `0,80` and `160,240` — chunks start every 80 characters (100 − 20), exactly as designed. Because the ids are the start positions, resuming after a crash overwrites instead of duplicating.

## 14.8 Other features you should be able to name %%GOOD%%

- **Streaming**: `for await (const update of await app.stream(input, { ...config, streamMode: "updates" }))` gives you each node's update as it happens — how the AI dev team's web UI shows live progress. (`"values"` streams the full state; `"messages"` streams LLM tokens.)
- **Inspecting state**: `app.getState(config)` (current values + next node) and the state history for debugging ("time travel").
- **Parallel branches**: a node with edges to two nodes runs them in the same step; their updates are merged with **reducers** — that's why reducers exist.
- **Human-in-the-loop**: `interrupt()` pauses the graph and waits for a person — next chapter.

:::remember
- Plain functions trap execution in the stack: no resume, no pause, messy parallelism, risky retries.
- LangGraph = **state machine**: **state** (memory) + **nodes** (work) + **edges** (control) + runtime.
- Nodes return **partial updates**; **reducers** merge them (last-value by default; append for lists).
- **Conditional edges** implement loops and branches with a router function returning a node name or `END`.
- **Checkpointer** saves state + next node after every node, per **`thread_id`**; `invoke(null, config)` resumes.
- Tested: after a crash, only the failed node re-ran; no duplicates. `MemorySaver` = in-process only; use SQLite/Postgres/Redis to survive restarts.
- Make side effects **idempotent** (stable ids / upsert). Raise **`recursionLimit`** for long loops.
:::

:::quiz
1. Why is `currentIndex` stored in the state instead of a loop variable?
2. What does a reducer do? Give an example where "last value wins" is wrong.
3. You call `app.invoke(null, config)`. What happens?
4. Your graph loops over 1000 chunks and stops with a recursion error. Why, and what do you change?
5. Why is `upsert` with `id = String(currentIndex)` safer than `insert` with a random id?
:::

:::answer
1. So progress is saved in checkpoints; after a crash the run can resume from the saved index instead of starting over.
2. It decides how a node's returned value is merged into the existing state. For a list of logs or messages built by several nodes (or parallel branches), "last value wins" would throw away earlier entries — use an append reducer.
3. LangGraph loads the latest checkpoint for that `thread_id` and continues from the saved next node.
4. Each loop round is several steps and the default `recursionLimit` (25) is far too small; raise it in the config (the course uses 500), or batch the work.
5. If a node is re-run after a crash, the same id is overwritten, so no duplicate vectors appear (idempotent).
:::

:::qa Interview questions — LangGraph basics
Q: Why use LangGraph instead of a simple loop or LangChain chain?
Long AI workflows need persistence, resumability, loops, branching, parallelism and human checkpoints. LangGraph models the workflow as a state machine — nodes, edges and typed state — and checkpoints state after every step per thread, so runs can pause, resume after crashes, and be inspected. A chain is a straight pipeline; a loop in a function keeps its progress only in memory.

Q: Explain nodes, edges, state and reducers.
State is the shared, typed data of a run. Nodes are functions that read the state and return partial updates. Edges decide what runs next — fixed edges or conditional edges whose router function returns the next node name or END. Reducers define how a node's update is merged into a state field, e.g. overwrite vs append, which matters when multiple nodes or parallel branches write the same field.

Q: What is a checkpointer and what is thread_id?
A checkpointer persists the state and the next node after each step. thread_id identifies which run a checkpoint belongs to; invoking again with the same thread_id (and null input) resumes it. MemorySaver is in-process only; SQLite, Postgres or Redis savers survive restarts.

Q: If a node crashes after writing to a database but before the checkpoint, what happens on resume?
The node runs again, so its side effects happen twice unless they're idempotent. I design writes as upserts with deterministic ids, or check-then-write, and keep irreversible actions behind confirmations.

Q: How do you process 1 million chunks efficiently with LangGraph?
Batch inside nodes: create a batch, embed it with limited parallelism (Promise.all with a concurrency cap and retries), bulk-upsert, update a cursor in state, and loop with a conditional edge — with a persistent checkpointer so progress survives crashes, deterministic ids for idempotency, and a recursion limit sized for the loop.
:::
