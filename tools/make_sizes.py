#!/usr/bin/env python3
"""
make_sizes.py — サイト用スクショの3サイズ生成＋HTML の width/height 宣言との機械照合

なぜ:
    2026-08-22 に同名のスクリプトをセッション用 scratchpad に置いたまま失い、
    App Store 用の原本 1320×2868 も消えた（handoff_app「B の訂正」）。リポジトリに恒久保存する。

使い方（keepy-site のルートで）:
    python3 tools/make_sizes.py <原本.png(1320×2868)> <出力の基底パス>        # 例: images/ss_02_detail.png
    python3 tools/make_sizes.py <原本.jpg> images/ss_notification.jpg         # 拡張子は基底パスに従う（jpg 可）
    python3 tools/make_sizes.py --check                                        # 全ページの <img> 宣言と実寸を照合（ずれがあれば終了コード1）

寸法規則（2026-08-22 の実物から逆算・2026-09-02 実測で確認）:
    幅 750 / 422 / 211 の3枚＝ <basename>.<ext> / <basename>-422.<ext> / <basename>-211.<ext>
    高さ＝ 750 → images/ は 1630・img/manual/ は 1629（HTML の宣言に合わせる。1320×2868 の比では 1629.5）
          422 → 917・211 → 458（四捨五入）
    リサイズは LANCZOS・**シャープ処理はしない**（2026-08-05 に4回作り直した結論＝目視で Kentaro 確定）
⚠️ 原本は必ず `~/Desktop/Keepy/site_screenshots_<日付>/` 等の永続パスに残す（scratchpad に置かない）。
"""
import os, re, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_SIZE = (1320, 2868)
WIDTHS = (750, 422, 211)

def height_for(width, base_rel):
    if width == 750:
        return 1629 if base_rel.startswith("img/manual/") else 1630
    return round(SRC_SIZE[1] * width / SRC_SIZE[0])

def make(src, base_rel):
    img = Image.open(src)
    if img.size != SRC_SIZE:
        print(f"❌ 原本の寸法が {img.size}＝{SRC_SIZE} で撮り直す（引き伸ばさない）"); sys.exit(2)
    stem, ext = os.path.splitext(base_rel)
    out = []
    for w in WIDTHS:
        h = height_for(w, base_rel)
        dst = os.path.join(ROOT, stem + ("" if w == 750 else f"-{w}") + ext)
        im = img.convert("RGB") if ext.lower() in (".jpg", ".jpeg") else img
        im = im.resize((w, h), Image.LANCZOS)
        if ext.lower() in (".jpg", ".jpeg"): im.save(dst, quality=88, optimize=True)
        else: im.save(dst, optimize=True)
        out.append((os.path.relpath(dst, ROOT), w, h))
    for rel, w, h in out: print(f"✅ {rel}  {w}×{h}")
    print("次＝HTML の `?v=N` を src と srcset 全候補で上げる／alt と写っている画面を照合／index.html 通知なら translateY を測り直す")

IMG_TAG = re.compile(r'<img\b[^>]*>', re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')
SRCSET = re.compile(r'([^\s,]+)\s+(\d+)w')

def dims(rel):
    p = os.path.join(ROOT, rel.split("?")[0].lstrip("/"))
    return Image.open(p).size if os.path.exists(p) else None

def check():
    problems = 0; checked = 0
    for fn in sorted(os.listdir(ROOT)):
        if not fn.endswith(".html"): continue
        html = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        for tag in IMG_TAG.findall(html):
            a = dict(ATTR.findall(tag))
            src = a.get("src", "")
            if not src or src.startswith("http") or "width" not in a: continue
            d = dims(src)
            if d is None: print(f"❌ {fn}: {src} が無い"); problems += 1; continue
            checked += 1
            if (str(d[0]), str(d[1])) != (a["width"], a.get("height", "")):
                print(f"❌ {fn}: {src} 宣言 {a['width']}×{a.get('height','?')} / 実寸 {d[0]}×{d[1]}"); problems += 1
            for cand, w in SRCSET.findall(a.get("srcset", "")):
                cd = dims(cand)
                if cd is None: print(f"❌ {fn}: srcset {cand} が無い"); problems += 1; continue
                checked += 1
                if cd[0] != int(w): print(f"❌ {fn}: srcset {cand} は {cd[0]}px 幅（宣言 {w}w）"); problems += 1
    print(f"対象＝{ROOT} の *.html の <img>（width 宣言あり）＋srcset 候補・{checked} 枚 ／ 除外＝外部 URL・width 宣言なし")
    print("✅ 宣言と実寸は全部一致" if problems == 0 else f"❌ ずれ {problems} 件")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--check": check()
    elif len(sys.argv) == 3: make(sys.argv[1], sys.argv[2])
    else: print(__doc__); sys.exit(2)
