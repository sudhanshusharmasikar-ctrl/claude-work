# Turns Pyodide's python_stdlib.zip into python_stdlib.json: a list of [path, text] pairs.
# Artifacts serve JSON but not zip files; py-worker.js rebuilds the library in memory.
import json, os, sys, zipfile

folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pyodide')
src = os.path.join(folder, 'python_stdlib.zip')
z = zipfile.ZipFile(src)
files = [[i.filename, z.read(i).decode('utf-8')] for i in z.infolist() if not i.is_dir()]
with open(os.path.join(folder, 'python_stdlib.json'), 'w', encoding='utf-8') as f:
    json.dump({'files': files}, f, ensure_ascii=False, separators=(',', ':'))
os.remove(src)
print(f'wrote python_stdlib.json with {len(files)} files')
