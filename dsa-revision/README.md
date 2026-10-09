# Daily DSA revision set

Picks **12 problems a day from problems you have already solved** — 9 LeetCode + 3 GFG,
of which **7 are ones you bookmarked/favourited** (5 LeetCode + 2 GFG) and 5 are not.

Picks are seeded by the date, so asking twice on the same day gives the same set, and a
cooldown keeps a problem from coming back until the pool has cycled. It is spaced revision,
not a lottery.

## Why you paste the lists instead of me fetching them

- **Bookmarks are private.** LeetCode favourites and GFG saved problems sit behind your
  login. There is no public API for them, and handing a session cookie to a cloud container
  is not worth the risk. (LeetCode *can* make a favourite list public, which would be
  readable without credentials — GFG has no equivalent.)
- **LeetCode's public API has no full solved list** either — only totals and your last ~20
  accepted submissions.
- This environment's network policy currently denies `leetcode.com` and `geeksforgeeks.org`
  outright, so even public data is unreachable from here.

So: you export once, this repo keeps the data, and nothing needs network access again.

## 1. Paste your lists

Put them in a text file under `lists/` using section headers. See
[`lists/example-input.txt`](lists/example-input.txt) for a full worked example.

```
# leetcode bookmarked
https://leetcode.com/problems/trapping-rain-water/ | hard | two-pointers, stack
Median of Two Sorted Arrays | hard | binary-search

# leetcode solved
Two Sum | easy | hashing
Group Anagrams | medium | hashing

# gfg bookmarked
https://www.geeksforgeeks.org/problems/kadanes-algorithm-1587115620/1 | medium | dp

# gfg solved
Job Sequencing Problem | medium | greedy
```

Each line can be a bare URL, a bare title, `title | difficulty`, or
`title | difficulty | topics`. Difficulty and topics are optional — they only improve the
output. A line starting with `*` is treated as bookmarked even inside a `solved` section,
so one flat list per platform works too. A problem listed in both sections counts as
bookmarked.

Fastest way to get the raw titles: on LeetCode open a favourite list and copy the problem
names; on GFG your profile's solved-problems section lists them.

## 2. Build the data file

```bash
python3 ingest.py lists/my-list.txt          # writes problems.json
python3 ingest.py lists/more.txt --merge     # add to what is already there
```

## 3. Get the day's set

```bash
python3 pick.py                  # today's 12
python3 pick.py --reroll         # swap today's set for a different one
python3 pick.py --dry-run        # preview without recording it
python3 pick.py --stats          # pool size, difficulty split, coverage
python3 pick.py --date 2026-10-12
```

Shape and spacing are adjustable:

```bash
python3 pick.py --leetcode 7 --gfg 3 --bookmarked 6 --cooldown 30
```

## Files

| File | What it is |
|---|---|
| `ingest.py` | turns a pasted list into `problems.json` |
| `pick.py` | picks and records the day's set |
| `problems.json` | your problems (created by `ingest.py`) |
| `history.json` | which problems came up on which day (created by `pick.py`) |
| `lists/` | the raw text you pasted |

**Commit `problems.json` and `history.json`.** Cloud sessions run in a throwaway container —
if the history is not in git, the rotation restarts from scratch every time.
