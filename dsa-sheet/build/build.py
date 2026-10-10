import re, json, sys, collections
sys.path.insert(0, sys.argv[1])
import pasted as P, meta as M

def slugify(t):
    s = t.lower().replace("`", "")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return re.sub(r"-+", "-", s)

TOPICS = ['Arrays & Hashing', 'Two Pointers', 'Sliding Window', 'Strings', 'Matrix', 'Intervals', 'Stack & Queue',
          'Binary Search', 'Linked List', 'Recursion & Backtracking', 'Binary Trees', 'Binary Search Trees', 'Heap',
          'Greedy', 'Graphs', 'Dynamic Programming', 'Design', 'Maths & Bits']

P_ = {}  # slug -> dict(num, title, diff, premium)
def put(slug, num=None, title=None, diff=None, premium=False, strong=False):
    d = P_.setdefault(slug, {})
    for k, v in (('num', num), ('title', title), ('diff', diff)):
        if v is not None and (strong or k not in d): d[k] = v
    if premium: d['premium'] = True

for ln in M.META.strip().splitlines():
    n, t, d = ln.split('|'); put(slugify(t), int(n), t, d)

src = collections.defaultdict(set)
topic_nc, topic_t150, topic_fraz = {}, {}, {}

for ln in P.STRIVER.splitlines():
    n, t, d = ln.split('|'); s = slugify(t); put(s, int(n), t, d, strong=True); src[s].add('Striver')
for ln in P.FAVS.splitlines():
    n, t, d = ln.split('|'); s = slugify(t); put(s, int(n), t, d, strong=True); src[s].add('Favourite')
cat = None
for ln in P.NEETCODE.splitlines():
    if ln.startswith('#'): cat = ln[1:]; continue
    parts = ln.split('|'); n, t, d = parts[:3]; s = slugify(t)
    put(s, int(n), t, d, premium=len(parts) > 3, strong=True); src[s].add('NeetCode'); topic_nc[s] = cat
cat = None
for ln in P.TOP150.splitlines():
    if ln.startswith('#'): cat = ln[1:]; continue
    t, d = ln.split('|'); s = slugify(t); put(s, title=t, diff=d, strong=True); src[s].add('Top 150'); topic_t150[s] = cat

# Fraz: parse the PDF text again, with sections fixed
fraz = open(sys.argv[1] + '/fraz.txt').read().splitlines()
sec = lvl = None
for raw in fraz:
    s0 = raw.strip()
    if not s0: continue
    head = re.split(r'\s{2,}', s0)[0]
    if 'http' not in s0 and re.fullmatch(r'[A-Za-z][A-Za-z &/\-()]{2,40}', head):
        h = head.upper().replace(' ', '')
        if h in ('EASY', 'MEDIUM', 'HARD', 'MEDIUM/HARD'): lvl = h
        elif not head.startswith('THAT'): sec = head.upper(); lvl = None
        continue
    m = re.search(r'https://leetcode\.com/problems/([a-z0-9\-]+)/?(\S*)', s0)
    if not m or m.group(2).startswith('discuss'): continue   # skip article links
    slug = M.RENAMED.get(m.group(1), m.group(1))
    src[slug].add('Fraz'); topic_fraz.setdefault(slug, sec)
    if lvl in ('EASY', 'MEDIUM', 'HARD'): put(slug, diff=lvl[0])

gfg_note = {}
for ln in M.GFG.splitlines():
    s, g = ln.split('|'); src[s].add('GFG'); gfg_note[s] = g

NC = {'Arrays & Hashing': 'Arrays & Hashing', 'Two Pointers': 'Two Pointers', 'Sliding Window': 'Sliding Window', 'Stack': 'Stack & Queue',
      'Binary Search': 'Binary Search', 'Linked List': 'Linked List', 'Trees': 'Binary Trees', 'Heap / Priority Queue': 'Heap',
      'Backtracking': 'Recursion & Backtracking', 'Graphs': 'Graphs', 'Advanced Graphs': 'Graphs', '1-D Dynamic Programming': 'Dynamic Programming',
      '2-D Dynamic Programming': 'Dynamic Programming', 'Greedy': 'Greedy', 'Intervals': 'Intervals', 'Math & Geometry': 'Maths & Bits',
      'Bit Manipulation': 'Maths & Bits', 'Tries': 'Trie'}
