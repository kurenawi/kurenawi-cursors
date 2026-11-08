"""Guard for the kurenawi mouse-cursor pack built into dist/kurenawi-cursors.

Checks the built pack, which build_cursors.py writes by hand (no cursor library):
- every .cur is a type-2 file with 32/64/96/128 entries whose hotspots match hotspots.tsv x scale,
  and its 32-bit DIB pixels round-trip to the PNG export (alpha kept, not flattened);
- busy/working .ani are RIFF/ACON with an anih header and 8 decodable frames;
- install.inf lists the 17 Windows scheme roles and every file it names exists;
- the Mousecape .cape keeps the macOS 26 aliases ArrowS/IBeamS (without them Tahoe
  silently keeps the system arrow and I-beam), and covers the CoreCursor ids browsers use.

Run after building: python3 build_cursors.py && python3 make_test_page.py && python3 -m unittest discover -s tests
(needs pillow and numpy)
"""
import re
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "dist/kurenawi-cursors"
SITE = ROOT / "dist/site"
PY = [sys.executable, "-c"]

CHECK = textwrap.dedent(r"""
    import io, plistlib, re, struct, sys
    from pathlib import Path
    import numpy as np
    from PIL import Image
    pack = Path(sys.argv[1]); win = pack / "windows"
    hot = {l.split("\t")[1]: (int(l.split("\t")[2]), int(l.split("\t")[3]))
           for l in (pack / "hotspots.tsv").read_text().splitlines()}

    def check_cur(b, name, hx, hy, ref=None):
        res, typ, n = struct.unpack("<HHH", b[:6])
        assert (res, typ, n) == (0, 2, 4), (name, res, typ, n)
        for i in range(n):
            w, h, _, _, x, y, ln, off = struct.unpack("<BBBBHHII", b[6 + 16 * i:22 + 16 * i])
            w = w or 256; s = w // 32
            assert w == h == 32 * (i + 1), (name, w, h)
            assert (x, y) == (hx * s, hy * s), (name, w, x, y)
            size, bw, bh, planes, bpp = struct.unpack("<IiiHH", b[off:off + 16])
            assert (size, bw, bh, bpp) == (40, w, 2 * w, 32), (name, size, bw, bh, bpp)
            if ref is not None and w == 32:
                px = np.frombuffer(b[off + 40:off + 40 + w * w * 4], np.uint8).reshape(w, w, 4)[::-1][..., [2, 1, 0, 3]]
                assert np.array_equal(px, ref), name + " DIB != png"
                assert px[..., 3].max() == 255 and px[..., 3].min() == 0, name + " alpha"

    for f in sorted(win.glob("*.cur")):
        check_cur(f.read_bytes(), f.name, *hot[f.name],
                  ref=np.array(Image.open(pack / "png" / (f.stem + "@32.png")).convert("RGBA")))
    anis = sorted(win.glob("*.ani"))
    assert [a.name for a in anis] == ["busy.ani", "working.ani"], anis
    for f in anis:
        b = f.read_bytes()
        assert b[:4] == b"RIFF" and b[8:12] == b"ACON" and struct.unpack("<I", b[4:8])[0] == len(b) - 8
        i, frames, anih = 12, 0, None
        while i < len(b):
            tag, ln = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
            if tag == b"anih":
                anih = struct.unpack("<9I", b[i + 8:i + 44])
            if tag == b"LIST":
                assert b[i + 8:i + 12] == b"fram"
                j = i + 12
                while j < i + 8 + ln:
                    l2 = struct.unpack("<I", b[j + 4:j + 8])[0]
                    check_cur(b[j + 8:j + 8 + l2], f.name, *hot[f.name]); frames += 1
                    j += 8 + l2 + (l2 & 1)
            i += 8 + ln + (ln & 1)
        assert anih and anih[0] == 36 and anih[1] == frames == 8 and anih[8] & 1, (f.name, anih, frames)
    inf = (win / "install.inf").read_text()
    scheme = re.search(r'Schemes","%SCHEME_NAME%",,"([^"]+)"', inf).group(1).split(",")
    assert len(scheme) == 17, len(scheme)
    for p in scheme:
        assert (win / p.split("\\")[-1]).exists(), p
    cape = plistlib.loads((pack / "macos/kurenawi.cape").read_bytes())
    cur = cape["Cursors"]
    for k in ("com.apple.coregraphics.Arrow", "com.apple.coregraphics.ArrowS",
              "com.apple.coregraphics.IBeam", "com.apple.coregraphics.IBeamS", "com.apple.coregraphics.Wait"):
        assert k in cur, k
    # CoreCursor ids that browsers ask macOS for (Chromium ui/base/cocoa/cursor_utils.mm, which
    # matches WebKit). The first cape mapped Mousecape's labels instead and missed crosshair (20)
    # and move (39), so those two kept the system cursor.
    css = {"crosshair": 20, "move": 39, "copy": 5, "alias": 2, "cell": 41, "zoom-in": 42,
           "zoom-out": 43, "not-allowed": 3, "progress": 4, "wait": 4, "pointer": 13, "help": 40,
           "vertical-text": 26, "context-menu": 24, "grab": 12, "grabbing": 11,
           "col-resize": 19, "row-resize": 23}
    for kw, n in css.items():
        assert f"com.apple.cursor.{n}" in cur, (kw, n)
    for k in ("com.apple.coregraphics.Copy", "com.apple.coregraphics.Alias"):
        assert k in cur, k
    w = cur["com.apple.coregraphics.Wait"]
    im = Image.open(io.BytesIO(w["Representations"][1]))
    assert w["FrameCount"] == 8 and im.size == (64, 64 * 8), (w["FrameCount"], im.size)
    print("ok")
""")


