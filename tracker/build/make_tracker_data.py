# Assigns DSA Master Sheet problems to the 26 working days of the Placement Sprint.
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
sheet = json.load(open(os.path.join(here, '..', '..', 'dsa-sheet', 'build', 'sheet.json')))
P = sheet['problems']; BYNUM = {p['n']: p for p in P}
tier = lambda p: 0 if len(p['src']) >= 3 else (1 if len(p['src']) == 2 or 'Favourite' in p['src'] else 2)
drank = {'E': 0, 'M': 1, 'H': 2}

# DSA important topic (4-5 h): every tree, graph and DP problem, one sub-topic per working day.
CORE = [
  ('Trees', 'Traversals: inorder, preorder, postorder, level order', [94, 144, 145, 102, 637, 103]),
  ('Trees', 'Height, diameter, balanced check, maximum path sum', [104, 110, 543, 124, 100, 101, 226]),
  ('Trees', 'Views, vertical order and width', [199, 987, 662, 116, 117, 572]),
  ('Trees', 'Lowest common ancestor, root-to-leaf paths, distance K', [236, 863, 2385, 112, 113, 437, 129, 257]),
  ('Trees', 'Build a tree from traversals; serialize and deserialize', [105, 106, 889, 297, 114, 617, 404]),
  ('Trees', 'BST basics: search, validate, kth smallest, build', [98, 230, 700, 108, 1008, 938, 530]),
  ('Trees', 'BST: LCA, iterator, two-sum, recover', [235, 173, 653, 99, 95, 1373]),
  ('Trees', 'Mixed tree problems and re-solving the weak ones', [1448, 222, 968]),
  ('Graphs', 'Representation, BFS, DFS, connected components', [733, 841, 1971, 547, 133, 997, 797, 690]),
  ('Graphs', 'Grids: islands, rotting oranges, surrounded regions', [200, 994, 695, 130, 1020, 1905, 1254, 417, 286, 1162]),
  ('Graphs', 'Cycle detection (undirected and directed), bipartite check', [207, 785, 886, 802, 261]),
  ('Graphs', 'Topological sort (Kahn and DFS), course schedule', [210, 399, 1376, 269]),
  ('Graphs', 'Shortest paths: BFS on unit weights, Dijkstra', [743, 1091, 127, 909, 433, 1654, 778, 126]),
  ('Graphs', 'Bellman-Ford and Floyd-Warshall', [787, 1334, 882]),
  ('Graphs', 'Minimum spanning tree: Prim and Kruskal, disjoint set union', [1584, 684, 1319, 323, 685]),
  ('Graphs', 'DSU problems: accounts merge, stones, equations; bridges', [721, 947, 990, 959, 1192]),
  ('Graphs', 'Mixed graph problems and re-solving the weak ones', [934, 827, 749, 675, 332, 834, 1719]),
  ('DP', '1D DP: climbing stairs, house robber, decode ways', [70, 746, 198, 213, 740, 91, 935]),
  ('DP', 'Grid DP: unique paths, minimum path sum, triangle, squares', [62, 63, 64, 120, 931, 221, 1277]),
  ('DP', 'Subsets and 0/1 knapsack: equal partition, target sum', [416, 494, 1049, 474, 2518]),
  ('DP', 'Unbounded knapsack: coin change I and II, word break', [322, 518, 139, 140, 472]),
  ('DP', 'Strings I: LCS, palindromic subsequences, supersequence', [1143, 5, 647, 718, 1092, 1312, 730]),
  ('DP', 'Strings II: edit distance, interleaving, distinct subsequences', [72, 97, 115, 10, 132]),
  ('DP', 'Stocks and games: buy and sell, max product, predict the winner', [123, 188, 309, 152, 486]),
  ('DP', 'LIS and its variants', [300, 1027, 646, 1626, 1691, 329, 403]),
  ('DP', 'Partition DP: burst balloons, cut stick, egg drop', [312, 1547, 1000, 546, 1335, 887, 96, 337]),
]
core_topics = {'Binary Trees', 'Binary Search Trees', 'Graphs', 'Dynamic Programming'}
assigned = [n for _, _, ns in CORE for n in ns]
assert len(assigned) == len(set(assigned)), 'a problem is on two days'
want = {p['n'] for p in P if p['topic'] in core_topics}
assert set(assigned) == want, (want - set(assigned), set(assigned) - want)
order = lambda p: (tier(p), drank[p['d']], p['n'])
core = [{'area': a, 'title': t, 'probs': [p['s'] for p in sorted((BYNUM[n] for n in ns), key=order)]} for a, t, ns in CORE]

# DSA revision (3 h): the Must do + Important problems of every other topic, spread over 24 days.
REV_PLAN = [(['Arrays & Hashing'], 'Arrays & Hashing', 4), (['Two Pointers'], 'Two Pointers', 1), (['Sliding Window'], 'Sliding Window', 2),
            (['Strings'], 'Strings', 2), (['Binary Search'], 'Binary Search', 2), (['Stack & Queue'], 'Stack & Queue', 3),
            (['Linked List'], 'Linked List', 2), (['Recursion & Backtracking'], 'Recursion & Backtracking', 2), (['Heap'], 'Heap', 1),
            (['Greedy'], 'Greedy', 1), (['Matrix', 'Intervals'], 'Matrix and Intervals', 1), (['Design', 'Maths & Bits'], 'Design, Maths & Bits', 3)]
sheet_order = {p['s']: i for i, p in enumerate(P)}
rev = []
for topics, title, k in REV_PLAN:
    pool = [p for p in P if p['topic'] in topics and tier(p) < 2]
    pool.sort(key=lambda p: (topics.index(p['topic']), sheet_order[p['s']]))
    parts = [[] for _ in range(k)]
    for i, p in enumerate(pool): parts[i % k].append(p)
    for j, part in enumerate(parts):
        rev.append({'title': title + (f' · part {j + 1} of {k}' if k > 1 else ''), 'probs': [p['s'] for p in sorted(part, key=order)]})
rev.append({'title': 'Re-solve everything you marked ⚑ to revise', 'probs': [], 'special': 'revise'})
rev.append({'title': 'Timed mock: 2 problems in 60 minutes', 'probs': [], 'special': 'mock'})
assert len(core) == 26 and len(rev) == 26
other = {p['s'] for p in P if p['topic'] not in core_topics and tier(p) < 2}
assert {s for r in rev for s in r['probs']} == other
out = {'topics': sheet['topics'], 'problems': P, 'excluded': sheet['excluded'], 'core': core, 'rev': rev}
json.dump(out, open(os.path.join(here, 'tracker_data.json'), 'w'), separators=(',', ':'))
print('core per day:', [len(c['probs']) for c in core])
print('revision per day:', [len(r['probs']) for r in rev])
print('scheduled:', sum(len(c['probs']) for c in core) + sum(len(r['probs']) for r in rev), 'of', len(P))
