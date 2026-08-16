#!/usr/bin/env python3
"""One-time: make English the master language of `index.html`.

The site's default moves to English, so the root page has to *be* English
— pinning it only in JavaScript would leave crawlers, link previews and
the first paint in Chinese. Traditional Chinese moves to `/tw/`, which
`bake.py` generates from here afterwards.

This exists as its own script because `bake.py` derives its search
patterns from whatever language the master currently holds, and during the
switch that language is changing underneath it. Once this has run,
`SOURCE_LANG = "en"` and the normal pipeline takes over; this file is
history, not a step anyone repeats.

URLs are deliberately untouched: the master was the root before and is the
root after, so canonical and og:url already say the right thing.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "index.html"
SITE = "https://adrianwu8516.github.io/agentpixel-site/"
s = MASTER.read_text(encoding="utf-8")

m = re.search(r"var I18N = (\{.*?\n  \});\n", s, re.S)
i18n = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(" + m.group(1) + "))"]))
zh, en = i18n["zh"], i18n["en"]

# ── body text: every data-i18n element currently holds the zh string ───
def find_close(out, tag, start):
    depth, i = 1, start
    open_re = re.compile(r"<" + tag + r"\b[^>]*?(/?)>")
    close_s = "</" + tag + ">"
    while depth:
        nc = out.find(close_s, i)
        mo = open_re.search(out, i)
        if mo and mo.start() < nc and not mo.group(1):
            depth += 1; i = mo.end()
        else:
            depth -= 1; i = nc + len(close_s)
            if depth == 0: return nc
    return -1

for attr in ("data-i18n", "data-i18n-html"):
    pat = re.compile(r'(<([a-zA-Z0-9]+)\b[^>]*\b' + attr + r'="([^"]+)"[^>]*>)')
    pos, res = 0, []
    for mm in pat.finditer(s):
        if mm.start() < pos:
            continue
        key, tag = mm.group(3), mm.group(2)
        start = mm.end()
        close = find_close(s, tag, start)
        res.append(s[pos:start]); res.append(en[key]); pos = close
    res.append(s[pos:])
    s = "".join(res)

def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")

def swap_attr(mm):
    tag = mm.group(0)
    for pair in mm.group(1).split("|"):
        name, key = pair.split(":")
        old = f'{name}="{esc_attr(zh[key])}"'
        if old in tag:
            tag = tag.replace(old, f'{name}="{esc_attr(en[key])}"')
    return tag
s = re.sub(r'<[^>]*data-i18n-attr="([^"]+)"[^>]*>', swap_attr, s)

# ── head ──────────────────────────────────────────────────────────────
ZH_OGALT = f'AgentPixel 主視覺：「{zh["meta.ogtitle"]}」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。'
EN_OGALT = f'AgentPixel key visual: “{en["meta.ogtitle"]}” with four pixel-art agents working side by side at laptops on a dark console.'
pairs = [
    ('<html lang="zh-Hant"><head>', '<html lang="en"><head>'),
    (f"<title>{zh['meta.title']}</title>", f"<title>{en['meta.title']}</title>"),
    (f'<meta name="description" content="{zh["meta.desc"]}">',
     f'<meta name="description" content="{en["meta.desc"]}">'),
    ('<meta property="og:locale" content="zh_TW">\n'
     '<meta property="og:locale:alternate" content="zh_CN">\n'
     '<meta property="og:locale:alternate" content="en_US">\n'
     '<meta property="og:locale:alternate" content="ja_JP">',
     '<meta property="og:locale" content="en_US">\n'
     '<meta property="og:locale:alternate" content="zh_CN">\n'
     '<meta property="og:locale:alternate" content="zh_TW">\n'
     '<meta property="og:locale:alternate" content="ja_JP">'),
    (f'<meta property="og:title" content="{zh["meta.ogtitle"]}">',
     f'<meta property="og:title" content="{en["meta.ogtitle"]}">'),
    (f'<meta property="og:description" content="{zh["meta.ogdesc"]}">',
     f'<meta property="og:description" content="{en["meta.ogdesc"]}">'),
    (f'<meta property="og:image" content="{SITE}{zh["meta.ogimg"]}">',
     f'<meta property="og:image" content="{SITE}{en["meta.ogimg"]}">'),
    (f'<meta property="og:image:secure_url" content="{SITE}{zh["meta.ogimg"]}">',
     f'<meta property="og:image:secure_url" content="{SITE}{en["meta.ogimg"]}">'),
    (f'<meta property="og:image:alt" content="{ZH_OGALT}">',
     f'<meta property="og:image:alt" content="{EN_OGALT}">'),
    (f'<meta name="twitter:title" content="{zh["meta.ogtitle"]}">',
     f'<meta name="twitter:title" content="{en["meta.ogtitle"]}">'),
    (f'<meta name="twitter:description" content="{zh["meta.ogdesc"]}">',
     f'<meta name="twitter:description" content="{en["meta.ogdesc"]}">'),
    (f'<meta name="twitter:image" content="{SITE}{zh["meta.ogimg"]}">',
     f'<meta name="twitter:image" content="{SITE}{en["meta.ogimg"]}">'),
    ('<meta name="twitter:image:alt" content="AgentPixel 主視覺：四個像素風 Agent 並排在筆電前工作的深色控制台。">',
     '<meta name="twitter:image:alt" content="AgentPixel key visual: four pixel-art agents working side by side at laptops on a dark console.">'),
    ('<!-- 不吃 Open Graph 的舊式 / 中文平台抓取器（LINE、QQ、部分內建瀏覽器） -->',
     '<!-- Legacy / non-Open-Graph scrapers (LINE, QQ, some in-app browsers) -->'),
    (f'<link rel="image_src" href="{SITE}{zh["meta.ogimg"]}">',
     f'<link rel="image_src" href="{SITE}{en["meta.ogimg"]}">'),
    (f'<meta itemprop="name" content="{zh["meta.title"]}">',
     f'<meta itemprop="name" content="{en["meta.title"]}">'),
    (f'<meta itemprop="description" content="{zh["meta.ogdesc"]}">',
     f'<meta itemprop="description" content="{en["meta.ogdesc"]}">'),
    (f'<meta itemprop="image" content="{SITE}{zh["meta.ogimg"]}">',
     f'<meta itemprop="image" content="{SITE}{en["meta.ogimg"]}">'),
    (f'"url":"{SITE}","image":"{SITE}{zh["meta.ogimg"]}","description":"{zh["meta.ogdesc"]}","inLanguage":"zh-Hant"',
     f'"url":"{SITE}","image":"{SITE}{en["meta.ogimg"]}","description":"{en["meta.ogdesc"]}","inLanguage":"en"'),
]
for old, new in pairs:
    if s.count(old) != 1:
        sys.exit(f"expected exactly one match, found {s.count(old)}: {old[:90]}")
    s = s.replace(old, new)

MASTER.write_text(s, encoding="utf-8")
print("index.html is now the English master")