class CursorPackTest(unittest.TestCase):
    def test_pack_is_valid(self):
        r = subprocess.run(PY + [CHECK, str(PACK)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok", r.stdout)

    def test_test_page_drag_sets_cursor_itself(self):
        # A native HTML drag refused by its target shows no forbidden cursor on Mac, so the
        # first page's "ここは受け付けない枠" never changed. The demo must drive the cursor itself.
        page = (PACK / "cursor-test.html").read_text()
        self.assertNotIn('draggable="true"', page)
        self.assertNotIn("dataTransfer", page)
        for eff in ("copy", "alias", "no-drop"):
            self.assertIn(f'data-effect="{eff}"', page)
        self.assertIn("!important", page)  # global cursor override while dragging

    def test_demo_has_ogp_card(self):
        # Link previews need absolute og/twitter image URLs and a 1200x630 card in the site.
        page = (SITE / "index.html").read_text()
        site = "https://kurenawi.github.io/kurenawi-cursors/"
        for tag in ('property="og:title"', 'property="og:description"', f'property="og:url" content="{site}"',
                    f'property="og:image" content="{site}og.png"', 'name="twitter:card" content="summary_large_image"',
                    f'name="twitter:image" content="{site}og.png"'):
            self.assertIn(tag, page)
        r = subprocess.run(PY + ["from PIL import Image; import sys; print(Image.open(sys.argv[1]).size)",
                                 str(SITE / "og.png")], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "(1200, 630)", r.stderr)

    def test_demo_and_test_page_are_separate(self):
        # The public demo must show kurenawi's cursors to people who have NOT installed the
        # pack, so every cursor there is an image cursor. The keyword-based install check is
        # local only: it must not be deployed, and it carries no OGP card.
        page = (SITE / "index.html").read_text()
        bare = re.findall(r"cursor:\s*([a-z-]+)\s*(?:!important)?\s*[;}]", page)
        self.assertEqual([b for b in bare if b != "inherit"], [])
        tiles = re.findall(r'<div class="tile (c-[a-z0-9_-]+)"', page)
        self.assertEqual(len(tiles), 27)
        for cls in tiles:
            rule = re.search(r"\." + re.escape(cls) + r"[,{][^}]*\}", page)
            self.assertTrue(rule and "url(png/" in rule.group(0), cls)
        for name in ("work_figures", "windows", "macos", "cursor-test.html"):
            self.assertFalse((SITE / name).exists(), name)
        test_page = (PACK / "cursor-test.html").read_text()
        self.assertNotIn("og:image", test_page)
        self.assertIn("cursor:crosshair", test_page.replace(" ", ""))
        wf = (ROOT / ".github/workflows/pages.yml").read_text()
        self.assertRegex(wf, r"path:\s*dist/site\b")

if __name__ == "__main__":
    unittest.main()
