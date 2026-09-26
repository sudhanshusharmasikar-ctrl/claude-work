"""Run the StanceScope stub classifier on the repo's own sample posts."""
import sys
import os
sys.path.insert(0, os.environ.get("STANCESCOPE_REPO", "../stancescope"))   # your repo clone
from app.classifier import StubClassifier
from app.seed_evidence import SAMPLE_POSTS
from app.config import CONFIDENCE_THRESHOLD

clf = StubClassifier()
for p in SAMPLE_POSTS:
    r = clf.classify(p["text"])
    flag = "  -> review" if r.confidence < CONFIDENCE_THRESHOLD else ""
    print(f"{r.stance:8} {r.confidence:.3f}  {p['text'][:52]}{flag}")
