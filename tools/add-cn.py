#!/usr/bin/env python3
"""One-time: add a Simplified-Chinese ('cn') entry to the I18N object in
index.html, machine-translated from the zh (Traditional, Taiwan-phrasing)
dict via OpenCC's tw2sp profile (Taiwan characters+vocabulary -> Simplified
characters + Mainland vocabulary, e.g. 軟體 -> 软件, 記憶體 -> 内存).

Idempotent: if a 'cn:' block already exists, it is replaced, not duplicated.
Run once, then hand-review the diff — machine conversion of vocabulary is
good but not perfect (proper nouns, brand names are left alone by OpenCC).
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "index.html"
OPENCC_PY = ROOT / "tools" / "opencc-venv" / "bin" / "python3"

src = MASTER.read_text(encoding="utf-8")
m = re.search(r"var I18N = (\{.*?\n  \});\n", src, re.S)
if not m:
    sys.exit("I18N object not found")
i18n = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(" + m.group(1) + "))"]))
zh = i18n["zh"]

conv_script = r"""
import sys, json
from opencc import OpenCC
cc = OpenCC('tw2sp')
data = json.load(sys.stdin)
out = {k: cc.convert(v) for k, v in data.items()}
json.dump(out, sys.stdout, ensure_ascii=False)
"""
cn = json.loads(subprocess.run(
    [str(OPENCC_PY), "-c", conv_script],
    input=json.dumps(zh, ensure_ascii=False), capture_output=True, text=True, check=True,
).stdout)

# meta.ogimg must point at the cn-specific OG asset, not a converted zh.png
cn["meta.ogimg"] = "og-cn.png?v=2"

def dict_literal(d):
    lines = ["    cn: {"]
    items = list(d.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        lines.append(f"      {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    lines.append("    }")
    return "\n".join(lines)

block = dict_literal(cn)

if re.search(r"\n    cn: \{.*?\n    \},\n", src, re.S):
    src = re.sub(r"\n    cn: \{.*?\n    \},\n", "\n" + block + ",\n", src, count=1, flags=re.S)
    print("replaced existing cn: block")
else:
    # insert right after the zh dict's closing "    },\n" (the first one, i.e. end of `zh: {...}`)
    zh_end = re.search(r"(\n    zh: \{.*?\n    \},\n)", src, re.S)
    if not zh_end:
        sys.exit("could not locate end of zh: block")
    insert_at = zh_end.end()
    src = src[:insert_at] + block + ",\n" + src[insert_at:]
    print("inserted new cn: block")

MASTER.write_text(src, encoding="utf-8")
print(f"cn dict written — {len(cn)} keys")
