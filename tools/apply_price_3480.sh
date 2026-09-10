#!/bin/bash
# 早期割引（先着100名・¥2,480）の終了＝サイト6ファイルを ¥3,480 の表記に差し替える（2026-09-10 準備）。
# 使い方: bash tools/apply_price_3480.sh 2026-09-1X   （終了日）→ git diff で目視 → commit → push（push＝即公開）
# ⚠️ ASC の価格変更と同じタイミングで実行する（特商法ページは法定表示＝ずれた時間を作らない）
set -euo pipefail
[ $# -eq 1 ] || { echo "使い方: $0 <終了日 YYYY-MM-DD>"; exit 1; }
D="$1"; JD="$(date -j -f '%Y-%m-%d' "$D" '+%Y年%-m月%-d日')"
cd "$(dirname "$0")/.."
python3 - "$JD" <<'PY'
import sys, re
JD=sys.argv[1]
def rep(path, pairs):
    s=open(path,encoding='utf-8').read()
    for a,b in pairs:
        assert s.count(a)==1, (path, a[:40], s.count(a)); s=s.replace(a,b)
    open(path,'w',encoding='utf-8').write(s); print("✅", path)
rep('index.html', [
 ('<strong>¥2,480</strong> 買い切り · 無料で試せます', '<strong>¥3,480</strong> 買い切り · 無料で試せます'),
 ('<span class="plan-flag">早期割引 · 先着100名</span>', '<span class="plan-flag">買い切り</span>'),
 ('<p class="plan-price">¥2,480<small>早期割引価格</small></p>', '<p class="plan-price">¥3,480</p>'),
 ('<p class="plan-note">先着100名、または1.0公開から1か月後には ¥3,480 になる予定です。</p>', f'<p class="plan-note">先着100名の早期割引は{JD}に終了しました。買い切りのため、月額や追加の課金はありません。</p>'),
])
rep('features.html', [('<strong>¥2,480</strong> 買い切り', '<strong>¥3,480</strong> 買い切り')])
rep('manual.html', [('<strong>買い切り ¥2,480</strong>', '<strong>買い切り ¥3,480</strong>')])
rep('support.html', [
 ('先着100名、または公開から1か月後のどちらか早い方までを予定しています。その後は ¥3,480 になる見込みです。<strong>買い切りのため、割引価格で購入されたあとに差額を請求することはありません。</strong>',
  f'先着100名に達したため、{JD}に終了しました。現在は ¥3,480 です。<strong>買い切りのため、割引価格で購入されたあとに差額を請求することはありません。</strong>'),
])
rep('press.html', [
 ('無料（プレミアム機能はアプリ内課金で買い切り 2,480 円・税込）<br><span class="note">2026年9月23日に 3,480 円へ改定予定です。</span>',
  f'無料（プレミアム機能はアプリ内課金で買い切り 3,480 円・税込）<br><span class="note">先着100名の早期割引（2,480 円）は{JD}に終了しました。</span>'),
])
rep('tokushoho.html', [
 ('Keepy プレミアム（買い切り）：¥2,480（税込）', 'Keepy プレミアム（買い切り）：¥3,480（税込）'),
 ('Keepy Premium (one-time purchase): ¥2,480 (tax included)', 'Keepy Premium (one-time purchase): ¥3,480 (tax included)'),
])
PY
echo "次＝git diff で目視 → 残る ¥2,480 を grep -rn '2,480' *.html で確認 → commit → push（即公開）"
