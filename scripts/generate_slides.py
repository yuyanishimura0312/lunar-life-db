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
    'private_room': {
        'ja': 'プライベートルーム', 'pdf_title': 'Private Room',
        'desc': '各クルーの個室。壁の中に配置され、机やベッドを壁にかけて省スペース化',
        'image': 'private_room.png',
    },
    'kitchen_dining': {
        'ja': 'ダイニングルーム', 'pdf_title': 'Dining Room',
        'desc': '季節感を感じる食事の時間。コミュニケーションの場としても機能する社交空間',
        'image': 'kitchen_dining.png',
    },
    'laboratory': {
        'ja': 'ワークスペースC（実験室）', 'pdf_title': 'Work Space C',
        'desc': '実験機器や宇宙服を備えた研究者のための実験空間。月面探査を支える拠点',
        'image': 'laboratory.png',
    },
    'workspace': {
        'ja': 'ワークルーム', 'pdf_title': 'Work Room A / B',
        'desc': '仕切りを自由に動かせるオフィス空間。低重力で什器移動も楽々',
        'image': 'workspace_a.png', 'image2': 'workspace_b.png',
    },
    'medical_bay': {
        'ja': 'バスルーム', 'pdf_title': 'Bathroom',
        'desc': '月の1/6Gで入浴・シャワーが可能。水場を一箇所に集めて循環する設計',
        'image': 'bathroom.png',
    },
    'training_room': {
        'ja': 'レクリエーションルーム', 'pdf_title': 'Recreation Room',
        'desc': 'スクリーンを設置し映画・音楽・イベントを楽しめる大空間。文化を生み出す場',
        'image': 'recreation.png',
    },
    'courtyard': {
        'ja': 'プレイパーク', 'pdf_title': 'Play Park',
        'desc': 'スポーツと緑の庭。借景として緑を配し、閉鎖環境に「見る」価値を提供',
        'image': 'courtyard.png',
    },
    'plantation': {
        'ja': 'プラントファクトリー', 'pdf_title': 'Plant Factory',
        'desc': '生鮮食料を確保する植物工場。植物の成長が癒しと生命の実感をもたらす',
        'image': 'plantation.png',
    },
}

IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')

ENTRY_TYPE_JA = {
    'technology': '技術', 'research': '研究', 'project': 'PJ',
    'concept': '概念', 'regulation': '規制', 'challenge': '課題', 'case_study': '事例',
}

SEVERITY_JA = {'critical': '深刻', 'high': '高', 'medium': '中', 'low': '低'}
SEVERITY_COLOR = {'critical': '#DC8766', 'high': '#B07256', 'medium': '#F0A671', 'low': '#CEA26F'}

