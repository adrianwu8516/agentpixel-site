#!/usr/bin/env python3
"""Bake cn/en/ja index.html from the zh master (index.html).

The four pages are the same document; cn/en/ja only differ in
  1. per-language <head> meta (title, description, canonical, og:*, twitter:*, JSON-LD),
  2. the static text pre-rendered inside every [data-i18n] / [data-i18n-html]
     / [data-i18n-attr] element (SEO + first paint before the JS runs),
  3. pick() returning a fixed language.
Everything else (CSS, markup, the I18N dictionaries, scripts) is byte-identical.
The zh master itself is also re-baked in place, so its own static text stays
normalized against the zh dict (catches drift from hand-edits).

Usage:  python3 tools/bake.py          # writes cn/, en/, ja/ index.html + normalizes the master
        python3 tools/bake.py --check  # only validate keys, write nothing
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "index.html"
SITE = "https://adrianwu8516.github.io/agentpixel-site/"

# lang code -> (folder, html-lang, og:locale, JSON-LD inLanguage)
LANGS = {
    "zh": (None,  "zh-Hant", "zh_TW", "zh-Hant"),
    "cn": ("cn",  "zh-Hans", "zh_CN", "zh-Hans"),
    "en": ("en",  "en",      "en_US", "en"),
    "ja": ("ja",  "ja",      "ja_JP", "ja"),
}
ORDER = ["zh", "cn", "en", "ja"]

src = MASTER.read_text(encoding="utf-8")

# ── 1. pull the I18N object out with node so escapes/quotes are exact ──
m = re.search(r"var I18N = (\{.*?\n  \});\n", src, re.S)
if not m:
    sys.exit("I18N object not found")
i18n = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(" + m.group(1) + "))"]))
DICTS = {lang: i18n[lang] for lang in ORDER}
zh = DICTS["zh"]

# ── 2. validate: every key referenced in markup exists in all four dicts ──
keys = set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', src))
for attr in re.findall(r'data-i18n-attr="([^"]+)"', src):
    for pair in attr.split("|"):
        keys.add(pair.split(":")[1])
missing = {lang: sorted(k for k in keys if k not in d) for lang, d in DICTS.items()}
bad = {k: v for k, v in missing.items() if v}
if bad:
    sys.exit(f"missing keys: {bad}")
extra = {lang: sorted(set(d) - set(zh)) for lang, d in DICTS.items() if lang != "zh"}
if any(extra.values()):
    print("note: keys present in a translation but not zh:", extra)
print(f"i18n OK — {len(keys)} keys referenced, all present in zh/cn/en/ja")
if "--check" in sys.argv:
    sys.exit(0)

def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")

def find_close(out, tag, start):
    # nesting-aware: skip inner <tag …>…</tag> pairs of the same tag name
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

def bake(lang, d, meta):
    out = src
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
    for old, new in meta:
        if out.count(old) != 1:
            sys.exit(f"[{lang}] head pattern count != 1: {old[:100]}")
        out = out.replace(old, new)
    old_pick = ("    var n = (navigator.language || 'zh').toLowerCase();\n"
                "    if (n.indexOf('ja') === 0) return 'ja';\n"
                "    if (/^zh-(cn|hans|sg)/.test(n)) return 'cn';\n"
                "    if (n.indexOf('zh') === 0) return 'zh';\n"
                "    return 'en';\n")
    if lang != "zh":
        if out.count(old_pick) != 1:
            sys.exit("pick() block not found")
        out = out.replace(old_pick, f'    return "{lang}";\n')
    return out

OGALT = {
    "cn": "AgentPixel 主视觉：「{}」右侧是四个像素风 Agent 并排在笔电前工作的深色控制台。".format(DICTS["cn"]["meta.ogtitle"]),
    "en": "AgentPixel key visual: “{}” with four pixel-art agents working side by side at laptops on a dark console.".format(DICTS["en"]["meta.ogtitle"]),
    "ja": "AgentPixel のキービジュアル：「{}」右側は 4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。".format(DICTS["ja"]["meta.ogtitle"]),
}
TWALT = {
    "cn": "AgentPixel 主视觉：四个像素风 Agent 并排在笔电前工作的深色控制台。",
    "en": "AgentPixel key visual: four pixel-art agents working side by side at laptops on a dark console.",
    "ja": "AgentPixel のキービジュアル：4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。",
}
LEGACY = {
    "cn": "<!-- 不支持 Open Graph 的旧式 / 中文平台抓取器（LINE、QQ、部分内置浏览器） -->",
    "en": "<!-- Legacy / non-Open-Graph scrapers (LINE, QQ, some in-app browsers) -->",
    "ja": "<!-- Open Graph 非対応 / レガシーなクローラー向け（LINE、QQ、各種アプリ内ブラウザ） -->",
}

def head_pairs(lang):
    folder, html_lang, locale, jsonld_lang = LANGS[lang]
    d = DICTS[lang]
    url = SITE if lang == "zh" else f"{SITE}{folder}/"
    ogimg = d["meta.ogimg"]
    zh_title, zh_desc, zh_og, zh_ogd = zh["meta.title"], zh["meta.desc"], zh["meta.ogtitle"], zh["meta.ogdesc"]
    zh_ogimg = zh["meta.ogimg"]
    alt_locales = [LANGS[l][2] for l in ORDER if l != lang]
    zh_locale_block = ('<meta property="og:locale" content="zh_TW">\n'
                        '<meta property="og:locale:alternate" content="zh_CN">\n'
                        '<meta property="og:locale:alternate" content="en_US">\n'
                        '<meta property="og:locale:alternate" content="ja_JP">')
    new_locale_block = (f'<meta property="og:locale" content="{locale}">\n' +
                         "\n".join(f'<meta property="og:locale:alternate" content="{a}">' for a in alt_locales))
    return [
        ('<html lang="zh-Hant"><head>', f'<html lang="{html_lang}"><head>'),
        (f"<title>{zh_title}</title>", f"<title>{d['meta.title']}</title>"),
        (f'<meta name="description" content="{zh_desc}">', f'<meta name="description" content="{d["meta.desc"]}">'),
        (f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{url}">'),
        (zh_locale_block, new_locale_block),
        (f'"url":"{SITE}","image":"{SITE}{zh_ogimg}","description":"{zh_ogd}","inLanguage":"zh-Hant"',
         f'"url":"{url}","image":"{SITE}{ogimg}","description":"{d["meta.ogdesc"]}","inLanguage":"{jsonld_lang}"'),
        (f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{url}">'),
        (f'<meta property="og:title" content="{zh_og}">', f'<meta property="og:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta property="og:description" content="{zh_ogd}">', f'<meta property="og:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta property="og:image" content="{SITE}{zh_ogimg}">', f'<meta property="og:image" content="{SITE}{ogimg}">'),
        (f'<meta property="og:image:secure_url" content="{SITE}{zh_ogimg}">', f'<meta property="og:image:secure_url" content="{SITE}{ogimg}">'),
        (f'<meta property="og:image:alt" content="AgentPixel 主視覺：「{zh_og}」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。">',
         f'<meta property="og:image:alt" content="{OGALT[lang]}">'),
        (f'<meta name="twitter:title" content="{zh_og}">', f'<meta name="twitter:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta name="twitter:description" content="{zh_ogd}">', f'<meta name="twitter:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta name="twitter:image" content="{SITE}{zh_ogimg}">', f'<meta name="twitter:image" content="{SITE}{ogimg}">'),
        ('<meta name="twitter:image:alt" content="AgentPixel 主視覺：四個像素風 Agent 並排在筆電前工作的深色控制台。">',
         f'<meta name="twitter:image:alt" content="{TWALT[lang]}">'),
        ('<!-- 不吃 Open Graph 的舊式 / 中文平台抓取器（LINE、QQ、部分內建瀏覽器） -->', LEGACY[lang]),
        (f'<link rel="image_src" href="{SITE}{zh_ogimg}">', f'<link rel="image_src" href="{SITE}{ogimg}">'),
        (f'<meta itemprop="name" content="{zh_title}">', f'<meta itemprop="name" content="{d["meta.title"]}">'),
        (f'<meta itemprop="description" content="{zh_ogd}">', f'<meta itemprop="description" content="{d["meta.ogdesc"]}">'),
        (f'<meta itemprop="image" content="{SITE}{zh_ogimg}">', f'<meta itemprop="image" content="{SITE}{ogimg}">'),
    ]

for lang in ORDER:
    folder = LANGS[lang][0]
    meta_pairs = [] if lang == "zh" else head_pairs(lang)
    out = bake(lang, DICTS[lang], meta_pairs)
    target = MASTER if lang == "zh" else ROOT / folder / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(out.splitlines())} lines)")
