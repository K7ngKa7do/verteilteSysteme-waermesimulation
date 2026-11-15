"""Kontaktabzug zur Sichtpruefung von Grafiken: je vier PNG eines Ordners auf ein Blatt.

Aufruf (braucht Pillow): python3 kontakt.py QUELLORDNER ZIELORDNER
Schreibt kontakt_1.png, kontakt_2.png, ... in den Zielordner."""
import sys, os, glob
from PIL import Image, ImageDraw
src = sys.argv[1]; out = sys.argv[2]
fs = sorted(glob.glob(os.path.join(src, "*.png")))
fs = [f for f in fs if not os.path.basename(f).startswith("Bildschirmfoto")]
W = 900
for k in range(0, len(fs), 4):
    tiles = []
    for f in fs[k:k+4]:
        im = Image.open(f).convert("RGB")
        im.thumbnail((W, W))
        canvas = Image.new("RGB", (W, im.height + 24), "white")
        canvas.paste(im, (0, 24))
        ImageDraw.Draw(canvas).text((4, 4), os.path.basename(f) + f"  ({Image.open(f).size[0]}x{Image.open(f).size[1]})", fill="black")
        tiles.append(canvas)
    h = max(t.height for t in tiles)
    sheet = Image.new("RGB", (2 * W, 2 * h), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * W, (i // 2) * h))
    sheet.save(os.path.join(out, f"kontakt_{k//4+1}.png"))
    print(os.path.join(out, f"kontakt_{k//4+1}.png"), [os.path.basename(f) for f in fs[k:k+4]])
