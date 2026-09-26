:::chapter 16 | Multi-Agent AI Dev Team | Lectures 22–26 · design doc + Lecture24–26 code · Good to know
- The goal: agents that **plan, design, code, review, test and fix** a web app
- The real graph: **4 phases, 27 nodes**, all communicating through **state**
- **Reducers in practice** — and the token-counting bug they caused
- **JSON-only agents**, retries and a **token budget**
- Loop control: review caps, **4-tier debugging**, rollback, human escalation
- **Context engineering**: file interface registry, filtered context, state compaction
- Sandboxes, git snapshots, Redis checkpoints, a live web dashboard
:::

Lectures 22–26 build the course's biggest system: a "mini Devin/Codex" that turns *"Build a blog API with auth"* into a working project. You won't memorise 4,700 lines — you'll learn the **design ideas**, because those are what interviewers ask: *how do agents communicate, how do you stop infinite loops, how do you control cost, how do you recover from failure?*

## 16.1 From the whiteboard plan to the real graph %%GOOD%%

The first plan (Lecture 22 notes): **PM agent** (understands and breaks down the task) → **human checkpoint** → **architect** (tech stack, DB schema, API routes, folders) → **coder** and **test planner** in parallel → **test runner** → **code reviewer** → human checkpoint → **DevOps** (Dockerfile, deployment). Failures loop back through the PM, who acts as the **traffic controller**.

The implemented version (design doc V2, Lectures 24–26) is more careful:

