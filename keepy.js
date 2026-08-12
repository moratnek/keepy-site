/* Keepy 共通スクリプト（2026-08-12 新設・全ページで読み込む）
 *
 * ナビの開閉だけを担当する。ページ固有の動き（トップのスクロール登場など）は
 * そのページの <script> に置く。
 * 要素が無いページでも安全に何もしないようにしてある。
 */
(function () {
  'use strict';

  var burger = document.getElementById('burger');
  var veil = document.getElementById('menuVeil');
  if (!burger || !veil) return;

  function close() {
    document.body.classList.remove('menu-open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'メニューを開く');
  }

  burger.addEventListener('click', function () {
    var open = document.body.classList.toggle('menu-open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
  });

  // リンクを押したとき／余白を押したときに閉じる
  veil.addEventListener('click', function (e) {
    if (e.target.tagName === 'A' || e.target === veil) close();
  });

  // Esc で閉じる（キーボード操作の逃げ道）
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.body.classList.contains('menu-open')) close();
  });
}());
