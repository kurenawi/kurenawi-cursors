#!/usr/bin/env python3
"""Write kurenawi-cursors/cursor-test.html: hover tiles for every cursor pattern.

Section 1 uses plain CSS cursor keywords, so the browser asks macOS for its own system
cursor and Mousecape's replacement shows (when the cape maps that cursor).
Section 2 uses the pack PNGs through CSS url(), so roles that macOS has no slot for
(Windows-only roles and extras) can still be seen live.

usage: python3 make_test_page.py   (after build_cursors.py; writes index.html too)
"""
import base64
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "dist", "kurenawi-cursors")

# (css keyword, kurenawi role or None, Japanese label, where it appears naturally on macOS)
SYSTEM = [
    ("default", "normal", "通常", "いつもの矢印"),
    ("pointer", "link", "リンク", "リンクやボタンの上"),
    ("text", "text", "文字選択", "入力欄・本文の上"),
    ("vertical-text", "text", "縦書きの文字選択", "縦書きテキストの上"),
    ("context-menu", "normal", "コンテキストメニュー", "control押しながら（アプリによる）"),
    ("help", "help", "ヘルプ", "ほぼこのページでしか見ない"),
    ("progress", "working", "処理中（操作できる）", "読み込み中のページ"),
    ("wait", "busy", "待ち", "アプリが固まったとき（虹色ボールの代わり）"),
    ("crosshair", "precision", "精密選択", "⌘⇧4のスクリーンショット範囲選択"),
    ("not-allowed", "unavailable", "利用不可", "ドロップできない場所へドラッグ"),
    ("no-drop", "unavailable", "ドロップ不可", "ドロップできない場所へドラッグ"),
    ("move", "move", "移動", "移動できる要素の上"),
    ("grab", "move", "つかめる（開いた手）", "地図・画像のドラッグ前"),
    ("grabbing", "move", "つかんでいる（閉じた手）", "地図・画像をドラッグ中"),
    ("ns-resize", "vertical", "上下リサイズ", "ウインドウの上下端"),
    ("n-resize", "vertical", "上へリサイズ", "最小サイズのウインドウ端"),
    ("s-resize", "vertical", "下へリサイズ", "最小サイズのウインドウ端"),
    ("row-resize", "vertical", "行の高さ変更", "表・分割ペインの境界"),
    ("ew-resize", "horizontal", "左右リサイズ", "ウインドウの左右端"),
    ("e-resize", "horizontal", "右へリサイズ", "最小サイズのウインドウ端"),
    ("w-resize", "horizontal", "左へリサイズ", "最小サイズのウインドウ端"),
    ("col-resize", "horizontal", "列の幅変更", "表・Finderの列の境界"),
    ("nwse-resize", "diagonal1", "斜めリサイズ ↖↘", "ウインドウの左上・右下の角"),
    ("nw-resize", "diagonal1", "左上へリサイズ", "ウインドウの左上の角"),
    ("se-resize", "diagonal1", "右下へリサイズ", "ウインドウの右下の角"),
    ("nesw-resize", "diagonal2", "斜めリサイズ ↗↙", "ウインドウの右上・左下の角"),
    ("ne-resize", "diagonal2", "右上へリサイズ", "ウインドウの右上の角"),
    ("sw-resize", "diagonal2", "左下へリサイズ", "ウインドウの左下の角"),
    ("copy", "copy", "コピー（＋付き）", "optionを押しながらドラッグ"),
    ("alias", "alias", "エイリアス作成", "⌘⌥を押しながらドラッグ"),
    ("cell", "cell", "セル選択", "スプレッドシート"),
    ("zoom-in", "zoomin", "ズームイン", "画像ビューア"),
    ("zoom-out", "zoomout", "ズームアウト", "画像ビューア"),
]

EXTRA = [
    ("handwriting", "手書き"), ("alternate", "代替選択"), ("location", "位置選択"),
    ("person", "人の選択"), ("extra_wave", "おまけ：バイバイ"), ("extra_wink", "おまけ：ウインク"), ("extra_sleepy", "おまけ：ねむい"),
    ("extra_tea", "おまけ：お茶"), ("extra_hooray", "おまけ：バンザイ"),
]


def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def main():
    hot = {}
    with open(os.path.join(PACK, "hotspots.tsv")) as f:
        for line in f:
            name, _, x, y = line.rstrip("\n").split("\t")
            hot[name] = (int(x), int(y))

    def png(role, size):
        return data_uri(os.path.join(PACK, "png", f"{role}@{size}.png"))

    tiles = []
    for kw, role, label, where in SYSTEM:
        thumb = f'<img src="{png(role, 64)}" alt="">' if role else '<span class="sys">macOS標準のまま</span>'
        tiles.append(
            f'<div class="tile" style="cursor:{kw}"><div class="kw">{kw}</div>'
            f'<div class="lb">{html.escape(label)}</div>{thumb}'
            f'<div class="wh">{html.escape(where)}</div></div>')
    extras = []
    for role, label in EXTRA:
        x, y = hot[role]
        c1, c2 = png(role, 32), png(role, 64)
        style = (f"cursor:url({c1}) {x} {y}, auto;"
                 f"cursor:-webkit-image-set(url({c1}) 1x, url({c2}) 2x) {x} {y}, auto;")
        extras.append(
            f'<div class="tile" style="{style}"><div class="kw">{role}</div>'
            f'<div class="lb">{html.escape(label)}</div><img src="{png(role, 64)}" alt="">'
            f'<div class="wh">Windows専用・おまけ（このページだけ）</div></div>')

    page = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>kurenawi cursor demo</title>
