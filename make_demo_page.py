#!/usr/bin/env python3
"""Write the PUBLIC demo site into dist/site/ (deployed to GitHub Pages).

Every cursor on the page is a CSS image cursor (url()/image-set() of the pack PNGs), so
visitors see kurenawi's cursors without installing anything, on Windows, macOS or Linux.
The local install check is make_test_page.py; it is not published.

usage: python3 build_cursors.py && python3 make_demo_page.py
"""
import html
import os
import shutil

import build_cursors as bc

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "dist", "kurenawi-cursors")
SITE_DIR = os.path.join(HERE, "dist", "site")
SITE = "https://kurenawi.github.io/kurenawi-cursors/"
REPO = "https://github.com/kurenawi/kurenawi-cursors"
TITLE = "kurenawi cursor demo"
DESC = ("紅（くれない）のピクセルアート・マウスカーソル。インストールしなくても、"
        "このページでWindows / macOSでの見え方を全パターン試せます。")

# role, label, where it shows up
ROLES = [
    ("normal", "通常", "いつもの矢印"),
    ("link", "リンク", "リンクやボタンの上"),
    ("text", "テキスト選択", "入力欄や本文の上"),
    ("help", "ヘルプ", "ヘルプ付きの選択"),
    ("working", "バックグラウンドで作業中", "読み込み中でも操作できるとき"),
    ("busy", "待ち", "アプリが応答待ちのとき"),
    ("precision", "精密選択", "範囲選択・スクリーンショット"),
    ("handwriting", "手書き", "ペン入力"),
    ("unavailable", "利用不可", "ドロップや操作ができない場所"),
    ("vertical", "上下に拡大/縮小", "ウインドウの上下の端"),
    ("horizontal", "左右に拡大/縮小", "ウインドウの左右の端・列の境界"),
    ("diagonal1", "斜めに拡大/縮小 ↖↘", "ウインドウの左上・右下の角"),
    ("diagonal2", "斜めに拡大/縮小 ↗↙", "ウインドウの右上・左下の角"),
    ("move", "移動", "移動できるもの・つかんでいるとき"),
    ("alternate", "代替選択", "Windowsの代替選択"),
    ("location", "位置の選択", "地図などで場所を選ぶとき"),
    ("person", "人の選択", "連絡先などで人を選ぶとき"),
    ("copy", "コピー", "optionを押しながらドラッグ"),
    ("alias", "エイリアス", "⌘⌥を押しながらドラッグ"),
    ("cell", "セル選択", "スプレッドシート"),
    ("zoomin", "ズームイン", "画像を拡大できるとき"),
    ("zoomout", "ズームアウト", "画像を縮小できるとき"),
    ("extra_wink", "おまけ：ウインク", "好きな場所に割り当て"),
    ("extra_sleepy", "おまけ：ねむい", "好きな場所に割り当て"),
    ("extra_tea", "おまけ：お茶", "好きな場所に割り当て"),
    ("extra_hooray", "おまけ：バンザイ", "好きな場所に割り当て"),
    ("extra_wave", "おまけ：バイバイ", "好きな場所に割り当て"),
]
ANIM = {"working": 8, "busy": 8}


def load_hotspots():
    hot = {}
    with open(os.path.join(PACK, "hotspots.tsv")) as f:
        for line in f:
            name, _, x, y = line.rstrip("\n").split("\t")
            hot[name] = (int(x), int(y))
    return hot


def cursor_decls(png32, png64, hx, hy, fallback, important=False):
    imp = " !important" if important else ""
    return (f"cursor:url({png32}) {hx} {hy},{fallback}{imp};"
            f"cursor:-webkit-image-set(url({png32}) 1x,url({png64}) 2x) {hx} {hy},{fallback}{imp};"
            f"cursor:image-set(url({png32}) 1x,url({png64}) 2x) {hx} {hy},{fallback}{imp};")