T1 = {'Array / String': 'Arrays & Hashing', 'Two Pointers': 'Two Pointers', 'Sliding Window': 'Sliding Window', 'Matrix': 'Matrix',
      'Hashmap': 'Arrays & Hashing', 'Intervals': 'Intervals', 'Stack': 'Stack & Queue', 'Linked List': 'Linked List',
      'Binary Tree General': 'Binary Trees', 'Binary Tree BFS': 'Binary Trees', 'Binary Search Tree': 'Binary Search Trees',
      'Graph General': 'Graphs', 'Graph BFS': 'Graphs', 'Trie': 'Trie', 'Backtracking': 'Recursion & Backtracking',
      'Divide & Conquer': 'Recursion & Backtracking', "Kadane's Algorithm": 'Arrays & Hashing', 'Binary Search': 'Binary Search',
      'Heap': 'Heap', 'Bit Manipulation': 'Maths & Bits', 'Math': 'Maths & Bits', '1D DP': 'Dynamic Programming',
      'Multidimensional DP': 'Dynamic Programming'}
FZ = {'ARRAYS': 'Arrays & Hashing', 'RECURSION': 'Recursion & Backtracking', 'DYNAMIC PROGRAMING': 'Dynamic Programming', 'STRINGS': 'Strings',
      'MATHS': 'Maths & Bits', 'GREEDY': 'Greedy', 'DFS': 'Graphs', 'TREE': 'Binary Trees', 'HASH TABLE': 'Arrays & Hashing',
      'BINARY SEARCH': 'Binary Search', 'BFS': 'Graphs', 'TWO POINTER': 'Two Pointers', 'STACK': 'Stack & Queue', 'DESIGN': 'Design',
      'GRAPH': 'Graphs', 'LINKED LIST': 'Linked List', 'HEAP': 'Heap', 'SLIDING WINDOW': 'Sliding Window', 'BIT MANIPULATION': 'Maths & Bits'}

def group(topic, slugs): return {s: topic for s in slugs.split()}
OVERRIDE = {}
OVERRIDE.update(group('Binary Search Trees', 'validate-binary-search-tree kth-smallest-element-in-a-bst lowest-common-ancestor-of-a-binary-search-tree convert-sorted-array-to-binary-search-tree binary-search-tree-iterator minimum-absolute-difference-in-bst search-in-a-binary-search-tree two-sum-iv-input-is-a-bst construct-binary-search-tree-from-preorder-traversal maximum-sum-bst-in-binary-tree recover-binary-search-tree unique-binary-search-trees-ii range-sum-of-bst'))
OVERRIDE.update(group('Strings', 'roman-to-integer integer-to-roman length-of-last-word longest-common-prefix reverse-words-in-a-string zigzag-conversion find-the-index-of-the-first-occurrence-in-a-string text-justification string-to-integer-atoi multiply-strings integer-to-english-words count-and-say compare-version-numbers repeated-string-match determine-if-two-strings-are-close sort-vowels-in-a-string sorting-the-sentence longest-palindrome largest-number rotate-string first-unique-character-in-a-string'))
OVERRIDE.update(group('Arrays & Hashing', 'maximum-subarray find-the-duplicate-number continuous-subarray-sum set-mismatch majority-element-ii max-consecutive-ones reverse-pairs non-decreasing-array rabbits-in-forest minimum-number-of-chairs-in-a-waiting-room corporate-flight-bookings find-the-first-player-to-win-k-games-in-a-row remove-letter-to-equalize-frequency path-crossing contiguous-array replace-elements-with-greatest-element-on-right-side minimum-difference-between-highest-and-lowest-of-k-scores sort-an-array relative-sort-array sort-array-by-increasing-frequency check-if-array-pairs-are-divisible-by-k'))
OVERRIDE.update(group('Matrix', 'rotate-image spiral-matrix set-matrix-zeroes game-of-life valid-sudoku range-sum-query-2d-immutable delete-greatest-value-in-each-row'))
OVERRIDE.update(group('Design', 'lru-cache lfu-cache design-twitter design-hashmap design-hashset insert-delete-getrandom-o1 insert-delete-getrandom-o1-duplicates-allowed encode-and-decode-tinyurl design-browser-history design-underground-system tweet-counts-per-frequency all-oone-data-structure'))
OVERRIDE.update(group('Heap', 'find-median-from-data-stream kth-largest-element-in-a-stream the-number-of-the-smallest-unoccupied-chair'))
OVERRIDE.update(group('Linked List', 'sort-list merge-k-sorted-lists swap-nodes-in-pairs add-two-numbers-ii flatten-a-multilevel-doubly-linked-list'))
OVERRIDE.update(group('Recursion & Backtracking', 'construct-quad-tree remove-invalid-parentheses 24-game sudoku-solver matchsticks-to-square find-the-winner-of-the-circular-game restore-ip-addresses'))
OVERRIDE.update(group('Dynamic Programming', 'house-robber-iii remove-boxes concatenated-words unique-binary-search-trees number-of-great-partitions palindrome-partitioning-ii predict-the-winner maximum-length-of-pair-chain best-team-with-no-conflicts maximum-height-by-stacking-cuboids minimum-falling-path-sum last-stone-weight-ii ones-and-zeroes'))
OVERRIDE.update(group('Stack & Queue', 'decode-string maximal-rectangle longest-valid-parentheses basic-calculator-ii minimum-add-to-make-parentheses-valid remove-outermost-parentheses 132-pattern beautiful-towers-i validate-stack-sequences next-greater-element-ii remove-all-adjacent-duplicates-in-string'))
OVERRIDE.update(group('Graphs', 'flood-fill redundant-connection-ii number-of-ways-to-reconstruct-a-tree sum-of-distances-in-tree number-of-enclaves count-sub-islands shortest-path-in-binary-matrix find-if-path-exists-in-graph'))
OVERRIDE.update(group('Binary Trees', 'binary-tree-preorder-traversal binary-tree-postorder-traversal path-sum-ii amount-of-time-for-binary-tree-to-be-infected'))
OVERRIDE.update(group('Greedy', 'maximum-number-of-non-overlapping-substrings separate-black-and-white-balls maximum-bags-with-full-capacity-of-rocks maximum-ice-cream-bars smallest-range-ii broken-calculator'))
OVERRIDE.update(group('Sliding Window', 'find-all-anagrams-in-a-string count-subarrays-where-max-element-appears-at-least-k-times longest-subarray-of-1s-after-deleting-one-element binary-subarrays-with-sum subarrays-with-k-different-integers'))
OVERRIDE.update(group('Two Pointers', 'longest-mountain-in-array'))
OVERRIDE.update(group('Binary Search', 'maximum-tastiness-of-candy-basket partition-array-into-two-arrays-to-minimize-sum-difference find-in-mountain-array single-element-in-a-sorted-array magnetic-force-between-two-balls'))
OVERRIDE.update(group('Intervals', 'divide-intervals-into-minimum-number-of-groups'))
OVERRIDE.update(group('Maths & Bits', 'hamming-distance divisor-game'))
OVERRIDE['shortest-common-supersequence'] = 'Dynamic Programming'

