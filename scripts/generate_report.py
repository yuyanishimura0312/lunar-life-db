#!/usr/bin/env python3
"""Generate a landscape A4 HTML report for the Lunar Life Research Database."""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'report.html')

CATEGORIES = {
    'food': {'ja': '食', 'color': '#F0A671', 'desc': '月面での食料生産・調理・栄養管理'},
    'water': {'ja': '水', 'color': '#CEA26F', 'desc': '水資源の確保・循環・浄化'},
    'hygiene': {'ja': '衛生', 'color': '#F8CDAC', 'desc': '個人衛生・微生物管理・廃棄物処理'},
    'medical': {'ja': '医療', 'color': '#DC8766', 'desc': '遠隔医療・放射線防護・メンタルヘルス'},
    'exercise': {'ja': '運動', 'color': '#B07256', 'desc': '筋力維持・骨密度保全・リハビリ'},
    'clothing': {'ja': '衣服', 'color': '#F2C792', 'desc': '宇宙服・船内着・スマートテキスタイル'},
    'communication': {'ja': '通信', 'color': '#F0BE83', 'desc': '通信インフラ・心理的接続・チーム支援'},
    'entertainment': {'ja': '娯楽', 'color': '#EFC4A4', 'desc': 'レクリエーション・心理的ウェルビーイング'},
    'sleep_habitat': {'ja': '睡眠・住環境', 'color': '#966D5E', 'desc': '居住モジュール・概日リズム・プライバシー'},
    'work_environment': {'ja': '作業環境', 'color': '#7A4033', 'desc': 'AR支援・テレロボティクス・人間工学'},
}

MODULES = {
    'private_room': {'ja': 'プライベートルーム', 'desc': '個人の居住・睡眠空間'},
    'kitchen_dining': {'ja': 'キッチン&ダイニング', 'desc': '調理・食事・社交空間'},
    'laboratory': {'ja': 'ラボラトリー', 'desc': '科学研究・分析施設'},
    'workspace': {'ja': 'ワークスペース', 'desc': '共同作業・オペレーション'},
    'medical_bay': {'ja': 'メディカルベイ', 'desc': '医療・健康管理施設'},
    'training_room': {'ja': 'トレーニングルーム', 'desc': '運動・フィットネス施設'},
    'courtyard': {'ja': 'コートヤード', 'desc': '植物のある共用空間'},
    'plantation': {'ja': 'プランテーション', 'desc': '食料生産・農業施設'},
}

TRL_STAGE = {1: '基本原理', 2: 'コンセプト', 3: '概念実証', 4: '実験室検証',
             5: '関連環境検証', 6: '環境実証', 7: '運用実証', 8: '適格性確認', 9: '運用済み'}

ENTRY_TYPE_JA = {
    'technology': '技術', 'research': '研究', 'project': 'プロジェクト',
    'concept': 'コンセプト', 'regulation': '規制', 'challenge': '課題', 'case_study': '事例',
}


def trl_color(trl):
    if trl is None: return '#999'
    if trl <= 3: return '#DC8766'
    if trl <= 6: return '#F0A671'
    return '#7A4033'


def generate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    entries = [dict(r) for r in conn.execute("SELECT * FROM entries ORDER BY category, id").fetchall()]
    challenges = [dict(r) for r in conn.execute("SELECT * FROM challenges ORDER BY category").fetchall()]

    # Parse JSON fields
    for e in entries:
        for f in ['related_modules', 'tags', 'authors']:
            if e.get(f):
                try: e[f] = json.loads(e[f])
                except: e[f] = []
            else: e[f] = []

    # Group by category
    by_cat = {}
    for e in entries:
        by_cat.setdefault(e['category'], []).append(e)

    ch_by_cat = {}
    for c in challenges:
        ch_by_cat.setdefault(c['category'], []).append(c)

    # Build module-entry mapping
    module_entries = {}
    for e in entries:
        for m in e.get('related_modules', []):
            module_entries.setdefault(m, []).append(e)

    # Stats
    orgs = set(e.get('source_org', '') for e in entries if e.get('source_org'))
    trl_dist = {}
    for e in entries:
        if e.get('trl'):
            trl_dist[e['trl']] = trl_dist.get(e['trl'], 0) + 1

    today = datetime.now().strftime('%Y年%m月%d日')

    # --- Generate HTML ---
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>月面生活リサーチレポート — Space Life on the Moon</title>
<style>
@page {{
  size: A4 landscape;
  margin: 12mm 15mm;
}}
@media print {{
  .page-break {{ page-break-before: always; }}
  body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Segoe UI", sans-serif;
  color: #1a1a1a;
  background: #fff;
  font-size: 9pt;
  line-height: 1.5;
}}
.page {{
  width: 277mm;
  min-height: 190mm;
  padding: 0;
  position: relative;
}}

