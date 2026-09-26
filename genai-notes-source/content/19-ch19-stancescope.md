:::chapter 19 | Your Project: StanceScope | github.com/sudhanshusharmasikar-ctrl/stancescope · Lighter
- Your pitch — the **honest** version (the classifier is still a stub)
- The LangGraph workflow: four nodes and a **real** `interrupt()`
- Python LangGraph ↔ the JavaScript LangGraph you learned in Chapters 14–15
- Bugs found by running it — three from your README, three more tested for this book
- The model behind it: **BERT + ViT** in one page
- 18 interview questions
:::

StanceScope is your **supporting** project: it shows LangGraph with a real human-in-the-loop pause, and it connects to your MTech thesis. Spend about one day on this chapter (Day 29 in the plan). The golden rule: **never present the stub as a trained model**.

## 19.1 Your pitch %%MUST%%

:::pitch 30 seconds (honest version)
"StanceScope takes a claim — for example *'the telecom merger will be approved'* — and a set of social posts, and reports how many posts **support**, **oppose** or are **neutral**, with every number traceable to a post. It's a **LangGraph** workflow: retrieve news evidence for the claim, classify each post, **pause for human review** with a real LangGraph interrupt when the classifier isn't confident, then build the report. Every prediction is stored with its source — model or human — so any run can be audited. The classifier slot is built for my thesis **BERT + ViT** multimodal model; right now a keyword stub runs in that slot so the orchestration can be tested end to end."
:::

:::honest The one sentence that protects you
"The agent framework, human review, storage and API are real and tested; the stance classifier is currently a **placeholder**." If you skip this and the interviewer opens `classifier.py`, you lose the whole interview — not just this project.
:::

## 19.2 The workflow %%MUST%%

[[fig:stance-graph|StanceScope: a fixed four-node LangGraph workflow. The pause is a real interrupt(); the checkpoint lives in RAM.]]

| File | Job |
|---|---|
| `app/graph.py` | The four nodes, the interrupt, `MemorySaver` |
| `app/classifier.py` | The **seam**: `BaseClassifier` → `StubClassifier` today, `CheckpointClassifier` (BERT + ViT) later |
| `app/evidence.py` + `seed_evidence.py` | MiniLM search over 6 seeded news snippets |
| `app/db.py` | SQLite: claims, posts, runs, **per-post predictions** (with `source` = model or human) |
| `app/report.py` | Counts, percentages, human-reviewed count, evidence, per-post detail |
| `app/api.py` | `POST /claims`, `POST /claims/{id}/run`, `POST /runs/{id}/review`, `GET /runs/{id}`, `/health` |

It's a **workflow**, not an open-ended agent: the edges are fixed, and no LLM decides what happens next. That's a good thing to say — Chapter 5's rule is *use the simplest structure that works*.

## 19.3 The key code %%MUST%%

```python title="app/graph.py — the human review node"
def human_review_node(state: RunState) -> RunState:
    if not state["low_confidence"]:
        return state                          # nothing flagged: no pause at all

    review_decisions = interrupt({            # graph STOPS here; payload goes out
        "reason": "low_confidence_predictions",
        "items": state["low_confidence"],
    })
    # on resume, interrupt() RETURNS the human's answer: {"<post_id>": stance}
    for pred in state["predictions"]:
        key = str(pred["post_id"])            # keys must be strings (bug #2 below)
        if key in review_decisions:
            pred["stance"] = review_decisions[key]
            pred["confidence"] = 1.0
            pred["source"] = "human"
    return state
```

- On resume the node **starts again from its first line**, and this time `interrupt()` returns the decisions (Chapter 15). Here the code before `interrupt()` is only a cheap check, so re-running it is harmless.
- `pred["source"] = "human"` is what makes the report honest: `human_reviewed_count` and the per-post detail show **who** decided each label.

