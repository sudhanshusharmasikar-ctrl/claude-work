#!/bin/bash
# Downloads the static Inter + JetBrains Mono fonts (SIL Open Font License) from Google Fonts
# into fonts/static/ and writes fonts/static.css, which template.html links to.
set -e
cd "$(dirname "$0")"
mkdir -p static
curl -sS --max-time 30 -o static/static.css \
  "https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:ital,wght@0,400;0,500;0,700;1,400"
python3 - <<'PY'
import re, subprocess
css = open('static/static.css').read()
out = []
for b in re.findall(r'@font-face \{(.*?)\}', css, re.S):
    fam = re.search(r"font-family: '([^']+)'", b).group(1)
    style = re.search(r"font-style: (\w+)", b).group(1)
    weight = re.search(r"font-weight: (\d+)", b).group(1)
    url = re.search(r"url\((https://[^)]+)\)", b).group(1)
    fn = f"{fam.replace(' ', '')}-{weight}{'i' if style == 'italic' else ''}.ttf"
    subprocess.run(['curl', '-sS', '--max-time', '30', '-o', f'static/{fn}', url], check=True)
    out.append(f"@font-face {{ font-family: '{fam}'; font-style: {style}; font-weight: {weight}; "
               f"src: url('static/{fn}') format('truetype'); }}")
open('static.css', 'w').write("\n".join(out) + "\n")
print(len(out), "fonts downloaded")
PY
rm -f static/static.css