/* Cover */
.cover {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 190mm;
  background: linear-gradient(135deg, #faf8f5 0%, #F8CDAC30 30%, #faf8f5 60%, #F0A67120 100%);
  text-align: center;
}}
.cover h1 {{
  font-size: 28pt;
  color: #783c28;
  letter-spacing: 0.15em;
  margin-bottom: 8mm;
  font-weight: 700;
}}
.cover .subtitle {{
  font-size: 14pt;
  color: #966D5E;
  margin-bottom: 4mm;
}}
.cover .desc {{
  font-size: 10pt;
  color: #6b5c52;
  max-width: 180mm;
  margin-bottom: 12mm;
}}
.cover .meta {{
  font-size: 9pt;
  color: #966D5E;
}}
.cover .stats {{
  display: flex;
  gap: 20mm;
  margin: 10mm 0;
}}
.cover .stat-box {{
  text-align: center;
}}
.cover .stat-num {{
  font-size: 24pt;
  font-weight: 700;
  color: #783c28;
}}
.cover .stat-label {{
  font-size: 8pt;
  color: #6b5c52;
}}

/* Section headers */
.section-header {{
  padding: 4mm 0 3mm;
  border-bottom: 2px solid;
  margin-bottom: 4mm;
  display: flex;
  align-items: baseline;
  gap: 3mm;
}}
.section-header h2 {{
  font-size: 16pt;
  font-weight: 700;
}}
.section-header .section-desc {{
  font-size: 9pt;
  color: #6b5c52;
}}

/* Entry cards in table */
.entry-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
  margin-bottom: 4mm;
}}
.entry-table th {{
  text-align: left;
  padding: 2mm 2mm;
  font-weight: 600;
  font-size: 7.5pt;
  color: #6b5c52;
  border-bottom: 1px solid #e8e0d8;
  white-space: nowrap;
}}
.entry-table td {{
  padding: 2mm 2mm;
  border-bottom: 1px solid #f0ebe5;
  vertical-align: top;
}}
.entry-table tr:last-child td {{
  border-bottom: none;
}}
.badge {{
  display: inline-block;
  padding: 0.5mm 2mm;
  border-radius: 2mm;
  font-size: 7pt;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}}
.badge-outline {{
  display: inline-block;
  padding: 0.5mm 2mm;
  border-radius: 2mm;
  font-size: 7pt;
  border: 0.5px solid;
  background: transparent;
  white-space: nowrap;
}}
.trl-bar {{
  display: inline-flex;
  gap: 0.5mm;
  align-items: center;
}}
.trl-dot {{
  width: 3mm;
  height: 2mm;
  border-radius: 0.5mm;
}}
.module-tag {{
  display: inline-block;
  padding: 0.3mm 1.5mm;
  border-radius: 1mm;
  font-size: 6.5pt;
  background: #f5f0eb;
  color: #6b5c52;
  margin: 0.3mm 0.3mm;
  white-space: nowrap;
}}
.challenge-box {{
  background: #fdf9f5;
  border-left: 3px solid;
  padding: 2mm 3mm;
  margin-bottom: 2mm;
  font-size: 8pt;
}}
.challenge-box .ch-title {{
  font-weight: 600;
  font-size: 8.5pt;
}}
.challenge-box .ch-desc {{
  color: #4a4a4a;
  margin-top: 1mm;
}}