```python title="app/api.py — start a run, and resume it (condensed)"
def _thread_config(run_id):
    return {"configurable": {"thread_id": f"run-{run_id}"}}   # one thread per run

# POST /claims/{claim_id}/run
result = graph.invoke(state, config=_thread_config(run_id))
if "__interrupt__" in result:                  # paused: tell the client why
    payload = result["__interrupt__"][0].value
    db.set_run_status(run_id, "awaiting_review")
    return {"status": "awaiting_review", "review_items": payload["items"], ...}

# POST /runs/{run_id}/review
if run_row["status"] != "awaiting_review":
    raise HTTPException(400, "Run is not awaiting review ...")
decisions = {str(d.post_id): d.stance for d in review.decisions}
result = graph.invoke(Command(resume=decisions), config=_thread_config(run_id))
```

- Pydantic validates each decision: `stance` must match `^(support|oppose|neutral)$`.
- The status check stops someone from "resuming" a run that isn't paused.

```python title="app/classifier.py — the seam (condensed)"
class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, text, image_path=None) -> ClassificationResult: ...

def get_classifier() -> BaseClassifier:
    if CLASSIFIER_CHECKPOINT:                  # env var set → the real model
        return CheckpointClassifier(CLASSIFIER_CHECKPOINT)
    return StubClassifier()                    # keyword matching placeholder
```

The graph, API and UI only call `get_classifier()`. Plugging in the thesis model means implementing one class — nothing else changes. (Interview words: **interface**, **dependency inversion**, **seam**.)

## 19.4 Python LangGraph ↔ JavaScript LangGraph %%GOOD%%

Your course code is JavaScript; this project is Python. The ideas are identical:

| Idea | JavaScript (Ch 14–15) | Python (StanceScope) |
|---|---|---|
| State | `Annotation.Root({...})` | `class RunState(TypedDict)` |
| Build | `new StateGraph(State)` | `StateGraph(RunState)` |
| Nodes / edges | `.addNode()` / `.addEdge()` | `add_node()` / `add_edge()` |
| Entry | `.addEdge(START, "x")` | `set_entry_point("x")` |
| Checkpointer | `compile({ checkpointer: new MemorySaver() })` | `compile(checkpointer=MemorySaver())` |
| Pause | `interrupt(payload)` | `interrupt(payload)` |
| Resume | `invoke(new Command({ resume }), config)` | `invoke(Command(resume=...), config=...)` |
| Thread | `{ configurable: { thread_id } }` | `{"configurable": {"thread_id": ...}}` |

## 19.5 Bugs found by running it (tested) %%MUST%%

Your README lists three bugs found while building — keep them ready, "how did you find it?" is a favourite follow-up:

1. **"Deterministic" confidence wasn't deterministic.** The stub seeded its randomness with Python's `hash()`, which is **randomised per process** (a security feature). Same post, different confidence every run. Fix: `hashlib.md5` — stable across runs.
2. **Integer keys crashed the resume.** LangGraph inspects the keys of the `Command(resume=...)` dict and raises `TypeError` on integer keys. Fix: `str(post_id)`.
3. **A broken INSERT**: 5 columns but 4 placeholders (`:run_id` missing) — it only failed when the first real prediction was saved.

I re-ran the graph on LangGraph 1.2.12 (the real nodes; only the news search was swapped for a stub, since it needs the MiniLM download) — bug 2 is still real — and found one more serious issue:

```output title="python restart_test.py  (the repo's sample claim and 8 posts)"
run 1: paused, review items = [3]
  resumed OK -> support 4, oppose 3, neutral 1 | human_reviewed 1
run 2: paused, review items = [3]
  int keys -> TypeError
run 3: paused, review items = [3]
  after restart -> KeyError: 'claim_text'
```

**4. A server restart loses every paused run.** `MemorySaver` keeps checkpoints in **RAM**. Run 3 simulates a restart (a fresh graph = a fresh MemorySaver): the resume finds no saved state, the graph starts from the beginning with empty input, and crashes. Meanwhile the database still says `awaiting_review` — a run stuck forever. Fix: a **persistent** checkpointer — `SqliteSaver` (package `langgraph-checkpoint-sqlite`) or Postgres in production — and a test that restarts the server between pause and resume.

**5. The review only catches mistakes the model is unsure about.** The stub on the repo's own sample posts:

