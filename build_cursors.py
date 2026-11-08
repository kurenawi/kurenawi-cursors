#!/usr/bin/env python3
"""Build the kurenawi mouse-cursor pack from a Codex chibi sheet.

usage: uv run --with pillow --with numpy python build_cursors.py [sheet.png]

Steps: cut the 4x4 chibi sheet -> transparent figures, compose each cursor on a
32-unit grid (pixel-art glyph top-left + figure bottom-right + white sticker
outline) at scales 1-4 (32/64/96/128 px), then write Windows .cur/.ani files,
install.inf, CSS-ready PNGs and a preview sheet.
"""
import io
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "art", "sheet_a.png")
SHEET2 = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "art", "sheet2_a.png")  # 3x2: copy alias cell zoomin zoomout wave
OUT = os.path.join(HERE, "dist", "kurenawi-cursors")
SCALES = (1, 2, 3, 4)  # 32, 64, 96, 128 px
BASE = 32

PAL = {
    "K": (42, 8, 20, 255),     # outline (deep plum-black)
    "R": (224, 16, 42, 255),   # crimson
    "D": (150, 10, 32, 255),   # dark crimson
    "P": (255, 150, 165, 255), # pale crimson highlight
    "W": (255, 250, 246, 255), # warm white
    "S": (255, 222, 205, 255), # skin
    "G": (214, 170, 72, 255),  # muted gold
}


def glyph(rows):
    w = max(len(r) for r in rows)
    im = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in PAL:
                px[x, y] = PAL[c]
    return im


ARROW = glyph([
    "K",
    "KK",
    "KPK",
    "KRPK",
    "KRRPK",
    "KRRRPK",
    "KRRRRPK",
    "KRRRRRPK",
    "KRRRRRRPK",
    "KRRRRKKKKK",
    "KRRKRRK",
    "KRK.KRRK",
    "KK..KRRK",
    "K....KRRK",
    ".....KKK",
])
QMARK = glyph([
    ".KKKK.",
    "KWWWWK",
    "KWKKWK",
    ".K.KWK",
    "..KWK.",
    "..KWK.",
    "..KK..",
    "..KWK.",
    "..KK..",
])
LEAF = glyph([
    ".....K.....",
    "....KRK....",
    ".K..KRK..K.",
    "KRK.KRK.KRK",
    ".KRKKRKKRK.",
    "KKRRRPRRRKK",
    "KRRRRPRRRRK",
    ".KKRRPRRKK.",
    "...KKDKK...",
    ".....D.....",
    ".....K.....",
])
CROSS = glyph([
    "....KKK....",
    "....KWK....",
    "....KWK....",
    "....KWK....",
    "KKKKK.KKKKK",
    "KWWW.R.WWWK",
    "KKKKK.KKKKK",
    "....KWK....",
    "....KWK....",
    "....KWK....",
    "....KKK....",
])
IBEAM = glyph([
    "KKK.KKK",
    "KWWKWWK",
    "KKKWKKK",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "..KWK..",
    "KKKWKKK",
    "KWWKWWK",
    "KKK.KKK",
])
BRUSH = glyph([
    "KK..........",
    "KKK.........",
    ".KKKK.......",
    ".KKWWK......",
    "..KWWWK.....",
    "...KWWGK....",
    "....KGGDK...",
    ".....KDRDK..",
    "......KDRDK.",
    ".......KDRDK",
    "........KDDK",
    ".........KK.",
])
NO = glyph([
    "...KKKKK...",
    ".KKRRRRRKK.",
    ".KRRKKKRRK.",
    "KRRKK..KRRK",
    "KRKRRK..KRK",
    "KRK.KRK.KRK",
    "KRK..KRRKRK",
    "KRRK..KKRRK",
    ".KRRKKKRRK.",
    ".KKRRRRRKK.",
    "...KKKKK...",
])
HAND = glyph([
    "..KK.......",
    ".KWWK......",
    ".KWWK......",
    ".KWWK......",
    ".KWWKKK....",
    ".KWWKWWKKK.",
    "KKWWKWWKWWK",
    "KWKWWWWKWWK",
    "KWWWWWWWWWK",
    ".KWWWWWWWWK",
    ".KWWWWWWWK.",
    "..KRRRRRRK.",
    "..KKKKKKKK.",
])
UPARROW = glyph([
    "....K....",
    "...KPK...",
    "..KRPRK..",
    ".KRRPRRK.",
    "KRRRPRRRK",
    "KKKRPRKKK",
    "..KRRRK..",
    "..KRRRK..",
    "..KRRRK..",
    "..KRRRK..",
    "..KRRRK..",
    "..KKKKK..",
])
PIN = glyph([
    "..KKKK..",
    ".KRRRRK.",
    "KRRKKRRK",
    "KRKWWKRK",
    "KRKWWKRK",
    "KRRKKRRK",
    ".KRRRRK.",
    ".KRRRRK.",
    "..KRRK..",
    "..KRRK..",
    "...KK...",
])
HEART = glyph([
    ".KK...KK.",
    "KRRK.KRRK",
    "KRPRKRRRK",
    "KRPRRRRRK",
    "KRRRRRRRK",
    ".KRRRRRK.",
    "..KRRRK..",
    "...KRK...",
    "....K....",
])
CHEV = glyph([
    "...KKK...",
    "..KRRRK..",
    ".KRRPRRK.",
    "KRRK.KRRK",
    "KKK...KKK",
])
CORNER = glyph([
    "KKKKKK",
    "KPRRRK",
    "KRKKKK",
    "KRK...",
    "KRK...",
    "KKK...",
])


