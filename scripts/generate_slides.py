#!/usr/bin/env python3
"""Generate a landscape A4 slide-style HTML report for Lunar Life Research DB."""

import sqlite3
import json
import os
import base64
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'slides.html')

CATEGORIES = {
    'food': {'ja': '食', 'color': '#F0A671', 'desc': '月面での食料生産・調理・栄養管理'},
    'water': {'ja': '水', 'color': '#CEA26F', 'desc': '水資源の確保・循環・浄化'},
    'hygiene': {'ja': '衛生', 'color': '#F8CDAC', 'desc': '個人衛生・微生物管理・廃棄物処理'},
    'medical': {'ja': '医療', 'color': '#DC8766', 'desc': '遠隔医療・放射線防護・メンタルヘルス'},
    'exercise': {'ja': '運動', 'color': '#B07256', 'desc': '筋力維持・骨密度保全・リハビリテーション'},
    'clothing': {'ja': '衣服', 'color': '#F2C792', 'desc': '宇宙服・船内着・スマートテキスタイル'},
    'communication': {'ja': '通信', 'color': '#F0BE83', 'desc': '通信インフラ・心理的接続・チーム支援'},
    'entertainment': {'ja': '娯楽', 'color': '#EFC4A4', 'desc': 'レクリエーション・心理的ウェルビーイング'},
    'sleep_habitat': {'ja': '睡眠・住環境', 'color': '#966D5E', 'desc': '居住モジュール・概日リズム・プライバシー'},
    'work_environment': {'ja': '作業環境', 'color': '#7A4033', 'desc': 'AR支援・テレロボティクス・人間工学'},
}

MODULES = {
    'private_room': {'ja': 'プライベートルーム', 'desc': '個人の居住・睡眠空間', 'image': 'private_room.png'},
    'kitchen_dining': {'ja': 'キッチン&ダイニング', 'desc': '調理・食事・社交空間', 'image': 'kitchen_dining.png'},
    'laboratory': {'ja': 'ラボラトリー', 'desc': '科学研究・分析施設', 'image': 'laboratory.png'},
    'workspace': {'ja': 'ワークスペース', 'desc': '共同作業・オペレーション', 'image': 'workspace.png'},
    'medical_bay': {'ja': 'メディカルベイ', 'desc': '医療・健康管理施設', 'image': 'medical_bay.png'},
    'training_room': {'ja': 'トレーニングルーム', 'desc': '運動・フィットネス施設', 'image': 'training_room.png'},
    'courtyard': {'ja': 'コートヤード', 'desc': '植物のある共用空間', 'image': 'courtyard.png'},
    'plantation': {'ja': 'プランテーション', 'desc': '食料生産・農業施設', 'image': 'plantation.png'},
}

IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')

ENTRY_TYPE_JA = {
    'technology': '技術', 'research': '研究', 'project': 'PJ',
    'concept': '概念', 'regulation': '規制', 'challenge': '課題', 'case_study': '事例',
}

SEVERITY_JA = {'critical': '深刻', 'high': '高', 'medium': '中', 'low': '低'}
SEVERITY_COLOR = {'critical': '#DC8766', 'high': '#B07256', 'medium': '#F0A671', 'low': '#CEA26F'}