FALLBACK = {"link": "pointer", "text": "text", "help": "help", "working": "progress", "busy": "wait",
            "precision": "crosshair", "unavailable": "not-allowed", "vertical": "ns-resize",
            "horizontal": "ew-resize", "diagonal1": "nwse-resize", "diagonal2": "nesw-resize",
            "move": "move", "copy": "copy", "alias": "alias", "cell": "cell", "zoomin": "zoom-in",
            "zoomout": "zoom-out"}


def where_tags(role):
    win = {r for _, r in bc.WIN}
    mac = set(bc.MAC.values())
    tags = []
    if role.startswith("extra_"):
        return ["おまけ"]
    if role in win:
        tags.append("Windows")
    if role in mac:
        tags.append("macOS")
    return tags


def css(hot):
    out = ["body *{cursor:inherit}"]  # beat UA defaults; .c-* classes and a[href]/inputs override
    for role, _, _ in ROLES:
        hx, hy = hot[role]
        fb = FALLBACK.get(role, "auto")
        if role in ANIM:
            for k in range(ANIM[role]):
                a, b = f"png/anim/{role}@32_{k}.png", f"png/anim/{role}@64_{k}.png"
                out.append(f".c-{role}-{k}{{{cursor_decls(a, b, hx, hy, fb)}}}")
                out.append(f"html.g-{role}-{k},html.g-{role}-{k} *{{{cursor_decls(a, b, hx, hy, fb, True)}}}")
            role_png = (f"png/anim/{role}@32_0.png", f"png/anim/{role}@64_0.png")
        else:
            role_png = (f"png/{role}@32.png", f"png/{role}@64.png")
        extra = {"link": ",a[href]", "text": ",input,textarea"}.get(role, "")
        out.append(f".c-{role}{extra}{{{cursor_decls(*role_png, hx, hy, fb)}}}")
        out.append(f"html.g-{role},html.g-{role} *{{{cursor_decls(*role_png, hx, hy, fb, True)}}}")
    return "\n".join(out)


def tiles(hot):
    out = []
    for role, label, where in ROLES:
        tags = "".join(f'<span class="tag">{t}</span>' for t in where_tags(role))
        if role in ANIM:
            cls, img = f"c-{role}-0", f'<img src="png/anim/{role}@64_0.png" data-anim="{role}" alt="">'
        else:
            cls, img = f"c-{role}", f'<img src="png/{role}@64.png" alt="">'
        out.append(f'<div class="tile {cls}" data-anim-cursor="{role if role in ANIM else ""}">'
                   f'<div class="lb">{html.escape(label)}</div>{img}'
                   f'<div class="wh">{html.escape(where)}</div><div class="tags">{tags}</div></div>')
    return "".join(out)


