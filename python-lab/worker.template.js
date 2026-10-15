// Runs Python for the Python DSA Lab inside a web worker, so long-running code
// never freezes the page. Python itself is Pyodide (CPython compiled to WebAssembly),
// loaded from the pyodide/ folder published next to the page.
let py = null, ready = null;
const HARNESS = /*HARNESS*/;

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
