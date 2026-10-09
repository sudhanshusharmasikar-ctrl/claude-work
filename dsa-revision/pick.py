#!/usr/bin/env python3
"""Pick the day's revision set from problems you have already solved.

Default shape: 12 problems — 9 LeetCode + 3 GFG, of which 7 are bookmarked
(5 LeetCode + 2 GFG) and 5 are not. Picks are seeded by the date, so asking
twice on the same day gives the same set; a cooldown keeps a problem from
coming back until the pool has cycled, so this behaves like spaced revision
rather than a lottery.

Usage:
    python3 pick.py                      # today's set
    python3 pick.py --date 2026-10-12    # a specific day's set
    python3 pick.py --reroll             # new set for today, replacing it
    python3 pick.py --dry-run            # show a set without recording it
    python3 pick.py --stats              # pool and coverage summary
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBLEMS_PATH = HERE / "problems.json"
HISTORY_PATH = HERE / "history.json"

PLATFORM_LABEL = {"leetcode": "LeetCode", "gfg": "GFG"}
DIFF_ORDER = {"easy": 0, "medium": 1, "hard": 2, None: 3}


def load_problems(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(
            f"no problem list at {path}\n"
            "Paste your solved + bookmarked lists into a text file and run:\n"
            "    python3 ingest.py lists/my-list.txt"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = data["problems"] if isinstance(data, dict) else data
    if not problems:
        sys.exit(f"{path} has no problems in it")
    for p in problems:
        p.setdefault("difficulty", None)
        p.setdefault("topics", [])
        p.setdefault("bookmarked", False)
    return problems


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"sets": {}, "last_shown": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("sets", {})
    data.setdefault("last_shown", {})
    return data


def key_of(p: dict) -> str:
    return f"{p['platform']}:{p['slug']}"


def days_since(last: str | None, today: dt.date) -> float:
    if not last:
        return float("inf")
    try:
        return (today - dt.date.fromisoformat(last)).days
    except ValueError:
        return float("inf")


def pick_bucket(pool: list[dict], n: int, rng: random.Random, history: dict, today: dt.date, cooldown: int) -> list[dict]:
    """Pick n problems, preferring ones not seen for longest; recent ones last."""
    if n <= 0 or not pool:
        return []

    scored = []
    for p in pool:
        gap = days_since(history["last_shown"].get(key_of(p)), today)
        scored.append((gap, rng.random(), p))

    fresh = [t for t in scored if t[0] == float("inf")]
    due = [t for t in scored if cooldown <= t[0] < float("inf")]
    recent = [t for t in scored if t[0] < cooldown]

    rng.shuffle(fresh)
    due.sort(key=lambda t: (-t[0], t[1]))
    recent.sort(key=lambda t: (-t[0], t[1]))

    ordered = [t[2] for t in fresh] + [t[2] for t in due] + [t[2] for t in recent]
    return ordered[:n]


def plan_quotas(lc_n: int, gfg_n: int, bm_total: int) -> dict[tuple[str, bool], int]:
    total = lc_n + gfg_n
    if bm_total > total:
        sys.exit(f"--bookmarked {bm_total} exceeds the {total} problems in a set")

    gfg_bm = round(bm_total * gfg_n / total) if total else 0
    gfg_bm = max(gfg_bm, bm_total - lc_n)          # LeetCode cannot absorb more than its own slots
    gfg_bm = min(gfg_bm, gfg_n, bm_total)
    lc_bm = bm_total - gfg_bm

    return {
        ("leetcode", True): lc_bm,
        ("leetcode", False): lc_n - lc_bm,
        ("gfg", True): gfg_bm,
        ("gfg", False): gfg_n - gfg_bm,
    }


def repair_quotas(quotas: dict[tuple[str, bool], int], pools: dict[tuple[str, bool], list[dict]]) -> list[str]:
    """Adjust quotas to what the pools can actually supply, keeping per-platform totals."""
    notes: list[str] = []

    # Within a platform, move unmet demand to the other bookmark state.
    for platform in ("leetcode", "gfg"):
        for want_bm in (True, False):
            key = (platform, want_bm)
            short = quotas[key] - len(pools[key])
            if short <= 0:
                continue
            other = (platform, not want_bm)
            spare = len(pools[other]) - quotas[other]
            moved = min(short, max(0, spare))
            quotas[key] -= short
            quotas[other] += moved
            if moved:
                kind = "bookmarked" if want_bm else "non-bookmarked"
                have = len(pools[key])
                notes.append(
                    f"{PLATFORM_LABEL[platform]} has only {have} {kind} "
                    f"problem{'' if have == 1 else 's'} to draw on, so {moved} "
                    f"slot{'' if moved == 1 else 's'} came from its other group"
                )

    return notes


def select(problems: list[dict], date: dt.date, lc_n: int, gfg_n: int, bm_total: int, cooldown: int, history: dict, salt: str) -> tuple[list[dict], list[str]]:
    pools = {
        (platform, bm): [p for p in problems if p["platform"] == platform and bool(p["bookmarked"]) is bm]
        for platform in ("leetcode", "gfg")
        for bm in (True, False)
    }

    quotas = plan_quotas(lc_n, gfg_n, bm_total)
    notes = repair_quotas(quotas, pools)

    # If one platform cannot supply its bookmark share, try the other platform for the shortfall.
    got_bm = quotas[("leetcode", True)] + quotas[("gfg", True)]
    if got_bm < bm_total:
        for platform in ("leetcode", "gfg"):
            if got_bm >= bm_total:
                break
            spare = len(pools[(platform, True)]) - quotas[(platform, True)]
            room = quotas[(platform, False)]
            move = min(bm_total - got_bm, max(0, spare), room)
            if move:
                quotas[(platform, True)] += move
                quotas[(platform, False)] -= move
                got_bm += move
        if got_bm < bm_total:
            notes.append(
                f"only {got_bm} of the {bm_total} requested bookmarked problems were available — "
                "the rest of the set is made up from your other solved problems"
            )

    picked: list[dict] = []
    for platform in ("leetcode", "gfg"):
        for bm in (True, False):
            key = (platform, bm)
            rng = random.Random(f"{date.isoformat()}|{platform}|{bm}|{salt}")
            picked.extend(pick_bucket(pools[key], quotas[key], rng, history, date, cooldown))

    wanted = lc_n + gfg_n
    if len(picked) < wanted:
        notes.append(f"your list holds only {len(picked)} usable problems for a set of {wanted}")

    order = random.Random(f"{date.isoformat()}|order|{salt}")
    order.shuffle(picked)
    picked.sort(key=lambda p: (p["platform"] != "leetcode", DIFF_ORDER.get(p["difficulty"], 3)))
    return picked, notes


def render(picked: list[dict], date: dt.date, prev_seen: dict[str, str | None], fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"date": date.isoformat(), "problems": picked}, indent=2, ensure_ascii=False)

    bm_count = sum(1 for p in picked if p["bookmarked"])
    lines = [f"## Revision set — {date.isoformat()}", ""]
    lines.append(
        f"{len(picked)} problems · {sum(1 for p in picked if p['platform'] == 'leetcode')} LeetCode · "
        f"{sum(1 for p in picked if p['platform'] == 'gfg')} GFG · {bm_count} bookmarked"
    )
    lines.append("")

    for i, p in enumerate(picked, 1):
        star = "★" if p["bookmarked"] else "·"
        diff = (p["difficulty"] or "?").capitalize()
        gap = days_since(prev_seen.get(key_of(p)), date)
        seen = "first time" if gap == float("inf") else f"{int(gap)}d ago"
        topics = f" — {', '.join(p['topics'])}" if p["topics"] else ""
        lines.append(
            f"{i:2d}. {star} [{PLATFORM_LABEL[p['platform']]}] {p['title']}  ({diff}, last seen {seen}){topics}"
        )
        lines.append(f"       {p['url']}")

    lines.append("")
    lines.append("★ = bookmarked/favourite")
    return "\n".join(lines)


def show_stats(problems: list[dict], history: dict, today: dt.date) -> None:
    print(f"{len(problems)} problems in the list")
    for platform in ("leetcode", "gfg"):
        sub = [p for p in problems if p["platform"] == platform]
        bm = [p for p in sub if p["bookmarked"]]
        print(f"  {PLATFORM_LABEL[platform]:9s} {len(sub):4d} total, {len(bm):4d} bookmarked")
        for d in ("easy", "medium", "hard", None):
            n = sum(1 for p in sub if p["difficulty"] == d)
            if n:
                print(f"    {str(d or 'unlabelled'):11s} {n:4d}")
    shown = len(history["last_shown"])
    print(f"\n{shown} of {len(problems)} problems have come up at least once ({len(history['sets'])} sets recorded)")
    never = [p for p in problems if key_of(p) not in history["last_shown"]]
    if never:
        print(f"{len(never)} never shown yet")
    if history["sets"]:
        last = max(history["sets"])
        print(f"last set: {last} ({days_since(last, today):.0f} days ago)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--leetcode", type=int, default=9, dest="lc_n")
    ap.add_argument("--gfg", type=int, default=3, dest="gfg_n")
    ap.add_argument("--bookmarked", type=int, default=7, help="how many of the set must be bookmarked")
    ap.add_argument("--cooldown", type=int, default=21, help="days before a problem may repeat")
    ap.add_argument("--reroll", action="store_true", help="replace today's recorded set with a new one")
    ap.add_argument("--dry-run", action="store_true", help="print a set without recording it")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--stats", action="store_true", help="print pool/coverage stats and exit")
    ap.add_argument("--problems", default=str(PROBLEMS_PATH))
    ap.add_argument("--history", default=str(HISTORY_PATH))
    args = ap.parse_args()

    problems = load_problems(Path(args.problems))
    history_path = Path(args.history)
    history = load_history(history_path)
    date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()

    if args.stats:
        show_stats(problems, history, date)
        return 0

    by_key = {key_of(p): p for p in problems}
    recorded = history["sets"].get(date.isoformat())
    prev_seen = {k: v for k, v in history["last_shown"].items()}

    if recorded and not args.reroll:
        picked = [by_key[k] for k in recorded if k in by_key]
        notes = ["showing the set already recorded for this date (use --reroll for a different one)"]
    else:
        if args.reroll:
            rerolls = history.setdefault("rerolls", {})
            rerolls[date.isoformat()] = rerolls.get(date.isoformat(), 0) + 1
            salt = f"reroll{rerolls[date.isoformat()]}"
        else:
            salt = ""
        picked, notes = select(problems, date, args.lc_n, args.gfg_n, args.bookmarked, args.cooldown, history, salt)
        if not args.dry_run:
            history["sets"][date.isoformat()] = [key_of(p) for p in picked]
            for p in picked:
                history["last_shown"][key_of(p)] = date.isoformat()
            history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(render(picked, date, prev_seen, args.format))
    for n in notes:
        print(f"\nnote: {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
