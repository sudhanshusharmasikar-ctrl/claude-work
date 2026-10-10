# Builds dsa-master-sheet.html from template.html and sheet.json.
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
data = open(os.path.join(here, 'sheet.json')).read()
assert '</' not in data and '<!--' not in data
page = open(os.path.join(root, 'template.html')).read().replace('/*DATA*/', data, 1)
open(os.path.join(root, 'dsa-master-sheet.html'), 'w').write(page)
print('wrote dsa-master-sheet.html', len(page), 'bytes')
