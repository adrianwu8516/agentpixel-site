#!/usr/bin/env python3
"""Add the Manager (delegation) copy and re-point the demoted office copy.

Section 03 is new, so every dictionary needs its keys. The office section
(now 04) keeps its visual but stops making a headline claim — it is
supporting material after the reorder, not a pillar of the pitch.

Copy is written from what the app actually does (see the app's
`i18n/locales/*.ts` delegation block): you write a briefing, set a
duration, pick what happens to anything you did not cover, and the
Manager answers agents' questions against that while you are offline.
Destructive operations always still wait for you — stated on the page
because a promise of unattended autonomy without that caveat would be
a promise the product does not make.
"""
import pathlib, re, sys

P = pathlib.Path(__file__).resolve().parents[1] / "index.html"
s = P.read_text(encoding="utf-8")

# key -> {lang: value}
COPY = {
    "nav.manager": {
        "zh": "代管", "cn": "代管", "en": "Hand off", "ja": "代理",
    },
    "s5.h2": {
        "zh": "連手機都不想看的時候，交給 Manager。",
        "cn": "连手机都不想看的时候，交给 Manager。",
        "en": "When you don’t even want to look at your phone.",
        "ja": "スマホも見たくないときは、Manager に任せる。",
    },
    "s5.lede": {
        "zh": "遠端能讓你在外面點頭。但有些時候你根本不想被打擾——開會、上飛機、睡覺。",
        "cn": "远程能让你在外面点头。但有些时候你根本不想被打扰——开会、上飞机、睡觉。",
        "en": "Remote lets you say yes from anywhere. Some hours you don’t want to be reachable at all — a meeting, a flight, a night’s sleep.",
        "ja": "リモートなら外からでも承認できる。でも会議中、飛行機の中、寝ている間は、そもそも邪魔されたくない。",
    },
    "s5.slogan": {
        "zh": "你交代一次，<br><span class=\"grad\">它照著看顧一整晚。</span>",
        "cn": "你交代一次，<br><span class=\"grad\">它照着看顾一整晚。</span>",
        "en": "Brief it once,<br><span class=\"grad\">it holds the line all night.</span>",
        "ja": "一度伝えておけば、<br><span class=\"grad\">ひと晩じゅう見ていてくれる。</span>",
    },
    "s5.sub": {
        "zh": "出門前寫下你的規則，Manager 就會在你離線的期間，<b>照著規則替你回答其他 agent 的提問</b>——該放行的放行，你說要留給自己的就停下來等你。回來時，它做過的每個決定和理由都列給你看。",
        "cn": "出门前写下你的规则，Manager 就会在你离线的期间，<b>照着规则替你回答其他 agent 的提问</b>——该放行的放行，你说要留给自己的就停下来等你。回来时，它做过的每个决定和理由都列给你看。",
        "en": "Write your rules before you go, and while you are offline the Manager <b>answers the other agents’ questions against them</b> — clearing what you cleared, holding what you said to hold. Every decision and its reason is waiting for you when you get back.",
        "ja": "出かける前にルールを書いておけば、オフラインの間 Manager が<b>そのルールに沿って他のエージェントの質問に答えます</b>。通してよいものは通し、自分で判断すると言ったものは止めて待つ。戻ったときには、下した判断とその理由がすべて並んでいます。",
    },
    "w.5": {
        "zh": "Manager — 代管中 · 剩 1 小時 12 分",
        "cn": "Manager — 代管中 · 剩 1 小时 12 分",
        "en": "Manager — on duty · 1h 12m left",
        "ja": "Manager — 代理中 · 残り 1 時間 12 分",
    },
    "d.g.blabel": {
        "zh": "你出門前的交代", "cn": "你出门前的交代",
        "en": "What you told it before leaving", "ja": "出かける前に伝えたこと",
    },
    "d.g.b1": {
        "zh": "<span class=\"mg-you\">agent 1 在做重構</span>，要拆檔案就說好。",
        "cn": "<span class=\"mg-you\">agent 1 在做重构</span>，要拆文件就说好。",
        "en": "<span class=\"mg-you\">agent 1 is refactoring</span> — if it wants to split files, say yes.",
        "ja": "<span class=\"mg-you\">agent 1 はリファクタ中</span>。ファイル分割は許可して。",
    },
    "d.g.b2": {
        "zh": "要動 <span class=\"mg-you\">DB schema</span> 或改測試，停下來等我。",
        "cn": "要动 <span class=\"mg-you\">DB schema</span> 或改测试，停下来等我。",
        "en": "Touching the <span class=\"mg-you\">DB schema</span> or the tests — stop and wait for me.",
        "ja": "<span class=\"mg-you\">DB スキーマ</span>やテストを触るなら、止めて私を待って。",
    },
    "d.g.m1": {
        "zh": "預計離開 <b>2 小時</b>", "cn": "预计离开 <b>2 小时</b>",
        "en": "Away for <b>2 hours</b>", "ja": "離席 <b>2 時間</b>",
    },
    "d.g.m2": {
        "zh": "沒交代到的 · <b>留給我處理</b>", "cn": "没交代到的 · <b>留给我处理</b>",
        "en": "Anything else · <b>leave it to me</b>", "ja": "伝えていない件 · <b>自分で判断する</b>",
    },
    "d.g.llabel": {
        "zh": "Manager 替你回答了 2 次", "cn": "Manager 替你回答了 2 次",
        "en": "The Manager answered twice for you", "ja": "Manager が 2 回、代わりに答えました",
    },
    "d.g.q1": {"zh": "拆成三個檔案？", "cn": "拆成三个文件？", "en": "split into three files?", "ja": "3 ファイルに分割？"},
    "d.g.q2": {"zh": "新增一個測試檔？", "cn": "新增一个测试文件？", "en": "add a test file?", "ja": "テストファイルを追加？"},
    "d.g.q3": {"zh": "改 users 表結構？", "cn": "改 users 表结构？", "en": "alter the users table?", "ja": "users テーブルを変更？"},
    "d.g.v1": {"zh": "照交代放行", "cn": "照交代放行", "en": "cleared, as briefed", "ja": "指示どおり許可"},
    "d.g.v2": {"zh": "照交代放行", "cn": "照交代放行", "en": "cleared, as briefed", "ja": "指示どおり許可"},
    "d.g.v3": {"zh": "留給你", "cn": "留给你", "en": "held for you", "ja": "あなたを待つ"},
    "d.g.guard": {
        "zh": "不論你怎麼交代，<b>刪除、sudo、force push</b> 這類破壞性操作一律仍會停下來等你。",
        "cn": "不论你怎么交代，<b>删除、sudo、force push</b> 这类破坏性操作一律仍会停下来等你。",
        "en": "However you brief it, destructive operations — <b>deletes, sudo, force push</b> — always still wait for you.",
        "ja": "どう伝えていても、<b>削除・sudo・force push</b> のような破壊的な操作は必ず止まってあなたを待ちます。",
    },
    # The office section is now supporting material.
    "s2.h2": {
        "zh": "誰在忙、誰在等你，一眼看完。",
        "cn": "谁在忙、谁在等你，一眼看完。",
        "en": "Who’s busy, who’s waiting on you.",
        "ja": "誰が動いていて、誰が待っているか。",
    },
}