PLUS = glyph([
    "..KKKKK..",
    ".KRRRRRK.",
    "KRRKWKRRK",
    "KRRKWKRRK",
    "KKKKWKKKK",
    "KWWWWWWWK",
    "KKKKWKKKK",
    "KRRKWKRRK",
    ".KRKWKRK.",
    "..KKKKK..",
])
CURL = glyph([
    "..KKKKK...",
    ".KRRRRRK..",
    "KRKKKKRRK.",
    "KRK..KKRRK",
    "KRK.KRRRRRK",
    "KRK..KRRRK",
    "KRRK..KRK.",
    ".KRRK..K..",
    "..KKK.....",
])
CELL = glyph([
    "....KKKKK....",
    "....KWWWK....",
    "....KWWWK....",
    "....KWWWK....",
    "KKKKKWWWKKKKK",
    "KWWWWWRWWWWWK",
    "KWWWWRRRWWWWK",
    "KWWWWWRWWWWWK",
    "KKKKKWWWKKKKK",
    "....KWWWK....",
    "....KWWWK....",
    "....KWWWK....",
    "....KKKKK....",
])


def magnifier(sign):
    rows = [
        "...KKKKK......",
        ".KKWWWWWKK....",
        ".KWWWWWWWK....",
        "KWWWWWWWWWK...",
        "KWWWWWWWWWK...",
        "KWWWWWWWWWK...",
        "KWWWWWWWWWK...",
        "KWWWWWWWWWK...",
        ".KWWWWWWWK....",
        ".KKWWWWWKKK...",
        "...KKKKKKDDK..",
        ".........KDDK.",
        "..........KDDK",
        "...........KK.",
    ]
    rows = [list(r) for r in rows]
    for x in range(3, 8):
        rows[5][x] = "R"
    if sign == "+":
        for y in range(3, 8):
            rows[y][5] = "R"
    return glyph(["".join(r) for r in rows])


ZOOMIN = magnifier("+")
ZOOMOUT = magnifier("-")