# Module-specific context relevance configuration
# primary_cats: categories most relevant to the module's purpose
# keywords: terms in title/summary that indicate strong fit
MODULE_CONTEXT = {
    'private_room': {
        'primary_cats': ['sleep_habitat', 'entertainment', 'communication'],
        'keywords': ['睡眠', 'プライバシー', '概日', '照明', '個室', '居住', 'サーカディアン',
                     'ベッド', 'リラックス', '安眠', '音響', '騒音', 'sleep', 'circadian', 'privacy',
                     'habitat', '住環境', 'プライベート', '休息'],
    },
    'kitchen_dining': {
        'primary_cats': ['food', 'water', 'entertainment'],
        'keywords': ['食', '調理', '栄養', '食事', '料理', 'メニュー', '培養肉', '昆虫',
                     '水耕', '発酵', 'food', 'dining', 'meal', 'cook', '食文化', 'キッチン',
                     '食料', '社交', 'コミュニケーション'],
    },
    'laboratory': {
        'primary_cats': ['work_environment', 'medical', 'hygiene'],
        'keywords': ['実験', '研究', '分析', 'ラボ', '科学', '検査', 'サンプル', '計測',
                     '宇宙服', '船外', 'EVA', 'laboratory', 'research', 'experiment',
                     '探査', 'レゴリス', '試料', '機器'],
    },
    'workspace': {
        'primary_cats': ['work_environment', 'communication'],
        'keywords': ['作業', 'オフィス', '仕事', 'デスク', 'AR', 'MR', 'ロボティクス',
                     '遠隔', 'デジタルツイン', 'スケジューリング', '認知', 'タスク',
                     'workspace', 'office', 'テレワーク', '会議', '協働', 'チーム'],
    },
    'medical_bay': {
        'primary_cats': ['hygiene', 'water', 'medical'],
        'keywords': ['衛生', '入浴', 'シャワー', '洗濯', '洗浄', '水', 'リサイクル',
                     '浄化', '殺菌', 'バスルーム', '清潔', 'hygiene', 'bath', 'water',
                     '循環', '排水', '廃棄物', 'トイレ', '無水'],
    },
    'training_room': {
        'primary_cats': ['entertainment', 'exercise', 'communication'],
        'keywords': ['娯楽', 'レクリエーション', 'VR', 'ゲーム', '映画', '音楽',
                     'スクリーン', 'イベント', '文化', '芸術', 'recreation', 'entertainment',
                     'アート', 'コンサート', '趣味', 'リラクゼーション', 'マインドフルネス'],
    },
    'courtyard': {
        'primary_cats': ['exercise', 'entertainment', 'sleep_habitat'],
        'keywords': ['運動', 'スポーツ', 'トレーニング', '筋力', '骨密度', 'フィットネス',
                     '緑', '植物', '庭', '散歩', 'exercise', 'sport', 'fitness', 'park',
                     'バスケ', '体操', 'ジム', '身体', '心理'],
    },
    'plantation': {
        'primary_cats': ['food', 'water', 'hygiene'],
        'keywords': ['植物', '栽培', '農業', '作物', 'LED', '水耕', 'エアロポニクス',
                     '藻類', '野菜', '収穫', 'plant', 'farm', 'crop', 'agriculture',
                     '光合成', '生態系', 'バイオ', '食料生産', 'レタス'],
    },
}


