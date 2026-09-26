#!/usr/bin/env python3
"""sheet.py file.pdf first last [dpi] -> sheets/sheet_<first>.png (3x2 grid per sheet)"""
import subprocess, sys, pathlib
from PIL import Image
pdf, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
dpi = sys.argv[4] if len(sys.argv) > 4 else "70"
out = pathlib.Path("sheets"); out.mkdir(exist_ok=True)
for f in out.glob("p-*.png"): f.unlink()
subprocess.run(["pdftoppm", "-r", dpi, "-png", "-f", str(first), "-l", str(last), pdf, str(out / "p")],
               check=True, stderr=subprocess.DEVNULL)
files = sorted(out.glob("p-*.png"))
for k in range(0, len(files), 6):
    imgs = [Image.open(f) for f in files[k:k + 6]]
    w, h = imgs[0].size
    sheet = Image.new("RGB", (w * 3, h * 2), "white")
    for j, im in enumerate(imgs):
        sheet.paste(im, ((j % 3) * w, (j // 3) * h))
    name = out / f"sheet_{first + k:03d}.png"
    sheet.save(name)
    print(name)
