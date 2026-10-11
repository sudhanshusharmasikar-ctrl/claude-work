# Runs every snippet, quiz and drill in lessons.py with python3, checks the
# answers, and writes course.json (with the real outputs) for make_page.py.
import json, os, subprocess, sys
from lessons import LESSONS

here = os.path.dirname(os.path.abspath(__file__))
EXC = ('TypeError', 'KeyError', 'IndexError', 'UnboundLocalError', 'AttributeError', 'ValueError', 'SyntaxError', 'RecursionError', 'ZeroDivisionError')


def run(src, stdin=''):
    p = subprocess.run([sys.executable, '-I', '-c', src], input=stdin, capture_output=True, text=True, timeout=20)
    out = '\n'.join(l.rstrip() for l in p.stdout.rstrip().split('\n'))   # trailing spaces from end=' '
    return p.returncode, out, p.stderr


def short_error(err):
    last = [l for l in err.strip().splitlines() if l.strip()][-1]
    return last.split(':')[0].strip()


problems = []
seen_ids, seen_slugs = set(), {}
for li, L in enumerate(LESSONS, 1):
    where = f"lesson {li} ({L['id']})"
    assert L['id'] not in seen_ids, where
    seen_ids.add(L['id'])
    for k in ('title', 'intro', 'map', 'code', 'watch', 'quiz', 'practice', 'drill'):
        assert L.get(k), f'{where}: missing {k}'

    for c in L['code']:
        if c.get('run') is False:
            c['out'] = None
            continue
        rc, out, err = run(c['src'], c.get('stdin', ''))
        if rc != 0:
            problems.append(f"{where} snippet '{c['title']}' failed:\n{err}")
        c['out'] = out

    for qi, q in enumerate(L['quiz'], 1):
        assert q['answer'] in q['options'], f'{where} quiz {qi}: answer not in options'
        assert len(set(q['options'])) == len(q['options']), f'{where} quiz {qi}: duplicate options'
        rc, out, err = run(q['code'])
        got = out if rc == 0 else short_error(err)
        if q['answer'] in EXC:
            ok = rc != 0 and got == q['answer']
        else:
            ok = rc == 0 and out == q['answer']
        if not ok:
            problems.append(f'{where} quiz {qi}: expected {q["answer"]!r}, got {got!r}')

    d = L['drill']
    src = d['src'] + ('\n' + d['test'] if d.get('test') else '')
    rc, out, err = run(src, d.get('stdin', ''))
    if rc != 0 or out != d['expect']:
        problems.append(f'{where} drill: expected {d["expect"]!r}, got {out!r} {err}')

    for p in L['practice']:
        if p['s'] in seen_slugs:
            problems.append(f"{where}: {p['n']} also in {seen_slugs[p['s']]}")
        seen_slugs[p['s']] = L['id']
        assert p['d'] in 'EMH', p

if problems:
    print('\n'.join(problems))
    sys.exit(1)

out = {'lessons': LESSONS, 'python': sys.version.split()[0]}
data = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(here, 'course.json'), 'w').write(data)
n_code = sum(len(L['code']) for L in LESSONS)
n_quiz = sum(len(L['quiz']) for L in LESSONS)
n_prac = sum(len(L['practice']) for L in LESSONS)
print(f'ok: {len(LESSONS)} lessons, {n_code} snippets, {n_quiz} quiz questions, {n_prac} practice problems, {len(LESSONS)} drills')
