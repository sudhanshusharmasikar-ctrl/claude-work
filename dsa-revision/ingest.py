#!/usr/bin/env python3
"""Turn a pasted problem list into dsa-revision/problems.json.

Input is a plain text file with section headers. Anything under a header is
taken to belong to that platform and bookmark state:

    # leetcode bookmarked
    https://leetcode.com/problems/two-sum/
    Longest Substring Without Repeating Characters | medium | sliding-window

    # leetcode solved
    ...

    # gfg bookmarked
    https://www.geeksforgeeks.org/problems/kadanes-algorithm-1587115620/1
    ...

Per line, these forms all work:
    <url>
    <title>
    <title> | <difficulty>
    <title> | <difficulty> | <topic, topic, ...>
A line may also start with * or [b] to mark it bookmarked inside a solved
section, so one flat list works if that is easier to paste.

Usage:
    python3 ingest.py lists/my-list.txt [-o problems.json] [--merge]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

DIFFICULTIES = {
    "easy": "easy",
    "medium": "medium",
    "med": "medium",
    "hard": "hard",
    "basic": "easy",
    "school": "easy",
}

HEADER_RE = re.compile(r"^#+\s*(.+?)\s*$")
BOOKMARK_PREFIX_RE = re.compile(r"^\s*(\*|\[b\]|\[bm\]|\[fav\])\s*", re.IGNORECASE)
LEADING_INDEX_RE = re.compile(r"^\s*\d+\s*[.)]\s+")


def platform_of_url(url: str) -> str | None:
    if "leetcode.com" in url:
        return "leetcode"
    if "geeksforgeeks.org" in url:
        return "gfg"
    return None


def title_from_url(url: str, platform: str) -> str:
    path = url.split("?")[0].rstrip("/")
    slug = path.rsplit("/", 1)[-1]
    if platform == "gfg":
        # GFG slugs often end in a numeric id and a trailing /1
        if slug.isdigit():
            slug = path.rsplit("/", 2)[-2]
        slug = re.sub(r"-\d{6,}$", "", slug)
    return slug.replace("-", " ").replace("_", " ").strip().title()


def slug_from_url(url: str, platform: str) -> str:
    path = url.split("?")[0].rstrip("/")
    slug = path.rsplit("/", 1)[-1]
    if platform == "gfg" and slug.isdigit():
        slug = path.rsplit("/", 2)[-2]
    return slug


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def canonical_url(platform: str, slug: str) -> str:
    if platform == "leetcode":
        return f"https://leetcode.com/problems/{slug}/"
    return f"https://www.geeksforgeeks.org/problems/{slug}/1"


def parse_header(text: str) -> tuple[str | None, bool | None]:
    low = text.lower()
    platform = None
    if "leetcode" in low or re.search(r"\blc\b", low):
        platform = "leetcode"
    elif "gfg" in low or "geeksforgeeks" in low or "geeks" in low:
        platform = "gfg"
    bookmarked = None
    if any(w in low for w in ("bookmark", "favourite", "favorite", "fav", "starred", "saved", "revise")):
        bookmarked = True
    elif any(w in low for w in ("solved", "done", "attempted", "all")):
        bookmarked = False
    return platform, bookmarked


def parse_line(line: str, platform: str | None, bookmarked: bool) -> dict | None:
    line = LEADING_INDEX_RE.sub("", line.strip())
    if not line:
        return None

    m = BOOKMARK_PREFIX_RE.match(line)
    if m:
        bookmarked = True
        line = line[m.end():]

    parts = [p.strip() for p in line.split("|")]
    head = parts[0]

    url = None
    url_match = re.search(r"https?://\S+", head)
    if url_match:
        url = url_match.group(0).rstrip(").,")
        detected = platform_of_url(url)
        if detected:
            platform = detected
        label = head[: url_match.start()].strip(" -–\t")
        title = label or (title_from_url(url, platform or "leetcode"))
        slug = slug_from_url(url, platform or "leetcode")
    else:
        title = head
        slug = slugify(title)

    if not platform:
        return None
    if not title:
        return None

    difficulty = None
    topics: list[str] = []
    if len(parts) > 1 and parts[1]:
        difficulty = DIFFICULTIES.get(parts[1].lower())
        if difficulty is None and parts[1]:
            topics.extend(t.strip() for t in parts[1].split(",") if t.strip())
    if len(parts) > 2 and parts[2]:
        topics.extend(t.strip() for t in parts[2].split(",") if t.strip())

    return {
        "platform": platform,
        "slug": slug,
        "title": title,
        "url": url or canonical_url(platform, slug),
        "difficulty": difficulty,
        "topics": sorted({t.lower() for t in topics}),
        "bookmarked": bookmarked,
    }


def parse_text(text: str) -> tuple[list[dict], list[str]]:
    problems: dict[tuple[str, str], dict] = {}
    warnings: list[str] = []
    platform: str | None = None
    bookmarked = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped:
            continue
        header = HEADER_RE.match(stripped)
        if header:
            p, b = parse_header(header.group(1))
            if p:
                platform = p
            if b is not None:
                bookmarked = b
            continue

        entry = parse_line(stripped, platform, bookmarked)
        if entry is None:
            warnings.append(f"line {lineno}: could not tell which platform — skipped: {stripped[:70]}")
            continue

        key = (entry["platform"], entry["slug"])
        if key in problems:
            # A problem listed in both the solved and bookmarked sections is bookmarked.
            existing = problems[key]
            existing["bookmarked"] = existing["bookmarked"] or entry["bookmarked"]
            existing["difficulty"] = existing["difficulty"] or entry["difficulty"]
            existing["topics"] = sorted(set(existing["topics"]) | set(entry["topics"]))
        else:
            problems[key] = entry

    return list(problems.values()), warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="text file with your pasted lists ('-' for stdin)")
    ap.add_argument("-o", "--output", default=str(HERE / "problems.json"))
    ap.add_argument("--merge", action="store_true", help="merge into the existing problems.json instead of replacing it")
    args = ap.parse_args()

    text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    problems, warnings = parse_text(text)

    out_path = Path(args.output)
    if args.merge and out_path.exists():
        old = json.loads(out_path.read_text(encoding="utf-8"))
        merged = {(p["platform"], p["slug"]): p for p in old.get("problems", old if isinstance(old, list) else [])}
        for p in problems:
            key = (p["platform"], p["slug"])
            if key in merged:
                merged[key]["bookmarked"] = merged[key]["bookmarked"] or p["bookmarked"]
                merged[key]["difficulty"] = merged[key]["difficulty"] or p["difficulty"]
                merged[key]["topics"] = sorted(set(merged[key]["topics"]) | set(p["topics"]))
            else:
                merged[key] = p
        problems = list(merged.values())

    problems.sort(key=lambda p: (p["platform"], p["title"].lower()))
    out_path.write_text(json.dumps({"problems": problems}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    def count(platform: str, bookmarked: bool | None = None) -> int:
        return sum(
            1
            for p in problems
            if p["platform"] == platform and (bookmarked is None or p["bookmarked"] == bookmarked)
        )

    print(f"wrote {out_path} — {len(problems)} problems")
    for platform in ("leetcode", "gfg"):
        print(f"  {platform:9s} {count(platform):4d} total, {count(platform, True):4d} bookmarked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