/* Module section */
.module-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3mm;
}}
.module-card {{
  border: 1px solid #e8e0d8;
  border-radius: 2mm;
  padding: 3mm;
  background: #fdfbf9;
}}
.module-card h4 {{
  font-size: 10pt;
  font-weight: 600;
  margin-bottom: 1mm;
  color: #783c28;
}}
.module-card .mod-desc {{
  font-size: 7.5pt;
  color: #6b5c52;
  margin-bottom: 2mm;
}}
.module-entries {{
  font-size: 7.5pt;
  line-height: 1.4;
}}
.module-entries li {{
  margin-bottom: 0.5mm;
  list-style: none;
  padding-left: 3mm;
  position: relative;
}}
.module-entries li::before {{
  content: "\\25CF";
  position: absolute;
  left: 0;
  font-size: 5pt;
  line-height: 1.8;
}}

/* TOC */
.toc {{
  columns: 2;
  column-gap: 8mm;
  font-size: 9pt;
}}
.toc-item {{
  display: flex;
  justify-content: space-between;
  padding: 1mm 0;
  border-bottom: 1px dotted #e8e0d8;
}}
.toc-item span:first-child {{
  font-weight: 500;
}}

/* Footer */
.page-footer {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  font-size: 7pt;
  color: #999;
  padding-top: 2mm;
  border-top: 0.5px solid #e8e0d8;
}}

/* Overview stats page */
.stat-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4mm;
}}
.stat-card {{
  border: 1px solid #e8e0d8;
  border-radius: 2mm;
  padding: 3mm;
}}
.stat-card h4 {{
  font-size: 8pt;
  color: #6b5c52;
  margin-bottom: 2mm;
}}
.bar-row {{
  display: flex;
  align-items: center;
  gap: 2mm;
  margin-bottom: 1mm;
}}
.bar-label {{
  font-size: 7.5pt;
  width: 25mm;
  text-align: right;
  flex-shrink: 0;
}}
.bar-track {{
  flex: 1;
  height: 3mm;
  background: #f0ebe5;
  border-radius: 1mm;
  overflow: hidden;
}}
.bar-fill {{
  height: 100%;
  border-radius: 1mm;
}}
.bar-value {{
  font-size: 7pt;
  width: 8mm;
  text-align: right;
  flex-shrink: 0;
  font-weight: 600;
}}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="page cover">
  <h1>月面生活リサーチレポート</h1>
  <p class="subtitle">Space Life on the Moon — Research Database Report</p>
  <p class="desc">
    月面基地での生活課題と、それに応える世界中の技術・研究・プロジェクトを集めたデータベースの全件レポート。
    JAXA「Space Life on the Moon」をベースに、NASA・ESA・JAXA・CNSA・大学・民間企業の取り組みを10カテゴリに分類。
  </p>
  <div class="stats">
    <div class="stat-box">
      <div class="stat-num">{len(entries)}</div>
      <div class="stat-label">エントリ</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">{len(orgs)}</div>
      <div class="stat-label">組織</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">10</div>
      <div class="stat-label">カテゴリ</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">{len(challenges)}</div>
      <div class="stat-label">課題</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">8</div>
      <div class="stat-label">モジュール</div>
    </div>
  </div>
  <p class="meta">NPO法人ミラツク / MIRA TUKU</p>
  <p class="meta">{today} 作成</p>
</div>

<!-- TOC + OVERVIEW PAGE -->
<div class="page page-break">
  <div class="section-header" style="border-color: #783c28;">
    <h2 style="color: #783c28;">目次・概要</h2>
  </div>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 4mm;">
    <div>
      <h3 style="font-size: 10pt; color: #783c28; margin-bottom: 3mm;">カテゴリ別事例集</h3>
      <div class="toc">
"""

    page_num = 3
    for cat_key, cat_info in CATEGORIES.items():
        count = len(by_cat.get(cat_key, []))
        html += f"""        <div class="toc-item">
          <span><span style="color:{cat_info['color']};">&#9679;</span> {cat_info['ja']}（{cat_info['desc'][:15]}...）</span>
          <span>{count}件</span>
        </div>\n"""

    html += f"""      </div>
      <h3 style="font-size: 10pt; color: #783c28; margin: 5mm 0 3mm;">月面基地モジュール別事例</h3>
      <div class="toc">
