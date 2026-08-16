#!/usr/bin/env python3
"""Drop the hero's third CTA, and replace the stale Manager card.

Two edits Adrian asked for after the section reorder:

1. The "See it run" ghost button goes. With the narrower hero copy column
   it was wrapping onto its own line anyway, and the section it linked to
   is the very next thing on the page.

2. The extras row still carried a "Manager mode (experimental)" card
   saying "it runs, but we are still working out the best way to use it"
   — directly contradicting section 03, which now presents the same
   feature as a finished pillar. Replaced rather than deleted, so the row
   keeps three cards, with the local-first claim that until now was only
   a five-word line in the strip under the hero. It earns a card: it is
   what makes unattended delegation (03) reasonable to agree to, and it
   is a real difference from the hosted alternatives.

Dictionary edits work on one dictionary's text span at a time, rewriting
that slice whole. An earlier attempt tracked byte offsets across edits and
inserted a key into the middle of another line; slicing per dictionary
removes the arithmetic entirely.
"""
import json, pathlib, re, sys

P = pathlib.Path(__file__).resolve().parents[1] / "index.html"
s = P.read_text(encoding="utf-8")

# ── 1. hero CTA ────────────────────────────────────────────────────────
btn = '          <a data-i18n="hero.cta2" class="btn btn-ghost" href="#see">看它怎麼跑</a>\n'
if s.count(btn) != 1:
    sys.exit("hero.cta2 button markup not found exactly once")
s = s.replace(btn, "")

# ── 2. extras card ─────────────────────────────────────────────────────
start = s.index('      <div class="card">\n        <span class="corner tl"></span><span class="corner br"></span>\n        <span class="kicker">Labs</span>')
end = s.index('    </div>\n  </div>\n</section>\n\n<section class="manifesto">', start)
s = s[:start] + '''      <div class="card">
        <span class="corner tl"></span><span class="corner br"></span>
        <span data-i18n="s4.c3k" class="kicker">本機優先</span>
        <h3 data-i18n="s4.c3h">你的檔案不會離開這台電腦</h3>
        <ul>
          <li data-i18n="s4.c3a">agent 直接讀寫你本機的資料夾。沒有上傳、沒有同步、沒有我們的伺服器。</li>
          <li data-i18n="s4.c3b">連遠端也是連回你自己的電腦，不是連到別人的雲端。</li>
        </ul>
        <div class="card-checklist">
          <div class="ck-row ok"><span class="ck-box"></span><span data-i18n="s4.c3l1" class="ck-name">你的檔案</span><span data-i18n="s4.c3v" class="ck-scope">這台電腦</span></div>
          <div class="ck-row ok"><span class="ck-box"></span><span data-i18n="s4.c3l2" class="ck-name">agent 對話</span><span data-i18n="s4.c3v" class="ck-scope">這台電腦</span></div>
          <div class="ck-row ok"><span class="ck-box"></span><span data-i18n="s4.c3l3" class="ck-name">遠端連線</span><span data-i18n="s4.c3v2" class="ck-scope">連回這台電腦</span></div>
        </div>
      </div>
''' + s[end:]

# ── 3. dictionaries ────────────────────────────────────────────────────
DROP = ["hero.cta2", "d.m.r1", "d.m.r2", "d.m.r3"]
COPY = {
    "s4.c3k": {"zh": "本機優先", "cn": "本机优先", "en": "Local-first", "ja": "ローカル優先"},
    "s4.c3h": {
        "zh": "你的檔案不會離開這台電腦",
        "cn": "你的文件不会离开这台电脑",
        "en": "Your files never leave this machine",
        "ja": "あなたのファイルは、この端末から出ない",
    },
    "s4.c3a": {
        "zh": "agent 直接讀寫你本機的資料夾。沒有上傳、沒有同步、沒有我們的伺服器。",
        "cn": "agent 直接读写你本机的文件夹。没有上传、没有同步、没有我们的服务器。",
        "en": "Agents read and write your local folders directly. No upload, no sync, no server of ours.",
        "ja": "エージェントはローカルのフォルダを直接読み書きします。アップロードも同期も、当社のサーバーもありません。",
    },
    "s4.c3b": {
        "zh": "連遠端也是連回你自己的電腦，不是連到別人的雲端。",
        "cn": "连远程也是连回你自己的电脑，不是连到别人的云端。",
        "en": "Even remote access connects back to your own machine, not to somebody’s cloud.",
        "ja": "リモート接続も、あなた自身の端末に戻ってくる接続です。どこかのクラウドではありません。",
    },
    "s4.c3l1": {"zh": "你的檔案", "cn": "你的文件", "en": "Your files", "ja": "ファイル"},
    "s4.c3l2": {"zh": "agent 對話", "cn": "agent 对话", "en": "Agent transcripts", "ja": "エージェントの履歴"},
    "s4.c3l3": {"zh": "遠端連線", "cn": "远程连接", "en": "Remote access", "ja": "リモート接続"},
    "s4.c3v": {"zh": "這台電腦", "cn": "这台电脑", "en": "this machine", "ja": "この端末"},
    "s4.c3v2": {"zh": "連回這台電腦", "cn": "连回这台电脑", "en": "back to this machine", "ja": "この端末へ戻る"},
}

def line_for(lang, key, value):
    if lang == "cn":
        return f"      {json.dumps(key, ensure_ascii=False)}: {json.dumps(value, ensure_ascii=False)},\n"
    return "      '" + key + "': '" + value.replace("\\", "\\\\").replace("'", "\\'") + "',\n"

def key_pattern(key):
    return re.compile(
        rf"^      (?:'{re.escape(key)}'|\"{re.escape(key)}\"): (?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),\n",
        re.M,
    )

for lang in ("zh", "cn", "en", "ja"):
    m = re.search(rf"\n    {lang}: \{{\n", s)
    if not m:
        sys.exit(f"dictionary for {lang} not found")
    body_start = m.end()
    # The dictionary ends at the first line that closes it at this indent.
    close = re.compile(r"^    \},?\n", re.M).search(s, body_start)
    if not close:
        sys.exit(f"could not find the end of the {lang} dictionary")
    body = s[body_start:close.start()]

    for key in DROP:
        body = key_pattern(key).sub("", body)
    additions = ""
    for key, per_lang in COPY.items():
        rep = line_for(lang, key, per_lang[lang])
        if key_pattern(key).search(body):
            body = key_pattern(key).sub(lambda _m, r=rep: r, body, count=1)
        else:
            additions += rep
    body = additions + body
    s = s[:body_start] + body + s[close.start():]

P.write_text(s, encoding="utf-8")
print(f"removed {len(DROP)} retired keys, upserted {len(COPY)} card keys in 4 languages")
