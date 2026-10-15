"""Put each exercise's 'before' and 'after' screenshots side by side, with labels (see screenshots.sh)."""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFont

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
FONT = sys.argv[3]
W = 1400            # final width in px (~2x the printed width)
GAP, PAD, LABEL_H = 60, 10, 54
bold = ImageFont.truetype(FONT, 26)

def label(draw, x, y, text, fill, color):
    tw = draw.textlength(text, font=bold)
    draw.rounded_rectangle([x, y, x + tw + 32, y + 40], radius=20, fill=fill)
    draw.text((x + 16, y + 6), text, font=bold, fill=color)

names = sorted({p.name.rsplit("-", 1)[0] for p in SRC.glob("*-before.png")})
for n in names:
    a, b = Image.open(SRC / f"{n}-before.png"), Image.open(SRC / f"{n}-after.png")
    col = (W - GAP - 2 * PAD) // 2
    scale = min(1.0, col / a.width, col / b.width)
    a = a.resize((int(a.width * scale), int(a.height * scale)), Image.LANCZOS)
    b = b.resize((int(b.width * scale), int(b.height * scale)), Image.LANCZOS)
    H = LABEL_H + max(a.height, b.height) + PAD
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    x1, x2 = PAD + (col - a.width) // 2, PAD + col + GAP + (col - b.width) // 2
    label(d, PAD, 2, "START  ·  the starter files", (241, 245, 249), (71, 85, 105))
    label(d, PAD + col + GAP, 2, "GOAL  ·  after your code", (237, 233, 254), (91, 33, 182))
    img.paste(a, (x1, LABEL_H)); img.paste(b, (x2, LABEL_H))
    for im, x in ((a, x1), (b, x2)):
        d.rectangle([x - 1, LABEL_H - 1, x + im.width, LABEL_H + im.height], outline=(203, 213, 225), width=2)
    # arrow between the panels
    ax, ay = PAD + col + 8, LABEL_H + min(a.height, b.height) // 2
    d.line([ax, ay, ax + GAP - 22, ay], fill=(124, 58, 237), width=5)
    d.polygon([(ax + GAP - 16, ay), (ax + GAP - 30, ay - 11), (ax + GAP - 30, ay + 11)], fill=(124, 58, 237))
    out = OUT / f"{n[:2]}.png"
    if n.startswith("16"):
        out = out.with_suffix(".jpg"); img.save(out, quality=88)
    else:
        img.save(out, optimize=True)
    print(out.name, img.size, out.stat().st_size // 1024, "KB")