def page(hot):
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="kurenawi cursors">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="kurenawi cursor demo: 14 pixel-art mouse cursors with a chibi kurenawi">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}og.png">
<style>
{css(hot)}
body{{margin:0;padding:24px;background:#2c0e18;color:#ffe6ea;font:14px/1.6 -apple-system,"Hiragino Sans","Yu Gothic UI","Segoe UI",sans-serif}}
main{{max-width:1100px;margin:0 auto}}
h1{{margin:0 0 6px;color:#fff;text-shadow:0 0 6px #e0102a}} h2{{margin:32px 0 6px;color:#ffb3c0}}
p{{margin:4px 0;color:#f3c6cf}} a{{color:#fff}}
.links a{{display:inline-block;margin:6px 8px 0 0;padding:8px 14px;border-radius:8px;background:#e0102a;color:#fff;text-decoration:none;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}}
.tile{{background:#3a1420;border:1px solid #5a2333;border-radius:10px;padding:10px;min-height:150px;
display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center}}
.tile:hover{{border-color:#e0102a;background:#4a1828}}
.lb{{font-size:13px;font-weight:600;color:#fff}} .wh{{font-size:11px;color:#d79aa7}}
.tile img{{width:64px;height:64px;image-rendering:pixelated}}
.tag{{display:inline-block;font-size:10px;margin:0 2px;padding:0 6px;border-radius:6px;background:#5a2333;color:#ffd0d8}}
.box{{background:#3a1420;border:1px solid #5a2333;border-radius:10px;padding:14px}}
.row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.zone{{background:#3a1420;border:2px dashed #7a3344;border-radius:10px;padding:16px;min-height:70px;text-align:center}}
.zone.hot{{border-color:#e0102a;background:#4a1828}} .out{{margin-top:6px;min-height:20px}}
.chip{{display:inline-block;background:#e0102a;color:#fff;border-radius:8px;padding:8px 14px;user-select:none;touch-action:none}}
#ghost{{position:fixed;display:none;pointer-events:none;opacity:.85;z-index:9;padding:4px 8px}}
.shake{{animation:shake .35s}} @keyframes shake{{25%{{transform:translateX(-6px)}}75%{{transform:translateX(6px)}}}}
input,textarea{{width:100%;box-sizing:border-box;background:#1d0910;color:#ffe6ea;border:1px solid #5a2333;border-radius:8px;padding:8px;font:inherit}}
button{{background:#e0102a;color:#fff;border:0;border-radius:8px;padding:8px 14px;font:inherit;font-weight:600}}
#sel{{position:relative;height:150px;background:#1d0910;border-radius:8px;overflow:hidden;user-select:none}}
#selrect{{position:absolute;border:2px solid #e0102a;background:rgba(224,16,42,.15);display:none}}
#zoomwrap{{height:150px;overflow:hidden;border-radius:8px;background:#1d0910;display:flex;align-items:center;justify-content:center}}
#zoomimg{{width:220px;image-rendering:pixelated;transition:transform .2s}} #zoomimg.zoomed{{transform:scale(2.4)}}
#resizable{{position:relative;width:220px;height:110px;background:#1d0910;border-radius:8px;border:1px solid #5a2333}}
.h{{position:absolute;background:transparent}}
#h-e{{right:-6px;top:10px;bottom:10px;width:12px}} #h-s{{bottom:-6px;left:10px;right:10px;height:12px}}
#h-se{{right:-8px;bottom:-8px;width:16px;height:16px;background:#e0102a;border-radius:4px}}
#h-ne{{right:-8px;top:-8px;width:16px;height:16px;background:#7a3344;border-radius:4px}}
#cells{{border-collapse:collapse}} #cells td{{width:44px;height:26px;border:1px solid #5a2333;background:#1d0910}}
#cells td.on{{background:#e0102a}}
footer{{margin-top:36px;font-size:12px;color:#b98390}}
</style></head>
<body class="c-normal">
<main>
<h1>{TITLE}</h1>
<p>紅（くれない）のピクセルアート・マウスカーソル。<b>インストールしなくても、このページの中ではくれないのカーソルになります</b>。Windows・macOSのどちらで開いても同じ見た目です。</p>
<div class="links">
<a class="c-link" href="{REPO}/releases/latest">ダウンロード（Windows / macOS）</a>
<a class="c-link" href="{REPO}#readme">インストール手順</a>
</div>

<h2>全カーソル</h2>
<p>マスに乗せると、そのカーソルに変わります。タグはインストール後にOSが自動で使う場所（おまけは自分で割り当てます）。</p>
<div class="grid">{tiles(hot)}</div>

<h2>触ってみる</h2>
<div class="row">
<div class="box">
<p><b>リンクと文字入力</b></p>
<p><a class="c-link" href="#top">リンクの上</a>・<button class="c-link" id="load">読み込んでみる</button></p>
<p style="margin-top:8px"><input class="c-text" value="ここは文字選択のカーソル"></p>
<p style="font-size:12px" id="loadmsg">ボタンを押すと、待ち → 作業中のアニメーションを再生します。</p>
</div>
<div class="box">
<p><b>範囲選択</b>（精密選択）</p>
<div id="sel" class="c-precision"><div id="selrect"></div></div>
</div>
<div class="box">
<p><b>ズーム</b>（クリックで拡大・縮小）</p>
<div id="zoomwrap"><img id="zoomimg" class="c-zoomin" src="png/normal@128.png" alt=""></div>
</div>
<div class="box">
<p><b>大きさを変える</b>（右端・下端・角をドラッグ）</p>
<div style="padding:8px 0 16px"><div id="resizable"><div class="h c-horizontal" id="h-e"></div><div class="h c-vertical" id="h-s"></div><div class="h c-diagonal1" id="h-se"></div><div class="h c-diagonal2" id="h-ne"></div></div></div>
</div>
<div class="box">
<p><b>セル選択</b>（クリックで塗る）</p>
<table id="cells" class="c-cell">{"".join("<tr>" + "<td></td>" * 5 + "</tr>" for _ in range(4))}</table>
</div>
<div class="box">
<p><b>ヘルプ・利用不可</b></p>
<p><span class="c-help" style="border-bottom:1px dotted #ffb3c0">？ここにヘルプ</span></p>
<p style="margin-top:8px"><button class="c-unavailable" disabled style="opacity:.5">押せないボタン</button></p>
</div>
</div>

<h2>ドラッグ＆ドロップ</h2>
<p>紅いチップをつかんで枠まで運んでみて。枠によってコピー・エイリアス・ドロップ不可に変わります。</p>
<div class="grid">
<div class="zone"><span class="chip c-move" id="chip">🍁 つかんでね</span></div>
<div class="zone" data-effect="copy">ここに落とす → コピー<div class="out"></div></div>
<div class="zone" data-effect="alias">ここに落とす → エイリアス<div class="out"></div></div>
<div class="zone" data-effect="unavailable">ここは受け付けない枠<div class="out"></div></div>
</div>
<div id="ghost" class="chip">🍁</div>

<footer>
カーソル画像: CC BY-NC 4.0 ・ コード: MIT ・ ちびキャラはAIで生成した絵を加工しています ・
レイアウトは <a href="https://x.com/crazyghsot/status/2119293841035698375">@crazyghsot さんの Momonga カーソル</a> を参考にしました（絵は使っていません）・
<a class="c-link" href="{REPO}">GitHub</a>
</footer>
</main>
<script>
const root = document.documentElement;
let global = null;  // role currently forced on the whole page
function setGlobal(cls) {{
  if (global) root.classList.remove(global);
  global = cls; if (cls) root.classList.add(cls);
}}
// animated cursors: swap frame classes every 100 ms
const ANIM = {{working: 8, busy: 8}};
let frame = 0, globalAnim = null;
setInterval(() => {{
  frame = (frame + 1) % 8;
  document.querySelectorAll("[data-anim-cursor]").forEach(el => {{
    const r = el.dataset.animCursor; if (!r) return;
    el.classList.remove(`c-${{r}}-${{(frame + 7) % 8}}`); el.classList.add(`c-${{r}}-${{frame}}`);
  }});
  document.querySelectorAll("img[data-anim]").forEach(img => {{
    img.src = `png/anim/${{img.dataset.anim}}@64_${{frame}}.png`;
  }});
  if (globalAnim) setGlobal(`g-${{globalAnim}}-${{frame}}`);
}}, 100);
// load button: busy -> working
document.getElementById("load").addEventListener("click", () => {{
  const msg = document.getElementById("loadmsg");
  globalAnim = "busy"; msg.textContent = "待ち…";
  setTimeout(() => {{ globalAnim = "working"; msg.textContent = "バックグラウンドで作業中…"; }}, 1600);
  setTimeout(() => {{ globalAnim = null; setGlobal(null); msg.textContent = "完了！"; }}, 3200);
}});
// range selection
const sel = document.getElementById("sel"), rect = document.getElementById("selrect");
let s0 = null;
sel.addEventListener("pointerdown", e => {{
  const b = sel.getBoundingClientRect(); s0 = [e.clientX - b.left, e.clientY - b.top];
  rect.style.display = "block"; Object.assign(rect.style, {{left: s0[0] + "px", top: s0[1] + "px", width: 0, height: 0}});
  sel.setPointerCapture(e.pointerId);
}});
sel.addEventListener("pointermove", e => {{
  if (!s0) return; const b = sel.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
  Object.assign(rect.style, {{left: Math.min(x, s0[0]) + "px", top: Math.min(y, s0[1]) + "px",
    width: Math.abs(x - s0[0]) + "px", height: Math.abs(y - s0[1]) + "px"}});
}});
sel.addEventListener("pointerup", () => {{ s0 = null; }});
// zoom
const zi = document.getElementById("zoomimg");
zi.addEventListener("click", () => {{
  const z = zi.classList.toggle("zoomed");
  zi.classList.toggle("c-zoomin", !z); zi.classList.toggle("c-zoomout", z);
}});
// resize handles
const box = document.getElementById("resizable");
for (const [id, dx, dy, cls] of [["h-e", 1, 0, "g-horizontal"], ["h-s", 0, 1, "g-vertical"],
                                  ["h-se", 1, 1, "g-diagonal1"], ["h-ne", 1, -1, "g-diagonal2"]]) {{
  const h = document.getElementById(id);
  h.addEventListener("pointerdown", e => {{
    e.preventDefault(); const w0 = box.offsetWidth, h0 = box.offsetHeight, x0 = e.clientX, y0 = e.clientY;
    setGlobal(cls);
    const mv = ev => {{
      if (dx) box.style.width = Math.max(80, w0 + (ev.clientX - x0)) + "px";
      if (dy) box.style.height = Math.max(50, h0 + dy * (ev.clientY - y0)) + "px";
    }};
    const up = () => {{ setGlobal(null); document.removeEventListener("pointermove", mv); document.removeEventListener("pointerup", up); }};
    document.addEventListener("pointermove", mv); document.addEventListener("pointerup", up);
  }});
}}
// cells
document.querySelectorAll("#cells td").forEach(td => td.addEventListener("click", () => td.classList.toggle("on")));
// drag and drop (pointer based, so the page controls the cursor)
const chip = document.getElementById("chip"), ghost = document.getElementById("ghost");
let dragging = false, overZone = null;
chip.addEventListener("pointerdown", e => {{ e.preventDefault(); dragging = true; ghost.style.display = "inline-block"; move(e); }});
function move(e) {{
  if (!dragging) return;
  ghost.style.left = (e.clientX + 14) + "px"; ghost.style.top = (e.clientY + 14) + "px";
  const el = document.elementFromPoint(e.clientX, e.clientY);
  const z = el && el.closest(".zone[data-effect]");
  document.querySelectorAll(".zone").forEach(x => x.classList.toggle("hot", x === z));
  overZone = z; setGlobal(z ? `g-${{z.dataset.effect}}` : "g-move");
}}
document.addEventListener("pointermove", move);
document.addEventListener("pointerup", () => {{
  if (!dragging) return;
  dragging = false; ghost.style.display = "none"; setGlobal(null);
  document.querySelectorAll(".zone").forEach(x => x.classList.remove("hot"));
  if (!overZone) return;
  const out = overZone.querySelector(".out"), eff = overZone.dataset.effect;
  if (eff === "unavailable") {{ out.textContent = "🙅 受け付けません"; overZone.classList.remove("shake"); void overZone.offsetWidth; overZone.classList.add("shake"); }}
  else out.textContent += eff === "copy" ? "🍁" : "↪🍁 ";
  overZone = null;
}});
</script>
</body></html>
"""


def main():
    hot = load_hotspots()
    if os.path.isdir(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    shutil.copytree(os.path.join(PACK, "png"), os.path.join(SITE_DIR, "png"))
    shutil.copyfile(os.path.join(HERE, "docs", "og.png"), os.path.join(SITE_DIR, "og.png"))
    with open(os.path.join(SITE_DIR, "index.html"), "w") as f:
        f.write(page(hot))
    print(os.path.join(SITE_DIR, "index.html"))


if __name__ == "__main__":
    main()
