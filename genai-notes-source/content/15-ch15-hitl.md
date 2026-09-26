:::chapter 15 | Pause, Resume and Human-in-the-Loop | Lectures 22–26 + LangGraph docs · Must-know
- **Why** agents need a human sometimes
- The course's approach: a node that **waits** (readline / a WebSocket "input bridge")
- Why that breaks in production
- LangGraph's **`interrupt()`** and **`Command({ resume })`** — tested
- The rule that surprises everyone: the node **re-runs from the start**
- Other gotchas: `try/catch`, checkpointer, `thread_id`, string keys
- API design around a paused graph (the StanceScope pattern)
:::

This chapter is directly about your **StanceScope** project: its whole selling point is that the graph *"genuinely pauses, hands the unsure posts to a person, and picks up exactly where it stopped."* Interviewers will poke at exactly this. Understand it deeply.

## 15.1 When should an agent stop and ask a human? %%MUST%%

- **Approval** before something expensive or irreversible — the PM agent shows its plan when complexity is HIGH; a coding agent shows a diff before writing files (Chapter 4).
- **Clarification** — the requirement is ambiguous ("build a blog" — with login? comments?).
- **Low confidence** — the model isn't sure (StanceScope: stance confidence below a threshold).
- **Escalation** — automation failed several times (the AI dev team's tier-4 escalation, Chapter 16).
- **Editing** — the human fixes the plan/state and the agent continues with the edited version.

These are also your answers to *"How do you make an agent safe and trustworthy?"*

## 15.2 The course's approach: a node that waits %%GOOD%%

In the CLI version (Lecture 24), the `humanInput` node simply asks on the terminal:

```js title="Lecture24 … src/nodes/humanInput.js (excerpt)"
export async function humanInputNode(state) {
  const questions = state.pmQuestions;
  if (!questions || questions.length === 0) return {};
  questions.forEach((q, i) => console.log(`  ${i + 1}. ${q}`));
  const answer = await askUser("  Your answers: ");   // readline: waits for typing
  return {
    pmConversation: [{ role: "user", answers: answer }],
    pmStatus: "idle",                                // so the PM agent runs again
  };
}
```

For the web dashboard (Lecture 26), the same node awaits a **Promise** that the WebSocket handler resolves later — an **input bridge**:

```js title="Lecture26 … server/services/graphRunner.js — InputBridge (excerpt)"
class InputBridge {
  waitForInput(type, payload) {
    this._emitFn?.({ type: "human_input_needed",
                     questions: payload?.questions || [] });
    return new Promise((resolve) => { this._resolver = resolve; }); // node waits
  }
  provideInput(data) {                         // called by the WebSocket handler
    if (this._resolver) {
      const r = this._resolver; this._resolver = null; r(data);
    }
  }
}
export const inputBridges = new Map();        // one bridge per active project
```

It works for a demo, and the comment in `humanInput.js` itself says LangGraph supports this natively via `interrupt()`. Why is the waiting-node approach weak?

| Problem | Why |
|---|---|
| **The run is stuck in memory** | The node is suspended inside a live process, holding the graph run open for minutes or hours |
| **A restart loses the question** | Server redeploys or crashes → the pending Promise is gone; nothing in the checkpoint says "waiting for an answer" |
| **Concurrency bugs** | The server-mode node looks up "any active bridge — there should be exactly one". With two users running projects at once, an answer can reach the wrong run |
| **Doesn't scale out** | The user's answer must reach the **same** process that holds the Promise; with several servers behind a load balancer it may not |

## 15.3 The right tool: `interrupt()` and `Command({ resume })` %%MUST%%

LangGraph's built-in human-in-the-loop:

1. Inside a node, call **`interrupt(payload)`**.
2. LangGraph **stops the run**, **saves a checkpoint**, and `invoke` **returns** — with the payload under `__interrupt__`. No process is left waiting.
3. Your app shows the payload to a person (web page, Slack message, email…) — minutes or days later, from any server.
4. Resume with **`app.invoke(new Command({ resume: value }), config)`** using the **same `thread_id`**.
5. The node runs again and this time **`interrupt()` returns `value`**; the graph continues.

[[fig:interrupt-flow|interrupt() turns "waiting for a human" into saved data. The run ends; a later request with the same thread_id resumes it.]]

I ran this with LangGraph JS 1.4:

```js title="interrupt_demo.mjs (tested)" lines
import { StateGraph, Annotation, START, END, MemorySaver, interrupt, Command }
  from "@langchain/langgraph";

const State = Annotation.Root({
  request: Annotation(), plan: Annotation(),
  approved: Annotation(), result: Annotation(),
});

async function makePlan(state) {                 // imagine an LLM call here
  return { plan: `1) design schema 2) build API for: ${state.request}` };
}
async function humanReview(state) {
  const answer = interrupt({ question: "Approve this plan?", plan: state.plan });
  // ↓ runs only after resume; `answer` is what the human sent
  return { approved: answer.approved, plan: answer.editedPlan ?? state.plan };
}
async function build(state) {
  return { result: `building: ${state.plan}` };
}

const app = new StateGraph(State)
  .addNode("makePlan", makePlan)
  .addNode("humanReview", humanReview)
  .addNode("build", build)
  .addEdge(START, "makePlan").addEdge("makePlan", "humanReview")
  .addConditionalEdges("humanReview", (s) => (s.approved ? "build" : END))
  .addEdge("build", END)
  .compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "job-42" } };
const first = await app.invoke({ request: "blog API" }, config);
console.log("paused? ", "__interrupt__" in first);
console.log("payload:", JSON.stringify(first.__interrupt__[0].value));
console.log("next node:", (await app.getState(config)).next);

// ... later, maybe from another HTTP request ...
const done = await app.invoke(new Command({ resume: { approved: true } }), config);
console.log("result:", done.result);
```