def spinner(phase, n=8):
    """15x15 donut split into 8 sectors; the lit sector walks clockwise with a fading tail."""
    import math
    im = Image.new("RGBA", (15, 15), (0, 0, 0, 0))
    px = im.load()
    tail = {0: PAL["R"], 1: (200, 46, 76, 255), 2: (236, 120, 140, 255)}
    for y in range(15):
        for x in range(15):
            dx, dy = x - 7, y - 7
            d = math.hypot(dx, dy)
            if d > 7.4:
                continue
            if d < 3.0:
                px[x, y] = PAL["W"]
                continue
            if d > 6.4 or d < 4.0:
                px[x, y] = PAL["K"]
                continue
            ang = (math.degrees(math.atan2(dx, -dy)) + 360) % 360  # 0 = up, clockwise
            sec = int(((ang + 22.5) % 360) // 45)
            px[x, y] = tail.get((phase - sec) % n, (255, 214, 220, 255))
    return im


# ---------------------------------------------------------------- figures
def extract_figures(sheet_path, cols=4, rows=4):
    sheet = Image.open(sheet_path).convert("RGB")
    W, H = sheet.size
    figs = []
    for i in range(cols * rows):
        cx, cy = i % cols, i // cols
        box = (round(cx * W / cols) + 4, round(cy * H / rows) + 4, round((cx + 1) * W / cols) - 4, round((cy + 1) * H / rows) - 4)
        a = np.array(sheet.crop(box)).astype(np.int16)
        h, w, _ = a.shape
        whiteish = (a.min(2) > 225) & ((a.max(2) - a.min(2)) < 30)
        bg = np.zeros((h, w), bool)
        stack = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
        while stack:
            y, x = stack.pop()
            if 0 <= y < h and 0 <= x < w and not bg[y, x] and whiteish[y, x]:
                bg[y, x] = True
                stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
        fg = ~bg
        # peel light antialias halo touching the background
        for _ in range(3):
            near = np.zeros_like(bg)
            near[1:] |= bg[:-1]; near[:-1] |= bg[1:]; near[:, 1:] |= bg[:, :-1]; near[:, :-1] |= bg[:, 1:]
            halo = fg & near & (a.min(2) > 190)
            bg |= halo
            fg &= ~halo
        # keep the largest connected component (drops loose sparkles / '?' / speed lines)
        lab = np.zeros((h, w), np.int32)
        sizes = [0]
        for y0 in range(h):
            for x0 in range(w):
                if fg[y0, x0] and not lab[y0, x0]:
                    k = len(sizes); sizes.append(0); st = [(y0, x0)]; lab[y0, x0] = k
                    while st:
                        y, x = st.pop(); sizes[k] += 1
                        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                            if 0 <= yy < h and 0 <= xx < w and fg[yy, xx] and not lab[yy, xx]:
                                lab[yy, xx] = k; st.append((yy, xx))
        keep = lab == int(np.argmax(sizes))
        rgba = np.dstack([a.astype(np.uint8), (keep * 255).astype(np.uint8)])
        im = Image.fromarray(rgba, "RGBA")
        figs.append(im.crop(im.getbbox()))
    return figs


def fit(fig, box_px):
    w, h = fig.size
    k = box_px / max(w, h)
    # premultiply to avoid dark/white fringes, then resize
    im = fig.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS, reducing_gap=3.0)
    a = np.array(im)
    alpha = a[..., 3]
    a[..., 3] = np.where(alpha > 110, 255, 0).astype(np.uint8)  # crisp edge
    return Image.fromarray(a, "RGBA")


# ---------------------------------------------------------------- compose
def sticker(im, s):
    """white sticker outline (radius s) under the artwork."""
    al = im.getchannel("A").point(lambda v: 255 if v else 0)
    grown = al.filter(ImageFilter.MaxFilter(2 * s + 1))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", im.size, (255, 255, 255, 255)), (0, 0), grown)
    out.alpha_composite(im)
    return out


def compose(s, fig=None, fig_box=(9, 9, 31, 31), parts=()):
    """parts: [(glyph, (x, y))] in 32-grid units, nearest-scaled by s."""
    size = BASE * s
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if fig is not None:
        x0, y0, x1, y1 = fig_box
        f = fit(fig, (x1 - x0) * s)
        im.alpha_composite(f, ((x1 * s) - f.width, (y1 * s) - f.height))
    for g, (x, y) in parts:
        gi = g.resize((g.width * s, g.height * s), Image.NEAREST)
        # each glyph gets its own white plate so it reads on top of the figure
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        layer.alpha_composite(gi, (x * s, y * s))
        im = Image.alpha_composite(im, sticker(layer, s))
    return sticker(im, s)