[[fig:dev-team|The AI dev team's LangGraph (simplified): four phases, with loops for clarification, validation, review and debugging.]]

| Phase | Nodes | What happens |
|---|---|---|
| **1 · Spec** | `pmAgent` ⇄ `humanInput` | PM asks up to 5–8 clarifying questions or outputs a full JSON spec; the loop repeats until `spec_ready` |
| **2 · Blueprint** | `architectStep1…5` → `blueprintValidator` | 5 steps: entities → DB schema → API endpoints → frontend pages → folders + dependencies; the validator can send it back to step 2, 3 or 4 (max 2 cycles) |
| **3 · Plan + sandbox** | `plannerAgent` → `setupSandbox` ⇄ `sandboxHealthCheck` | Task queue in phases; Docker containers (DB, backend, frontend) + `git init` |
| **4 · Dev loop** | `selectNextTask` → `contextBuilder` → `coderAgent` → `updateRegistry` → `reviewerAgent` → `executorAgent` → `snapshotManager` (or `debuggerAgent` / `humanEscalation` / `simplifyTask`); per phase: `phaseVerification` → `patternExtractor` → `stateCompactor`; at the end `deploymentVerifier` → `presentToUser` | Build every task, verify, learn patterns, compact state |

## 16.2 State is the only way agents talk %%MUST%%

The state file begins with a first-principles comment: *"In LangGraph, state is the ONLY way nodes communicate. Node A writes to state → Node B reads from state. There's no direct function call between nodes."* The whole team's memory is one `Annotation.Root` with ~30 fields — and each field's **reducer** is a design decision:

```js title="src/config/state.js (excerpt)"
export const AgentState = Annotation.Root({
  userRequirement: Annotation({ reducer: (_, y) => y ?? "", default: () => "" }),

  // PM ⇄ human Q&A accumulates across rounds → APPEND
  pmConversation: Annotation({
    reducer: (existing, incoming) => {
      if (!incoming) return existing;
      if (Array.isArray(incoming)) return [...existing, ...incoming];
      return [...existing, incoming];
    },
    default: () => [],
  }),

  // Built across 5 architect steps → MERGE objects
  blueprint: Annotation({
    reducer: (existing, incoming) =>
      (incoming ? { ...existing, ...incoming } : existing),
    default: () => ({ entities: [], dbSchema: {}, apiEndpoints: [],
                      frontendPages: [], folderStructure: "", dependencies: {} }),
  }),

  // One entry per file, updated after every task → MERGE BY KEY (path)
  fileRegistry: Annotation({
    reducer: (existing, incoming) => {
      if (!incoming || !Array.isArray(incoming)) return existing;
      const map = new Map(existing.map((f) => [f.path, f]));
      for (const entry of incoming) map.set(entry.path, entry);
      return Array.from(map.values());
    },
    default: () => [],
  }),

  // Token usage: ADD the delta each agent reports
  tokenUsage: Annotation({
    reducer: (existing, incoming) => !incoming ? existing : ({
      calls: [...(existing.calls || []), ...(incoming.newCalls || [])],
      totalInput: existing.totalInput + (incoming.addedInput || 0),
      totalOutput: existing.totalOutput + (incoming.addedOutput || 0),
      estimatedCost: existing.estimatedCost + (incoming.addedCost || 0),
    }),
    default: () => ({ calls: [], totalInput: 0, totalOutput: 0, estimatedCost: 0 }),
  }),
  // ... pmStatus, clarifiedSpec, taskQueue, currentTask, reviewResult,
  //     debugState, sandboxId, deploymentConfig, ...
});
```

| Reducer style | Field | Why |
|---|---|---|
| **Last value wins** | `pmStatus`, `currentTask`, `reviewResult` | Only the latest matters |
| **Append** | `pmConversation`, `userFeedback` | History must be kept |
| **Merge objects** | `blueprint`, `projectPatterns`, `taskStatuses` | Built piece by piece by different nodes |
| **Merge by key** | `fileRegistry` | Update the entry for a path, add new paths |
| **Add numbers** | `tokenUsage` | Running totals |

:::cpp Reducers = how `operator+=` is defined for each field
Think of each field having its own "combine" function: for `int` counters it's `+=`, for `vector` logs it's `insert(end, …)`, for a `map<string, File>` it's `m[key] = value`. LangGraph calls that combine function every time a node returns an update.
:::

## 16.3 The reducer bug that multiplied token counts %%GOOD%%

The Gemini wrapper's header comment tells a real bug story. **Old approach:** each agent received the `tokenUsage` object, **added** its own call to it, and returned the **whole** object. But the reducer also **adds** — so old totals were counted again on every call:

| Call | Real total | Agent returned (full object) | Reducer: existing + returned |
|---|---|---|---|
| 1 (+100) | 100 | 100 | 0 + 100 = **100** ✓ |
| 2 (+50) | 150 | 150 | 100 + 150 = **250** ✗ |
| 3 (+50) | 200 | 250 + 50 = 300 | 250 + 300 = **550** ✗ |

The error grows explosively ("exponential duplication"), and the **token budget** check — which reads this total — would stop the run far too early. **Fix:** agents return only a **delta** (`makeTokenDelta` → `{ newCalls, addedInput, addedOutput, addedCost }`), and the reducer adds it once.

> Rule: a node returns **what changed**, never the full accumulated value of a field that has an accumulating reducer.

## 16.4 JSON-only agents with retries and a budget %%GOOD%%

Every agent talks to Gemini through one wrapper:

```js title="src/utils/gemini.js — callGemini (excerpt)"
export async function callGemini({ systemPrompt, userPrompt, agentName,
                                   currentCost = 0, tokenBudget = 2.0 }) {
  if (currentCost >= tokenBudget) {                          // cost guard FIRST
    throw new Error(`TOKEN_BUDGET_EXCEEDED: $${currentCost.toFixed(4)}`
                    + ` >= budget $${tokenBudget}`);
  }
  const fullPrompt = `${systemPrompt}\n\n---\n\nINPUT:\n${userPrompt}\n\n---\n\n`
    + `IMPORTANT: Respond with ONLY valid JSON. No markdown, no backticks.`;

  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await client.models.generateContent({
        model: process.env.GEMINI_MODEL || "gemini-2.5-flash",
        contents: fullPrompt,
        config: { responseMimeType: "application/json" },    // JSON mode
      });
      const usage = response.usageMetadata;                  // real token counts
      // ... compute cost, strip ``` fences, JSON.parse (retry on parse failure) ...
      return { parsed, raw: response.text, tokens: { input, output, cost } };
    } catch (error) {
      if (error.message?.includes("TOKEN_BUDGET_EXCEEDED")) throw error;
      if (attempt === 3) throw error;
      const waitMs = Math.pow(2, attempt) * 1000;             // 2 s, then 4 s
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }
}
```

- **Budget guard** before every call (default **$2** per project, from `TOKEN_BUDGET`) — protection against runaway loops (OWASP **LLM10 Unbounded Consumption**).
- **JSON mode** + an explicit "ONLY valid JSON" instruction + fence stripping + parse-retry.
- **Exponential backoff** on errors (2 s, 4 s).
- Real token counts from `usageMetadata`. (The cost formula uses hard-coded per-million prices — prices change, so in real systems read them from config.)

Every agent's prompt follows the same shape — **ROLE → GOAL → BOUNDARIES/RULES → OUTPUT FORMAT (strict JSON)**. For example the PM: "Max 5–8 clarifying questions… don't ask about the tech stack (it's fixed)… return `needs_clarification` with questions, or `spec_ready` with a full spec, always with `assumptions`".

## 16.5 Stopping infinite loops %%MUST%%

A multi-agent system is full of loops. Each one needs an **exit**:

```js title="reviewer and executor routers"
export function reviewerRouter(state) {            // src/agents/reviewerAgent.js
  const { verdict, reviewCycle } = state.reviewResult || {};
  if (verdict === "approved") return "executorAgent";
  if (reviewCycle >= 3) return "simplifyTask";   // rejected 3 times → split it
  return "coderAgent";                           // retry with reviewer feedback
}

