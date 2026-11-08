#!/usr/bin/env python3
"""Render docs/og.png (1200x630 OGP card) from the built cursor PNGs.

usage: python3 build_cursors.py && python3 make_og_image.py
Run on macOS: it uses the system Avenir Next font. The card is committed, so CI does not
need to rerun this; make_test_page.py copies docs/og.png into the site.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "dist", "kurenawi-cursors", "png")
OUT = os.path.join(HERE, "docs", "og.png")
FONT = "/System/Library/Fonts/Avenir Next.ttc"
W, H = 1200, 630

ROWS = [
    ["normal", "link", "text", "help", "busy", "precision", "unavailable"],
    ["copy", "alias", "zoomin", "move", "extra_wink", "extra_tea", "extra_wave"],
]


def font(size, index):
    return ImageFont.truetype(FONT, size, index=index)


def main():
    im = Image.new("RGBA", (W, H), (44, 14, 24, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 30):
        for x in range(0, W, 30):
            if (x // 30 + y // 30) % 2:
                d.rectangle([x, y, x + 29, y + 29], fill=(56, 19, 31, 255))
    d.rectangle([0, 0, W - 1, 10], fill=(224, 16, 42, 255))
    d.rectangle([0, H - 11, W - 1, H - 1], fill=(224, 16, 42, 255))

    bold, demi = font(76, 0), font(30, 2)  # Avenir Next: 0 Bold, 2 Demi Bold
    d.text((W // 2, 82), "kurenawi cursor demo", font=bold, anchor="mm", fill=(255, 245, 246, 255),
           stroke_width=5, stroke_fill=(224, 16, 42, 255))
    d.text((W // 2, 150), "Pixel-art mouse cursors  ·  Windows / macOS / CSS", font=demi, anchor="mm",
           fill=(255, 200, 210, 255))

    cell, size = 160, 128
    for r, names in enumerate(ROWS):
        x0 = (W - cell * len(names)) // 2 + (cell - size) // 2
        y = 196 + r * 190
        for i, n in enumerate(names):
            c = Image.open(os.path.join(PNG, f"{n}@128.png")).convert("RGBA")
            im.alpha_composite(c, (x0 + i * cell, y))
    im.convert("RGB").save(OUT, optimize=True)
    print(OUT, im.size)


if __name__ == "__main__":
    main()
