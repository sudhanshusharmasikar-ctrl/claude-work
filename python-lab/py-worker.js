// Runs Python for the Python DSA Lab inside a web worker, so long-running code
// never freezes the page. Python itself is Pyodide (CPython compiled to WebAssembly),
// loaded from the pyodide/ folder published next to the page.
let py = null, ready = null;
const HARNESS = "# Runs learner code and checks it against tests. The same file runs in the browser\n# (Pyodide, inside a web worker) and in build.py, so both judge answers the same way.\nimport sys, io, json, copy, traceback, linecache, inspect\n\nFILE = 'solution.py'\n\n\ndef _register(code):\n    # Lets tracebacks show the learner's own lines.\n    linecache.cache[FILE] = (len(code), None, code.splitlines(True), FILE)\n\n\ndef _err(e):\n    if isinstance(e, SyntaxError) and e.filename == FILE:\n        text = (e.text or '').strip()\n        return f'{type(e).__name__}: {e.msg} (line {e.lineno})' + (f'\\n    {text}' if text else '')\n    frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == FILE]\n    head = ''\n    if frames:\n        head = 'Traceback (most recent call last):\\n' + ''.join(\n            f'  line {f.lineno}, in {f.name}\\n    {(f.line or \"\").strip()}\\n' for f in frames[-6:])\n    return head + f'{type(e).__name__}: {e}'\n\n\ndef _exec(code, stdin=''):\n    _register(code)\n    ns = {'__name__': '__main__'}\n    out = io.StringIO()\n    old = sys.stdout, sys.stdin\n    sys.stdout, sys.stdin = out, io.StringIO(stdin or '')\n    err = None\n    try:\n        exec(compile(code, FILE, 'exec'), ns)\n    except SystemExit:\n        pass\n    except BaseException as e:  # every error goes back to the learner\n        err = _err(e)\n    finally:\n        sys.stdout, sys.stdin = old\n    return ns, out.getvalue(), err\n\n\ndef _norm(v):\n    if isinstance(v, (list, tuple)):\n        return [_norm(x) for x in v]\n    if isinstance(v, dict):\n        return {k: _norm(x) for k, x in v.items()}\n    return v\n\n\ndef _key(v):\n    return json.dumps(v, sort_keys=True, default=str)\n\n\ndef _same(got, exp, mode):\n    g = _norm(got)\n    if mode == 'any_order':\n        return isinstance(g, list) and sorted(map(_key, g)) == sorted(map(_key, exp))\n    if mode == 'groups':\n        if not isinstance(g, list) or not all(isinstance(x, list) for x in g):\n            return False\n        flat = lambda groups: sorted(_key(sorted(map(_key, x))) for x in groups)\n        return flat(g) == flat(exp)\n    if isinstance(exp, bool) or isinstance(g, bool):\n        return type(g) is type(exp) and g == exp\n    return g == exp\n\n\ndef _show(v, limit=300):\n    s = repr(v)\n    return s if len(s) <= limit else s[:limit] + ' \u2026'\n\n\ndef _lines(text):\n    text = (text or '').rstrip()\n    return '\\n'.join(line.rstrip() for line in text.split('\\n')) if text else ''\n\n\ndef lab_run(req):\n    r = json.loads(req)\n    ns, out, err = _exec(r['code'], r.get('stdin', ''))\n    return json.dumps({'stdout': out[-20000:], 'error': err})\n\n\ndef lab_check(req):\n    r = json.loads(req)\n    code, kind = r['code'], r.get('kind', 'func')\n    res = {'error': None, 'stdout': '', 'results': []}\n    if kind == 'stdin':\n        for t in r['tests']:\n            ns, out, err = _exec(code, t['stdin'])\n            got, exp = _lines(out), _lines(t['expected'])\n            res['results'].append({'ok': err is None and got == exp, 'input': t['stdin'].rstrip('\\n'),\n                                   'expected': exp, 'got': got, 'error': err, 'stdout': ''})\n        return json.dumps(res)\n\n    ns, out, err = _exec(code)\n    res['stdout'] = out[-5000:]\n    if err:\n        res['error'] = err\n        return json.dumps(res)\n    f = ns.get(r['func'])\n    if not callable(f):\n        res['error'] = f'Your code needs a function called {r[\"func\"]}(...). Check the name in the def line.'\n        return json.dumps(res)\n    try:\n        names = list(inspect.signature(f).parameters)\n    except (TypeError, ValueError):\n        names = []\n    mode = r.get('mode', 'exact')\n    for t in r['tests']:\n        args = copy.deepcopy(t['args'])\n        labels = names if len(names) == len(args) else [f'arg{i + 1}' for i in range(len(args))]\n        shown = ', '.join(f'{n} = {_show(a, 120)}' for n, a in zip(labels, t['args']))\n        buf, old = io.StringIO(), sys.stdout\n        sys.stdout = buf\n        got, e_txt = None, None\n        try:\n            got = f(*args)\n        except BaseException as e:\n            e_txt = _err(e)\n        finally:\n            sys.stdout = old\n        if mode == 'inplace':\n            got = args[0]\n            ok = e_txt is None and _norm(got) == t['expected']\n        else:\n            ok = e_txt is None and _same(got, t['expected'], mode)\n        res['results'].append({'ok': ok, 'input': shown, 'expected': _show(t['expected']),\n                               'got': None if e_txt else _show(got), 'error': e_txt,\n                               'stdout': buf.getvalue()[-2000:]})\n    return json.dumps(res)\n";

