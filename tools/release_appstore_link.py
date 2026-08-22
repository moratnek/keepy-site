#!/usr/bin/env python3
"""App Store 審査通過後に、サイトのダウンロード導線を一括で「公開状態」にする。

なぜスクリプトにするか
    リリース当日に手作業でやると、置換そのものより **付随する3つを忘れる** 方が怖い。
    実際 README は href の差し替えしか書いておらず、そのとおりにやると
    トップのボタン2つは**灰色のまま押せず**、全ページのラベルが「（準備中）」のまま残る。

やること（`<a ... data-appstore ...>` だけが対象）
    ① href="#" → 実 URL
    ② class の ` is-disabled` と ` aria-disabled="true"` を外す（トップのヒーロー2つ）
    ③ ラベルの「（準備中）」を消す

    ⚠️ `keepy.css` の `a[data-appstore][href="#"]` は href を入れた時点で自動的に効かなくなるので、
       CSS 側は触らない。トップのフッター導線を CSS で隠しているのも意図どおりなので触らない。

使い方
    python3 tools/release_appstore_link.py            # 下見（何も書かない）
    python3 tools/release_appstore_link.py --apply    # 実行
    python3 tools/release_appstore_link.py --revert   # 元に戻す（動作確認用）

終了コード 0＝すべて期待どおり／1＝取りこぼしあり
"""
import argparse
import glob
import re
import sys

URL = "https://apps.apple.com/jp/app/id6786194974"
SUFFIX = "（準備中）"

ANCHOR = re.compile(r"<a\b[^>]*\bdata-appstore\b[^>]*>.*?</a>", re.S)


def to_released(tag: str) -> str:
    """1つの <a data-appstore> を公開状態に書き換える。"""
    tag = tag.replace('href="#"', f'href="{URL}"')
    tag = tag.replace(' is-disabled"', '"')
    tag = tag.replace(' aria-disabled="true"', "")
    return tag.replace(SUFFIX, "")


def to_prerelease(tag: str) -> str:
    """--revert 用。公開状態を「準備中」へ戻す（動作確認のため）。"""
    is_hero = "btn-island" in tag
    tag = tag.replace(f'href="{URL}"', 'href="#"')
    if is_hero:
        tag = tag.replace('class="btn-island"', 'class="btn-island is-disabled"')
        tag = tag.replace("data-appstore>", 'data-appstore aria-disabled="true">')
    return re.sub(r"(ダウンロード)(?!" + re.escape(SUFFIX) + r")", r"\1" + SUFFIX, tag)


def run(apply_changes: bool, revert: bool) -> int:
    convert = to_prerelease if revert else to_released
    total = 0
    for path in sorted(glob.glob("*.html")):
        src = open(path, encoding="utf-8").read()
        hits = ANCHOR.findall(src)
        if not hits:
            continue
        out = ANCHOR.sub(lambda m: convert(m.group(0)), src)
        changed = sum(1 for h in hits if convert(h) != h)
        total += len(hits)
        print(f"  {path:16s} 導線 {len(hits)} 件 / 書き換え {changed} 件")
        if apply_changes and out != src:
            open(path, "w", encoding="utf-8").write(out)

    marks = sum(open(p, encoding="utf-8").read().count("<!-- APPSTORE_LINK -->")
                for p in glob.glob("*.html"))
    print(f"\n導線 {total} 件 / APPSTORE_LINK マーカー {marks} 件")
    if total != marks:
        print("❌ マーカーと導線の数が合わない＝マーカーだけの箇所か、data-appstore の付け忘れがある")
        return 1

    if not apply_changes:
        hint = "--apply --revert" if revert else "--apply"
        print(f"（下見のみ。書き込むには {hint}）")
        return 0

    # ── 検算：書いた後に、取りこぼしが無いことを実ファイルで確かめる ──
    leftovers = []
    for path in sorted(glob.glob("*.html")):
        s = open(path, encoding="utf-8").read()
        for tag in ANCHOR.findall(s):
            if revert:
                if 'href="#"' not in tag:
                    leftovers.append(f"{path}: href が実 URL のまま")
                if SUFFIX not in tag:
                    leftovers.append(f"{path}: ラベルに「準備中」が戻っていない")
                if "btn-island" in tag and "is-disabled" not in tag:
                    leftovers.append(f"{path}: ヒーローの無効化が戻っていない")
                continue
            if 'href="#"' in tag:
                leftovers.append(f"{path}: href が # のまま")
            if "is-disabled" in tag or "aria-disabled" in tag:
                leftovers.append(f"{path}: 無効化の指定が残っている")
            if SUFFIX in tag:
                leftovers.append(f"{path}: ラベルに「準備中」が残っている")
    if leftovers:
        print("❌ 取りこぼし:")
        for x in leftovers:
            print("   -", x)
        return 1
    print("✅ 取りこぼしなし（準備中へ戻した）" if revert
          else "✅ 取りこぼしなし（href / 無効化 / ラベルの3点すべて）")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="実際に書き換える")
    p.add_argument("--revert", action="store_true", help="「準備中」の状態へ戻す")
    a = p.parse_args()
    sys.exit(run(a.apply, a.revert))
