# Writes SHEET.md: the same sheet as a plain list, for reading on GitHub.
import json, os
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
d = json.load(open(os.path.join(here, 'sheet.json')))
tier = lambda p: 'Must do' if len(p['src']) >= 3 else ('Important' if len(p['src']) == 2 or 'Favourite' in p['src'] else 'Extra')
diff = {'E': 'Easy', 'M': 'Medium', 'H': 'Hard'}
out = ['# DSA Problem Tracker', '',
       f"{len(d['problems'])} LeetCode problems from Striver SDE, Top Interview 150, NeetCode 150, the Fraz sheet, GFG Must-Do "
       "(each converted to the closest LeetCode problem) and your favourites, with duplicates merged.", '',
       '**Must do** = in 3 or more lists. **Important** = in 2 lists, or one of your favourites. **Extra** = in 1 list. '
       '★ = your LeetCode favourite. Trie and segment tree problems are left out: ' + ', '.join(f"{e['n']}. {e['t']}" for e in d['excluded']) + '.', '']
for t in d['topics']:
    ps = [p for p in d['problems'] if p['topic'] == t]
    out += [f'## {t} ({len(ps)})', '', '| # | Problem | Level | Priority | Lists |', '|---|---|---|---|---|']
    for p in ps:
        note = f" — replaces GFG: {p['g']}" if p.get('g') else ''
        prem = ' (Premium)' if p.get('p') else ''
        star = '★ ' if 'Favourite' in p['src'] else ''
        out.append(f"| {p['n']} | {star}[{p['t']}](https://leetcode.com/problems/{p['s']}/){prem}{note} | {diff[p['d']]} | {tier(p)} | {', '.join(p['src'])} |")
    out.append('')
open(os.path.join(root, 'SHEET.md'), 'w').write('\n'.join(out))
print('wrote SHEET.md')