def img_to_base64(filename):
    # Prefer cropped JPEG version
    jpg_name = filename.replace('.png', '.jpg')
    cropped_path = os.path.join(IMG_DIR, 'cropped', jpg_name)
    if os.path.exists(cropped_path):
        with open(cropped_path, 'rb') as f:
            return 'jpeg', base64.b64encode(f.read()).decode()
    path = os.path.join(IMG_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return 'png', base64.b64encode(f.read()).decode()
    return '', ''


def trl_color(trl):
    if trl is None: return '#ccc'
    if trl <= 3: return '#DC8766'
    if trl <= 6: return '#F0A671'
    return '#7A4033'

def trl_stage(trl):
    if trl is None: return ''
    if trl <= 3: return '基礎研究'
    if trl <= 6: return '技術実証'
    return '実用化'

def truncate(s, n):
    if not s: return ''
    return s[:n] + ('...' if len(s) > n else '')


def generate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    entries = [dict(r) for r in conn.execute("SELECT * FROM entries ORDER BY category, id").fetchall()]
    challenges = [dict(r) for r in conn.execute("SELECT * FROM challenges ORDER BY category").fetchall()]
    conn.close()

    for e in entries:
        for f in ['related_modules', 'tags', 'authors']:
            try: e[f] = json.loads(e[f]) if e.get(f) else []
            except: e[f] = []

    by_cat = {}
    for e in entries:
        by_cat.setdefault(e['category'], []).append(e)
    ch_by_cat = {}
    for c in challenges:
        ch_by_cat.setdefault(c['category'], []).append(c)
    module_entries = {}
    for e in entries:
        for m in e.get('related_modules', []):
            module_entries.setdefault(m, []).append(e)

    orgs = set(e.get('source_org', '') for e in entries if e.get('source_org'))
    trl_dist = {}
    for e in entries:
        if e.get('trl'): trl_dist[e['trl']] = trl_dist.get(e['trl'], 0) + 1

    today = datetime.now().strftime('%Y年%m月%d日')

    # ─── CSS ───
    css = """
@page { size: A4 landscape; margin: 0; }
@media print {
  .slide { page-break-after: always; }
  .slide:last-child { page-break-after: auto; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Segoe UI", sans-serif;
  color: #1a1a1a; background: #e8e0d8;
}
.slide {
  width: 297mm; height: 210mm;
  background: #fff;
  position: relative; overflow: hidden;
  margin: 0 auto;
}
@media screen {
  .slide { margin: 8mm auto; box-shadow: 0 2px 12px rgba(0,0,0,0.12); }
}
.slide-inner { padding: 14mm 18mm 18mm; height: 100%; display: flex; flex-direction: column; }

/* ── Accent bar at top ── */
.accent-bar { position: absolute; top: 0; left: 0; right: 0; height: 4mm; }

/* ── Footer ── */
.slide-footer {
  position: absolute; bottom: 6mm; left: 18mm; right: 18mm;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 7pt; color: #966D5E;
}
.slide-footer .org { font-weight: 600; }

/* ── Cover ── */
.cover-slide .slide-inner {
  justify-content: center; align-items: center; text-align: center;
}
.cover-title { font-size: 32pt; font-weight: 800; color: #783c28; letter-spacing: 0.12em; margin-bottom: 5mm; }
.cover-sub { font-size: 14pt; color: #966D5E; margin-bottom: 3mm; }
.cover-desc { font-size: 10pt; color: #6b5c52; max-width: 200mm; line-height: 1.7; margin-bottom: 10mm; }
.cover-stats { display: flex; gap: 14mm; }
.cover-stat { text-align: center; }
.cover-stat-num { font-size: 28pt; font-weight: 800; color: #783c28; }
.cover-stat-label { font-size: 8pt; color: #6b5c52; margin-top: 1mm; }
.cover-meta { font-size: 9pt; color: #966D5E; margin-top: 8mm; }

/* ── Section title slide ── */
.section-slide .slide-inner {
  justify-content: center; padding-left: 30mm;
}
.section-num { font-size: 60pt; font-weight: 800; opacity: 0.12; position: absolute; right: 25mm; top: 50%; transform: translateY(-50%); }
.section-cat { font-size: 11pt; font-weight: 600; margin-bottom: 2mm; }
.section-title { font-size: 30pt; font-weight: 800; margin-bottom: 5mm; }
.section-desc-text { font-size: 12pt; color: #6b5c52; max-width: 160mm; line-height: 1.6; }
.section-challenge-list { margin-top: 8mm; max-width: 200mm; }
.section-ch-item {
  display: flex; align-items: flex-start; gap: 3mm; margin-bottom: 3mm;
  font-size: 9pt; line-height: 1.5;
}
.section-ch-badge {
  display: inline-block; padding: 0.5mm 2.5mm; border-radius: 1.5mm;
  font-size: 7pt; font-weight: 700; color: #fff; white-space: nowrap; flex-shrink: 0; margin-top: 0.5mm;
}
.section-ch-text { color: #4a4a4a; }

/* ── Content slide (card grid) ── */
.content-header { display: flex; align-items: baseline; gap: 4mm; margin-bottom: 5mm; }
.content-header h2 { font-size: 16pt; font-weight: 700; }
.content-header .content-sub { font-size: 9pt; color: #6b5c52; }
.card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3mm; flex: 1; }
.card-grid-2col { grid-template-columns: repeat(2, 1fr); }
.card {
  border: 1px solid #e8e0d8; border-radius: 2.5mm; padding: 3mm;
  display: flex; flex-direction: column; background: #fdfbf9; overflow: hidden;
}
.card-top { display: flex; align-items: center; gap: 1.5mm; margin-bottom: 1.5mm; flex-wrap: wrap; }
.card-title { font-size: 8.5pt; font-weight: 700; line-height: 1.35; margin-bottom: 1.5mm; flex: 1; }
.card-summary { font-size: 7.5pt; color: #4a4a4a; line-height: 1.4; flex: 1; }
.card-bottom { margin-top: auto; padding-top: 1.5mm; display: flex; flex-wrap: wrap; gap: 1mm; }
.badge {
  display: inline-block; padding: 0.4mm 2mm; border-radius: 1.5mm;
  font-size: 6.5pt; font-weight: 700; color: #fff; white-space: nowrap;
}
.badge-sm { font-size: 6pt; padding: 0.3mm 1.5mm; }
.badge-outline {
  display: inline-block; padding: 0.4mm 2mm; border-radius: 1.5mm;
  font-size: 6.5pt; font-weight: 600; border: 0.5px solid; background: transparent; white-space: nowrap;
}
.mod-tag {
  display: inline-block; padding: 0.3mm 1.5mm; border-radius: 1mm;
  font-size: 6pt; background: #f0ebe5; color: #6b5c52; white-space: nowrap;
}

/* ── Module slide ── */
.module-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; flex: 1; }
.module-card {
  border: 1px solid #e8e0d8; border-radius: 2.5mm; padding: 3.5mm;
  background: #fdfbf9; display: flex; flex-direction: column;
}
.module-card h3 { font-size: 11pt; font-weight: 700; color: #783c28; margin-bottom: 1mm; }
.module-desc { font-size: 7.5pt; color: #6b5c52; margin-bottom: 2mm; padding-bottom: 2mm; border-bottom: 1px solid #f0ebe5; }
.module-list { font-size: 7pt; line-height: 1.5; flex: 1; }
.module-list li { list-style: none; padding: 0.5mm 0; display: flex; align-items: baseline; gap: 1.5mm; }
.module-dot { width: 1.5mm; height: 1.5mm; border-radius: 50%; flex-shrink: 0; margin-top: 1mm; }

/* ── Module image slide ── */
.mod-slide-layout {
  display: grid; grid-template-columns: 48% 52%; gap: 4mm; flex: 1; overflow: hidden;
}
.mod-image-area {
  position: relative; border-radius: 3mm; overflow: hidden;
  background: #f5f0eb; display: flex; align-items: center; justify-content: center;
}
.mod-image-area img {
  width: 100%; height: 100%; object-fit: cover; border-radius: 3mm;
}
.mod-image-label {
  position: absolute; bottom: 2mm; left: 2mm; right: 2mm;
  background: rgba(26,26,26,0.65); color: #fff; padding: 1.5mm 3mm;
  border-radius: 1.5mm; font-size: 7pt; backdrop-filter: blur(4px);
}
.mod-right-area { display: flex; flex-direction: column; gap: 3mm; overflow: hidden; }
.mod-featured {
  border: 1.5px solid; border-radius: 3mm; padding: 4mm;
  background: #fdfbf9; flex: none;
}
.mod-featured-title { font-size: 11pt; font-weight: 700; line-height: 1.3; margin-bottom: 1.5mm; }
.mod-featured-summary { font-size: 8pt; color: #4a4a4a; line-height: 1.5; }
.mod-featured-meta { display: flex; gap: 2mm; align-items: center; margin-top: 2mm; flex-wrap: wrap; }
.mod-rest-area {
  flex: 1; border: 1px solid #e8e0d8; border-radius: 2.5mm;
  padding: 3mm; background: #fdfbf9; overflow: hidden;
}
.mod-rest-title { font-size: 8pt; font-weight: 600; color: #6b5c52; margin-bottom: 2mm; }
.mod-rest-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5mm; }
.mod-rest-item {
  display: flex; align-items: baseline; gap: 1.5mm;
  font-size: 7pt; line-height: 1.4; padding: 0.5mm 0;
}
.mod-rest-dot { width: 1.5mm; height: 1.5mm; border-radius: 50%; flex-shrink: 0; margin-top: 1.2mm; }

/* ── Stats slide ── */
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; flex: 1; }
.stats-block { border: 1px solid #e8e0d8; border-radius: 2.5mm; padding: 4mm; background: #fdfbf9; }
.stats-block h3 { font-size: 10pt; font-weight: 600; color: #783c28; margin-bottom: 3mm; }
.bar-row { display: flex; align-items: center; gap: 2mm; margin-bottom: 1.5mm; }
.bar-label { font-size: 8pt; width: 28mm; text-align: right; flex-shrink: 0; color: #4a4a4a; }
.bar-track { flex: 1; height: 4mm; background: #f0ebe5; border-radius: 1mm; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 1mm; }
.bar-value { font-size: 7.5pt; width: 8mm; text-align: right; flex-shrink: 0; font-weight: 700; }

/* ── KPI row ── */
.kpi-row { display: flex; gap: 5mm; margin-bottom: 5mm; }
.kpi-box {
  flex: 1; text-align: center; padding: 4mm;
  border: 1px solid #e8e0d8; border-radius: 2.5mm; background: #fdfbf9;
}
.kpi-num { font-size: 22pt; font-weight: 800; color: #783c28; }
.kpi-label { font-size: 8pt; color: #6b5c52; margin-top: 1mm; }
"""

    # ─── HTML ───
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>月面生活リサーチレポート — Slides</title>
<style>{css}</style>
</head>
<body>
"""

    page = 1

    def footer(p, color='#783c28'):
        return f'''<div class="slide-footer">
  <span class="org">NPO法人ミラツク / MIRA TUKU</span>
  <span>月面生活リサーチレポート</span>
  <span>{p}</span>
</div>'''

    # ━━━ SLIDE 1: COVER ━━━
    html += f"""
<div class="slide cover-slide">
  <div class="accent-bar" style="background:linear-gradient(90deg,#F0A671,#DC8766,#B07256,#966D5E,#7A4033);"></div>
  <div class="slide-inner">
    <div class="cover-title">月面生活リサーチレポート</div>
    <div class="cover-sub">Space Life on the Moon — Research Database</div>
    <div class="cover-desc">
      月面基地での生活課題と、それに応える世界中の技術・研究・プロジェクトを<br>
      10カテゴリに分類し、月面基地モジュールとの関連を整理したデータベースレポート
    </div>
    <div class="cover-stats">
      <div class="cover-stat"><div class="cover-stat-num">{len(entries)}</div><div class="cover-stat-label">エントリ</div></div>
      <div class="cover-stat"><div class="cover-stat-num">{len(orgs)}</div><div class="cover-stat-label">組織</div></div>
      <div class="cover-stat"><div class="cover-stat-num">10</div><div class="cover-stat-label">カテゴリ</div></div>
      <div class="cover-stat"><div class="cover-stat-num">{len(challenges)}</div><div class="cover-stat-label">課題</div></div>
      <div class="cover-stat"><div class="cover-stat-num">8</div><div class="cover-stat-label">モジュール</div></div>
    </div>
    <div class="cover-meta">{today} &nbsp;|&nbsp; NPO法人ミラツク &nbsp;|&nbsp; JAXA「Space Life on the Moon」準拠</div>
  </div>
</div>
"""
    page += 1

    # ━━━ SLIDE 2: OVERVIEW / STATS ━━━
    org_count = {}
    for e in entries:
        org = e.get('source_org', 'Unknown') or 'Unknown'
        if 'NASA' in org: org = 'NASA'
        elif 'ESA' in org or 'European' in org: org = 'ESA'
        elif 'JAXA' in org or 'Japan Aerospace' in org: org = 'JAXA'
        elif 'CNSA' in org or 'Chinese' in org: org = 'CNSA'
        org_count[org] = org_count.get(org, 0) + 1
    top_orgs = sorted(org_count.items(), key=lambda x: -x[1])[:8]
    max_org = top_orgs[0][1] if top_orgs else 1
    max_trl = max(trl_dist.values()) if trl_dist else 1

    html += f"""
<div class="slide">
  <div class="accent-bar" style="background:#783c28;"></div>
  <div class="slide-inner">
    <div class="content-header"><h2 style="color:#783c28;">統計サマリー</h2></div>

    <div class="kpi-row">
      <div class="kpi-box"><div class="kpi-num">{len(entries)}</div><div class="kpi-label">エントリ総数</div></div>
      <div class="kpi-box"><div class="kpi-num">{len(orgs)}</div><div class="kpi-label">組織数</div></div>
      <div class="kpi-box"><div class="kpi-num">10</div><div class="kpi-label">生活課題カテゴリ</div></div>
      <div class="kpi-box"><div class="kpi-num">{len(challenges)}</div><div class="kpi-label">月面環境課題</div></div>
      <div class="kpi-box"><div class="kpi-num">8</div><div class="kpi-label">基地モジュール</div></div>
    </div>

    <div class="stats-grid">
      <div class="stats-block">
        <h3>技術成熟度（TRL）分布</h3>
"""
    for t in range(1, 10):
        v = trl_dist.get(t, 0)
        html += f'        <div class="bar-row"><span class="bar-label">TRL {t} {trl_stage(t)}</span><div class="bar-track"><div class="bar-fill" style="width:{v/max_trl*100:.0f}%;background:{trl_color(t)};"></div></div><span class="bar-value">{v}</span></div>\n'
    html += '      </div>\n      <div class="stats-block">\n        <h3>組織別エントリ数</h3>\n'
    for org, cnt in top_orgs:
        html += f'        <div class="bar-row"><span class="bar-label">{truncate(org,18)}</span><div class="bar-track"><div class="bar-fill" style="width:{cnt/max_org*100:.0f}%;background:#783c28;"></div></div><span class="bar-value">{cnt}</span></div>\n'
    html += f"""      </div>
      <div class="stats-block">
        <h3>カテゴリ別エントリ数</h3>
"""
    max_cat = max(len(v) for v in by_cat.values()) if by_cat else 1
    for ck, ci in CATEGORIES.items():
        cnt = len(by_cat.get(ck, []))
        html += f'        <div class="bar-row"><span class="bar-label">{ci["ja"]}</span><div class="bar-track"><div class="bar-fill" style="width:{cnt/max_cat*100:.0f}%;background:{ci["color"]};"></div></div><span class="bar-value">{cnt}</span></div>\n'
    html += """      </div>
      <div class="stats-block">
        <h3>タイムライン別</h3>
"""
    tl_count = {}
    for e in entries:
        t = e.get('timeline', 'unknown') or 'unknown'
        tl_count[t] = tl_count.get(t, 0) + 1
    max_tl = max(tl_count.values()) if tl_count else 1
    for t in ['ongoing', '2020s', '2030s', '2040s']:
        v = tl_count.get(t, 0)
        if v:
            html += f'        <div class="bar-row"><span class="bar-label">{t}</span><div class="bar-track"><div class="bar-fill" style="width:{v/max_tl*100:.0f}%;background:#966D5E;"></div></div><span class="bar-value">{v}</span></div>\n'
    html += f"""      </div>
    </div>
  </div>
  {footer(page)}
</div>
"""
    page += 1

    # ━━━ CATEGORY SLIDES (2 slides per category: title + cards) ━━━
    cat_num = 0
    for cat_key, cat_info in CATEGORIES.items():
        cat_num += 1
        cat_entries = by_cat.get(cat_key, [])
        cat_challenges = ch_by_cat.get(cat_key, [])
        color = cat_info['color']

        # ── Section title slide ──
        html += f"""
<div class="slide section-slide">
  <div class="accent-bar" style="background:{color};"></div>
  <div class="section-num" style="color:{color};">{cat_num:02d}</div>
  <div class="slide-inner">
    <div class="section-cat" style="color:{color};">CATEGORY {cat_num:02d}</div>
    <div class="section-title" style="color:{color};">{cat_info['ja']}</div>
    <div class="section-desc-text">{cat_info['desc']}<br>{len(cat_entries)}件のエントリ</div>
"""
        if cat_challenges:
            html += '    <div class="section-challenge-list">\n'
            html += '      <div style="font-size:9pt;font-weight:600;color:#6b5c52;margin-bottom:2mm;">月面環境の主要課題</div>\n'
            for ch in cat_challenges:
                sc = SEVERITY_COLOR.get(ch.get('severity', 'medium'), '#999')
                sl = SEVERITY_JA.get(ch.get('severity', 'medium'), '?')
                html += f'      <div class="section-ch-item"><span class="section-ch-badge" style="background:{sc};">{sl}</span><span class="section-ch-text"><strong>{ch["name_ja"]}</strong> — {truncate(ch.get("description",""), 80)}</span></div>\n'
            html += '    </div>\n'

        html += f"""  </div>
  {footer(page, color)}
</div>
"""
        page += 1

        # ── Content cards slide (5x2 grid) ──
        html += f"""
<div class="slide">
  <div class="accent-bar" style="background:{color};"></div>
  <div class="slide-inner">
    <div class="content-header">
      <h2 style="color:{color};">{cat_info['ja']}</h2>
      <span class="content-sub">事例一覧 — {len(cat_entries)}件</span>
    </div>
    <div class="card-grid">
"""
        for e in cat_entries:
            trl = e.get('trl')
            org = truncate(e.get('source_org', ''), 10) or ''
            etype = ENTRY_TYPE_JA.get(e.get('entry_type', ''), '')
            mods = e.get('related_modules', [])

            html += f"""      <div class="card">
        <div class="card-top">
          <span class="badge badge-sm" style="background:{color};">{etype}</span>
"""
            if trl:
                html += f'          <span class="badge badge-sm" style="background:{trl_color(trl)};">TRL{trl}</span>\n'
            if org:
                html += f'          <span class="badge-outline badge-sm" style="border-color:#966D5E;color:#966D5E;">{org}</span>\n'
            html += f"""        </div>
        <div class="card-title">{truncate(e['title'], 40)}</div>
        <div class="card-summary">{truncate(e.get('summary', ''), 80)}</div>
        <div class="card-bottom">
"""
            for m in mods[:3]:
                mj = MODULES.get(m, {}).get('ja', m)
                html += f'          <span class="mod-tag">{mj}</span>\n'
            html += """        </div>
      </div>
"""
        html += f"""    </div>
  </div>
  {footer(page, color)}
</div>
"""
        page += 1

    # ━━━ MODULE MAPPING SLIDES (1 slide per module = 8 slides) ━━━
    for mk, mod in MODULES.items():
        ments = module_entries.get(mk, [])
        img_fmt, img_b64 = img_to_base64(mod.get('image', ''))

        # Pick top 2 featured entries (prefer highest TRL, diverse categories)
        sorted_ments = sorted(ments, key=lambda x: (x.get('trl') or 0, x.get('source_year') or 0), reverse=True)
        featured = sorted_ments[:2]
        rest = sorted_ments[2:]

        html += f"""
<div class="slide">
  <div class="accent-bar" style="background:linear-gradient(90deg,#F0A671,#7A4033);"></div>
  <div class="slide-inner">
    <div class="content-header">
      <h2 style="color:#783c28;">{mod['ja']}</h2>
      <span class="content-sub">{mod['desc']} — {len(ments)}件の関連事例</span>
    </div>
    <div class="mod-slide-layout">
      <div class="mod-image-area">
"""
        if img_b64:
            html += f'        <img src="data:image/{img_fmt};base64,{img_b64}" alt="{mod["ja"]}">\n'
        else:
            html += f'        <div style="font-size:14pt;color:#966D5E;">{mod["ja"]}</div>\n'
        html += f"""        <div class="mod-image-label">JAXA「Space Life on the Moon」月面基地イメージパース — {mod['ja']}</div>
      </div>
      <div class="mod-right-area">
"""
        # Featured entries (2 large cards)
        for fe in featured:
            cat_c = CATEGORIES.get(fe['category'], {}).get('color', '#999')
            cat_j = CATEGORIES.get(fe['category'], {}).get('ja', '')
            trl = fe.get('trl')
            org = truncate(fe.get('source_org', ''), 15) or ''
            etype = ENTRY_TYPE_JA.get(fe.get('entry_type', ''), '')

            html += f"""        <div class="mod-featured" style="border-color:{cat_c};">
          <div class="mod-featured-title" style="color:{cat_c};">{truncate(fe['title'], 50)}</div>
          <div class="mod-featured-summary">{truncate(fe.get('summary', ''), 120)}</div>
          <div class="mod-featured-meta">
            <span class="badge badge-sm" style="background:{cat_c};">{cat_j}</span>
"""
            if trl:
                html += f'            <span class="badge badge-sm" style="background:{trl_color(trl)};">TRL {trl}</span>\n'
            html += f'            <span class="badge-outline badge-sm" style="border-color:#966D5E;color:#966D5E;">{etype}</span>\n'
            if org:
                html += f'            <span style="font-size:7pt;color:#6b5c52;">{org}</span>\n'
            html += """          </div>
        </div>
"""

        # Rest entries (smaller, 2-column grid)
        if rest:
            html += f"""        <div class="mod-rest-area">
          <div class="mod-rest-title">その他の関連事例（{len(rest)}件）</div>
          <div class="mod-rest-grid">
"""
            for re_entry in rest[:12]:
                rc = CATEGORIES.get(re_entry['category'], {}).get('color', '#999')
                rj = CATEGORIES.get(re_entry['category'], {}).get('ja', '')
                rtrl = re_entry.get('trl')
                rtrl_s = f' TRL{rtrl}' if rtrl else ''
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:{rc};"></span><span><strong>{rj}</strong> {truncate(re_entry["title"], 28)}{rtrl_s}</span></div>\n'
            if len(rest) > 12:
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:#ccc;"></span><span style="color:#999;">他 {len(rest)-12}件</span></div>\n'
            html += """          </div>
        </div>
"""

        html += f"""      </div>
    </div>
  </div>
  {footer(page)}
</div>
"""
        page += 1

    # ━━━ CLOSING SLIDE ━━━
    html += f"""
<div class="slide cover-slide">
  <div class="accent-bar" style="background:linear-gradient(90deg,#F0A671,#DC8766,#B07256,#966D5E,#7A4033);"></div>
  <div class="slide-inner">
    <div class="cover-title" style="font-size:24pt;">月面生活リサーチDB</div>
    <div class="cover-sub">Lunar Life Research Database</div>
    <div class="cover-desc" style="margin-top:5mm;">
      本レポートはJAXA「Space Life on the Moon」企業向け資料をベースに、<br>
      月面生活のイメージをより具体的にするための世界中のリサーチを集積したものです。<br>
      追加のリサーチやアイディエーションにご活用ください。
    </div>
    <div class="cover-meta" style="margin-top:10mm;">
      NPO法人ミラツク / MIRA TUKU<br>
      {today}
    </div>
  </div>
</div>
"""

    html += "\n</body>\n</html>"

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Slides generated: {os.path.abspath(OUTPUT_PATH)}")
    print(f"  {page} slides total")


if __name__ == '__main__':
    generate()