rows, excluded, missing = [], [], []
for s, srcs in src.items():
    if s in M.EXCLUDE or topic_nc.get(s) == 'Tries' or topic_t150.get(s) == 'Trie':
        excluded.append((s, M.EXCLUDE.get(s, 'Trie'), sorted(srcs))); continue
    d = P_.get(s, {})
    if not all(k in d for k in ('num', 'title', 'diff')): missing.append(s); continue
    t = OVERRIDE.get(s) or NC.get(topic_nc.get(s)) or T1.get(topic_t150.get(s)) or FZ.get(topic_fraz.get(s))
    if not t: missing.append('TOPIC:' + s); continue
    order = ['Striver', 'Top 150', 'NeetCode', 'Fraz', 'GFG', 'Favourite']
    rows.append({'n': d['num'], 't': d['title'], 's': s, 'd': d['diff'], 'topic': t, 'src': [x for x in order if x in srcs],
                 **({'p': 1} if d.get('premium') else {}), **({'g': gfg_note[s]} if s in gfg_note else {}),
                 **({'alt': M.PREMIUM_ALT[s]} if s in M.PREMIUM_ALT else {})})

print('MISSING:', missing)
assert all(r['topic'] in TOPICS for r in rows), [r for r in rows if r['topic'] not in TOPICS]
nums = collections.Counter(r['n'] for r in rows); dup = [n for n, c in nums.items() if c > 1]
print('duplicate numbers:', dup, [r['s'] for r in rows if r['n'] in dup])
rank = {'E': 0, 'M': 1, 'H': 2}
rows.sort(key=lambda r: (TOPICS.index(r['topic']), -len(r['src']), rank[r['d']], r['n']))
print('unique problems:', len(rows), '| excluded:', [(e[0], e[1]) for e in excluded])
print('by difficulty:', collections.Counter(r['d'] for r in rows))
print('by #lists:', sorted(collections.Counter(len(r['src']) for r in rows).items()))
for tp in TOPICS:
    rs = [r for r in rows if r['topic'] == tp]
    print(f"{tp:26} {len(rs):3}  must(3+)={sum(len(r['src'])>=3 for r in rs):2}  " + ', '.join(f"{r['n']}" for r in rs[:6]) + ' …')
ex = [{'n': P_[s]['num'], 't': P_[s]['title'], 'why': why} for s, why, _ in excluded]
ex.sort(key=lambda e: e['n'])
json.dump({'topics': TOPICS, 'problems': rows, 'excluded': ex}, open(sys.argv[1] + '/sheet.json', 'w'), separators=(',', ':'))
