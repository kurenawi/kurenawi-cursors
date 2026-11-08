#!/usr/bin/env python3
"""Copy the launch video into docs/ and make its two stills.

docs/launch.mp4         the Discord-size encode (1080p, < 10 MB), served by Pages
docs/launch_poster.jpg  a title frame for <video poster> on the demo page (native controls draw the play button)
docs/launch_play.jpg    the same frame with a play button, for the README (GitHub cannot play repo videos inline)

usage: python3 make_launch_assets.py <path/to/kurenawi_cursors_launch_discord.mp4> [time_s]
The video is built in lilpacy/hermes-workspace assets/video/2026-11-10_cursors_launch.
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")


def main():
    src = sys.argv[1]
    t = sys.argv[2] if len(sys.argv) > 2 else "12.5"
    shutil.copyfile(src, os.path.join(DOCS, "launch.mp4"))
    frame = os.path.join(DOCS, "_frame.png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", t, "-i", src, "-frames:v", "1", "-vf", "scale=1280:-2", frame],
                   check=True)
    im = Image.open(frame).convert("RGB")
    os.remove(frame)
    im.save(os.path.join(DOCS, "launch_poster.jpg"), quality=85)
    w, h = im.size
    ov = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))     # 2x supersampled play button
    d = ImageDraw.Draw(ov)
    cx, cy, r = w, h, 110
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 6, 10, 210), outline=(255, 255, 255, 255), width=8)   # dark disc: the hero arrow behind is red
    d.polygon([(cx - 34, cy - 54), (cx - 34, cy + 54), (cx + 60, cy)], fill=(255, 255, 255, 255))
    ov = ov.resize((w, h), Image.LANCZOS)
    play = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    play.save(os.path.join(DOCS, "launch_play.jpg"), quality=85)
    for n in ("launch.mp4", "launch_poster.jpg", "launch_play.jpg"):
        print(n, os.path.getsize(os.path.join(DOCS, n)))


if __name__ == "__main__":
    main()