def context_fit_score(entry, module_key):
    """Score how well an entry fits a module's context (higher = better fit)."""
    ctx = MODULE_CONTEXT.get(module_key, {})
    score = 0.0

    # 1. Category match (strongest signal)
    primary_cats = ctx.get('primary_cats', [])
    cat = entry.get('category', '')
    if cat in primary_cats:
        # Higher score for first (most relevant) category
        rank = primary_cats.index(cat)
        score += (3 - rank) * 10  # 30, 20, 10

    # 2. Keyword match in title and summary
    keywords = ctx.get('keywords', [])
    title = (entry.get('title', '') or '').lower()
    summary = (entry.get('summary', '') or '').lower()
    text = title + ' ' + summary
    keyword_hits = sum(1 for kw in keywords if kw.lower() in text)
    score += keyword_hits * 5

    # 3. Specificity bonus: entries that list fewer modules are more focused
    mods = entry.get('related_modules', [])
    if len(mods) > 0:
        score += 3.0 / len(mods)

    # 4. Small TRL tiebreaker (prefer more mature, but low weight)
    trl = entry.get('trl') or 0
    score += trl * 0.3

    return score


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
.slide-inner { padding: 14mm 20mm 18mm 18mm; height: 100%; display: flex; flex-direction: column; }

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
  display: grid; grid-template-columns: 46% 1fr; gap: 5mm;
  height: 150mm; overflow: hidden;
}
.mod-image-area {
  position: relative; border-radius: 3mm; overflow: hidden;
  background: #f5f0eb; display: flex; align-items: center; justify-content: center;
  height: 100%;
}
.mod-image-area img {
  width: 100%; height: 100%; object-fit: cover; object-position: center 40%; border-radius: 3mm;
}
.mod-image-label {
  position: absolute; bottom: 2mm; left: 2mm; right: 2mm;
  background: rgba(26,26,26,0.65); color: #fff; padding: 1.5mm 3mm;
  border-radius: 1.5mm; font-size: 7pt; backdrop-filter: blur(4px);
}
.mod-right-area {
  display: flex; flex-direction: column; gap: 2mm;
  height: 100%; overflow: hidden;
}
.mod-featured {
  border: 1.5px solid; border-radius: 2.5mm; padding: 3mm;
  background: #fdfbf9; flex: none;
}
.mod-featured-title { font-size: 9.5pt; font-weight: 700; line-height: 1.25; margin-bottom: 1mm; }
.mod-featured-summary { font-size: 7pt; color: #4a4a4a; line-height: 1.4; }
.mod-featured-meta { display: flex; gap: 1.5mm; align-items: center; margin-top: 1.5mm; flex-wrap: wrap; }
.mod-rest-area {
  flex: 1; border: 1px solid #e8e0d8; border-radius: 2mm;
  padding: 2.5mm; background: #fdfbf9;
  overflow: hidden;
}
.mod-rest-title { font-size: 7pt; font-weight: 600; color: #6b5c52; margin-bottom: 1.5mm; }
.mod-rest-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8mm; }
.mod-rest-item {
  display: flex; align-items: baseline; gap: 1mm;
  font-size: 6pt; line-height: 1.3; padding: 0.2mm 0;
}
.mod-rest-dot { width: 1.2mm; height: 1.2mm; border-radius: 50%; flex-shrink: 0; margin-top: 0.8mm; }

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

    # ━━━ SLIDE 1: COVER (simplified) ━━━
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
    <div class="cover-meta" style="margin-top:10mm;">
      NPO法人ミラツク / MIRA TUKU<br>
      {today}
    </div>
  </div>
</div>
"""
    page += 1

    # ━━━ SLIDE 2: LUNAR ENVIRONMENT ━━━
    html += f"""
<div class="slide">
  <div class="accent-bar" style="background:#783c28;"></div>
  <div class="slide-inner">
    <div class="content-header"><h2 style="color:#783c28;">月面環境</h2><span class="content-sub">人が暮らすために知るべき月の条件</span></div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:4mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:4mm; background:#fdfbf9;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:2mm;">基本物理環境</div>
          <table style="width:100%; font-size:8pt; border-collapse:collapse;">
            <tr><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5; width:35%;"><strong>重力</strong></td><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;">地球の1/6（約1.62 m/s²）</td></tr>
            <tr><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;"><strong>大気</strong></td><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;">ほぼ真空（10⁻¹² Pa）</td></tr>
            <tr><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;"><strong>日中温度</strong></td><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;">+127°C（14.75日間継続）</td></tr>
            <tr><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;"><strong>夜間温度</strong></td><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;">-173°C（14.75日間継続）</td></tr>
            <tr><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;"><strong>1日の長さ</strong></td><td style="padding:1.5mm 0; border-bottom:1px solid #f0ebe5;">29.5地球日（約708時間）</td></tr>
            <tr><td style="padding:1.5mm 0;"><strong>地球との距離</strong></td><td style="padding:1.5mm 0;">約384,400km（通信遅延 片道1.3秒）</td></tr>
          </table>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:4mm; background:#fdfbf9;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:2mm;">水氷資源</div>
          <p style="font-size:8pt; line-height:1.6; color:#4a4a4a;">
            月の南極・北極の永久影地帯に数百万トンの水氷が賦存すると推定されている。
            飲料水・農業用水・ロケット燃料（水素+酸素）の原料として、月面基地の立地を決める最重要資源。
            NASAのVIPERローバやPRIME-1実験で採掘技術の実証が進む。
          </p>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #DC8766; border-radius:2.5mm; padding:4mm; background:#DC876608;">
          <div style="font-size:10pt; font-weight:700; color:#DC8766; margin-bottom:2mm;">宇宙放射線</div>
          <p style="font-size:8pt; line-height:1.6; color:#4a4a4a;">
            月面には地球のような磁気圏が存在せず、銀河宇宙線（GCR）と太陽粒子線（SPE）が直接到達する。
            長期滞在では発がんリスク・中枢神経障害が懸念され、居住モジュールの遮蔽設計やレゴリスを利用した
            シールド構造が不可欠。太陽フレア時は緊急退避が必要。
          </p>
        </div>
        <div style="border:1px solid #B07256; border-radius:2.5mm; padding:4mm; background:#B0725608;">
          <div style="font-size:10pt; font-weight:700; color:#B07256; margin-bottom:2mm;">月面レゴリス（ダスト）</div>
          <p style="font-size:8pt; line-height:1.6; color:#4a4a4a;">
            月面を覆う微細な砂塵は非常に鋭角で、静電気により帯電しあらゆる表面に付着する。
            ナノスケール鉄が活性酸素を生成し、吸入すると肺・中枢神経に障害をもたらすリスクがある。
            アポロ飛行士も鼻腔充血やくしゃみを経験した。推奨曝露限界は0.3 mg/m³。
          </p>
        </div>
        <div style="border:1px solid #966D5E; border-radius:2.5mm; padding:4mm; background:#966D5E08;">
          <div style="font-size:10pt; font-weight:700; color:#966D5E; margin-bottom:2mm;">心理的課題</div>
          <p style="font-size:8pt; line-height:1.6; color:#4a4a4a;">
            閉鎖空間での長期滞在による心理的負荷。対人摩擦、単調さ、地球との隔絶感、
            概日リズムの乱れ（29.5日周期）が重なり、メンタルヘルスの維持が生命維持と同等に重要となる。
          </p>
        </div>
      </div>
    </div>
  </div>
  {footer(page)}
</div>
"""
    page += 1

    # ━━━ SLIDE 3: NATIONAL ROADMAPS ━━━
    html += f"""
<div class="slide">
  <div class="accent-bar" style="background:#783c28;"></div>
  <div class="slide-inner">
    <div class="content-header"><h2 style="color:#783c28;">各国の月面基地ロードマップ</h2></div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:3mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">米国 — Artemis計画</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2026</strong> Artemis II 月周回飛行（完了）</div>
            <div style="margin-bottom:1mm;"><strong>2027</strong> Artemis III HLS軌道テスト</div>
            <div style="margin-bottom:1mm;"><strong>2028</strong> Artemis IV <span style="color:#DC8766;font-weight:700;">初有人月面着陸</span></div>
            <div style="margin-bottom:1mm;"><strong>2029-36</strong> 月面地表基地建設へ転換</div>
            <div><strong>HLS</strong>: SpaceX Starship / Blue Origin Blue Moon</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">欧州 — ESA</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2026</strong> Moonlight初号機（Lunar Pathfinder）</div>
            <div style="margin-bottom:1mm;"><strong>2028</strong> Moonlight運用開始</div>
            <div style="margin-bottom:1mm;"><strong>2030</strong> 5衛星通信・測位完全運用</div>
            <div><strong>Moon Village</strong>: 国際的永続月面プレゼンス構想</div>
          </div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">中国 — ILRS</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2028</strong> Chang'e-7（ILRS基本構成）</div>
            <div style="margin-bottom:1mm;"><strong>2029</strong> Chang'e-8（ISRU実験）</div>
            <div style="margin-bottom:1mm;"><strong>2035</strong> <span style="color:#DC8766;font-weight:700;">ILRS基本モデル完成</span></div>
            <div style="margin-bottom:1mm;"><strong>2040s</strong> ILRS拡張モデル</div>
            <div>17ヶ国・50以上の研究機関が参加</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">日本 — JAXA</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2025</strong> Lunar Cruiser開発フェーズ開始</div>
            <div style="margin-bottom:1mm;"><strong>2027+</strong> Artemis計画に統合参加</div>
            <div style="margin-bottom:1mm;"><strong>2030s初</strong> <span style="color:#DC8766;font-weight:700;">Lunar Cruiser月面投入</span></div>
            <div>Toyota共同開発・水素燃料電池・航続10,000km</div>
          </div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">インド — ISRO</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2023</strong> Chandrayaan-3 南極着陸成功</div>
            <div style="margin-bottom:1mm;"><strong>計画中</strong> Chandrayaan-4 サンプルリターン</div>
            <div><strong>2040</strong> 有人月面着陸目標</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">ロシア — Roscosmos</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>2029-36</strong> Luna-27~30 段階的探査</div>
            <div><strong>ILRS</strong> 中国と共同で月面基地参加</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9; flex:1;">
          <div style="font-size:10pt; font-weight:700; color:#783c28; margin-bottom:1.5mm;">その他</div>
          <div style="font-size:7.5pt; line-height:1.55; color:#4a4a4a;">
            <div style="margin-bottom:1mm;"><strong>UAE</strong> Lunar Gateway参加（2025年宣言）</div>
            <div><strong>韓国</strong> 2032年月面着陸機ミッション目標</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  {footer(page)}
</div>
"""
    page += 1

    # ━━━ SLIDE 4: HISTORICAL MILESTONES ━━━
    html += f"""
<div class="slide">
  <div class="accent-bar" style="background:#783c28;"></div>
  <div class="slide-inner">
    <div class="content-header"><h2 style="color:#783c28;">月面基地に至る人類の歩み</h2></div>
    <div style="position:relative; flex:1; padding:2mm 0;">
      <div style="position:absolute; left:50%; top:0; bottom:0; width:2px; background:linear-gradient(180deg,#F0A671,#7A4033);"></div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0; height:100%;">
        <div style="display:flex; flex-direction:column; justify-content:space-between; padding-right:8mm; text-align:right;">
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#F0A671;">1959</div>
            <div style="color:#4a4a4a;">Luna 2 — 人類初の月面到達（衝突）</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#F0A671;">1966</div>
            <div style="color:#4a4a4a;">Luna 9 — 初の軟着陸・月面写真撮影</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#DC8766;">1969-72</div>
            <div style="color:#4a4a4a;">Apollo計画 — 6回の有人着陸、12人が月面歩行</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#DC8766;">2007-13</div>
            <div style="color:#4a4a4a;">かぐや / Chandrayaan-1 / LCROSS / Chang'e-1~3<br>月面探査の国際化</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#B07256;">2019</div>
            <div style="color:#4a4a4a;">Chang'e 4 — 人類初の月裏側着陸</div>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; justify-content:space-between; padding-left:8mm;">
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#B07256;">2023</div>
            <div style="color:#4a4a4a;">Chandrayaan-3 南極着陸 / SLIM精密着陸</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#966D5E;">2025</div>
            <div style="color:#4a4a4a;">商用月面着陸の幕開け<br>Firefly Blue Ghost成功 / IM-2 南極探査</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#966D5E;">2026</div>
            <div style="color:#4a4a4a;">Artemis II 月周回完了 / 商用着陸加速</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#7A4033;">2028</div>
            <div style="color:#DC8766; font-weight:700;">Artemis IV — Apollo以来の有人月面着陸</div>
          </div>
          <div style="font-size:8pt; line-height:1.5;">
            <div style="font-size:11pt; font-weight:800; color:#7A4033;">2030s-40s</div>
            <div style="color:#4a4a4a;">Artemis Base Camp建設 / ILRS基本モデル完成<br>Lunar Cruiser投入 / 月面永住の時代へ</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  {footer(page)}
</div>
"""
    page += 1

    # ━━━ SLIDE 5: WORLDWIDE PROJECTS ━━━
    html += f"""
<div class="slide">
  <div class="accent-bar" style="background:#783c28;"></div>
  <div class="slide-inner">
    <div class="content-header"><h2 style="color:#783c28;">世界の月面基地プロジェクト</h2><span class="content-sub">政府機関と民間企業が並走する月面開発</span></div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:4mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9;">
          <div style="font-size:9pt; font-weight:700; color:#783c28; margin-bottom:2mm;">有人輸送・着陸システム</div>
          <div style="font-size:7.5pt; line-height:1.6; color:#4a4a4a;">
            <div style="margin-bottom:1.5mm;"><strong>SpaceX Starship HLS</strong> — NASA主契約、Block 3仕様、2028年初着陸予定</div>
            <div style="margin-bottom:1.5mm;"><strong>Blue Origin Blue Moon Mk2</strong> — 最大4名乗員、30日滞在対応</div>
            <div><strong>Toyota Lunar Cruiser</strong> — JAXA共同、圧力化ローバ、航続10,000km</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9;">
          <div style="font-size:9pt; font-weight:700; color:#783c28; margin-bottom:2mm;">商用ロボット着陸機（CLPS）</div>
          <div style="font-size:7.5pt; line-height:1.6; color:#4a4a4a;">
            <div style="margin-bottom:1.5mm;"><strong>Intuitive Machines</strong> — IM-2南極探査中、IM-3計画</div>
            <div style="margin-bottom:1.5mm;"><strong>Firefly Aerospace</strong> — Blue Ghost Mission 1成功（2025年3月）</div>
            <div style="margin-bottom:1.5mm;"><strong>Astrobotic</strong> — Griffin着陸機（月南極、2026年）</div>
            <div><strong>ispace</strong> — APEX 1.0（月裏側Schrödinger Basin、2026年）</div>
          </div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9;">
          <div style="font-size:9pt; font-weight:700; color:#783c28; margin-bottom:2mm;">基地建設・ハビタット技術</div>
          <div style="font-size:7.5pt; line-height:1.6; color:#4a4a4a;">
            <div style="margin-bottom:1.5mm;"><strong>ICON Project Olympus</strong> — レーザー月壌溶融による3D印刷建設（NASA $57M契約）</div>
            <div style="margin-bottom:1.5mm;"><strong>NASA Artemis Base Camp</strong> — 南極エリア永続基地、NextSTEPハビタット</div>
            <div style="margin-bottom:1.5mm;"><strong>Sierra Space LIFE</strong> — 拡張式高圧ハビタット（軌道・月面両対応）</div>
            <div><strong>BIG + SEArch+</strong> — Project Olympus建築設計パートナー</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9;">
          <div style="font-size:9pt; font-weight:700; color:#783c28; margin-bottom:2mm;">通信・測位インフラ</div>
          <div style="font-size:7.5pt; line-height:1.6; color:#4a4a4a;">
            <div style="margin-bottom:1.5mm;"><strong>ESA Moonlight</strong> — 月衛星通信＆Galileo測位（5衛星、2030年完全運用）</div>
            <div><strong>NASA LunaNet</strong> — 月面通信・航法アーキテクチャ</div>
          </div>
        </div>
        <div style="border:1px solid #e8e0d8; border-radius:2.5mm; padding:3.5mm; background:#fdfbf9;">
          <div style="font-size:9pt; font-weight:700; color:#783c28; margin-bottom:2mm;">資源探査・ISRU</div>
          <div style="font-size:7.5pt; line-height:1.6; color:#4a4a4a;">
            <div style="margin-bottom:1.5mm;"><strong>NASA PRIME-1</strong> — 極地水氷採掘実験（2025年）</div>
            <div><strong>CNSA/Roscosmos ILRS</strong> — 月地質・ISRU科学拠点（2035年）</div>
          </div>
        </div>
      </div>
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

        # Pick top 2 featured entries by context fit (not just TRL)
        scored = [(context_fit_score(e, mk), e) for e in ments]
        scored.sort(key=lambda x: x[0], reverse=True)
        featured = [e for _, e in scored[:2]]
        rest = [e for _, e in scored[2:]]

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
        html += f"""        <div class="mod-image-label">JAXA「Space Life on the Moon」— {mod.get('pdf_title', mod['ja'])}</div>
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
          <div class="mod-featured-title" style="color:{cat_c};">{truncate(fe['title'], 40)}</div>
          <div class="mod-featured-summary">{truncate(fe.get('summary', ''), 75)}</div>
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
            for re_entry in rest[:8]:
                rc = CATEGORIES.get(re_entry['category'], {}).get('color', '#999')
                rj = CATEGORIES.get(re_entry['category'], {}).get('ja', '')
                rtrl = re_entry.get('trl')
                rtrl_s = f' TRL{rtrl}' if rtrl else ''
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:{rc};"></span><span><strong>{rj}</strong> {truncate(re_entry["title"], 22)}{rtrl_s}</span></div>\n'
            if len(rest) > 8:
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:#ccc;"></span><span style="color:#999;">他 {len(rest)-8}件</span></div>\n'
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
