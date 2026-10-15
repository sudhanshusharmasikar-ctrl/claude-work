# What was checked, and how to check it again

The guide's solutions were tested against
[dexterhere04/accenture-frontend-practice](https://github.com/dexterhere04/accenture-frontend-practice)
at commit `9927254` (23 September 2026).

| Folder / script | What it holds | Result |
|---|---|---|
| `exercises/NN-*/` | the finished files of the 14 exercises in the guide, exactly as the guide shows them | — |
| `run.sh` | copies those files into a temporary copy of the practice repo and runs its Playwright tests | **57 passed** (14 exercises) |
| `../tools/check_snippets.py` | checks that every solution block in the guide (titled `NN/file`) appears in these files, and that every `solution/... (part)` excerpt appears in the repo's own solutions | **34 blocks, 0 mismatches** |
| `examples/*.js` | the small examples whose output is printed in the guide | run with `node examples/<file>.js` |

The repository's own reference solutions were also run (`npm run test:solutions`): **77 passed**.

```bash
verify/run.sh                       # clones the practice repo into a temp folder, then grades
verify/run.sh ~/accenture-frontend-practice   # or use your clone (it is copied, never changed)
python3 tools/check_snippets.py ~/accenture-frontend-practice
```

Set `PW_CHROMIUM=/path/to/chrome` to use an already-installed Chromium instead of Playwright's download.