def resize_parts(kind):
    c = 16
    lx, ly = c - 5, c - 5
    parts = [(LEAF, (lx, ly))]
    up = CHEV
    dn = CHEV.transpose(Image.FLIP_TOP_BOTTOM)
    lf = CHEV.transpose(Image.ROTATE_90)
    rt = CHEV.transpose(Image.ROTATE_270)
    nw = CORNER
    ne = CORNER.transpose(Image.FLIP_LEFT_RIGHT)
    sw = CORNER.transpose(Image.FLIP_TOP_BOTTOM)
    se = CORNER.transpose(Image.ROTATE_180)
    if kind in ("ns", "move"):
        parts += [(up, (c - 4, 3)), (dn, (c - 4, 24))]
    if kind in ("we", "move"):
        parts += [(lf, (3, c - 4)), (rt, (24, c - 4))]
    if kind == "nwse":
        parts += [(nw, (4, 4)), (se, (22, 22))]
    if kind == "nesw":
        parts += [(ne, (22, 4)), (sw, (4, 22))]
    return parts


# role -> (figure index or None, parts, hotspot in 32-grid, animated?)
def roles(figs):
    A = (1, 1)
    return {
        "normal":      dict(fig=0, parts=[(ARROW, A)], hot=(1, 1)),
        "help":        dict(fig=1, parts=[(ARROW, A), (QMARK, (11, 1))], hot=(1, 1)),
        "working":     dict(fig=2, parts=[(ARROW, A)], spin_at=(12, 1), hot=(1, 1)),
        "busy":        dict(fig=3, parts=[], spin_at=(1, 1), hot=(8, 8)),
        "precision":   dict(fig=4, parts=[(CROSS, A)], hot=(6, 6)),
        "text":        dict(fig=5, parts=[(IBEAM, (1, 1))], hot=(4, 8)),
        "handwriting": dict(fig=6, parts=[(BRUSH, A)], hot=(1, 1)),
        "unavailable": dict(fig=7, parts=[(NO, A)], hot=(6, 6)),
        "link":        dict(fig=8, parts=[(HAND, A)], hot=(3, 1)),
        "alternate":   dict(fig=9, parts=[(UPARROW, A)], hot=(5, 1)),
        "location":    dict(fig=10, parts=[(ARROW, A), (PIN, (11, 1))], hot=(1, 1)),
        "person":      dict(fig=11, parts=[(ARROW, A), (HEART, (11, 1))], hot=(1, 1)),
        "move":        dict(fig=None, parts=resize_parts("move"), hot=(16, 16)),
        "vertical":    dict(fig=None, parts=resize_parts("ns"), hot=(16, 16)),
        "horizontal":  dict(fig=None, parts=resize_parts("we"), hot=(16, 16)),
        "diagonal1":   dict(fig=None, parts=resize_parts("nwse"), hot=(16, 16)),
        "diagonal2":   dict(fig=None, parts=resize_parts("nesw"), hot=(16, 16)),
        # bonus alternates (not in the Windows scheme by default)
        "extra_wink":  dict(fig=13, parts=[(ARROW, A)], hot=(1, 1)),
        "extra_sleepy": dict(fig=14, parts=[(ARROW, A)], hot=(1, 1)),
        "extra_tea":   dict(fig=15, parts=[(ARROW, A)], hot=(1, 1)),
        "extra_hooray": dict(fig=12, parts=[(ARROW, A)], hot=(1, 1)),
        "extra_wave":  dict(fig=21, parts=[(ARROW, A)], hot=(1, 1)),
        # macOS-only roles (Windows has no scheme slot; the .cur files are still written)
        "copy":        dict(fig=16, parts=[(ARROW, A), (PLUS, (11, 1))], hot=(1, 1)),
        "alias":       dict(fig=17, parts=[(ARROW, A), (CURL, (11, 1))], hot=(1, 1)),
        "cell":        dict(fig=18, parts=[(CELL, A)], hot=(7, 7)),
        "zoomin":      dict(fig=19, parts=[(ZOOMIN, A)], hot=(6, 6)),
        "zoomout":     dict(fig=20, parts=[(ZOOMOUT, A)], hot=(6, 6)),
    }


