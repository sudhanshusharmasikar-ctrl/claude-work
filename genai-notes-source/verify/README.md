# Verification scripts

These scripts produced the outputs quoted in Chapters 17–21. They read your project code but never change it.
Clone the project repos next to this folder (or point the environment variables at your clones).

| Script | Book section | How to run |
|---|---|---|
| `paperrag/twocol_test.py` | 17.5 two-column bug | `PAPERRAG_REPO=../paperrag python3 paperrag/twocol_test.py` (needs `pymupdf`) |
| `schemamind/executor_test.py` | 18.6 executor + time limit | run from inside a SchemaMind clone after `python -m app.seed_db` |
| `schemamind/template_test.py` | 18.7 silent wrong answers | run from inside a SchemaMind clone after `python -m app.seed_db` |
| `schemamind/fixed_test.py` | 18.6 validator fix | `python3 fixed_test.py` (uses `validate_fixed.py`; needs `sqlglot`) |
| `stancescope/stub_test.py` | 19.5 stub classifier | `STANCESCOPE_REPO=../stancescope python3 stancescope/stub_test.py` |
| `stancescope/restart_test.py` | 19.5 restart + resume keys | same, plus `pip install langgraph` |
| `js/agent_improved.mjs` | 3.7 improved agent loop | `node js/agent_improved.mjs` (needs `@google/genai`, `dotenv`; the model call is mocked) |
| `js/scan_test.mjs` | 4.5 folder-scan bug + path jail | `cd js && node scan_test.mjs` |
| `js21/memory.mjs` | 21.8 cosine + RRF | `node js21/memory.mjs` |
| `cpp/similarity.cpp` | 6.4 cosine vs Euclidean | `g++ -O2 cpp/similarity.cpp -o sim && ./sim` |

To test the validator on another sqlglot version: `pip install --target sg_26 sqlglot==26.0.0`, then run with
`PYTHONPATH=sg_26`.
