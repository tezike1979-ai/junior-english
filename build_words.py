"""スプレッドシート「中学生英単語」から words.json を作り直すスクリプト。

使い方（リポジトリのルートで実行）:
    python tools/build_words.py              # 全シートを取り込み直す
    python tools/build_words.py idiom verb   # 指定したシートだけ差し替える

スプレッドシートは「リンクを知っている全員が閲覧可」にしておく必要があります。
各シートの列: A=番号(空欄可), B=単語/熟語, C=意味, D=例文(英), E=日本語訳
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

SHEET_ID = "1GpdD2h-tGfhuFC92qjS1LRrujrFfFkz23VbvbcTL528"
SHEETS = {  # index.html の PARTS_OF_SPEECH と同じ順番・キー
    "noun": "0",
    "pronoun": "973845469",
    "verb": "997419758",
    "auxiliary": "296755217",
    "adjective": "1693781741",
    "adverb": "1924216966",
    "preposition": "1340365523",
    "conjunction": "931669290",
    "idiom": "2096441416",
}
OUT = Path(__file__).resolve().parent.parent / "words.json"


def fetch_rows(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    with urllib.request.urlopen(url) as res:
        text = res.read().decode("utf-8")
    return list(csv.reader(io.StringIO(text)))[1:]  # 1行目は見出し


def to_words(rows, pos):
    words = []
    for cols in rows:
        cols = [c.strip() for c in cols] + [""] * 5
        word = cols[1]
        if not word:
            continue
        words.append({
            "word": word,
            "meaning": cols[2].replace("\n", " / "),
            "pos": pos,
            "exEn": cols[3].replace("\n", " "),
            "exJa": cols[4].replace("\n", " "),
        })
    return words


def main():
    targets = sys.argv[1:] or list(SHEETS)
    unknown = [t for t in targets if t not in SHEETS]
    if unknown:
        sys.exit(f"不明なシート名: {unknown}（使えるのは {list(SHEETS)}）")

    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for pos in targets:
        data[pos] = to_words(fetch_rows(SHEETS[pos]), pos)
        print(f"{pos}: {len(data[pos])}件")

    data = {k: data.get(k, []) for k in SHEETS}  # キーの順番をそろえる
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT.name} を更新しました（合計 {sum(map(len, data.values()))}件）")


if __name__ == "__main__":
    main()