# Dictionaries in file order; cn uses JSON-style double quotes (generated).
BOUNDS = []
for lang in ("zh", "cn", "en", "ja"):
    m = re.search(rf"\n    {lang}: \{{\n", s)
    if not m:
        sys.exit(f"dictionary for {lang} not found")
    BOUNDS.append((lang, m.end()))

def q(lang, key, value):
    if lang == "cn":
        import json
        return f'      {json.dumps(key, ensure_ascii=False)}: {json.dumps(value, ensure_ascii=False)},\n'
    esc = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"      '{key}': '{esc}',\n"

# Replace existing keys in place; insert new ones at the top of each dict.
for lang, insert_at in reversed(BOUNDS):
    additions = ""
    for key, per_lang in COPY.items():
        value = per_lang[lang]
        pat_single = re.compile(rf"^      '{re.escape(key)}': '(?:[^'\\]|\\.)*',\n", re.M)
        pat_double = re.compile(rf'^      "{re.escape(key)}": "(?:[^"\\]|\\.)*",\n', re.M)
        # Only touch the occurrence inside this dictionary.
        end = len(s)
        for _, nxt in BOUNDS:
            if nxt > insert_at:
                end = min(end, nxt)
        region = s[insert_at:end]
        hit = pat_single.search(region) or pat_double.search(region)
        if hit:
            region = region[:hit.start()] + q(lang, key, value) + region[hit.end():]
            s = s[:insert_at] + region + s[end:]
        else:
            additions += q(lang, key, value)
    if additions:
        s = s[:insert_at] + additions + s[insert_at:]

P.write_text(s, encoding="utf-8")
print(f"applied {len(COPY)} keys to four dictionaries")