// The standard library is published as JSON ([path, text] pairs). Pyodide wants it as a
// zip, so we build an uncompressed ("stored") zip in memory and hand it over below.
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(buf) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}
function makeZip(files) {
  const enc = new TextEncoder(), parts = [], central = [];
  let offset = 0;
  for (const [name, text] of files) {
    const nameB = enc.encode(name), data = enc.encode(text), crc = crc32(data);
    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0, 0x04034b50, true); local.setUint16(4, 20, true);
    local.setUint16(12, 0x21, true);                         // date 1980-01-01, method 0 = stored
    local.setUint32(14, crc, true); local.setUint32(18, data.length, true); local.setUint32(22, data.length, true);
    local.setUint16(26, nameB.length, true);
    parts.push(new Uint8Array(local.buffer), nameB, data);
    const cen = new DataView(new ArrayBuffer(46));
    cen.setUint32(0, 0x02014b50, true); cen.setUint16(4, 20, true); cen.setUint16(6, 20, true);
    cen.setUint16(14, 0x21, true);
    cen.setUint32(16, crc, true); cen.setUint32(20, data.length, true); cen.setUint32(24, data.length, true);
    cen.setUint16(28, nameB.length, true); cen.setUint32(42, offset, true);
    central.push(new Uint8Array(cen.buffer), nameB);
    offset += 30 + nameB.length + data.length;
  }
  const cenSize = central.reduce((n, a) => n + a.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, cenSize, true); end.setUint32(16, offset, true);
  const all = [...parts, ...central, new Uint8Array(end.buffer)];
  const out = new Uint8Array(all.reduce((n, a) => n + a.length, 0));
  let p = 0;
  for (const a of all) { out.set(a, p); p += a.length; }
  return out;
}

async function init() {
  // Fail fast, with a clear reason, if this app view does not allow WebAssembly.
  await WebAssembly.compile(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
  const base = new URL('pyodide/', self.location.href).href;
  const res = await fetch(base + 'python_stdlib.json');
  if (!res.ok) throw new Error('Could not load the Python standard library (' + res.status + ').');
  const stdlib = makeZip((await res.json()).files);
  // Pyodide fetches the library from this address; answer from memory instead of the network.
  const stdlibURL = base + 'python_stdlib.zip';
  const realFetch = self.fetch.bind(self);
  self.fetch = (url, opts) => String(url) === stdlibURL ? Promise.resolve(new Response(stdlib)) : realFetch(url, opts);
  importScripts(base + 'pyodide.js');
  py = await loadPyodide({ indexURL: base, stdLibURL: stdlibURL, stdout: () => {}, stderr: () => {} });
  py.runPython(HARNESS);
  return { version: py.runPython('import sys; sys.version.split()[0]') };
}

self.onmessage = async e => {
  const m = e.data;
  try {
    if (!ready) ready = init();
    const info = await ready;
    if (m.type === 'init') { postMessage({ id: m.id, ok: true, version: info.version }); return; }
    const fn = py.globals.get(m.type === 'check' ? 'lab_check' : 'lab_run');
    const out = fn(JSON.stringify(m.req));
    fn.destroy();
    postMessage({ id: m.id, ok: true, result: JSON.parse(out) });
  } catch (err) {
    postMessage({ id: m.id, ok: false, error: String((err && err.message) || err) });
  }
};

self.addEventListener('unhandledrejection', ev => {
  postMessage({ id: null, fatal: true, ok: false, error: String((ev.reason && ev.reason.message) || ev.reason) });
});
