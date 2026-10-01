:::chapter Part 2 | LangGraph: Workflows as State Machines | Lectures 20–21 · 21 questions
- **A.** Core concepts (Q1–Q5)
- **B.** Saving progress and resuming (Q6–Q11)
- **C.** The PDF pipeline and Lecture 21's three designs (Q12–Q16)
- **D.** Other features (Q17–Q19)
- **E.** Your project, StanceScope (Q20–Q21)
:::

## A. Core concepts

:::qa -
Q: What is LangGraph, and why not just write a loop? {{p:133–134}}
LangGraph builds AI workflows as a **state machine**: state, nodes and edges, plus a runtime that **saves progress after every step**. A plain loop keeps its progress only in memory: if it crashes at chunk 237 of 1,000 you start again, and you can't pause for a human or inspect where it stopped. LangGraph gives you resume, loops, branching, parallel steps and human pauses.

Q: Explain state, nodes and edges. {{p:136}}
- **State** is the shared data of one run, like `pdfText`, `chunks` and `currentIndex`.
- **Nodes** are functions that read the state and return only the fields they changed.
- **Edges** decide what runs next. They can be fixed, or **conditional**: a router function looks at the state and returns the next node's name or `END`. Loops are built from conditional edges.

Q: What is a reducer, and when do you need one? {{p:136}}
A reducer decides how a node's update is merged into a state field. By default the last value wins, which is right for `currentIndex`. For a list like `log` or `messages` you need an **append** reducer; otherwise each update wipes out the earlier entries. Reducers are also needed when two parallel nodes write the same field.

Q: What happens if two parallel nodes update the same field without a reducer? {{p:140}}
LangGraph raises an error, because a plain field can only take one value per step. In LangGraph JS it is an `InvalidUpdateError`: "LastValue can only receive one value per step" (I tested it). You add a reducer, such as append or merge, so both updates are combined.

Q: LangGraph vs LangChain? {{p:141}}
LangChain provides building blocks: prompts, models, parsers, retrievers. LangGraph is the runtime that orchestrates them in stateful, looping workflows with checkpoints. They're used together: a LangGraph node can call a LangChain component.
:::

## B. Saving progress and resuming

:::qa -
Q: What is a checkpointer, and what does it save? {{p:137}}
After every node it saves **(state, next node)** under a `thread_id`. That's what makes resume, pause and inspection possible. Without a checkpointer, a stopped graph has nothing to resume from.

Q: What is `thread_id` for? {{p:137}}
It identifies one run. The same `thread_id` continues that run; a new one starts fresh. In a web app it's usually one conversation, one job or one request. StanceScope uses `run-<id>`.

Q: How do you resume after a crash, and what re-runs? {{p:137–138}}
Call `invoke(null, config)` with the same `thread_id`. LangGraph loads the last checkpoint and continues from the saved next node. I tested this: it crashed while storing chunk 2, and on resume only `storeEmbedding` ran again. Loading, chunking and the earlier embeddings were not repeated, and the result was exactly 4 vectors with no duplicates.

Q: Trap question: why `invoke(null, …)` and not `invoke({}, …)`? {{p:138}}
`null` means "continue the stopped run". Passing new input, even `{}`, starts a **new** run from START on that thread. I tested both: with `null` only the failed node ran again; with `{}` the first node ran again as well.

Q: MemorySaver vs SqliteSaver vs Postgres? {{p:137}}
- **MemorySaver** keeps checkpoints in RAM: good for learning and tests, but lost if the process dies.
- **SqliteSaver** uses a file on disk, for single-machine apps.
- **Postgres or Redis** savers are for production with many servers.

Q: What is idempotency, and why does LangGraph need it? {{p:139}}
The checkpoint is written **after** a node finishes. If the process dies after the database write but before the checkpoint, that node runs again on resume. So side effects must be safe to repeat: use an **upsert with a fixed id** (like the chunk index), not an insert with a random id. Something like "send email" must go behind a check or a human approval.
:::

## C. The PDF pipeline and Lecture 21's three designs

:::qa -
Q: Why store `currentIndex` in the state? {{p:135}}
So progress is saved in every checkpoint. After a crash you resume from index 237, not from 0.

Q: Explain the three designs, and which you'd pick. {{p:139–140}}
- **One by one:** the simplest, with the finest resume, but one API call and one database write per chunk, so it's slow.
- **Batches:** embed a batch in parallel with `Promise.all` and save it with one bulk upsert. Much faster, but all chunks stay in memory.
- **Streaming batches:** create only the next batch from a text cursor. Low memory, at the cost of a bit more state to track.

For big files I'd pick streaming batches, with fixed ids so resume never duplicates anything.

Q: Your loop over 1,000 chunks fails with a "recursion limit" error. Why, and what's the fix? {{p:140–141}}
Each round of the loop counts as steps, and the default limit is 25 in the JS version. The error says "Recursion limit of 25 reached without hitting a stop condition". Raise `recursionLimit` in the config (the course uses 500), or batch the work so there are fewer rounds.

Q: How would you process 1 million chunks? {{p:141}}
- Streaming batches.
- Limited parallelism inside each node, with retries and backoff.
- Bulk upserts with fixed ids.
- A persistent checkpointer, so progress survives crashes.
- A recursion limit sized for the loop.

Q: What if the embedding API rate-limits you in the middle of a run? {{p:137–138}}
The node fails and the run stops there, but the checkpoint keeps all finished work. I'd retry with exponential backoff inside the node, or resume later with `invoke(null, config)`. Nothing already embedded is redone.
:::

## D. Other features

:::qa -
Q: How do you show live progress to a user? {{p:140}}
Streaming. `app.stream(input, { streamMode: "updates" })` sends each node's update as it happens. `"values"` streams the full state, and `"messages"` streams the LLM's tokens.

Q: How do you debug a run? {{p:140}}
`getState(config)` shows the current values and the next node, and the state history lets you look at any earlier step ("time travel"). Unit-test each node as a plain function, and add one test that crashes in the middle and resumes.

Q: When would you NOT use LangGraph?
For one LLM call or a short straight-line pipeline. LangGraph adds structure you don't need there; a plain function is simpler.
:::

## E. Your project, StanceScope

:::qa -
Q: How does StanceScope use LangGraph? {{p:191}}
Four nodes: retrieve evidence → classify posts → human review → aggregate. It uses a checkpointer (MemorySaver) and `thread_id = run-<id>`, so a run can pause for human review and continue later.

Q: What would you change in StanceScope, and why? {{p:194}}
Switch MemorySaver to **SqliteSaver**. I tested a server restart while a run was waiting for review: the resume failed with a KeyError, because the checkpoint was only in memory. A persistent checkpointer fixes that.
:::

:::tip How to practise Part 2
Answer each one out loud in under 45 seconds without looking. Mark the ones where you get stuck, and re-read their pages the next morning. **Q6–Q11 and Q13** come up most often.
:::