```output title="node interrupt_demo.mjs  (plus counters I added)"
paused?  true
payload: {"question":"Approve this plan?",
          "plan":"1) design schema 2) build API for: blog API"}
next node: [ 'humanReview' ]
result: building: 1) design schema 2) build API for: blog API
makePlan ran 1x, humanReview started 2x      #> the paused node restarted on resume
```

- **Line 13** — `interrupt(...)` pauses. The payload is anything JSON-serialisable you want the human to see.
- **Line 15** — what the node does **with** the answer (approve, or use an edited plan).
- **Line 26** — the router after review: approved → build, rejected → END.
- **Line 28** — no checkpointer = no interrupt (there would be nowhere to resume from).
- **Lines 31–34** — the first `invoke` **returns** instead of hanging; `getState` shows the thread is waiting at `humanReview`.
- **Line 37** — `Command({ resume })` delivers the human's answer.

## 15.4 The surprising rule: the node restarts from the beginning %%MUST%%

Look at the last output line: **`humanReview started 2x`**. On resume, LangGraph does **not** continue from the middle of the function (JavaScript can't freeze a function's stack into a database). It **re-runs the whole node from its first line**; when execution reaches `interrupt()` again, it returns the resume value instead of pausing.

Consequences:

1. **Code before `interrupt()` runs twice.** Don't put side effects there (DB writes, emails, LLM calls you pay for). Put them **after** `interrupt()`, in a separate node, or make them idempotent. (`makePlan` ran only once because it's a **separate, completed node** — its result was in the checkpoint.)
2. **Several `interrupt()` calls in one node** are matched to resume values **by order** — keep the order deterministic.
3. **Don't catch everything around `interrupt()`.** It pauses by throwing a special error. I tested wrapping it in `try { … } catch (err) { … }`: the graph **did not pause** — the catch received `GraphInterrupt` and the node returned normally. Catch only the errors you mean to.
4. **Resume values must be serialisable** (plain JSON) because they're stored in checkpoints. In Python LangGraph, StanceScope hit a related bug: a resume dict with **integer keys** caused a `TypeError` inside LangGraph's resume handling — the fix was to convert post ids to **strings**. A nice "bug I found by running it" story.

:::cpp Why can't it resume mid-function?
Resuming mid-function would mean saving the **call stack** — local variables, the program counter, every frame — to a database and restoring it in another process. C++ can't do that portably either. LangGraph's design choice: save **state between nodes** (plain data), and re-run the interrupted node. That's why nodes should be small and their pre-interrupt part cheap and side-effect free.
:::

## 15.5 Human-in-the-loop patterns %%GOOD%%