<style>
body{{margin:0;padding:24px;background:#2c0e18;color:#ffe6ea;font:14px/1.5 -apple-system,"Hiragino Sans",sans-serif}}
h1{{margin:0 0 4px;color:#fff;text-shadow:0 0 6px #e0102a}} h2{{margin:28px 0 6px;color:#ffb3c0}}
p{{margin:4px 0;color:#f3c6cf}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}}
.tile{{background:#3a1420;border:1px solid #5a2333;border-radius:10px;padding:10px;min-height:150px;
display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center}}
.tile:hover{{border-color:#e0102a;background:#4a1828}}
.kw{{font:600 13px ui-monospace,Menlo,monospace;color:#fff}} .lb{{font-size:13px}}
.wh{{font-size:11px;color:#d79aa7}} img{{width:64px;height:64px;image-rendering:pixelated}}
.zone{{background:#3a1420;border:2px dashed #7a3344;border-radius:10px;padding:16px;min-height:70px;text-align:center}}
.chip{{display:inline-block;background:#e0102a;color:#fff;border-radius:8px;padding:8px 14px;cursor:grab;user-select:none;touch-action:none}}
#ghost{{position:fixed;display:none;pointer-events:none;opacity:.85;z-index:9;padding:4px 8px}}
.zone.hot{{border-color:#e0102a;background:#4a1828}} .out{{margin-top:6px;min-height:20px}}
.shake{{animation:shake .35s}} @keyframes shake{{25%{{transform:translateX(-6px)}}75%{{transform:translateX(6px)}}}}
textarea{{width:100%;box-sizing:border-box;height:80px;background:#1d0910;color:#ffe6ea;border:1px solid #5a2333;border-radius:8px;resize:both;padding:8px}}
.sys{{font-size:11px;color:#9a6a76;height:64px;display:flex;align-items:center}}
</style></head><body>
<h1>kurenawi cursor demo</h1>
<p>マスに乗せると、そのカーソルに変わるよ。小さい絵は「こうなるはず」の見本。</p>
<p>配布: <a href="https://github.com/kurenawi/kurenawi-cursors/releases/latest" style="color:#fff">GitHub Releases（Windows / macOS / PNG のzip）</a> ・ <a href="macos/kurenawi.cape" download style="color:#fff">kurenawi.cape だけ落とす</a> ・ <a href="https://github.com/kurenawi/kurenawi-cursors#readme" style="color:#fff">インストール手順</a></p>
<h2>macOSのカーソル（Mousecapeで置き換わる）</h2>
<p>ブラウザがmacOSのカーソルを呼ぶから、Mousecapeの置き換えがそのまま見える。「macOS標準のまま」はcapeで置き換えていない種類。</p>
<div class="grid">{''.join(tiles)}</div>
<h2>実際に触って確かめる</h2>
<p>紅いチップをつかんで、下の枠の上まで運んでみて。枠に乗るとカーソルがコピー・エイリアス・ドロップ不可に変わって、離すと結果が出るよ。テキスト欄は右下の角をつかむと大きさを変えられる。</p>
<div class="grid">
<div class="zone" id="home"><span class="chip" id="chip">🍁 つかんでね</span></div>
<div class="zone" data-effect="copy">ここに落とす → コピー<div class="out"></div></div>
<div class="zone" data-effect="alias">ここに落とす → エイリアス<div class="out"></div></div>
<div class="zone" data-effect="no-drop">ここは受け付けない枠<div class="out"></div></div>
</div>
<div id="ghost" class="chip">🍁</div>
<style id="dragcursor"></style>
<p style="margin-top:10px"><textarea>ここをクリックすると文字選択カーソル。右下の角でリサイズ。</textarea></p>
<script>
// Pointer-based drag: the page sets the cursor itself, because a native HTML drag that the
// target refuses never shows the forbidden cursor on Mac (Chromium: Dnd cursors "do not apply on Mac").
const chip = document.getElementById("chip"), ghost = document.getElementById("ghost");
const cur = document.getElementById("dragcursor");
let dragging = false, overZone = null;
const setCursor = c => {{ cur.textContent = c ? `*{{cursor:${{c}} !important}}` : ""; }};
chip.addEventListener("pointerdown", e => {{
  e.preventDefault(); dragging = true; ghost.style.display = "inline-block"; move(e);
}});
function move(e) {{
  if (!dragging) return;
  ghost.style.left = (e.clientX + 14) + "px"; ghost.style.top = (e.clientY + 14) + "px";
  const el = document.elementFromPoint(e.clientX, e.clientY);
  const z = el && el.closest(".zone[data-effect]");
  document.querySelectorAll(".zone").forEach(x => x.classList.toggle("hot", x === z));
  overZone = z;
  setCursor(z ? z.dataset.effect : "grabbing");
}}
document.addEventListener("pointermove", move);
document.addEventListener("pointerup", () => {{
  if (!dragging) return;
  dragging = false; ghost.style.display = "none"; setCursor("");
  document.querySelectorAll(".zone").forEach(x => x.classList.remove("hot"));
  if (!overZone) return;
  const out = overZone.querySelector(".out"), eff = overZone.dataset.effect;
  if (eff === "no-drop") {{ out.textContent = "🙅 受け付けません"; overZone.classList.remove("shake"); void overZone.offsetWidth; overZone.classList.add("shake"); }}
  else out.textContent += eff === "copy" ? "🍁" : "↪🍁 ";
  overZone = null;
}});
</script>
<h2>macOSに出番がない絵（このページで画像として表示）</h2>
<p>macOSには対応するカーソルがないから、普段は出てこない。ここだけ画像カーソルで見せてる。</p>
<div class="grid">{''.join(extras)}</div>
</body></html>
"""
    for name in ("cursor-test.html", "index.html"):
        out = os.path.join(PACK, name)
        with open(out, "w") as f:
            f.write(page)
    print(out, len(page))


if __name__ == "__main__":
    main()
