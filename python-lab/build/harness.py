# Runs learner code and checks it against tests. The same file runs in the browser
# (Pyodide, inside a web worker) and in build.py, so both judge answers the same way.
import sys, io, json, copy, traceback, linecache, inspect

FILE = 'solution.py'


def _register(code):
    # Lets tracebacks show the learner's own lines.
    linecache.cache[FILE] = (len(code), None, code.splitlines(True), FILE)


def _err(e):
    if isinstance(e, SyntaxError) and e.filename == FILE:
        text = (e.text or '').strip()
        return f'{type(e).__name__}: {e.msg} (line {e.lineno})' + (f'\n    {text}' if text else '')
    frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == FILE]
    head = ''
    if frames:
        head = 'Traceback (most recent call last):\n' + ''.join(
            f'  line {f.lineno}, in {f.name}\n    {(f.line or "").strip()}\n' for f in frames[-6:])
    return head + f'{type(e).__name__}: {e}'


def _exec(code, stdin=''):
    _register(code)
    ns = {'__name__': '__main__'}
    out = io.StringIO()
    old = sys.stdout, sys.stdin
    sys.stdout, sys.stdin = out, io.StringIO(stdin or '')
    err = None
    try:
        exec(compile(code, FILE, 'exec'), ns)
    except SystemExit:
        pass
    except BaseException as e:  # every error goes back to the learner
        err = _err(e)
    finally:
        sys.stdout, sys.stdin = old
    return ns, out.getvalue(), err


def _norm(v):
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in v.items()}
    return v


def _key(v):
    return json.dumps(v, sort_keys=True, default=str)


def _same(got, exp, mode):
    g = _norm(got)
    if mode == 'any_order':
        return isinstance(g, list) and sorted(map(_key, g)) == sorted(map(_key, exp))
    if mode == 'groups':
        if not isinstance(g, list) or not all(isinstance(x, list) for x in g):
            return False
        flat = lambda groups: sorted(_key(sorted(map(_key, x))) for x in groups)
        return flat(g) == flat(exp)
    if isinstance(exp, bool) or isinstance(g, bool):
        return type(g) is type(exp) and g == exp
    return g == exp


def _show(v, limit=300):
    s = repr(v)
    return s if len(s) <= limit else s[:limit] + ' …'


def _lines(text):
    text = (text or '').rstrip()
    return '\n'.join(line.rstrip() for line in text.split('\n')) if text else ''


def lab_run(req):
    r = json.loads(req)
    ns, out, err = _exec(r['code'], r.get('stdin', ''))
    return json.dumps({'stdout': out[-20000:], 'error': err})


def lab_check(req):
    r = json.loads(req)
    code, kind = r['code'], r.get('kind', 'func')
    res = {'error': None, 'stdout': '', 'results': []}
    if kind == 'stdin':
        for t in r['tests']:
            ns, out, err = _exec(code, t['stdin'])
            got, exp = _lines(out), _lines(t['expected'])
            res['results'].append({'ok': err is None and got == exp, 'input': t['stdin'].rstrip('\n'),
                                   'expected': exp, 'got': got, 'error': err, 'stdout': ''})
        return json.dumps(res)

    ns, out, err = _exec(code)
    res['stdout'] = out[-5000:]
    if err:
        res['error'] = err
        return json.dumps(res)
    f = ns.get(r['func'])
    if not callable(f):
        res['error'] = f'Your code needs a function called {r["func"]}(...). Check the name in the def line.'
        return json.dumps(res)
    try:
        names = list(inspect.signature(f).parameters)
    except (TypeError, ValueError):
        names = []
    mode = r.get('mode', 'exact')
    for t in r['tests']:
        args = copy.deepcopy(t['args'])
        labels = names if len(names) == len(args) else [f'arg{i + 1}' for i in range(len(args))]
        shown = ', '.join(f'{n} = {_show(a, 120)}' for n, a in zip(labels, t['args']))
        buf, old = io.StringIO(), sys.stdout
        sys.stdout = buf
        got, e_txt = None, None
        try:
            got = f(*args)
        except BaseException as e:
            e_txt = _err(e)
        finally:
            sys.stdout = old
        if mode == 'inplace':
            got = args[0]
            ok = e_txt is None and _norm(got) == t['expected']
        else:
            ok = e_txt is None and _same(got, t['expected'], mode)
        res['results'].append({'ok': ok, 'input': shown, 'expected': _show(t['expected']),
                               'got': None if e_txt else _show(got), 'error': e_txt,
                               'stdout': buf.getvalue()[-2000:]})
    return json.dumps(res)
