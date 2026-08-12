# keepy-site

Keepy アプリの公式サイト。**GitHub Pages が `main` を直配信**しているため、`main` への push ＝即公開。

- 公開URL: **https://keepy.jp**（カスタムドメイン・`CNAME` 参照。2026-07-18 に github.io から移行・HTTPS 有効）
- リポジトリ: https://github.com/moratnek/keepy-site

## ファイル構成（8ページ・2026-08-12 現在）

```
index.html      — トップ（2026-08-12 に全面刷新。物語順の機能紹介・料金・セキュリティ）
features.html   — 使い方（機能紹介 9節・交互レイアウト）
guide.html      — 引き継ぎガイド（#handover＝アプリのオンボーディング④の着地先）
manual.html     — 使い方マニュアル
support.html    — サポート（FAQ・問い合わせ）
privacy.html    — プライバシーポリシー
tokushoho.html  — 特定商取引法に基づく表記（日英併記）
404.html        — 存在しない URL の受け皿（GitHub Pages がルートの 404.html を自動で使う）

keepy.css       — 共通スタイルの単一ソース（色・浮遊ナビ・フッター・body）
                  ページ固有のスタイルは各ページの <style> に残す
keepy.js        — 共通スクリプト（モバイルのメニュー開閉だけ）
images/         — 機能紹介・トップ用スクショ（750px・width/height 属性つき）
img/            — マニュアル・ガイド用スクショ／favicon／OGP（同じく 750px 作法）
docs/           — 内部の設計メモ・デザイン試作（.gitignore 対象・公開されない）
```

## デザイン（2026-08-12 刷新）

- クリーム地（`#FBF7EF`）＋**インディゴ1色**のアクセント。テラコッタはアプリアイコンの中だけ
- ヘッダーは**画面の上に浮くピル型ナビ**（全ページ共通）。768px 以下はハンバーガー→全画面メニュー
  - **中身は全ページ同じ5項目**（トップ・使い方・引き継ぎガイド・マニュアル・サポート）。
    ページごとに項目を変えない。いま見ているページはインディゴ＋淡い下地で示す
  - ダウンロード導線は**ヘッダーに置かない**（2026-08-12 に撤去）。フッターに1つ置く
  - **ナビは `position: fixed` ＝場所を取らない**ので、下位ページは `<body class="has-nav">` で
    上の余白を確保する。これを外すと本文がナビの下に潜る
- 試作と比較検討の記録は `docs/redesign/`
  （proto_soft / proto_taste / proto_hybrid / nav_options / nav_options2）

## App Store 申請で使用している URL

- プライバシーポリシー: `https://keepy.jp/privacy.html`
- サポート: `https://keepy.jp/support.html`

## 編集時のルール

- **共通の見た目（ヘッダー・フッター・基本色）は `keepy.css` を1回直す**。各ページの `<style>` に複製しない
  （2026-08-05 に単一ソース化。それ以前は7ページに手で複製されていた）
- **画像は 750px にリサイズして置く**（最大表示幅 220px × Retina 3x に十分。原寸を置くと1枚 2MB 超になる）。
  `<img>` には `width`/`height` 属性と `loading="lazy"` を付ける
- 料金・機能の記述は**アプリの実態と一致させる**（無料枠=サブスク3件/カード1枚/資産1件・¥2,480 買い切り）
- 外部リンクの `target="_blank"` には `rel="noopener"` を付ける
- フッターの **Logo.dev 帰属表示は必須**（無料プランの商用利用条件・2026-08-04 追加）

## 公開時に残っている作業（App Store 審査通過後）

- `<!-- APPSTORE_LINK -->` マーカー（**全8ページ・13箇所**＝index 3／features 3／guide 2／
  manual・support・privacy・tokushoho・404 各1。2026-08-12 実測）を実リンク
  `https://apps.apple.com/jp/app/id6786194974` に差し替え。
  バッジは `href="#"` の間だけ無効化してあるので、URL を入れれば自動で押せるようになる。
  ⚠️ **トップだけフッターの導線を CSS で隠している**（すぐ上のクロージングに同じボタンがあるため）。
  マーカー自体は残してあるので置換の対象からは外さないこと
- 1.0 公開から1ヶ月後（または先着100名到達時）に **¥2,480 → ¥3,480 へ値上げ**し、
  index.html の料金表を実態化（Obsidian Dashboard のリリースTODO 参照）