"""
    for mod_key, mod_info in MODULES.items():
        count = len(module_entries.get(mod_key, []))
        html += f"""        <div class="toc-item">
          <span>{mod_info['ja']}</span>
          <span>{count}件</span>
        </div>\n"""

    html += """      </div>
    </div>
    <div>
      <h3 style="font-size: 10pt; color: #783c28; margin-bottom: 3mm;">統計サマリー</h3>
"""
    # TRL distribution
    html += '      <div class="stat-card" style="margin-bottom: 3mm;">\n'
    html += '        <h4>技術成熟度（TRL）分布</h4>\n'
    max_trl = max(trl_dist.values()) if trl_dist else 1
    for t in range(1, 10):
        v = trl_dist.get(t, 0)
        html += f"""        <div class="bar-row">
          <span class="bar-label">TRL {t}</span>
          <div class="bar-track"><div class="bar-fill" style="width:{v/max_trl*100:.0f}%;background:{trl_color(t)};"></div></div>
          <span class="bar-value">{v}</span>
        </div>\n"""
    html += '      </div>\n'

    # Org distribution
    org_count = {}
    for e in entries:
        org = e.get('source_org', 'Unknown') or 'Unknown'
        # Normalize
        if 'NASA' in org: org = 'NASA'
        elif 'ESA' in org or 'European' in org: org = 'ESA'
        elif 'JAXA' in org or 'Japan Aerospace' in org: org = 'JAXA'
        elif 'CNSA' in org or 'Chinese' in org: org = 'CNSA'
        org_count[org] = org_count.get(org, 0) + 1
    top_orgs = sorted(org_count.items(), key=lambda x: -x[1])[:10]
    max_org = top_orgs[0][1] if top_orgs else 1

    html += '      <div class="stat-card">\n'
    html += '        <h4>組織別エントリ数（上位10）</h4>\n'
    for org, cnt in top_orgs:
        html += f"""        <div class="bar-row">
          <span class="bar-label">{org[:15]}</span>
          <div class="bar-track"><div class="bar-fill" style="width:{cnt/max_org*100:.0f}%;background:#783c28;"></div></div>
          <span class="bar-value">{cnt}</span>
        </div>\n"""
    html += '      </div>\n'

    html += """    </div>
  </div>
  <div class="page-footer">
    <span>月面生活リサーチレポート — NPO法人ミラツク</span>
    <span>2</span>
  </div>
</div>
"""

    # --- CATEGORY PAGES ---
    page_num = 3
    for cat_key, cat_info in CATEGORIES.items():
        cat_entries = by_cat.get(cat_key, [])
        cat_challenges = ch_by_cat.get(cat_key, [])

        html += f"""
<!-- {cat_info['ja']} -->
<div class="page page-break">
  <div class="section-header" style="border-color: {cat_info['color']};">
    <h2 style="color: {cat_info['color']};">{cat_info['ja']}</h2>
    <span class="section-desc">{cat_info['desc']} — {len(cat_entries)}件のエントリ</span>
  </div>
"""
        # Challenges
        if cat_challenges:
            html += '  <div style="margin-bottom: 4mm;">\n'
            html += '    <h3 style="font-size: 9pt; color: #6b5c52; margin-bottom: 2mm;">主要課題</h3>\n'
            for ch in cat_challenges:
                sev_colors = {'critical': '#DC8766', 'high': '#B07256', 'medium': '#F0A671', 'low': '#CEA26F'}
                sev_labels = {'critical': '深刻', 'high': '高', 'medium': '中', 'low': '低'}
                sc = sev_colors.get(ch.get('severity', 'medium'), '#999')
                sl = sev_labels.get(ch.get('severity', 'medium'), '?')
                html += f"""    <div class="challenge-box" style="border-color: {sc};">
      <span class="badge" style="background:{sc};font-size:6.5pt;">{sl}</span>
      <span class="ch-title">{ch['name_ja']}</span>
      <div class="ch-desc">{ch.get('description', '')[:120]}</div>
    </div>\n"""
            html += '  </div>\n'

        # Entry table
        html += """  <table class="entry-table">
    <thead>
      <tr>
        <th style="width:30%;">タイトル</th>
        <th style="width:30%;">概要</th>
        <th style="width:8%;">組織</th>
        <th style="width:6%;">TRL</th>
        <th style="width:6%;">タイプ</th>
        <th style="width:20%;">関連モジュール</th>
      </tr>
    </thead>
    <tbody>