```output title="python stub_test.py  (StubClassifier, threshold 0.6)"
support  0.664  This merger will obviously get approved, both compan
oppose   0.607  No way this passes, regulators blocked the exact sam
oppose   0.583  Not sure what to think, could go either way honestly  -> review
support  0.840  I agree it will happen, rural coverage improvement i
support  0.607  Consumer groups are furious, prices will go up if th
oppose   0.830  Just here for the news, no opinion on this one.
oppose   0.812  This is definitely going to be denied, too much mark
support  0.684  Great news if it goes through, better coverage for e
```

"Not sure what to think" and "no opinion" are clearly **neutral**, but the stub says **oppose** — its keyword check is a plain substring test, so `"no"` matches inside **No**t. Only the first of those is sent to review (0.583); the other is accepted at **0.830**. The complaint about prices is labelled **support** because it contains "confirmed". The lesson is bigger than the stub: **routing by confidence is only as good as the confidence**. A real model's softmax scores must be **calibrated** before a threshold means anything (19.6).

**6. Models are built per request.** `get_classifier()` creates a new classifier on every call, and the evidence node re-embeds the whole corpus on every run. Harmless for a stub and 6 snippets; with a real BERT + ViT checkpoint it would **reload the weights on every request** — the same bug PaperRAG's `get_model()` comment warns about. Fix: build both once at startup (FastAPI lifespan) and reuse them.

## 19.6 The model behind it: BERT + ViT in one page %%GOOD%%

**Stance detection** = given a **target** (the claim) and a **text** (a post), predict whether the text **supports**, **opposes** or is **neutral** toward the target. A classic public benchmark is SemEval-2016 Task 6 (tweets: favour / against / none). **Multimodal** stance adds the post's **image** — memes and screenshots often carry the real opinion.

How a BERT + ViT classifier is usually built:

1. **Text**: BERT reads `[CLS] claim [SEP] post [SEP]`; the `[CLS]` output (768 numbers) summarises the pair.
2. **Image**: ViT cuts the image into small **patches** (e.g. 16 × 16 pixels), treats them like tokens, and its `[CLS]` output (768 numbers) summarises the image.
3. **Fusion**: join the two vectors — simplest is **concatenation** (1,536 numbers) → a small neural network → 3 scores → **softmax** → probabilities. (Richer: cross-attention between text and image tokens.)
4. **Training**: cross-entropy loss on labelled posts; report **macro-F1** (the average F1 over the three classes), because classes are usually imbalanced and accuracy hides a weak minority class.
5. **Confidence** = the highest softmax probability. Neural networks are often **over-confident**, so fit **temperature scaling** on a validation set and check with a **reliability diagram** (or ECE, expected calibration error). Then set the review threshold from data — for example, the lowest threshold where auto-accepted predictions are ≥ 95% correct, within your reviewers' budget.

:::honest Know your own thesis numbers
Interviewers **will** ask about your thesis model. Before interviews, write down from **your** thesis: the dataset (name, size, label balance), the fusion method you used, your macro-F1 with and without images, and one error you analysed. Also: your `stance-detection` repository currently contains **only a README** — push the training code and results, or don't link it.
:::

## 19.7 When we build %%GOOD%%

:::build StanceScope, in order (after PaperRAG and SchemaMind)
1. **Persistent checkpointer** (`SqliteSaver`) + a restart test between pause and resume.
2. **Load models once** at startup; implement `CheckpointClassifier` with the thesis checkpoint.
3. **Calibrate** on a labelled validation set; choose the threshold from data; report macro-F1, review rate and accuracy of auto-accepted predictions.
4. **Audit sampling**: also send a small random sample of **high-confidence** predictions to review, to measure errors the threshold can't see.
5. **Reviewer records**: who reviewed, when (the unused `reviewed` column and `apply_human_review()` in `db.py` are the start); authentication on the review endpoint.
6. **Evidence that matters**: today evidence is only attached to the report — it doesn't influence the stance. Use a real news source with dates, and show which snippet supports which side.
:::

## 19.8 Interview questions — StanceScope %%MUST%%

:::qa StanceScope
Q: What does StanceScope do, in one line?
It measures how a set of posts stands on a claim — support, oppose or neutral — with human review for uncertain cases and a report where every number traces back to a post.

