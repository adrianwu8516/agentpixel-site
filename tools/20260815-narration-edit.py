#!/usr/bin/env python3
"""One-shot narration rewrite (2026-08-15): "Terminal，升級成辦公軟體了。"

Applies exact-string replacements to index.html (the zh master). Every
pattern must match exactly once, otherwise the script aborts before writing.
en/ and ja/ are regenerated afterwards by tools/bake.py.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "index.html"
s = P.read_text(encoding="utf-8")
orig = s

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"ABORT: expected {count} match(es), found {n} for:\n{old[:120]}")
    s = s.replace(old, new)

# ───────────────────────── head meta (zh) ─────────────────────────
rep('<title>AgentPixel — Terminal 才是最強辦公軟體</title>',
    '<title>AgentPixel — Terminal，升級成辦公軟體了</title>')
rep('<meta name="description" content="你下指令，Agent 寫文件，你在旁邊看著它一個字一個字寫出來。不順眼的地方，自己改。支援 Claude Code 與 Codex。">',
    '<meta name="description" content="AI 在左邊寫，你在右邊改——同一份檔案、同一個時間。Excel、Word、PDF、CSV 都在旁邊直接看，該改就改。支援 Claude Code 與 Codex。">')
rep('<meta property="og:title" content="Terminal 才是最強辦公軟體！">',
    '<meta property="og:title" content="Terminal，升級成辦公軟體了。">')
rep('<meta property="og:description" content="看著 Agent 幫你寫報告。看不順眼，直接改。支援 Claude Code 與 Codex。">',
    '<meta property="og:description" content="AI 在左邊寫，你在右邊改。你看的是文件，不是指令。支援 Claude Code 與 Codex。">')
rep('<meta name="twitter:title" content="Terminal 才是最強辦公軟體！">',
    '<meta name="twitter:title" content="Terminal，升級成辦公軟體了。">')
rep('<meta name="twitter:description" content="看著 Agent 幫你寫報告。看不順眼，直接改。支援 Claude Code 與 Codex。">',
    '<meta name="twitter:description" content="AI 在左邊寫，你在右邊改。你看的是文件，不是指令。支援 Claude Code 與 Codex。">')
rep('<meta itemprop="name" content="AgentPixel — Terminal 才是最強辦公軟體">',
    '<meta itemprop="name" content="AgentPixel — Terminal，升級成辦公軟體了">')
rep('<meta itemprop="description" content="看著 Agent 幫你寫報告。看不順眼，直接改。支援 Claude Code 與 Codex。">',
    '<meta itemprop="description" content="AI 在左邊寫，你在右邊改。你看的是文件，不是指令。支援 Claude Code 與 Codex。">')
rep('content="AgentPixel 主視覺：「最強的辦公軟體，是一個 Terminal。」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。"',
    'content="AgentPixel 主視覺：「Terminal，升級成辦公軟體了。」右側是四個像素風 Agent 並排在筆電前工作的深色控制台。"')
# cache-bust the OG image (pixels change in this same commit)
rep('og.png?v=3', 'og.png?v=4', count=s.count('og.png?v=3'))

# ───────────────────────── hero (static zh) ─────────────────────────
rep('<span data-i18n="hero.eyebrow">用 AI 全面提升日常工作生產力</span>',
    '<span data-i18n="hero.eyebrow">跟 AI 並肩工作 · Claude Code 與 Codex</span>')
rep('<h1 data-i18n-html="hero.h1" class="headline punch"><span class="nowrap">Terminal 才是</span><span class="grad">最強辦公軟體！</span></h1>',
    '<h1 data-i18n-html="hero.h1" class="headline punch"><span class="nowrap">Terminal，</span><span class="grad">升級成辦公軟體了。</span></h1>')
rep('<p data-i18n="hero.sub" class="sub">看著 AI 寫，隨時動手改。像搭檔一樣，一起把工作做完。</p>',
    '<p data-i18n="hero.sub" class="sub">AI 在左邊寫，你在右邊改——同一份檔案、同一個時間。你看的是文件，不是指令。</p>')

# ───────────────────────── nav ─────────────────────────
rep('<a data-i18n="nav.see" href="#see">看得見</a>', '<a data-i18n="nav.see" href="#see">並肩工作</a>')

# ───────────────────────── section 1 (static zh) ─────────────────────────
rep('<h2 data-i18n="s1.h2">AI 寫完了。檔案在哪？</h2>',
    '<h2 data-i18n="s1.h2">它寫，你改。同一份檔案。</h2>')
rep('<p data-i18n="s1.lede" class="pillar-lede">它一次生五份檔案。你不該還要開 Finder 一個一個找，更不該為了改四個字重下一次 prompt。</p>',
    '<p data-i18n="s1.lede" class="pillar-lede">我們叫它並肩工作：AI 一次生五份檔案，生出來就在左邊；你看著它寫，不順眼就直接改——不必等它跑完，也不必為了改四個字重下一次 prompt。</p>')

# third feature button (after f2)
rep('''            <li data-i18n="s1.f2b">想改就點進去打字，人和 AI 共用同一份檔案。</li>
          </ul></div></div>
          <div class="feat-progress"><span></span></div>
        </button>
      </div>
''', '''            <li data-i18n="s1.f2b">想改就點進去打字，人和 AI 共用同一份檔案。</li>
          </ul></div></div>
          <div class="feat-progress"><span></span></div>
        </button>
        <button class="feat" type="button">
          <span data-i18n="s1.f3k" class="feat-kicker">Excel、Word、PDF 也一樣</span>
          <h3 data-i18n="s1.f3h">40 多種格式，在旁邊直接看，該改就改</h3>
          <div class="feat-body"><div><ul>
            <li data-i18n-html="s1.f3a">試算表、Word、PDF、CSV、Notebook、資料庫……<b>都在同一個視窗裡渲染出來</b>，不用切去別的 App。</li>
            <li data-i18n="s1.f3b">表格類（CSV、Excel、SQLite）直接改儲存格、存回原檔；文件類一鍵交給預設 App。</li>
          </ul></div></div>
          <div class="feat-progress"><span></span></div>
        </button>
      </div>
''')

# third demo (spreadsheet) after demo-doc
rep('''                  <div data-i18n-html="d.d.note" class="d-doc-note"><b>LLM 生成</b> · 你可以直接<b>選取、刪改</b>、續寫</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
''', '''                  <div data-i18n-html="d.d.note" class="d-doc-note"><b>LLM 生成</b> · 你可以直接<b>選取、刪改</b>、續寫</div>
                </div>
              </div>
            </div>
            <div class="demo demo-doc demo-xlsx" data-title="Q2-expenses.xlsx — 直接看，直接改" data-i18n-attr="data-title:w.4">
              <div class="d-split">
                <div class="d-l">
                  <div data-i18n-html="d.s.cmd"><span class="d-clr-p">$</span> claude "把 Q2 開支整理成 Excel"</div>
                  <div data-i18n-html="d.s.a" class="l2"><span class="d-clr-a">◇</span> <span class="d-clr-o">建立 Q2-expenses.xlsx</span></div>
                  <div data-i18n-html="d.s.b" class="l3"><span class="d-clr-t">✓</span> <span class="d-clr-o">2 個工作表 · 48 列</span></div>
                </div>
                <div class="d-r">
                  <div class="d-doc-tabs">
                    <span class="d-doc-tab active">Q2-expenses.xlsx</span>
                    <span class="d-doc-tab">report.md</span>
                  </div>
                  <div class="d-sheet-tabs"><span data-i18n="d.s.sh1" class="active">明細</span><span data-i18n="d.s.sh2">摘要</span></div>
                  <table class="d-grid" aria-label="Q2 expenses">
                    <thead><tr><th data-i18n="d.s.h1">項目</th><th data-i18n="d.s.h2">上季</th><th data-i18n="d.s.h3">本季</th><th data-i18n="d.s.h4">變化</th></tr></thead>
                    <tbody>
                      <tr><td data-i18n="d.s.r1">雲端運算</td><td>412,000</td><td>348,000</td><td class="neg">−15.5%</td></tr>
                      <tr><td data-i18n="d.s.r2">供應商</td><td>265,000</td><td>240,000</td><td class="neg">−9.4%</td></tr>
                      <tr><td data-i18n="d.s.r3">訂閱服務</td><td>88,000</td><td class="d-cell-h">61,000</td><td class="neg">−30.7%</td></tr>
                    </tbody>
                  </table>
                  <div data-i18n="d.s.tag" class="d-edit-tag d-edit-tag-x">✎ 手動修改 · 已存回 .xlsx</div>
                  <div data-i18n-html="d.s.note" class="d-doc-note"><b>Agent 產出</b> · 你直接改儲存格，<b>樣式與其他工作表原封不動</b></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
''')

# CSS for the spreadsheet demo — appended right after the co-edit block
rep('''  .d-l .l2 { opacity: 0; }
  .demo.active .d-l .l2 { animation: fadeUp .4s ease .5s forwards; }
''', '''  .d-l .l2 { opacity: 0; }
  .demo.active .d-l .l2 { animation: fadeUp .4s ease .5s forwards; }
  .d-l .l3 { opacity: 0; }
  .demo.active .d-l .l3 { animation: fadeUp .4s ease 1.1s forwards; }

  /* --- demo 3: spreadsheet, agent-made, human-edited cell --- */
  .d-sheet-tabs { display: flex; gap: 2px; margin: -4px 0 10px; font-size: 10.5px; }
  .d-sheet-tabs span {
    padding: 2px 10px; border: 1px solid #e3e6eb; border-bottom: none; border-radius: 5px 5px 0 0;
    color: #6b7280; background: #f4f6f9;
  }
  .d-sheet-tabs span.active { color: #12161c; background: #fff; font-weight: 600; }
  .d-grid {
    width: 100%; border-collapse: collapse; font-size: 11.5px; color: #1a1f27;
    font-variant-numeric: tabular-nums;
  }
  .d-grid th, .d-grid td { border: 1px solid #e3e6eb; padding: 5px 8px; text-align: right; white-space: nowrap; }
  .d-grid th { background: #f4f6f9; color: #4a515c; font-weight: 600; font-size: 10.5px; }
  .d-grid th:first-child, .d-grid td:first-child { text-align: left; }
  .d-grid td.neg { color: #0f7b6c; }
  .d-grid td.d-cell-h {
    color: #1e4fa3; font-weight: 600; position: relative;
    box-shadow: inset 0 0 0 1.5px rgba(59,130,246,0); background: rgba(59,130,246,0);
  }
  .demo.active .d-grid td.d-cell-h { animation: cellEdit .5s ease 1.6s forwards; }
  @keyframes cellEdit {
    to { box-shadow: inset 0 0 0 1.5px rgba(59,130,246,.9); background: rgba(59,130,246,.12); }
  }
  .d-edit-tag-x { opacity: 0; transform: translateY(-3px); }
  .demo.active .d-edit-tag-x { animation: fadeUp .3s ease 2.1s forwards; }
''')

# ───────────────────────── section 2 (static zh) ─────────────────────────
rep('<p data-i18n="s2.lede" class="pillar-lede">誰在忙、誰舉手、誰做完了，一眼看完。順便告訴你，電腦還撐得住幾個。</p>',
    '<p data-i18n="s2.lede" class="pillar-lede">誰在忙、誰舉手、誰做完了，一眼看完。順便告訴你：整台電腦用了多少、AgentPixel 占多少、還撐得住幾個。</p>')
rep('<div data-i18n-html="d.o.cpu" class="po-mlab"><span>CPU</span><span class="po-mval">42%</span></div>',
    '<div data-i18n-html="d.o.cpu" class="po-mlab"><span>整台電腦</span><span class="po-mval">6.1 / 16 GB</span></div>')
rep('<div data-i18n-html="d.o.mem" class="po-mlab"><span>記憶體</span><span class="po-mval">6.1 / 16 GB</span></div>',
    '<div data-i18n-html="d.o.mem" class="po-mlab"><span>AgentPixel</span><span class="po-mval">1.4 GB</span></div>')

# ───────────────────────── download ─────────────────────────
rep('<h2 data-i18n="dl.h2">讓 Terminal 成為你的辦公室</h2>', '<h2 data-i18n="dl.h2">把你的 Terminal 升級成辦公軟體</h2>')

# ───────────────────────── i18n dicts ─────────────────────────
# zh
rep("'meta.title': 'AgentPixel — Terminal 才是最強辦公軟體',", "'meta.title': 'AgentPixel — Terminal，升級成辦公軟體了',")
rep("'meta.desc': '你下指令，Agent 寫文件，你在旁邊看著它一個字一個字寫出來。不順眼的地方，自己改。支援 Claude Code 與 Codex。',",
    "'meta.desc': 'AI 在左邊寫，你在右邊改——同一份檔案、同一個時間。Excel、Word、PDF、CSV 都在旁邊直接看，該改就改。支援 Claude Code 與 Codex。',")
rep("'meta.ogtitle': 'Terminal 才是最強辦公軟體！',", "'meta.ogtitle': 'Terminal，升級成辦公軟體了。',")
rep("'meta.ogdesc': '看著 Agent 幫你寫報告。看不順眼，直接改。支援 Claude Code 與 Codex。',",
    "'meta.ogdesc': 'AI 在左邊寫，你在右邊改。你看的是文件，不是指令。支援 Claude Code 與 Codex。',")
# (zh 'meta.ogimg' already bumped by the global og.png?v=3 → v=4 replace above)
rep("'nav.see': '看得見',", "'nav.see': '並肩工作',")
rep("'hero.eyebrow': '用 AI 全面提升日常工作生產力',", "'hero.eyebrow': '跟 AI 並肩工作 · Claude Code 與 Codex',")
rep("'hero.h1': '<span class=\"nowrap\">Terminal 才是</span><span class=\"grad\">最強辦公軟體！</span>',",
    "'hero.h1': '<span class=\"nowrap\">Terminal，</span><span class=\"grad\">升級成辦公軟體了。</span>',")
rep("'hero.sub': '看著 AI 寫，隨時動手改。像搭檔一樣，一起把工作做完。',",
    "'hero.sub': 'AI 在左邊寫，你在右邊改——同一份檔案、同一個時間。你看的是文件，不是指令。',")
rep("'s1.h2': 'AI 寫完了。檔案在哪？',", "'s1.h2': '它寫，你改。同一份檔案。',")
rep("'s1.lede': '它一次生五份檔案。你不該還要開 Finder 一個一個找，更不該為了改四個字重下一次 prompt。',",
    "'s1.lede': '我們叫它並肩工作：AI 一次生五份檔案，生出來就在左邊；你看著它寫，不順眼就直接改——不必等它跑完，也不必為了改四個字重下一次 prompt。',")
rep("      's1.f2b': '想改就點進去打字，人和 AI 共用同一份檔案。',\n",
    "      's1.f2b': '想改就點進去打字，人和 AI 共用同一份檔案。',\n"
    "      's1.f3k': 'Excel、Word、PDF 也一樣', 's1.f3h': '40 多種格式，在旁邊直接看，該改就改',\n"
    "      's1.f3a': '試算表、Word、PDF、CSV、Notebook、資料庫……<b>都在同一個視窗裡渲染出來</b>，不用切去別的 App。',\n"
    "      's1.f3b': '表格類（CSV、Excel、SQLite）直接改儲存格、存回原檔；文件類一鍵交給預設 App。',\n")
rep("'s2.lede': '誰在忙、誰舉手、誰做完了，一眼看完。順便告訴你，電腦還撐得住幾個。',",
    "'s2.lede': '誰在忙、誰舉手、誰做完了，一眼看完。順便告訴你：整台電腦用了多少、AgentPixel 占多少、還撐得住幾個。',")
rep("'dl.h2': '讓 Terminal 成為你的辦公室',", "'dl.h2': '把你的 Terminal 升級成辦公軟體',")
rep("      'd.d.note': '<b>LLM 生成</b> · 你可以直接<b>選取、刪改</b>、續寫',\n",
    "      'd.d.note': '<b>LLM 生成</b> · 你可以直接<b>選取、刪改</b>、續寫',\n"
    "\n"
    "      'd.s.cmd': '<span class=\"d-clr-p\">$</span> claude \"把 Q2 開支整理成 Excel\"',\n"
    "      'd.s.a': '<span class=\"d-clr-a\">◇</span> <span class=\"d-clr-o\">建立 Q2-expenses.xlsx</span>',\n"
    "      'd.s.b': '<span class=\"d-clr-t\">✓</span> <span class=\"d-clr-o\">2 個工作表 · 48 列</span>',\n"
    "      'd.s.sh1': '明細', 'd.s.sh2': '摘要',\n"
    "      'd.s.h1': '項目', 'd.s.h2': '上季', 'd.s.h3': '本季', 'd.s.h4': '變化',\n"
    "      'd.s.r1': '雲端運算', 'd.s.r2': '供應商', 'd.s.r3': '訂閱服務',\n"
    "      'd.s.tag': '✎ 手動修改 · 已存回 .xlsx',\n"
    "      'd.s.note': '<b>Agent 產出</b> · 你直接改儲存格，<b>樣式與其他工作表原封不動</b>',\n")
rep("'d.o.cpu': '<span>CPU</span><span class=\"po-mval\">42%</span>',\n      'd.o.mem': '<span>記憶體</span><span class=\"po-mval\">6.1 / 16 GB</span>',",
    "'d.o.cpu': '<span>整台電腦</span><span class=\"po-mval\">6.1 / 16 GB</span>',\n      'd.o.mem': '<span>AgentPixel</span><span class=\"po-mval\">1.4 GB</span>',")
rep("      'w.3': 'Remote — 手機接手'\n", "      'w.3': 'Remote — 手機接手',\n      'w.4': 'Q2-expenses.xlsx — 直接看，直接改'\n")

# en
rep("'meta.title': 'AgentPixel — The best office software is a terminal',", "'meta.title': 'AgentPixel — The terminal just became office software',")
rep("'meta.desc': 'You give the order, the agent writes the doc, and you watch every word land. Don\\u2019t like something? Fix it yourself. Works with Claude Code and Codex.',",
    "'meta.desc': 'The AI writes on the left, you edit on the right \\u2014 same file, same moment. Excel, Word, PDF and CSV open right beside the agent, ready to edit. Works with Claude Code and Codex.',")
rep("'meta.ogtitle': 'The best office software is a terminal.',", "'meta.ogtitle': 'The terminal just became office software.',")
rep("'meta.ogdesc': 'Watch an agent write your report. Don\\u2019t like it? Fix it yourself. Claude Code and Codex.',",
    "'meta.ogdesc': 'The AI writes on the left, you edit on the right. You look at the document, not the commands. Claude Code and Codex.',")
rep("'meta.ogimg': 'og-en.png?v=3',", "'meta.ogimg': 'og-en.png?v=4',")
rep("'nav.see': 'See it',", "'nav.see': 'Side by side',")
rep("'hero.eyebrow': 'AI-powered productivity for everyday work',", "'hero.eyebrow': 'You and your agents, on the same file \\u00b7 Claude Code & Codex',")
rep("'hero.h1': 'The best office software<br><span class=\"grad\">is a terminal.</span>',",
    "'hero.h1': 'The terminal just became<br><span class=\"grad\">office software.</span>',")
rep("'hero.sub': 'Watch it write, and jump in anytime. Like a teammate \\u2014 you get the work done together.',",
    "'hero.sub': 'The AI writes on the left, you edit on the right \\u2014 same file, same moment. You look at the document, not the commands.',")
rep("'s1.h2': 'The AI is done. Where are the files?',", "'s1.h2': 'It writes. You edit. Same file.',")
rep("'s1.lede': 'It just wrote five of them. You shouldn\\u2019t have to dig through Finder \\u2014 or re-run the whole prompt to change four words.',",
    "'s1.lede': 'We call it working side by side: the agent turns out five files and they appear on the left as they land. Watch it write, step in when something\\u2019s off \\u2014 no waiting for it to finish, no re-prompting to change four words.',")
rep("      's1.f2b': 'Click in and start typing. You and the AI share one file.',\n",
    "      's1.f2b': 'Click in and start typing. You and the AI share one file.',\n"
    "      's1.f3k': 'Excel, Word, PDF too', 's1.f3h': '40+ formats open beside the agent, ready to edit',\n"
    "      's1.f3a': 'Spreadsheets, Word, PDF, CSV, notebooks, databases \\u2014 <b>all rendered in the same window</b>, no switching apps.',\n"
    "      's1.f3b': 'Grid files (CSV, Excel, SQLite) edit in place and save back to the original; documents hand off to your default app in one click.',\n")
rep("'s2.lede': 'Who\\u2019s working, who\\u2019s stuck, who\\u2019s done \\u2014 at a glance. And how many more your Mac can take.',",
    "'s2.lede': 'Who\\u2019s working, who\\u2019s stuck, who\\u2019s done \\u2014 at a glance. Plus what the whole machine is using, what AgentPixel is using, and how many more it can take.',")
rep("'dl.h2': 'Make the terminal your office',", "'dl.h2': 'Upgrade your terminal to office software',")
rep("      'd.d.note': '<b>Written by the LLM</b> \\u00b7 you can <b>select, delete, rewrite</b>',\n",
    "      'd.d.note': '<b>Written by the LLM</b> \\u00b7 you can <b>select, delete, rewrite</b>',\n"
    "\n"
    "      'd.s.cmd': '<span class=\"d-clr-p\">$</span> claude \"turn Q2 expenses into an Excel file\"',\n"
    "      'd.s.a': '<span class=\"d-clr-a\">\\u25c7</span> <span class=\"d-clr-o\">created Q2-expenses.xlsx</span>',\n"
    "      'd.s.b': '<span class=\"d-clr-t\">\\u2713</span> <span class=\"d-clr-o\">2 sheets \\u00b7 48 rows</span>',\n"
    "      'd.s.sh1': 'Detail', 'd.s.sh2': 'Summary',\n"
    "      'd.s.h1': 'Item', 'd.s.h2': 'Last Q', 'd.s.h3': 'This Q', 'd.s.h4': 'Change',\n"
    "      'd.s.r1': 'Cloud compute', 'd.s.r2': 'Vendors', 'd.s.r3': 'Subscriptions',\n"
    "      'd.s.tag': '\\u270e Edited by you \\u00b7 saved back to .xlsx',\n"
    "      'd.s.note': '<b>Made by the agent</b> \\u00b7 edit the cell directly, <b>styles and other sheets stay untouched</b>',\n")
rep("'d.o.cpu': '<span>CPU</span><span class=\"po-mval\">42%</span>',\n      'd.o.mem': '<span>Memory</span><span class=\"po-mval\">6.1 / 16 GB</span>',",
    "'d.o.cpu': '<span>Whole machine</span><span class=\"po-mval\">6.1 / 16 GB</span>',\n      'd.o.mem': '<span>AgentPixel</span><span class=\"po-mval\">1.4 GB</span>',")
rep("      'w.3': 'Remote \\u2014 hand off to your phone'\n", "      'w.3': 'Remote \\u2014 hand off to your phone',\n      'w.4': 'Q2-expenses.xlsx \\u2014 view it, edit it'\n")

# ja
rep("'meta.title': 'AgentPixel — 最強のオフィスソフトは、ターミナルだった',", "'meta.title': 'AgentPixel — ターミナルが、オフィスソフトになりました',")
rep("'meta.desc': '指示を出せば書き始める。一文字ずつ書かれていくのを横で見ながら、気に入らないところは自分で直す。Claude Code と Codex に対応。',",
    "'meta.desc': 'AI が左で書き、あなたが右で直す——同じファイル、同じ瞬間。Excel・Word・PDF・CSV もすぐ横で開いて、そのまま編集。Claude Code と Codex に対応。',")
rep("'meta.ogtitle': '最強のオフィスソフトは、ターミナルだった。',", "'meta.ogtitle': 'ターミナルが、オフィスソフトになりました。',")
rep("'meta.ogdesc': 'エージェントがレポートを書くのを見ながら、気に入らなければ自分で直す。Claude Code と Codex に対応。',",
    "'meta.ogdesc': 'AI が左で書き、あなたが右で直す。見ているのは書類で、コマンドじゃない。Claude Code と Codex に対応。',")
rep("'meta.ogimg': 'og-ja.png?v=3',", "'meta.ogimg': 'og-ja.png?v=4',")
rep("'nav.see': '見える',", "'nav.see': '並んで働く',")
rep("'hero.eyebrow': 'AI で日常業務の生産性を底上げ',", "'hero.eyebrow': 'AI と並んで働く · Claude Code と Codex',")
rep("'hero.h1': '最強のオフィスソフトは、<br><span class=\"grad\">ターミナルだった。</span>',",
    "'hero.h1': 'ターミナルが、<br><span class=\"grad\">オフィスソフトになりました。</span>',")
rep("'hero.sub': '書いているところを見ながら、いつでも手を入れられる。相棒として、一緒に仕事を仕上げる。',",
    "'hero.sub': 'AI が左で書き、あなたが右で直す——同じファイル、同じ瞬間。見ているのは書類で、コマンドじゃない。',")
rep("'s1.h2': 'AI は書き終えた。ファイルはどこ？',", "'s1.h2': 'AI が書く。あなたが直す。同じファイル。',")
rep("'s1.lede': '一度に5つのファイルができる。Finder で一つずつ探す必要も、四文字直すためにプロンプトを打ち直す必要もない。',",
    "'s1.lede': 'これを「並んで働く」と呼んでいます。AI が一気に 5 つのファイルを作れば、左側にすぐ現れる。書いているのを見ながら、気に入らなければその場で直す——終わるのを待たなくていいし、4 文字直すためにプロンプトを打ち直す必要もない。',")
rep("      's1.f2b': 'クリックして打ち込むだけ。人と AI が同じファイルを共有する。',\n",
    "      's1.f2b': 'クリックして打ち込むだけ。人と AI が同じファイルを共有する。',\n"
    "      's1.f3k': 'Excel も Word も PDF も', 's1.f3h': '40 種類以上のファイルを横で開いて、そのまま編集',\n"
    "      's1.f3a': '表計算、Word、PDF、CSV、ノートブック、データベース……<b>すべて同じウィンドウで表示</b>。別のアプリに切り替えなくていい。',\n"
    "      's1.f3b': '表形式（CSV・Excel・SQLite）はセルを直接編集して元のファイルに保存。文書類はワンクリックで既定のアプリへ。',\n")
rep("'s2.lede': '誰が動いていて、誰が手を挙げ、誰が終わったか。ついでに、あと何個動かせるかも。',",
    "'s2.lede': '誰が動いていて、誰が手を挙げ、誰が終わったか。ついでに、マシン全体の使用量、AgentPixel の使用量、あと何個動かせるかも。',")
rep("'dl.h2': 'ターミナルを、あなたのオフィスに',", "'dl.h2': 'あなたのターミナルを、オフィスソフトに',")
rep("      'd.d.note': '<b>LLM が生成</b> · <b>選択・削除・書き直し</b>ができる',\n",
    "      'd.d.note': '<b>LLM が生成</b> · <b>選択・削除・書き直し</b>ができる',\n"
    "\n"
    "      'd.s.cmd': '<span class=\"d-clr-p\">$</span> claude \"Q2 の経費を Excel にまとめて\"',\n"
    "      'd.s.a': '<span class=\"d-clr-a\">◇</span> <span class=\"d-clr-o\">Q2-expenses.xlsx を作成</span>',\n"
    "      'd.s.b': '<span class=\"d-clr-t\">✓</span> <span class=\"d-clr-o\">2 シート · 48 行</span>',\n"
    "      'd.s.sh1': '明細', 'd.s.sh2': 'サマリー',\n"
    "      'd.s.h1': '項目', 'd.s.h2': '前四半期', 'd.s.h3': '今四半期', 'd.s.h4': '増減',\n"
    "      'd.s.r1': 'クラウド', 'd.s.r2': 'ベンダー', 'd.s.r3': 'サブスク',\n"
    "      'd.s.tag': '✎ 手動で修正 · .xlsx に保存済み',\n"
    "      'd.s.note': '<b>エージェントが作成</b> · セルを直接編集、<b>書式も他のシートもそのまま</b>',\n")
rep("'d.o.cpu': '<span>CPU</span><span class=\"po-mval\">42%</span>',\n      'd.o.mem': '<span>メモリ</span><span class=\"po-mval\">6.1 / 16 GB</span>',",
    "'d.o.cpu': '<span>マシン全体</span><span class=\"po-mval\">6.1 / 16 GB</span>',\n      'd.o.mem': '<span>AgentPixel</span><span class=\"po-mval\">1.4 GB</span>',")
rep("      'w.3': 'リモート — スマホで引き継ぐ'\n", "      'w.3': 'リモート — スマホで引き継ぐ',\n      'w.4': 'Q2-expenses.xlsx — 見て、そのまま直す'\n")

if s == orig:
    sys.exit("nothing changed?")
P.write_text(s, encoding="utf-8")
print("index.html rewritten OK")