def frames_for(r, figs, s, nframes=8):
    fig = figs[r["fig"]] if r["fig"] is not None else None
    if "spin_at" not in r:
        return [compose(s, fig, parts=r["parts"])]
    out = []
    for p in range(nframes):
        bob = 0 if p % 4 < 2 else 1
        box = (9, 9 - bob, 31, 31 - bob)
        out.append(compose(s, fig, box, parts=r["parts"] + [(spinner(p), r["spin_at"])]))
    return out


# ---------------------------------------------------------------- writers
def dib(im):
    w, h = im.size
    a = np.array(im.convert("RGBA"))
    bgra = a[::-1][..., [2, 1, 0, 3]].tobytes()
    row = ((w + 31) // 32) * 4
    mask = bytearray()
    for y in range(h - 1, -1, -1):
        bits = 0
        line = bytearray(row)
        for x in range(w):
            if a[y, x, 3] == 0:
                line[x // 8] |= 0x80 >> (x % 8)
        mask += line
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(bgra) + len(mask), 0, 0, 0, 0)
    return hdr + bgra + bytes(mask)


def cur_bytes(imgs_by_scale, hot):
    entries, blobs = [], []
    for s, im in imgs_by_scale:
        blobs.append(dib(im))
        entries.append((im.width, im.height, hot[0] * s, hot[1] * s))
    n = len(entries)
    out = struct.pack("<HHH", 0, 2, n)
    off = 6 + 16 * n
    for (w, h, hx, hy), b in zip(entries, blobs):
        out += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, hx, hy, len(b), off)
        off += len(b)
    return out + b"".join(blobs)


def chunk(tag, data):
    pad = b"\0" if len(data) % 2 else b""
    return tag + struct.pack("<I", len(data)) + data + pad


def ani_bytes(frame_curs, jiffies):
    anih = struct.pack("<9I", 36, len(frame_curs), len(frame_curs), 0, 0, 0, 0, jiffies, 1)
    fram = b"fram" + b"".join(chunk(b"icon", c) for c in frame_curs)
    body = b"ACON" + chunk(b"anih", anih) + chunk(b"LIST", fram)
    return b"RIFF" + struct.pack("<I", len(body)) + body


WIN = [  # (registry value, role) in scheme order
    ("Arrow", "normal"), ("Help", "help"), ("AppStarting", "working"), ("Wait", "busy"),
    ("Crosshair", "precision"), ("IBeam", "text"), ("NWPen", "handwriting"), ("No", "unavailable"),
    ("SizeNS", "vertical"), ("SizeWE", "horizontal"), ("SizeNWSE", "diagonal1"), ("SizeNESW", "diagonal2"),
    ("SizeAll", "move"), ("UpArrow", "alternate"), ("Hand", "link"), ("Pin", "location"), ("Person", "person"),
]


def write_inf(files):
    scheme = ",".join("%10%\\Cursors\\kurenawi\\" + files[r] for _, r in WIN)
    lines = [
        "[Version]", 'signature="$CHICAGO$"', "", "[DefaultInstall]",
        "CopyFiles = Scheme.Cur", "AddReg = Scheme.Reg", "", "[DestinationDirs]",
        "Scheme.Cur = 10,\"Cursors\\kurenawi\"", "", "[Scheme.Reg]",
        'HKCU,"Control Panel\\Cursors\\Schemes","%SCHEME_NAME%",,"' + scheme + '"', "", "[Scheme.Cur]",
    ] + sorted(set(files.values())) + ["", "[Strings]", 'SCHEME_NAME = "kurenawi"', ""]
    with open(os.path.join(OUT, "windows", "install.inf"), "w", newline="\r\n") as f:
        f.write("\n".join(lines))


