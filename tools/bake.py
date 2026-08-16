#!/usr/bin/env python3
"""Bake every language page from one master document.

`index.html` is both the editable master and the site's default-language
page. Every other language is the same document with three things swapped:

  1. per-language <head> meta (title, description, canonical, og:*,
     twitter:*, JSON-LD),
  2. the static text pre-rendered inside every [data-i18n] /
     [data-i18n-html] / [data-i18n-attr] element, so the page reads
     correctly before the JS runs and to crawlers that never run it,
  3. pick() pinned to that language.

Everything else — CSS, markup, the I18N dictionaries, scripts — is
byte-identical across all four files.

**SOURCE_LANG is the language the master file is currently baked in**, and
it is what the swap patterns match against. It is not necessarily the
site's default: on 2026-08-17 the default moved to English while Chinese
kept the master's editing history, and for one run those differed. Keep
this in step with whatever `index.html` actually contains.

Usage:  python3 tools/bake.py          # write every page
        python3 tools/bake.py --check  # validate keys only, write nothing
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "index.html"
SITE = "https://adrianwu8516.github.io/agentpixel-site/"

# The language `index.html` currently holds. See the note above.
SOURCE_LANG = "en"

# lang -> (folder or None for the site root, html lang, og:locale, JSON-LD)
LANGS = {
    "en": (None,  "en",      "en_US", "en"),
    "cn": ("cn",  "zh-Hans", "zh_CN", "zh-Hans"),
    "zh": ("tw",  "zh-Hant", "zh_TW", "zh-Hant"),
    "ja": ("ja",  "ja",      "ja_JP", "ja"),
}
# Also the order the switcher renders in.
ORDER = ["en", "cn", "zh", "ja"]

src = MASTER.read_text(encoding="utf-8")

# ── 1. pull the I18N object out with node so escapes/quotes are exact ──
m = re.search(r"var I18N = (\{.*?\n  \});\n", src, re.S)
if not m:
    sys.exit("I18N object not found")
i18n = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(" + m.group(1) + "))"]))
DICTS = {lang: i18n[lang] for lang in ORDER}
base = DICTS[SOURCE_LANG]

# ── 2. validate: every key referenced in markup exists in every dict ───
keys = set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', src))
for attr in re.findall(r'data-i18n-attr="([^"]+)"', src):
    for pair in attr.split("|"):
        keys.add(pair.split(":")[1])
missing = {lang: sorted(k for k in keys if k not in d) for lang, d in DICTS.items()}
bad = {k: v for k, v in missing.items() if v}
if bad:
    sys.exit(f"missing keys: {bad}")
print(f"i18n OK — {len(keys)} keys referenced, all present in {'/'.join(ORDER)}")
if "--check" in sys.argv:
    sys.exit(0)

def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")

def find_close(out, tag, start):
    """Nesting-aware close-tag search: skip inner <tag …></tag> pairs."""
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
            if cur != base[key]:
                print(f"  note[{lang}]: master text for {key} != {SOURCE_LANG} dict "
                      f"({cur[:40]!r} vs {base[key][:40]!r}) — overwritten")
            res.append(out[pos:start]); res.append(d[key]); pos = close
        res.append(out[pos:])
        return "".join(res)
    out = swap_inner(out, "data-i18n")
    out = swap_inner(out, "data-i18n-html")

    def swap_attr(mm):
        tag = mm.group(0)
        for pair in mm.group(1).split("|"):
            name, key = pair.split(":")
            old = f'{name}="{esc_attr(base[key])}"'
            new = f'{name}="{esc_attr(d[key])}"'
            if old not in tag:
                sys.exit(f"[{lang}] attr {name} for {key} not found in tag: {tag[:120]}")
            tag = tag.replace(old, new)
        return tag
    out = re.sub(r'<[^>]*data-i18n-attr="([^"]+)"[^>]*>', swap_attr, out)

    for old, new in meta:
        if out.count(old) != 1:
            sys.exit(f"[{lang}] head pattern count != 1 ({out.count(old)}): {old[:100]}")
        out = out.replace(old, new)

    pin = f'    return "{lang}";\n'
    generic = ("    var n = (navigator.language || 'en').toLowerCase();\n"
               "    if (n.indexOf('ja') === 0) return 'ja';\n"
               "    if (/^zh-(cn|hans|sg)/.test(n)) return 'cn';\n"
               "    if (n.indexOf('zh') === 0) return 'zh';\n"
               "    return 'en';\n")
    if generic in out:
        out = out.replace(generic, pin)
    else:
        sys.exit("pick()'s detection block not found — did its text change?")
    return out

ALT = {
    "en": ('AgentPixel key visual: “{og}” with four pixel-art agents working side by side at laptops on a dark console.',
           "AgentPixel key visual: four pixel-art agents working side by side at laptops on a dark console.",
           "<!-- Legacy / non-Open-Graph scrapers (LINE, QQ, some in-app browsers) -->"),
    "cn": ('AgentPixel 主视觉：「{og}」右侧是四个像素风 Agent 并排在笔电前工作的深色控制台。',
           "AgentPixel 主视觉：四个像素风 Agent 并排在笔电前工作的深色控制台。",
           "<!-- 不支持 Open Graph 的旧式 / 中文平台抓取器（LINE、QQ、部分内置浏览器） -->"),
    "zh": ('AgentPixel 主視覺：「{og}」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。',
           "AgentPixel 主視覺：四個像素風 Agent 並排在筆電前工作的深色控制台。",
           "<!-- 不吃 Open Graph 的舊式 / 中文平台抓取器（LINE、QQ、部分內建瀏覽器） -->"),
    "ja": ('AgentPixel のキービジュアル：「{og}」右側は 4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。',
           "AgentPixel のキービジュアル：4 体のピクセルアートのエージェントがノートPCで作業しているダークなコンソール。",
           "<!-- Open Graph 非対応 / レガシーなクローラー向け（LINE、QQ、各種アプリ内ブラウザ） -->"),
}

def url_for(lang):
    folder = LANGS[lang][0]
    return SITE if folder is None else f"{SITE}{folder}/"

def locale_block(lang):
    own = LANGS[lang][2]
    others = [LANGS[l][2] for l in ORDER if l != lang]
    return (f'<meta property="og:locale" content="{own}">\n' +
            "\n".join(f'<meta property="og:locale:alternate" content="{a}">' for a in others))

def head_pairs(lang):
    d, s0 = DICTS[lang], DICTS[SOURCE_LANG]
    img, img0 = d["meta.ogimg"], s0["meta.ogimg"]
    ogalt, twalt, legacy = ALT[lang]
    ogalt0, twalt0, legacy0 = ALT[SOURCE_LANG]
    return [
        (f'<html lang="{LANGS[SOURCE_LANG][1]}"><head>', f'<html lang="{LANGS[lang][1]}"><head>'),
        (f"<title>{s0['meta.title']}</title>", f"<title>{d['meta.title']}</title>"),
        (f'<meta name="description" content="{s0["meta.desc"]}">', f'<meta name="description" content="{d["meta.desc"]}">'),
        (f'<link rel="canonical" href="{url_for(SOURCE_LANG)}">', f'<link rel="canonical" href="{url_for(lang)}">'),
        (locale_block(SOURCE_LANG), locale_block(lang)),
        (f'"url":"{url_for(SOURCE_LANG)}","image":"{SITE}{img0}","description":"{s0["meta.ogdesc"]}","inLanguage":"{LANGS[SOURCE_LANG][3]}"',
         f'"url":"{url_for(lang)}","image":"{SITE}{img}","description":"{d["meta.ogdesc"]}","inLanguage":"{LANGS[lang][3]}"'),
        (f'<meta property="og:url" content="{url_for(SOURCE_LANG)}">', f'<meta property="og:url" content="{url_for(lang)}">'),
        (f'<meta property="og:title" content="{s0["meta.ogtitle"]}">', f'<meta property="og:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta property="og:description" content="{s0["meta.ogdesc"]}">', f'<meta property="og:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta property="og:image" content="{SITE}{img0}">', f'<meta property="og:image" content="{SITE}{img}">'),
        (f'<meta property="og:image:secure_url" content="{SITE}{img0}">', f'<meta property="og:image:secure_url" content="{SITE}{img}">'),
        (f'<meta property="og:image:alt" content="{ogalt0.format(og=s0["meta.ogtitle"])}">',
         f'<meta property="og:image:alt" content="{ogalt.format(og=d["meta.ogtitle"])}">'),
        (f'<meta name="twitter:title" content="{s0["meta.ogtitle"]}">', f'<meta name="twitter:title" content="{d["meta.ogtitle"]}">'),
        (f'<meta name="twitter:description" content="{s0["meta.ogdesc"]}">', f'<meta name="twitter:description" content="{d["meta.ogdesc"]}">'),
        (f'<meta name="twitter:image" content="{SITE}{img0}">', f'<meta name="twitter:image" content="{SITE}{img}">'),
        (f'<meta name="twitter:image:alt" content="{twalt0}">', f'<meta name="twitter:image:alt" content="{twalt}">'),
        (legacy0, legacy),
        (f'<link rel="image_src" href="{SITE}{img0}">', f'<link rel="image_src" href="{SITE}{img}">'),
        (f'<meta itemprop="name" content="{s0["meta.title"]}">', f'<meta itemprop="name" content="{d["meta.title"]}">'),
        (f'<meta itemprop="description" content="{s0["meta.ogdesc"]}">', f'<meta itemprop="description" content="{d["meta.ogdesc"]}">'),
        (f'<meta itemprop="image" content="{SITE}{img0}">', f'<meta itemprop="image" content="{SITE}{img}">'),
    ]

for lang in ORDER:
    folder = LANGS[lang][0]
    # The source language still goes through head_pairs; every pair is an
    # identity replacement, which keeps one code path instead of two.
    out = bake(lang, DICTS[lang], head_pairs(lang))
    target = MASTER if folder is None else ROOT / folder / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(out.splitlines())} lines)")
