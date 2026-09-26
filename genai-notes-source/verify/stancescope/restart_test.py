"""StanceScope graph with the real nodes; only evidence retrieval is faked
(no model download needed). Needs: pip install langgraph."""
import os, sys, tempfile, traceback
os.environ["STANCESCOPE_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
sys.path.insert(0, os.environ.get("STANCESCOPE_REPO", "../stancescope"))   # your repo clone
import app.graph as g
from app import db
from app.seed_evidence import SAMPLE_CLAIM, SAMPLE_POSTS
from langgraph.types import Command

class FakeRetriever:
    def retrieve(self, claim_text):
        return []
g.EvidenceRetriever = FakeRetriever

db.init_db()
claim_id, posts = db.create_claim(SAMPLE_CLAIM, SAMPLE_POSTS)

def start(graph):
    run_id = db.create_run(claim_id, "stub")
    cfg = {"configurable": {"thread_id": f"run-{run_id}"}}
    state = {"run_id": run_id, "claim_id": claim_id, "claim_text": SAMPLE_CLAIM,
             "evidence": [], "predictions": [], "low_confidence": [], "report": {}}
    out = graph.invoke(state, config=cfg)
    items = out["__interrupt__"][0].value["items"]
    print(f"run {run_id}: paused, review items = {[i['post_id'] for i in items]}")
    return cfg, items[0]["post_id"]

graph = g.build_graph()
cfg, pid = start(graph)                          # 1) normal resume
out = graph.invoke(Command(resume={str(pid): "neutral"}), config=cfg)
b = out["report"]["breakdown"]
print(f"  resumed OK -> support {b['support']['count']}, oppose {b['oppose']['count']}, "
      f"neutral {b['neutral']['count']} | human_reviewed {out['report']['human_reviewed_count']}")

cfg, pid = start(graph)                          # 2) integer keys
try:
    graph.invoke(Command(resume={pid: "neutral"}), config=cfg)
    print("  int keys: no error on this version")
except Exception as e:
    print(f"  int keys -> {type(e).__name__}")

cfg, pid = start(graph)                          # 3) server restart
graph2 = g.build_graph()                         # new process = new MemorySaver
try:
    out = graph2.invoke(Command(resume={str(pid): "neutral"}), config=cfg)
    print("  after restart -> returned:", {k: out.get(k) for k in ("report",)} if isinstance(out, dict) else out)
except Exception as e:
    print(f"  after restart -> {type(e).__name__}: {str(e)[:70]}")
