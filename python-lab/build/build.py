# Builds the Python DSA Lab.
#  1. Runs every lesson example (to show its real output) and checks every problem:
#     the reference solution must pass all tests and the starter code must not.
#  2. Writes lab.json, python-lab.html (from template.html) and py-worker.js
#     (from worker.template.js, with harness.py inside).
# Uses the same judge (harness.py) as the browser, so results match.
import json, os, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
sys.path.insert(0, here)
import harness
from content import DAYS

problems, seen = [], set()
for day in DAYS:
    for k in ('id', 'n', 'title', 'goal', 'map', 'examples', 'traps', 'problems'):
        assert day.get(k) is not None, f"{day.get('id')}: missing {k}"
    for ex in day['examples']:
        res = json.loads(harness.lab_run(json.dumps({'code': ex['src'], 'stdin': ex.get('stdin', '')})))
        if res['error']:
            problems.append(f"{day['id']} example '{ex['title']}' failed:\n{res['error']}")
        ex['out'] = res['stdout'].rstrip('\n')
    for p in day['problems']:
        assert p['id'] not in seen, f"duplicate problem id {p['id']}"
        seen.add(p['id'])
        json.dumps(p)
        req = {'kind': p['kind'], 'func': p.get('func'), 'mode': p.get('mode', 'exact'), 'tests': p['tests']}
        good = json.loads(harness.lab_check(json.dumps({**req, 'code': p['solution']})))
        bad = [r for r in good['results'] if not r['ok']]
        if good['error'] or bad or len(good['results']) != len(p['tests']):
            problems.append(f"{p['id']}: the solution fails: {good['error'] or bad[:1]}")
        start = json.loads(harness.lab_check(json.dumps({**req, 'code': p['starter']})))
        if not start['error'] and all(r['ok'] for r in start['results']):
            problems.append(f"{p['id']}: the starter code already passes")

if problems:
    print('\n'.join(problems))
    sys.exit(1)

data = {'days': DAYS}
text = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(here, 'lab.json'), 'w').write(text)

safe = text.replace('<', '\\u003c')          # nothing in the data can close the page's <script>
page = open(os.path.join(root, 'template.html')).read().replace('/*DATA*/', safe, 1)
open(os.path.join(root, 'python-lab.html'), 'w').write(page)

worker = open(os.path.join(root, 'worker.template.js')).read().replace(
    '/*HARNESS*/', json.dumps(open(os.path.join(here, 'harness.py')).read()), 1)
open(os.path.join(root, 'py-worker.js'), 'w').write(worker)

n_p = sum(len(d['problems']) for d in DAYS)
n_t = sum(len(p['tests']) for d in DAYS for p in d['problems'])
n_e = sum(len(d['examples']) for d in DAYS)
print(f'ok: {len(DAYS)} days, {n_e} examples run, {n_p} problems, {n_t} tests passed by the solutions')
print(f'wrote python-lab.html ({len(page)} bytes) and py-worker.js')
