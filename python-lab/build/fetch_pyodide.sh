#!/bin/sh
# Downloads Pyodide 0.26.4 (CPython 3.12 for the browser) from the npm registry and
# copies the files the lab needs into ../pyodide/. They are published with the page.
# The standard library zip is turned into JSON, because artifacts do not serve zip files.
set -e
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d)
curl -sS -o "$tmp/pyodide.tgz" https://registry.npmjs.org/pyodide/-/pyodide-0.26.4.tgz
echo "e1420722d86d78cb35a4734404eee5b070ca7189  $tmp/pyodide.tgz" | sha1sum -c -
tar -xzf "$tmp/pyodide.tgz" -C "$tmp"
mkdir -p "$here/../pyodide"
for f in pyodide.js pyodide.asm.js pyodide.asm.wasm python_stdlib.zip pyodide-lock.json; do
  cp "$tmp/package/$f" "$here/../pyodide/"
done
rm -rf "$tmp"
python3 "$here/stdlib_to_json.py" "$here/../pyodide"
echo "copied Pyodide into $(cd "$here/.." && pwd)/pyodide"