MAC = {  # Mousecape identifier -> role (names from Mousecape MCDefs.m cursorMap)
    "com.apple.coregraphics.Arrow": "normal", "com.apple.coregraphics.ArrowS": "normal",
    "com.apple.coregraphics.ArrowCtx": "normal", "com.apple.cursor.24": "normal",
    "com.apple.coregraphics.IBeam": "text", "com.apple.coregraphics.IBeamS": "text",
    "com.apple.coregraphics.IBeamXOR": "text", "com.apple.cursor.26": "text",
    "com.apple.coregraphics.Wait": "busy", "com.apple.cursor.4": "busy",
    "com.apple.cursor.13": "link", "com.apple.cursor.40": "help",
    # numeric ids are CoreCursor types; Chromium ui/base/cocoa/cursor_utils.mm names them
    # (crosshair = 20 and move = 39, not Mousecape's "Cell XOR" / "Resize Square" labels)
    "com.apple.cursor.20": "precision", "com.apple.cursor.7": "precision", "com.apple.cursor.8": "precision",
    "com.apple.cursor.39": "move",
    "com.apple.coregraphics.Copy": "copy", "com.apple.cursor.5": "copy",
    "com.apple.coregraphics.Alias": "alias", "com.apple.cursor.2": "alias",
    "com.apple.cursor.41": "cell", "com.apple.cursor.42": "zoomin", "com.apple.cursor.43": "zoomout",
    "com.apple.cursor.3": "unavailable",
    "com.apple.coregraphics.Move": "move", "com.apple.cursor.11": "move", "com.apple.cursor.12": "move",
    "com.apple.cursor.19": "horizontal", "com.apple.cursor.17": "horizontal", "com.apple.cursor.18": "horizontal",
    "com.apple.cursor.28": "horizontal", "com.apple.cursor.27": "horizontal", "com.apple.cursor.38": "horizontal",
    "com.apple.cursor.23": "vertical", "com.apple.cursor.21": "vertical", "com.apple.cursor.22": "vertical",
    "com.apple.cursor.32": "vertical", "com.apple.cursor.31": "vertical", "com.apple.cursor.36": "vertical",
    "com.apple.cursor.34": "diagonal1", "com.apple.cursor.33": "diagonal1", "com.apple.cursor.35": "diagonal1",
    "com.apple.cursor.30": "diagonal2", "com.apple.cursor.29": "diagonal2", "com.apple.cursor.37": "diagonal2",
}