Q: Is the classifier trained?
Not in this repo yet. The classifier slot is an interface; a keyword stub runs today so the workflow, human review, storage and API can be tested. The trained BERT + ViT model is from my thesis and plugs into that interface.

Q: Why LangGraph here?
Because the workflow must pause for a human and continue later. LangGraph gives an explicit graph, a checkpointer that saves state after every node, and interrupt/resume — I don't have to build pause-and-continue myself.

Q: Why a real interrupt and not just a "pending" flag in the database?
With a flag I'd have to rebuild the workflow's state myself when the review arrives. With interrupt, the framework saves the exact state and resumes at the same node with the human's answer — that's the feature's whole purpose.

Q: How does the interrupt work?
The node calls `interrupt(payload)`. LangGraph saves a checkpoint for the thread and invoke returns with `__interrupt__`. My API returns "awaiting_review" with the flagged posts. When the review arrives, I call invoke with Command(resume=decisions) and the same thread_id; the node runs again from its start and interrupt() now returns the decisions.

Q: What happens if the server restarts while a run is waiting?
I tested it: with MemorySaver the checkpoint is gone, the resume starts from scratch and fails with KeyError, and the database still says awaiting_review. The fix is a persistent checkpointer such as SqliteSaver or Postgres.

Q: Why is the thread_id "run-{id}"?
Each run is its own thread, so checkpoints of different runs never mix, and the review for run 7 resumes exactly run 7.

Q: Why must the resume keys be strings?
LangGraph inspects the keys of the resume dictionary, and integer keys raise a TypeError — I hit this and still see it on the current version. Post ids are converted with str().

Q: Why threshold 0.6?
It's a placeholder. The right value comes from calibration on labelled data: pick the threshold that keeps auto-accepted predictions accurate enough for the number of reviews people can do.

Q: What if the model is confidently wrong?
The threshold never sends it to review — the stub does exactly this with "no opinion" at 0.83. Fixes: calibrate the confidence, and review a small random sample of confident predictions to measure the hidden error rate.

Q: Why store every prediction instead of only the final percentages?
Traceability. "Why does the report say 40% oppose?" becomes a query. You can compare two runs, see which labels humans changed, and reuse human labels as training data.

Q: Is the retrieved evidence used by the classifier?
Honestly, no — it's attached to the report as context. The next step would be evidence-aware classification or showing which evidence supports which side.

Q: Why did hash() break the stub's determinism?
Python randomises string hashing per process to protect against hash-flooding attacks, so hash("same text") changes between runs. md5 gives a stable number.

Q: How would you scale to 100,000 posts?
Load the model once, classify in GPU batches in a background job, stream progress, store predictions in bulk, and give reviewers a prioritised queue instead of one giant pause.

Q: How would multiple reviewers work?
Store reviewer id and time per decision, give disagreements to a second reviewer or majority vote, and measure agreement between reviewers (for example Cohen's kappa).

Q: Is this an agent?
It's a workflow with a human-in-the-loop step: fixed edges, no model choosing the next step. That's deliberate — the task is predictable, so a workflow is simpler and easier to test than an autonomous agent.

Q: What is multimodal stance detection?
Deciding a post's stance toward a claim using both its text and its image. BERT encodes the claim and post, ViT encodes the image, the two vectors are fused and classified into support, oppose or neutral.

Q: What would you do differently?
Use a persistent checkpointer from day one, load models once at startup, and never use raw substring matching even in a stub. And test restarts, not just the happy path.
:::

:::remember StanceScope in numbers
**4 nodes**: retrieve_evidence → classify_posts → human_review → aggregate · evidence: **MiniLM**, **top-3** of **6** seeded snippets · review if confidence **< 0.6** (placeholder) · stub confidence 0.55–0.85 (neutral 0.50–0.70), keyword substring matching · `interrupt({reason, items})` → API **awaiting_review** → `Command(resume={"<post_id>": stance})` · thread **run-{id}** · **MemorySaver** (RAM — lost on restart) · SQLite: claims, posts, runs, predictions (**source = model or human**) · 3 README bugs + restart, confidence-routing and per-request loading issues.
:::
