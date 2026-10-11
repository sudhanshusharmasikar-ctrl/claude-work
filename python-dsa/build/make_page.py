# Builds python-dsa-bridge.html from template.html and course.json.
import os
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
data = open(os.path.join(here, 'course.json')).read()
assert '</' not in data and '<!--' not in data
page = open(os.path.join(root, 'template.html')).read().replace('/*DATA*/', data, 1)
open(os.path.join(root, 'python-dsa-bridge.html'), 'w').write(page)
print('wrote python-dsa-bridge.html', len(page), 'bytes')
