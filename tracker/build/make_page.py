# Builds placement-sprint.html from template.html and tracker_data.json.
import os
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
data = open(os.path.join(here, 'tracker_data.json')).read()
assert '</' not in data and '<!--' not in data
page = open(os.path.join(root, 'template.html')).read()
assert page.count('/*SHEET*/') == 1
open(os.path.join(root, 'placement-sprint.html'), 'w').write(page.replace('/*SHEET*/', data))
print('wrote placement-sprint.html', len(page) + len(data), 'bytes')
