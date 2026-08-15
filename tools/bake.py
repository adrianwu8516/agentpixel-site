#!/usr/bin/env python3
"""Bake en/index.html and ja/index.html from the zh master (index.html).

The three pages are the same document; en/ and ja/ only differ in
  1. per-language <head> meta (title, description, canonical, og:*, twitter:*),
  2. the static text pre-rendered inside every [data-i18n] / [data-i18n-html]
     / [data-i18n-attr] element (SEO + first paint before the JS runs),
  3. pick() returning a fixed language.
Everything else (CSS, markup, the I18N dictionaries, scripts) is byte-identical.

Usage:  python3 tools/bake.py          # writes en/index.html and ja/index.html
        python3 tools/bake.py --check  # only validate keys, write nothing
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "index.html"
SITE = "https://adrianwu8516.github.io/agentpixel-site/"

src = MASTER.read_text(encoding="utf-8")

# ── 1. pull the I18N object out with node so escapes/quotes are exact ──
m = re.search(r"var I18N = (\{.*?\n  \});\n", src, re.S)
if not m:
    sys.exit("I18N object not found")
i18n = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(" + m.group(1) + "))"]))
zh, en, ja = i18n["zh"], i18n["en"], i18n["ja"]

# ── 2. validate: every key referenced in markup exists in all three dicts ──
keys = set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', src))
for attr in re.findall(r'data-i18n-attr="([^"]+)"', src):
    for pair in attr.split("|"):
        keys.add(pair.split(":")[1])
missing = {lang: sorted(k for k in keys if k not in d) for lang, d in (("zh", zh), ("en", en), ("ja", ja))}
bad = {k: v for k, v in missing.items() if v}
if bad:
    sys.exit(f"missing keys: {bad}")
extra = {lang: sorted(set(d) - set(zh)) for lang, d in (("en", en), ("ja", ja))}
if any(extra.values()):
    print("note: keys present in en/ja but not zh:", extra)
print(f"i18n OK — {len(keys)} keys referenced, all present in zh/en/ja")
if "--check" in sys.argv:
    sys.exit(0)

def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")

def bake(lang, d, meta):
    out = src
    # 2a. static text inside data-i18n / data-i18n-html elements.
    # The master is zh-baked, so the element's current inner text == zh[key];
    # replace that exact inner text with the target language's value.
    def find_close(out, tag, start):
        # nesting-aware: skip inner <tag …>…</tag> pairs of the same tag name
        depth, i = 1, start
        open_re = re.compile(r'<' + tag + r'\b[^>]*?(/?)>')
        close_s = '</' + tag + '>'
        while depth:
            nc = out.find(close_s, i)
            mo = open_re.search(out, i)
            if mo and mo.start() < nc and not mo.group(1):
                depth += 1; i = mo.end()
            else:
                depth -= 1; i = nc + len(close_s)
                if depth == 0: return nc
        return -1
    def swap_inner(out, attr):
        pat = re.compile(r'(<([a-zA-Z0-9]+)\b[^>]*\b' + attr + r'="([^"]+)"[^>]*>)')
        pos, res = 0, []
        for mm in pat.finditer(out):
            if mm.start() < pos: continue
            key, tag = mm.group(3), mm.group(2)
            start = mm.end()
            close = find_close(out, tag, start)
            cur = out[start:close]
            if cur != zh[key]:
                print(f"  note[{lang}]: master text for {key} != zh dict ({cur[:40]!r} vs {zh[key][:40]!r}) — overwritten")
            res.append(out[pos:start]); res.append(d[key]); pos = close
        res.append(out[pos:])
        return "".join(res)
    out = swap_inner(out, "data-i18n")
    out = swap_inner(out, "data-i18n-html")
    # 2b. attribute values driven by data-i18n-attr
    def swap_attr(mm):
        tag = mm.group(0)
        for pair in mm.group(1).split("|"):
            name, key = pair.split(":")
            old = f'{name}="{esc_attr(zh[key])}"'
            new = f'{name}="{esc_attr(d[key])}"'
            if old not in tag:
                sys.exit(f"[{lang}] attr {name} for {key} not found in tag: {tag[:120]}")
            tag = tag.replace(old, new)
        return tag
    out = re.sub(r'<[^>]*data-i18n-attr="([^"]+)"[^>]*>', swap_attr, out)
    # 3. head meta
    for old, new in meta:
        if out.count(old) != 1:
            sys.exit(f"[{lang}] head pattern count != 1: {old[:100]}")
        out = out.replace(old, new)
    # 4. fixed language
    old_pick = ("    var n = (navigator.language || 'zh').toLowerCase();\n"
                "    if (n.indexOf('ja') === 0) return 'ja';\n"
                "    if (n.indexOf('zh') === 0) return 'zh';\n"
                "    return 'en';\n")
    if lang != "zh":
        if out.count(old_pick) != 1:
            sys.exit("pick() block not found")
        out = out.replace(old_pick, f'    return "{lang}";\n')
    return out

def head_pairs(lang, d, ogfile, locale, alt_locale, ogalt, twalt, legacy_comment):
    zh_title = zh["meta.title"]; zh_desc = zh["meta.desc"]; zh_og = zh["meta.ogtitle"]; zh_ogd = zh["meta.ogdesc"]
    ogimg = zh["meta.ogimg"]  # og.png?v=N
    return [
        ('<html lang="zh-Hant"><head>', f'<html lang="{ {"en":"en","ja":"ja"}[lang] }"><head>'),
        (f"<title>{zh_title}</title>", f"<title>{d['meta.title']}</title>"),
        (f'<meta name="description" content="{zh_desc}">', f'<meta name="description" content="{d["meta.desc"]}">'),
        (f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{SITE}{lang}/">'),
        ('<meta property="og:locale" content="zh_TW">\n<meta property="og:locale:alternate" content="en_US">\n<meta property="og:locale:alternate" content="ja_JP">',
         f'<meta property="og:locale" content="{locale}">\n<meta property="og:locale:alternate" content="zh_TW">\n<meta property="og:locale:alternate" content="{alt_locale}">'),
        (f'"url":"{SITE}","image":"{SITE}{ogimg}","description":"{zh_ogd}","inLanguage":"zh-Hant"',
         f'"url":"{SITE}{lang}/","image":"{SITE}{ogfile}","description":"{d["meta.ogdesc"]}","inLanguage":"{ {"en":"en","ja":"ja"}[lang] }"'),
        (f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{SITE}{lang}/">'),
        (f'<meta property="og:title" content="{zh_og}">', f'<meta property="og:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta property="og:description" content="{zh_ogd}">', f'<meta property="og:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta property="og:image" content="{SITE}{ogimg}">', f'<meta property="og:image" content="{SITE}{ogfile}">'),
        (f'<meta property="og:image:secure_url" content="{SITE}{ogimg}">', f'<meta property="og:image:secure_url" content="{SITE}{ogfile}">'),
        (f'<meta property="og:image:alt" content="AgentPixel 主視覺：「{zh_og}」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。">',
         f'<meta property="og:image:alt" content="{ogalt}">'),
        (f'<meta name="twitter:title" content="{zh_og}">', f'<meta name="twitter:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta name="twitter:description" content="{zh_ogd}">', f'<meta name="twitter:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta name="twitter:image" content="{SITE}{ogimg}">', f'<meta name="twitter:image" content="{SITE}{ogfile}">'),
        ('<meta name="twitter:image:alt" content="AgentPixel 主視覺：四個像素風 Agent 並排在筆電前工作的深色控制台。">',
         f'<meta name="twitter:image:alt" content="{twalt}">'),
        ('<!-- 不吃 Open Graph 的舊式 / 中文平台抓取器（LINE、QQ、部分內建瀏覽器） -->', legacy_comment),
        (f'<link rel="image_src" href="{SITE}{ogimg}">', f'<link rel="image_src" href="{SITE}{ogfile}">'),
        (f'<meta itemprop="name" content="{zh_title}">', f'<meta itemprop="name" content="{d["meta.title"]}">'),
        (f'<meta itemprop="description" content="{zh_ogd}">', f'<meta itemprop="description" content="{d["meta.ogdesc"]}">'),
        (f'<meta itemprop="image" content="{SITE}{ogimg}">', f'<meta itemprop="image" content="{SITE}{ogfile}">'),
    ]

EN = head_pairs("en", en, en["meta.ogimg"], "en_US", "ja_JP",
    f'AgentPixel key visual: “{en["meta.ogtitle"]}” with four pixel-art agents working side by side at laptops on a dark console.',
    "AgentPixel key visual: four pixel-art agents working side by side at laptops on a dark console.",
    "<!-- Legacy / non-Open-Graph scrapers (LINE, QQ, some in-app browsers) -->")
JA = head_pairs("ja", ja, ja["meta.ogimg"], "ja_JP", "en_US",
    f'AgentPixel のキービジュアル：「{ja["meta.ogtitle"]}」右側は 4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。',
    "AgentPixel のキービジュアル：4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。",
    "<!-- Open Graph 非対応 / レガシーなクローラー向け（LINE、QQ、各種アプリ内ブラウザ） -->")

for lang, d, pairs in (("zh", zh, []), ("en", en, EN), ("ja", ja, JA)):
    out = bake(lang, d, pairs)
    target = MASTER if lang == "zh" else ROOT / lang / "index.html"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(out.splitlines())} lines)")
