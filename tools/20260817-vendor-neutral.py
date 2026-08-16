#!/usr/bin/env python3
"""Swap the extras card to vendor-neutrality, and rewrite the manifesto.

Adrian's calls, and the reasoning behind how they are worded:

* The local-first card goes; vendor-neutrality takes the slot.
* "後天用還沒出生的那個" reads oddly in Chinese and is gone.
* "Anthropic 和 Microsoft 都說不出口" is gone. Punching at named
  competitors is not an argument, and it dates badly.

What is claimed was checked against the code rather than assumed:

  - `AGENT_PATTERN_TABLE` carries full pattern sets for **Copilot, Codex
    and Claude Code**, and `AgentType` also has Aider. That is what backs
    "it knows which one is working and which is waiting for you".
  - Everything else — Gemini CLI, Antigravity's CLI, whatever ships next —
    runs because the app is a real terminal, not because we integrated it.
    That distinction is stated on the page instead of blurred, since
    claiming status awareness for an agent we have no patterns for would
    be a promise the product does not keep.

The card carries the names and the distinction; the manifesto is left as
one idea with no list, because they sit next to each other and the page
already had one section repeating the section above it.
"""
import json, pathlib, re, sys

P = pathlib.Path(__file__).resolve().parents[1] / "index.html"
s = P.read_text(encoding="utf-8")

# ── 1. the extras card ─────────────────────────────────────────────────
start = s.index('      <div class="card">\n        <span class="corner tl"></span><span class="corner br"></span>\n        <span data-i18n="s4.c3k" class="kicker">本機優先</span>')
end = s.index('    </div>\n  </div>\n</section>\n\n<section class="manifesto">', start)
s = s[:start] + '''      <div class="card">
        <span class="corner tl"></span><span class="corner br"></span>
        <span data-i18n="s4.c3k" class="kicker">不綁廠商</span>
        <h3 data-i18n="s4.c3h">能在終端機裡跑的，這裡都能跑</h3>
        <ul>
          <li data-i18n-html="s4.c3a">Claude Code、Codex、GitHub Copilot CLI <b>還多懂一層</b>——它知道誰在忙、誰在等你、誰做完了。</li>
          <li data-i18n="s4.c3b">其他的照樣跑：Gemini CLI、Antigravity、aider，或明年才出現的那個。這本來就是一台真的終端機。</li>
        </ul>
        <div class="card-checklist">
          <div class="ck-row ok"><span class="ck-box"></span><span class="ck-name">Claude Code</span><span data-i18n="s4.c3v" class="ck-scope">看得懂狀態</span></div>
          <div class="ck-row ok"><span class="ck-box"></span><span class="ck-name">Codex</span><span data-i18n="s4.c3v" class="ck-scope">看得懂狀態</span></div>
          <div class="ck-row ok"><span class="ck-box"></span><span class="ck-name">Copilot CLI</span><span data-i18n="s4.c3v" class="ck-scope">看得懂狀態</span></div>
          <div class="ck-row wait"><span class="ck-box"></span><span data-i18n="s4.c3l4" class="ck-name">其他任何 CLI</span><span data-i18n="s4.c3v2" class="ck-scope">照樣跑</span></div>
        </div>
      </div>
''' + s[end:]

# ── 2. the manifesto: one idea, no list (the card above carries names) ──
mstart = s.index('<section class="manifesto">')
mend = s.index('<section class="download" id="download">')
manifesto = s[mstart:mend]
chips = re.search(r'\n      <div class="mani-logos">.*?</div>\n', manifesto, re.S)
if not chips:
    sys.exit("mani-logos block not found")
manifesto = manifesto.replace(chips.group(0), "\n")
s = s[:mstart] + manifesto + s[mend:]

# ── 3. copy ────────────────────────────────────────────────────────────
DROP = ["mani.next", "s4.c3l1", "s4.c3l2", "s4.c3l3"]
COPY = {
    "s4.c3k": {"zh": "不綁廠商", "cn": "不绑厂商", "en": "Vendor-neutral", "ja": "ベンダー中立"},
    "s4.c3h": {
        "zh": "能在終端機裡跑的，這裡都能跑",
        "cn": "能在终端里跑的，这里都能跑",
        "en": "If it runs in a terminal, it runs here",
        "ja": "ターミナルで動くものは、ここでも動く",
    },
    "s4.c3a": {
        "zh": "Claude Code、Codex、GitHub Copilot CLI <b>還多懂一層</b>——它知道誰在忙、誰在等你、誰做完了。",
        "cn": "Claude Code、Codex、GitHub Copilot CLI <b>还多懂一层</b>——它知道谁在忙、谁在等你、谁做完了。",
        "en": "Claude Code, Codex and GitHub Copilot CLI get <b>one layer more</b> — it knows which is working, which is waiting on you, and which is done.",
        "ja": "Claude Code・Codex・GitHub Copilot CLI は<b>もう一段深く</b>——どれが動いていて、どれがあなたを待っていて、どれが終わったかを把握します。",
    },
    "s4.c3b": {
        "zh": "其他的照樣跑：Gemini CLI、Antigravity、aider，或明年才出現的那個。這本來就是一台真的終端機。",
        "cn": "其他的照样跑：Gemini CLI、Antigravity、aider，或明年才出现的那个。这本来就是一台真的终端。",
        "en": "The rest just run — Gemini CLI, Antigravity, aider, or whatever ships next year. This is a real terminal.",
        "ja": "それ以外もそのまま動きます。Gemini CLI、Antigravity、aider、来年出るものも。これは本物のターミナルだからです。",
    },
    "s4.c3l4": {"zh": "其他任何 CLI", "cn": "其他任何 CLI", "en": "Any other CLI", "ja": "その他の CLI"},
    "s4.c3v": {"zh": "看得懂狀態", "cn": "看得懂状态", "en": "state-aware", "ja": "状態を把握"},
    "s4.c3v2": {"zh": "照樣跑", "cn": "照样跑", "en": "just runs", "ja": "そのまま動く"},

    "mani.label": {"zh": "不綁定廠商", "cn": "不绑定厂商", "en": "Vendor-neutral", "ja": "ベンダー中立"},
    "mani.big": {
        "zh": "我們不賭哪一家會贏。<br><span class=\"grad\">你也不必。</span>",
        "cn": "我们不赌哪一家会赢。<br><span class=\"grad\">你也不必。</span>",
        "en": "We’re not betting on a winner.<br><span class=\"grad\">You don’t have to either.</span>",
        "ja": "どこが勝つかに賭けていません。<br><span class=\"grad\">あなたも賭けなくていい。</span>",
    },
    "mani.small": {
        "zh": "換 agent 的時候，你不用連工作檯一起換。",
        "cn": "换 agent 的时候，你不用连工作台一起换。",
        "en": "When you change agents, you shouldn’t have to change your workbench too.",
        "ja": "エージェントを乗り換えるとき、作業台まで乗り換える必要はありません。",
    },
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
    close = re.compile(r"^    \},?\n", re.M).search(s, body_start)
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
    s = s[:body_start] + additions + body + s[close.start():]

P.write_text(s, encoding="utf-8")
print(f"card + manifesto rewritten; dropped {len(DROP)} keys, wrote {len(COPY)} x4")