"""
        for e in cat_entries:
            trl = e.get('trl')
            trl_html = ''
            if trl:
                trl_html = f'<span class="badge" style="background:{trl_color(trl)};">TRL {trl}</span>'

            modules_html = ''
            for m in e.get('related_modules', []):
                m_name = MODULES.get(m, {}).get('ja', m)
                modules_html += f'<span class="module-tag">{m_name}</span>'

            etype = ENTRY_TYPE_JA.get(e.get('entry_type', ''), e.get('entry_type', ''))
            summary = (e.get('summary', '') or '')[:100]
            if len(e.get('summary', '') or '') > 100:
                summary += '...'

            html += f"""      <tr>
        <td><strong>{e['title']}</strong></td>
        <td>{summary}</td>
        <td>{e.get('source_org', '')[:12] or '-'}</td>
        <td>{trl_html}</td>
        <td><span class="badge-outline" style="border-color:{cat_info['color']};color:{cat_info['color']};">{etype}</span></td>
        <td>{modules_html}</td>
      </tr>\n"""

        html += f"""    </tbody>
  </table>
  <div class="page-footer">
    <span>月面生活リサーチレポート — NPO法人ミラツク</span>
    <span>{page_num}</span>
  </div>
</div>
"""
        page_num += 1

    # --- MODULE PAGES (2 pages, 4 modules each) ---
    mod_keys = list(MODULES.keys())
    for page_i in range(2):
        html += f"""
<div class="page page-break">
  <div class="section-header" style="border-color: #783c28;">
    <h2 style="color: #783c28;">月面基地モジュール別 事例マッピング{'（続き）' if page_i > 0 else ''}</h2>
    <span class="section-desc">JAXA月面基地イメージパースの各モジュールに関連する技術・研究</span>
  </div>

  <div class="module-grid">
"""
        for mod_key in mod_keys[page_i*4:(page_i+1)*4]:
            mod_info = MODULES[mod_key]
            mod_ents = module_entries.get(mod_key, [])
            html += f"""    <div class="module-card">
      <h4>{mod_info['ja']}</h4>
      <div class="mod-desc">{mod_info['desc']} — {len(mod_ents)}件の関連エントリ</div>
      <ul class="module-entries">
"""
            # Show top entries per module (max 8)
            seen_cats = set()
            shown = 0
            for me in mod_ents:
                if shown >= 8:
                    break
                cat = me['category']
                cat_ja = CATEGORIES.get(cat, {}).get('ja', cat)
                cat_color = CATEGORIES.get(cat, {}).get('color', '#999')
                title = me['title'][:35]
                if len(me['title']) > 35:
                    title += '...'
                trl = me.get('trl')
                trl_txt = f' (TRL{trl})' if trl else ''
                html += f'        <li><span class="badge" style="background:{cat_color};font-size:6pt;padding:0.3mm 1.5mm;">{cat_ja}</span> {title}{trl_txt}</li>\n'
                shown += 1

            if len(mod_ents) > 8:
                html += f'        <li style="color:#999;">...他 {len(mod_ents)-8}件</li>\n'

            html += """      </ul>
    </div>
"""
        html += f"""  </div>
  <div class="page-footer">
    <span>月面生活リサーチレポート — NPO法人ミラツク</span>
    <span>{page_num}</span>
  </div>
</div>
"""
        page_num += 1

    # Close
    html += """
</body>
</html>"""

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Report generated: {os.path.abspath(OUTPUT_PATH)}")
    print(f"  {len(entries)} entries across {len(CATEGORIES)} categories")
    print(f"  {page_num - 1} pages total")

    conn.close()


if __name__ == '__main__':
    generate()