| Pattern | Payload shown | Resume value | Example |
|---|---|---|---|
| **Approve / reject** | The plan or action | `{ approved: true/false }` | PM plan, deploy step |
| **Edit state** | The draft | `{ editedPlan: "…" }` | Human fixes the architecture before coding |
| **Review a tool call** | Tool name + arguments | approve / modify / reject | Confirm `write_file` or "send email" (Chapter 4's safety fix) |
| **Answer questions** | Clarifying questions | The answers | PM agent's clarification loop |
| **Label uncertain items** | Low-confidence predictions | `{ "<post_id>": "support" … }` | **StanceScope** |

## 15.6 Where does the paused state live? %%MUST%%

The pause is only as durable as the **checkpointer**:

- `MemorySaver` → the paused run lives in the server's RAM. Restart the server → the pending review is **gone**. That's StanceScope's current setup — say so honestly, and say the fix: **`SqliteSaver`** (or Postgres) so a review can wait days and survive restarts.
- A persistent checkpointer + `thread_id` = the pause survives restarts, and **any** server instance can resume it.

## 15.7 Designing an API around a paused graph (the StanceScope pattern) %%GOOD%%

```text title="the request/response flow"
POST /claims/{id}/run
   → graph.invoke(initialState, { thread_id: "run-17" })
   → result has __interrupt__ ?  → save status "awaiting_review",
                                   return the flagged items
                               else → return the final report

POST /runs/17/review   { decisions: { "101": "oppose", "104": "neutral" } }
   → check status == "awaiting_review"  (reject double submits)
   → graph.invoke(new Command({ resume: decisions }), { thread_id: "run-17" })
   → return the final report
```

Details interviewers like: **validate** the review payload (only allowed stance labels, only the flagged post ids); guard against **double submission**; store **who** reviewed and **when**; and record for every prediction whether it came from the **model or a human** (StanceScope does this in its database — that's what makes every number auditable).

:::remember
- Humans are needed for **approval, clarification, low confidence, escalation, editing**.
- A node that **awaits** a Promise/readline keeps the run alive in memory: lost on restart, concurrency bugs, doesn't scale out.
- **`interrupt(payload)`** saves a checkpoint and returns control (`__interrupt__`); **`Command({ resume })`** with the same **`thread_id`** continues.
- Tested: the paused node **re-runs from its start** on resume; earlier completed nodes don't.
- So: no side effects before `interrupt()`; don't swallow it in `try/catch`; resume values = plain JSON (string keys).
- Needs a **checkpointer**; `MemorySaver` loses paused runs on restart → use SQLite/Postgres.
- API: run → "awaiting_review" + items; review endpoint validates and resumes; log model vs human decisions.
:::

:::quiz
1. What does `invoke` return when a node calls `interrupt()`?
2. On resume, which line of the interrupted node runs first?
3. Your node sends an email, then calls `interrupt()`. What goes wrong?
4. Why did wrapping `interrupt()` in `try/catch` break the pause?
5. StanceScope uses `MemorySaver`. What happens to a pending review if the server restarts, and what's the fix?
:::

:::answer
1. The state so far plus an `__interrupt__` array whose items carry the payload (`[0].value`); the run is paused at that node.
2. The **first** line — the whole node re-runs; `interrupt()` then returns the resume value.
3. The email is sent twice: once before the pause and again when the node re-runs on resume.
4. `interrupt()` pauses by throwing a special `GraphInterrupt` error; a catch-all handler caught it, so LangGraph never saw the pause.
5. It's lost — the checkpoint lived in RAM. Use a persistent checkpointer (SqliteSaver/Postgres) so the thread can be resumed after a restart.
:::

:::qa Interview questions — human-in-the-loop
Q: How do you implement human-in-the-loop in LangGraph?
Call `interrupt(payload)` inside a node. With a checkpointer attached, LangGraph saves the state and returns control with the payload under `__interrupt__`. The app shows it to a person; later it calls `invoke(new Command({ resume: answer }), { thread_id })`, the node re-runs, `interrupt()` returns the answer, and the graph continues.

Q: What happens to code written before interrupt() in the same node?
It runs again on resume, because the node restarts from the beginning. So I keep side effects out of the pre-interrupt part — put them after the interrupt, in their own node, or make them idempotent.

Q: Why not just wait for user input inside the node with a Promise or readline?
The run then lives in process memory: it's lost on restart, blocks resources, can route answers to the wrong run when several users are active, and breaks with multiple server instances. interrupt() turns the wait into persisted state that any process can resume.

Q: In StanceScope, what happens if the server restarts during a review?
Currently the paused run is lost, because I use MemorySaver, which keeps checkpoints in memory — I tested it: the resume starts from scratch and fails with a KeyError (Chapter 19.5). The fix is a persistent checkpointer such as SqliteSaver, keyed by the run's thread_id, so reviews can wait days and survive restarts. The run table already records the status, so the UI can show "awaiting review" after the fix.

Q: How do you make human review safe and auditable?
Validate the review payload (allowed labels, only flagged items), prevent double submission by checking the run status, record reviewer identity and time, and store for every decision whether it came from the model or a human, so every reported number can be traced.
:::