export function executorRouter(state) {            // src/agents/executorAgent.js
  if (state.executionResult?.result === "pass") return "snapshotManager";
  return "debuggerAgent";
}
```

The debugger escalates in **tiers** instead of retrying the same thing forever:

[[fig:escalation|The debugger's escalation ladder: each tier costs more context or more drastic action, and the last step is a human.]]

| Tier | Action | Limit |
|---|---|---|
| **1** | Read the error + the failing files → suggest a specific fix → coder retries | 3 attempts (or earlier if the debugger reports **low confidence**) |
| **2** | Also read up to 10 other project files (first 50 lines each) for context | 2 attempts |
| **2.5** | **Roll back** the sandbox to the last good git tag and retry the task from scratch | once |
| **3** | **Escalate to a human**: skip the task, give guidance, or simplify it | — |

Other exits in the graph: the blueprint validator proceeds with warnings after **2** cycles; the PM loop ends at `spec_ready`; the whole run has `recursionLimit: 500`; and the **token budget** stops everything.

## 16.6 Context engineering: small, relevant prompts %%GOOD%%

A 50-file project can't fit in every prompt, and sending it would be slow and costly. Three tricks:

1. **File interface registry** — after the coder writes files, `updateRegistry` asks a small LLM call to extract each file's **public interface**: exports, the exact `import` statement, a one-line description. Later tasks receive only these **signatures**, not full files.
2. **Context builder** — for each task, send: the task + acceptance criteria, the interfaces of the files it depends on, only the **relevant DB tables**, the naming map, the project's **patterns** (error format, naming convention), and one completed similar file as a **style template**.
3. **State compactor** — after each phase, completed tasks are reduced to id + title + files; the pattern extractor summarises conventions learned so far. State stays small, so later prompts don't bloat.

These ideas transfer directly: SchemaMind's "send only relevant tables" is the same move.

## 16.7 Safety, recovery and the web UI %%GOOD%%

- **Docker sandbox** per project (database, backend and frontend containers on a private network). Generated code runs **there**, never on the host.
- **Executor test levels**: file exists → syntax check → `npm install` → runtime import (server entry points are tested later, in phase verification).
- **Git snapshots**: after every passing task, commit + tag (`v0.N.0`) → the debugger can **roll back**.
- **Checkpoints**: Redis checkpointer if `REDIS_URL` is set (auto-starting a Redis container), otherwise `MemorySaver`; `thread_id = project-<timestamp>`; resume = `graph.invoke(null, config)` after reconnecting the sandbox.
- **Web dashboard (Lecture 26)**: Express + WebSocket; `graph.stream(…, { streamMode: "updates" })` pushes every node's update to a React UI; human input goes through the Promise "input bridge" (Chapter 15 explains why `interrupt()` would be sturdier).

## 16.8 What you'd improve (great interview discussion) %%GOOD%%

- `interrupt()` + a persistent checkpointer instead of Promise bridges (restarts, many users).
- Default to a **persistent** checkpointer; `MemorySaver` loses everything on a crash.
- **Evaluation**: task success rate, tests passing, cost per project, human-intervention rate — on a fixed set of app requirements.
- Run independent tasks **in parallel** (tasks already carry a `canParallelize` flag).
- Harden the sandbox (no internet by default, CPU/memory limits) — generated code is untrusted.
- A reviewer LLM can miss bugs: rely on **tests** as the real judge, and keep humans in the loop for merges.

:::remember
- 4 phases: **spec (PM ⇄ human) → blueprint (architect ×5 + validator) → plan + sandbox → dev loop**.
- **State is the only communication channel**; each field's **reducer** (last-wins, append, merge, merge-by-key, add) is a design decision.
- Token bug: returning the **full** accumulated value into an **additive** reducer double-counts → return **deltas**.
- Agents: role/goal/rules/**strict JSON** prompts, JSON mode, parse-retry, backoff, **budget guard**.
- Loop exits: review cap 3 → simplify; debugger tiers 1 → 2 → rollback → human; validator cap 2; recursionLimit; budget.
- Context engineering: **interface registry**, filtered context, **state compaction**, learned patterns.
- Recovery: Docker sandbox, git tags for rollback, Redis checkpoints, resume with `invoke(null)`.
:::

:::quiz
1. How does the coder agent know what the reviewer said?
2. Why was the old token tracking wrong, and what's the fix?
3. What happens after the reviewer rejects the same task three times?
4. What is tier 2.5 of the debugger?
5. Why does the context builder send export signatures instead of whole files?
:::

:::answer
1. Through the state: the reviewer writes `reviewResult` (verdict + issues); the router sends control to the coder, which reads `reviewResult` from the state.
2. Agents returned the full running total into an additive reducer, so earlier totals were added again each call. Return only the delta for this call.
3. `reviewerRouter` sends it to `simplifyTask`, which breaks the task into smaller pieces.
4. Roll back the sandbox to the last good git snapshot and retry the task from scratch (once).
5. To keep prompts small and focused: the coder only needs to know how to import and call other files, not their implementation — saving tokens and reducing confusion.
:::

:::qa Interview questions — multi-agent systems
Q: How do agents communicate in a LangGraph multi-agent system?
Through shared state only: each agent node reads the fields it needs and returns a partial update; reducers merge updates; routers read the state to decide the next agent. There are no direct calls between agents, which keeps the flow inspectable and checkpointable.

Q: How do you prevent infinite loops between agents?
Every loop gets an explicit exit: counters in state (review cycles, debug attempts), escalation tiers that change strategy, a human fallback, a graph-level recursion limit, and a global token/cost budget checked before every LLM call.

Q: How do you control cost in a multi-agent system?
Track real token usage per call (as deltas into state), enforce a budget before each call, keep prompts small with context engineering (interfaces not files, filtered schema, compacted state), use cheaper models for simple steps, and cap retries.

Q: What is context engineering in this project?
Choosing exactly what each agent sees: the current task, acceptance criteria, dependency interfaces from a file registry, relevant schema tables, project conventions and one template file — plus compacting old state. It improves quality and cuts tokens.

Q: How does the system recover from bad code?
Code runs in a Docker sandbox; each passing task is committed and tagged in git; failures go to a debugger that escalates from targeted fixes to wider context, then rolls back to the last good tag, and finally asks a human.

Q: What would you change for production?
Use interrupt() with a persistent checkpointer for human steps, persistent checkpoints by default, stronger sandbox isolation, parallel execution of independent tasks, tests as the source of truth over LLM review, and an evaluation suite measuring success rate, cost and human interventions.
:::
