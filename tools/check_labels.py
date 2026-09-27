#!/usr/bin/env python3
"""
check_labels.py — サイトの「」で囲んだ名前が、公開中のアプリの文言にあるかを確かめる

なぜ:
    2026-09-27 にサイト全体を公開中の 2.1（build29）と照合したら、ボタン名・画面名の食い違いが多数見つかった。
    版を出すたびに人が読んで照らすのでは漏れる（反証役の指摘「ボタン名が実在するかを版ごとに機械で確かめる」・
    Kentaro「ボタン名の機械検査＝作る」）。

使い方（keepy-site のルートで）:
    python3 tools/check_labels.py                    # 既定＝アプリのいちばん新しい buildNN タグと照合
    python3 tools/check_labels.py --tag build29      # タグを指定
    python3 tools/check_labels.py --all              # 見つかったものも含めて全部出す

判定:
    「」の中身が、そのタグの Swift・services.json の文言に**部分一致で**あれば OK。
    「設定 → 通知設定」のような道順は「→」で区切り、1 段ずつ照らす（「（ご家族の名前）」のような丸かっこの段は飛ばす）。
    「○○」「〇〇」「◯◯」は名前が入る場所（アプリ側の \\(…) に当たる）として何にでも一致させる。
    アプリの文言ではない「」（iOS の画面・Apple のボタン・例の文・語の強調）は
    tools/check_labels_allow.txt に理由つきで書く＝無ければ「アプリに無い」と報告して終了コード 1。
    Swift のコメント（// と ///）は照らす前に取り除く（コメントにだけ残る旧名で OK にしないため）。
    画像の説明（alt・aria-label）の「」も照らす。
⚠️ 見られないこと:
    ・「」で囲んでいない名前（本文に地の文で書いたボタン名）
    ・名前はあるが、その画面・その場所には無い（部分一致なので別の画面の文言にも一致する）
    ・名前の欠け（「家族を管理する」を「家族を管理」と書いても、前半が一致するので OK になる）
    ・アプリに表記が 2 通りあるとき、その場面で正しい方か（例＝ロック画面の「ご家族はこちら」と「ご家族の方はこちら」）
    ・アプリ側が文字列を組み立てている名前（\\(…) を2つ以上含む等）
"""
import argparse, glob, io, os, re, subprocess, sys, tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_REPO = os.path.expanduser("~/Desktop/Claude/Keepy2")
ALLOW = os.path.join(ROOT, "tools", "check_labels_allow.txt")
PLACEHOLDER = re.compile(r"[○〇◯]+")


def latest_build_tag():
    tags = subprocess.run(["git", "-C", APP_REPO, "tag", "-l", "build*"],
                          capture_output=True, text=True, check=True).stdout.split()
    return max(tags, key=lambda t: int(re.sub(r"\D", "", t) or 0))


def app_text(tag):
    """タグ時点の Swift と services.json を1本の文字列にする（作業ツリーは見ない＝未公開の変更を拾わない）"""
    raw = subprocess.run(["git", "-C", APP_REPO, "archive", tag],
                         capture_output=True, check=True).stdout
    parts = []
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
        for m in tar.getmembers():
            if not m.isfile():
                continue
            if m.name.endswith(".swift") or m.name.endswith("services.json") or m.name.endswith(".xcstrings"):
                if "Tests/" in m.name:  # テストの文字列はアプリに出ない
                    continue
                parts.append(tar.extractfile(m).read().decode("utf-8", "replace"))
    text = "\n".join(parts)
    # Swift の補間 \(…) を印に置き換える（「Keepy○○」を「Keepy\(member.name)」に当てるため）
    text = "\n".join(strip_comment(line) for line in text.split("\n"))
    return re.sub(r"\\\([^()]*(\([^()]*\)[^()]*)*\)", "\u0000", text)


def strip_comment(line):
    """文字列リテラルの外にある // から行末を落とす（"https://…" の中は残す）"""
    in_str = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and in_str:
            i += 2
            continue
        if c == '"':
            in_str = not in_str
        elif not in_str and line.startswith("//", i):
            return line[:i]
        i += 1
    return line


def load_allow():
    allow = {}
    if os.path.exists(ALLOW):
        for line in open(ALLOW, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            label, _, reason = line.partition("\t")
            if not reason.strip():
                sys.exit(f"❌ 許可リストの行に理由がありません: {line}")
            allow[label] = reason.strip()
    return allow


def site_labels():
    """ページごとに「」の中身を行番号つきで集める（HTML のタグは外す）"""
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            plain = re.sub(r"<[^>]+>", "", line)
            attrs = " ".join(re.findall(r'(?:alt|aria-label)="([^"]*)"', line))
            for label in re.findall(r"「([^「」]{1,60})」", plain + " " + attrs):
                out.append((os.path.basename(path), n, label.strip()))
    return out


def found(label, text):
    if "→" in label:
        # 「（ご家族の名前）」のように丸かっこで書いた段は、利用者ごとに変わる所＝照らさない
        return all(found(step.strip(), text) for step in label.split("→")
                   if step.strip() and not step.strip().startswith("（"))
    pieces = [p for p in PLACEHOLDER.split(label) if p]
    if not pieces:
        return True
    if len(pieces) == 1:
        return pieces[0] in text
    # 「Keepy○○」のような形＝断片が補間の印を挟んで並ぶ
    pat = "\u0000?".join(re.escape(p) for p in pieces)
    return re.search(pat.replace("\u0000?", "[^\"\n]{0,40}"), text) is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    tag = a.tag or latest_build_tag()
    text = app_text(tag)
    allow = load_allow()
    missing, used_allow = [], set()
    for page, n, label in site_labels():
        if found(label, text):
            if a.all:
                print(f"  OK  {page}:{n}「{label}」")
            continue
        if label in allow:
            used_allow.add(label)
            if a.all:
                print(f"  除外 {page}:{n}「{label}」＝{allow[label]}")
            continue
        missing.append((page, n, label))
    for page, n, label in missing:
        print(f"❌ {page}:{n}「{label}」＝{tag} のアプリの文言に無い")
    stale = sorted(set(allow) - used_allow)
    for label in stale:
        print(f"⚠️ 許可リストの「{label}」はもうサイトに無いか、アプリに見つかる＝行を消す")
    print(f"照合＝{tag}・アプリに無い {len(missing)} 件・使われていない除外 {len(stale)} 件")
    sys.exit(1 if missing or stale else 0)


if __name__ == "__main__":
    main()