def png_bytes(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def write_cape(R, rendered):
    import plistlib
    cursors = {}
    for ident, role in MAC.items():
        r = R[role]
        reps = []
        for s in (1, 2):
            fr = rendered[role][s]
            strip = Image.new("RGBA", (BASE * s, BASE * s * len(fr)), (0, 0, 0, 0))
            for k, im in enumerate(fr):
                strip.paste(im, (0, BASE * s * k))
            reps.append(png_bytes(strip))
        cursors[ident] = {
            "FrameCount": len(rendered[role][1]), "FrameDuration": 0.1 if len(rendered[role][1]) > 1 else 1.0,
            "HotSpotX": float(r["hot"][0]), "HotSpotY": float(r["hot"][1]),
            "PointsWide": float(BASE), "PointsHigh": float(BASE), "Representations": reps,
        }
    cape = {
        "Author": "kurenawi", "CapeName": "kurenawi", "CapeVersion": 1.0, "Cloud": False,
        "Cursors": cursors, "HiDPI": True, "Identifier": "local.kurenawi.cursors",
        "MinimumVersion": 2.0, "Version": 2.0,
    }
    os.makedirs(os.path.join(OUT, "macos"), exist_ok=True)
    with open(os.path.join(OUT, "macos", "kurenawi.cape"), "wb") as f:
        plistlib.dump(cape, f)


def main():
    figs = extract_figures(SHEET) + extract_figures(SHEET2, 3, 2)  # 0-15 sheet 1, 16-21 sheet 2
    os.makedirs(os.path.join(OUT, "work_figures"), exist_ok=True)
    for i, f in enumerate(figs):
        f.save(os.path.join(OUT, "work_figures", f"{i + 1:02d}.png"))
    R = roles(figs)
    files = {}
    for d in ("windows", "png", "png/anim"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    previews = {}
    rendered = {}
    for name, r in R.items():
        per_scale = {s: frames_for(r, figs, s) for s in SCALES}
        rendered[name] = per_scale
        n = len(per_scale[1])
        previews[name] = per_scale[4][0]
        for s in (1, 2, 4):
            per_scale[s][0].save(os.path.join(OUT, "png", f"{name}@{BASE * s}.png"))
        if n == 1:
            data = cur_bytes([(s, per_scale[s][0]) for s in SCALES], r["hot"])
            fn = f"{name}.cur"
        else:
            curs = [cur_bytes([(s, per_scale[s][k]) for s in SCALES], r["hot"]) for k in range(n)]
            data = ani_bytes(curs, 6)  # 6 jiffies = 100 ms
            fn = f"{name}.ani"
            for k in range(n):
                per_scale[1][k].save(os.path.join(OUT, "png", "anim", f"{name}@32_{k}.png"))
                per_scale[2][k].save(os.path.join(OUT, "png", "anim", f"{name}@64_{k}.png"))
            per_scale[4][0].save(os.path.join(OUT, "png", "anim", f"{name}@128.gif"), save_all=True,
                                 append_images=per_scale[4][1:], duration=100, loop=0, disposal=2,
                                 transparency=0)
        with open(os.path.join(OUT, "windows", fn), "wb") as f:
            f.write(data)
        files[name] = fn
    write_inf(files)
    write_cape(R, rendered)
    with open(os.path.join(OUT, "hotspots.tsv"), "w") as f:
        for name, r in R.items():
            f.write(f"{name}\t{files[name]}\t{r['hot'][0]}\t{r['hot'][1]}\n")
    # preview sheet (static PNG) + animated promo GIF
    names = [r for _, r in WIN] + ["copy", "alias", "cell", "zoomin", "zoomout"] + [n for n in R if n.startswith("extra_")]
    cols, cell, top = 7, 150, 70
    rows = (len(names) + cols - 1) // cols
    try:
        from PIL import ImageFont
        title_font = ImageFont.load_default(size=30)
        label_font = ImageFont.load_default(size=13)
    except TypeError:
        title_font = label_font = None

    def board(k):
        sheet = Image.new("RGBA", (cols * cell, rows * cell + top + 10), (44, 14, 24, 255))
        d = ImageDraw.Draw(sheet)
        for y in range(0, sheet.height, 25):
            for x in range(0, sheet.width, 25):
                if (x // 25 + y // 25) % 2:
                    d.rectangle([x, y, x + 24, y + 24], fill=(58, 20, 32, 255))
        d.text((sheet.width // 2, 24), "kurenawi  |  MOUSE CURSOR", fill=(255, 236, 238, 255),
               font=title_font, anchor="mm", stroke_width=3, stroke_fill=(224, 16, 42, 255))
        for i, n in enumerate(names):
            fr = rendered[n][4]
            x, y = (i % cols) * cell + 11, (i // cols) * cell + top
            sheet.alpha_composite(fr[k % len(fr)], (x, y))
            d.text((x + 64, y + 136), n, fill=(255, 220, 225, 255), font=label_font, anchor="mm")
        return sheet

    board(0).save(os.path.join(OUT, "preview.png"))
    fr = [board(k).convert("RGB") for k in range(8)]
    fr[0].save(os.path.join(OUT, "preview.gif"), save_all=True, append_images=fr[1:], duration=100, loop=0)
    print("built", len(files), "cursors ->", OUT)


if __name__ == "__main__":
    main()
