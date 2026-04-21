#!/usr/bin/env python3
"""Generate landscape A4 HTML slides for the Lunar Life Research Database.

Design: Miratuku brand standard — white background, restrained palette,
generous whitespace, clear typographic hierarchy.
"""

import sqlite3
import json
import os
import base64
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'slides.html')
IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')

CATEGORIES = {
    'food': {'ja': '食', 'color': '#B07256', 'desc': '月面での食料生産・調理・栄養管理'},
    'water': {'ja': '水', 'color': '#7A9BAE', 'desc': '水資源の確保・循環・浄化'},
    'hygiene': {'ja': '衛生', 'color': '#A0896E', 'desc': '個人衛生・微生物管理・廃棄物処理'},
    'medical': {'ja': '医療', 'color': '#C47D5A', 'desc': '遠隔医療・放射線防護・メンタルヘルス'},
    'exercise': {'ja': '運動', 'color': '#8B7355', 'desc': '筋力維持・骨密度保全・リハビリテーション'},
    'clothing': {'ja': '衣服', 'color': '#9E8C73', 'desc': '宇宙服・船内着・スマートテキスタイル'},
    'communication': {'ja': '通信', 'color': '#7E8B6D', 'desc': '通信インフラ・心理的接続・チーム支援'},
    'entertainment': {'ja': '娯楽', 'color': '#A07E6E', 'desc': 'レクリエーション・心理的ウェルビーイング'},
    'sleep_habitat': {'ja': '睡眠・住環境', 'color': '#6E7B7C', 'desc': '居住モジュール・概日リズム・プライバシー'},
    'work_environment': {'ja': '作業環境', 'color': '#5C6B5E', 'desc': 'AR支援・テレロボティクス・人間工学'},
}

MODULES = {
    'private_room': {'ja': 'プライベートルーム', 'pdf_title': 'Private Room',
        'desc': '各クルーの個室。壁の中に配置され、机やベッドを壁にかけて省スペース化', 'image': 'private_room.png'},
    'kitchen_dining': {'ja': 'ダイニングルーム', 'pdf_title': 'Dining Room',
        'desc': '季節感を感じる食事の時間。コミュニケーションの場としても機能する社交空間', 'image': 'kitchen_dining.png'},
    'laboratory': {'ja': 'ワークスペースC（実験室）', 'pdf_title': 'Work Space C',
        'desc': '実験機器や宇宙服を備えた研究者のための実験空間。月面探査を支える拠点', 'image': 'laboratory.png'},
    'workspace': {'ja': 'ワークルーム', 'pdf_title': 'Work Room A / B',
        'desc': '仕切りを自由に動かせるオフィス空間。低重力で什器移動も楽々', 'image': 'workspace_a.png'},
    'medical_bay': {'ja': 'バスルーム', 'pdf_title': 'Bathroom',
        'desc': '月の1/6Gで入浴・シャワーが可能。水場を一箇所に集めて循環する設計', 'image': 'bathroom.png'},
    'training_room': {'ja': 'レクリエーションルーム', 'pdf_title': 'Recreation Room',
        'desc': 'スクリーンを設置し映画・音楽・イベントを楽しめる大空間。文化を生み出す場', 'image': 'recreation.png'},
    'courtyard': {'ja': 'プレイパーク', 'pdf_title': 'Play Park',
        'desc': 'スポーツと緑の庭。借景として緑を配し、閉鎖環境に「見る」価値を提供', 'image': 'courtyard.png'},
    'plantation': {'ja': 'プラントファクトリー', 'pdf_title': 'Plant Factory',
        'desc': '生鮮食料を確保する植物工場。植物の成長が癒しと生命の実感をもたらす', 'image': 'plantation.png'},
}

ENTRY_TYPE_JA = {'technology': '技術', 'research': '研究', 'project': 'PJ',
    'concept': '概念', 'regulation': '規制', 'challenge': '課題', 'case_study': '事例'}
SEVERITY_JA = {'critical': '深刻', 'high': '高', 'medium': '中', 'low': '低'}

MODULE_CONTEXT = {
    'private_room': {'primary_cats': ['sleep_habitat', 'entertainment', 'communication'],
        'keywords': ['睡眠','プライバシー','概日','照明','個室','居住','ベッド','安眠','音響','住環境','休息']},
    'kitchen_dining': {'primary_cats': ['food', 'water', 'entertainment'],
        'keywords': ['食','調理','栄養','食事','料理','培養肉','昆虫','水耕','発酵','食文化','食料','社交']},
    'laboratory': {'primary_cats': ['work_environment', 'medical', 'hygiene'],
        'keywords': ['実験','研究','分析','ラボ','科学','検査','宇宙服','EVA','探査','レゴリス','試料','機器']},
    'workspace': {'primary_cats': ['work_environment', 'communication'],
        'keywords': ['作業','オフィス','仕事','AR','MR','ロボティクス','遠隔','デジタルツイン','認知','タスク','会議','協働']},
    'medical_bay': {'primary_cats': ['hygiene', 'water', 'medical'],
        'keywords': ['衛生','入浴','シャワー','洗濯','洗浄','水','浄化','殺菌','清潔','循環','排水','廃棄物','無水']},
    'training_room': {'primary_cats': ['entertainment', 'exercise', 'communication'],
        'keywords': ['娯楽','レクリエーション','VR','ゲーム','映画','音楽','スクリーン','イベント','文化','芸術']},
    'courtyard': {'primary_cats': ['exercise', 'entertainment', 'sleep_habitat'],
        'keywords': ['運動','スポーツ','トレーニング','筋力','骨密度','フィットネス','緑','植物','庭','散歩','身体']},
    'plantation': {'primary_cats': ['food', 'water', 'hygiene'],
        'keywords': ['植物','栽培','農業','作物','LED','水耕','藻類','野菜','収穫','光合成','バイオ','食料生産']},
}

def context_fit_score(entry, module_key):
    ctx = MODULE_CONTEXT.get(module_key, {})
    score = 0.0
    primary_cats = ctx.get('primary_cats', [])
    cat = entry.get('category', '')
    if cat in primary_cats:
        score += (3 - primary_cats.index(cat)) * 10
    text = ((entry.get('title', '') or '') + ' ' + (entry.get('summary', '') or '')).lower()
    score += sum(1 for kw in ctx.get('keywords', []) if kw.lower() in text) * 5
    mods = entry.get('related_modules', [])
    if mods: score += 3.0 / len(mods)
    score += (entry.get('trl') or 0) * 0.3
    return score

def img_to_base64(filename):
    for ext, mime in [('.jpg', 'jpeg'), ('.png', 'png')]:
        p = os.path.join(IMG_DIR, 'cropped', filename.replace('.png', ext))
        if os.path.exists(p):
            with open(p, 'rb') as f: return mime, base64.b64encode(f.read()).decode()
    p = os.path.join(IMG_DIR, filename)
    if os.path.exists(p):
        with open(p, 'rb') as f: return 'png', base64.b64encode(f.read()).decode()
    return '', ''

def trl_color(trl):
    if trl is None: return '#D1D5DB'
    if trl <= 3: return '#9CA3AF'
    if trl <= 6: return '#6B7280'
    return '#374151'

def truncate(s, n):
    if not s: return ''
    return s[:n] + ('...' if len(s) > n else '')


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
CSS = """
@page { size: A4 landscape; margin: 0; }
@media print {
  .slide { page-break-after: always; }
  .slide:last-child { page-break-after: auto; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}

*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --c-bg:      #FFFFFF;
  --c-text:    #1A1A1A;
  --c-muted:   #6B7280;
  --c-subtle:  #9CA3AF;
  --c-border:  #E5E7EB;
  --c-surface: #F9FAFB;
  --c-accent:  #374151;
  --c-warm:    #78552E;
}

body {
  font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", -apple-system,
               BlinkMacSystemFont, "Noto Sans JP", sans-serif;
  color: var(--c-text);
  background: #E5E7EB;
  font-feature-settings: "palt";
  -webkit-font-smoothing: antialiased;
}

/* ═══ Slide ═══ */
.slide {
  width: 297mm; height: 210mm;
  background: var(--c-bg);
  position: relative; overflow: hidden;
  margin: 0 auto;
}
@media screen {
  .slide { margin: 12mm auto; box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 8px 32px rgba(0,0,0,0.08); }
}
.si {
  padding: 18mm 24mm 22mm;
  height: 100%; display: flex; flex-direction: column;
}

/* ═══ Top rule ═══ */
.rule { position: absolute; top: 0; left: 0; right: 0; height: 1.5mm; background: var(--c-accent); }

/* ═══ Footer ═══ */
.ft {
  position: absolute; bottom: 8mm; left: 24mm; right: 24mm;
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 6pt; color: var(--c-subtle); letter-spacing: 0.06em;
}

/* ═══ Cover ═══ */
.cover .si {
  justify-content: center; align-items: flex-start;
  padding-left: 36mm; padding-right: 36mm;
}
.cover .rule { height: 2mm; background: var(--c-warm); }
.c-kicker {
  font-size: 8pt; font-weight: 600; color: var(--c-subtle);
  letter-spacing: 0.15em; text-transform: uppercase;
  margin-bottom: 5mm;
}
.c-title {
  font-size: 30pt; font-weight: 800; color: var(--c-text);
  letter-spacing: 0.06em; line-height: 1.2; margin-bottom: 6mm;
}
.c-title em { font-style: normal; color: var(--c-warm); }
.c-rule { width: 32mm; height: 1px; background: var(--c-border); margin-bottom: 6mm; }
.c-desc {
  font-size: 10pt; color: var(--c-muted); line-height: 1.9;
  max-width: 200mm; margin-bottom: 16mm;
}
.c-meta { font-size: 8pt; color: var(--c-subtle); letter-spacing: 0.05em; }

/* ═══ Page header ═══ */
.ph { margin-bottom: 5mm; }
.ph-kicker { font-size: 7pt; font-weight: 600; color: var(--c-subtle); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1.5mm; }
.ph h2 { font-size: 16pt; font-weight: 700; color: var(--c-text); letter-spacing: 0.02em; line-height: 1.3; }
.ph-sub { font-size: 8pt; color: var(--c-muted); margin-top: 2mm; line-height: 1.6; max-width: 220mm; }

/* ═══ Divider (category title slide) ═══ */
.divider .si { justify-content: center; padding-left: 36mm; }
.div-num {
  font-size: 120pt; font-weight: 900; color: var(--c-border);
  position: absolute; right: 24mm; bottom: 20mm;
  line-height: 1; letter-spacing: -0.02em;
}
.div-kicker { font-size: 8pt; font-weight: 600; letter-spacing: 0.15em; margin-bottom: 3mm; }
.div-title { font-size: 28pt; font-weight: 800; color: var(--c-text); margin-bottom: 4mm; letter-spacing: 0.03em; }
.div-desc { font-size: 10pt; color: var(--c-muted); max-width: 160mm; line-height: 1.8; margin-bottom: 8mm; }
.div-challenges { max-width: 200mm; }
.div-ch {
  display: flex; align-items: flex-start; gap: 3mm;
  margin-bottom: 2.5mm; font-size: 8pt; line-height: 1.6;
}
.div-ch-sev {
  font-size: 6pt; font-weight: 700; color: #fff;
  padding: 0.5mm 2mm; border-radius: 1mm; flex-shrink: 0; margin-top: 0.8mm;
}

/* ═══ Info block ═══ */
.ib { border-radius: 2mm; padding: 4mm; background: var(--c-surface); }
.ib-line { border-left: 2px solid var(--c-border); }
.ib h3 { font-size: 9pt; font-weight: 700; color: var(--c-text); margin-bottom: 2mm; }
.ib h4 { font-size: 8pt; font-weight: 700; color: var(--c-text); margin-bottom: 1.5mm; }
.ib .t { font-size: 7.5pt; line-height: 1.65; color: var(--c-muted); }
.ib table { width: 100%; font-size: 7.5pt; border-collapse: collapse; }
.ib td { padding: 1.5mm 1mm; border-bottom: 1px solid var(--c-border); }
.ib td:first-child { font-weight: 600; color: var(--c-text); width: 28%; }
.ib .hi { color: var(--c-warm); font-weight: 700; }

/* ═══ Timeline ═══ */
.tl { display: flex; align-items: flex-start; gap: 3mm; margin-bottom: 2.5mm; }
.tl-y { font-size: 8pt; font-weight: 700; width: 14mm; text-align: right; flex-shrink: 0; color: var(--c-text); }
.tl-d { width: 2mm; height: 2mm; border-radius: 50%; flex-shrink: 0; margin-top: 1.5mm; }
.tl-t { font-size: 7.5pt; color: var(--c-muted); line-height: 1.5; flex: 1; }
.tl-t strong { color: var(--c-text); }

/* ═══ Card grid ═══ */
.cg { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2.5mm; flex: 1; }
.card {
  border-radius: 2mm; padding: 3mm; display: flex; flex-direction: column;
  background: var(--c-surface); overflow: hidden;
}
.card-top { display: flex; align-items: center; gap: 1.5mm; margin-bottom: 1.5mm; flex-wrap: wrap; }
.card-title { font-size: 7.5pt; font-weight: 700; line-height: 1.35; margin-bottom: 1mm; color: var(--c-text); }
.card-desc { font-size: 6.5pt; color: var(--c-muted); line-height: 1.45; flex: 1; }
.card-foot { margin-top: auto; padding-top: 1mm; display: flex; flex-wrap: wrap; gap: 1mm; }

/* ═══ Badges ═══ */
.b { display: inline-block; padding: 0.4mm 2mm; border-radius: 1mm; font-size: 6pt; font-weight: 600; color: #fff; white-space: nowrap; }
.b-o { display: inline-block; padding: 0.3mm 1.5mm; border-radius: 1mm; font-size: 6pt; font-weight: 500; border: 0.5px solid var(--c-border); color: var(--c-muted); white-space: nowrap; background: transparent; }
.tag { display: inline-block; padding: 0.3mm 1.5mm; border-radius: 1mm; font-size: 5.5pt; background: var(--c-border); color: var(--c-muted); white-space: nowrap; }

/* ═══ Module slide ═══ */
.mod-grid { display: grid; grid-template-columns: 44% 1fr; gap: 6mm; flex: 1; min-height: 0; }
.mod-img { position: relative; border-radius: 2mm; overflow: hidden; background: var(--c-surface); min-height: 0; }
.mod-img img { width: 100%; height: 100%; object-fit: cover; object-position: center 40%; }
.mod-img-cap {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.55));
  color: #fff; padding: 8mm 3mm 2.5mm; font-size: 6pt; letter-spacing: 0.04em;
}
.mod-right { display: flex; flex-direction: column; gap: 2.5mm; min-height: 0; overflow: hidden; }
.mod-feat { border-left: 2px solid; border-radius: 2mm; padding: 3mm; background: var(--c-surface); }
.mod-feat h3 { font-size: 9pt; font-weight: 700; line-height: 1.3; margin-bottom: 1mm; }
.mod-feat p { font-size: 7pt; color: var(--c-muted); line-height: 1.5; }
.mod-feat-meta { display: flex; gap: 1.5mm; align-items: center; margin-top: 1.5mm; flex-wrap: wrap; }
.mod-rest {
  flex: 1; border-top: 1px solid var(--c-border); padding-top: 2mm; overflow: hidden;
}
.mod-rest h4 { font-size: 6.5pt; font-weight: 600; color: var(--c-subtle); margin-bottom: 1.5mm; letter-spacing: 0.05em; }
.mod-rest-list { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5mm 2mm; }
.mod-rest-item { font-size: 6pt; color: var(--c-muted); line-height: 1.4; display: flex; gap: 1mm; align-items: baseline; }
.mod-rest-item::before { content: ''; width: 1mm; height: 1mm; border-radius: 50%; flex-shrink: 0; margin-top: 0.8mm; }
"""


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

    today = datetime.now().strftime('%Y年%m月%d日')

    html = f'<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="UTF-8">\n<title>月面生活リサーチレポート</title>\n<style>{CSS}</style>\n</head>\n<body>\n'

    page = 1
    def ft(p):
        return f'<div class="ft"><span>NPO法人ミラツク</span><span>月面生活リサーチレポート</span><span>{p}</span></div>'

    # ━━━ 1. COVER ━━━
    html += f'''
<div class="slide cover">
  <div class="rule"></div>
  <div class="si">
    <div class="c-kicker">JAXA Space Life on the Moon</div>
    <div class="c-title">月面生活<em>リサーチ</em>レポート</div>
    <div class="c-rule"></div>
    <div class="c-desc">
      月面基地での暮らしに必要な技術と知見を、世界中の研究・プロジェクトから集め、<br>
      10の生活課題カテゴリと8つの基地モジュールに整理したレポート。
    </div>
    <div class="c-meta">NPO法人ミラツク &mdash; {today}</div>
  </div>
</div>
'''
    page += 1

    # ━━━ 2. LUNAR ENVIRONMENT ━━━
    html += f'''
<div class="slide">
  <div class="rule" style="background:var(--c-warm);"></div>
  <div class="si">
    <div class="ph">
      <div class="ph-kicker">Background</div>
      <h2>月面環境</h2>
      <div class="ph-sub">人が暮らすために理解すべき条件。月面は真空・極端温度・放射線・有害ダストに晒される過酷な環境である。</div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:4mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div class="ib" style="flex:none;">
          <h3>基本物理環境</h3>
          <table>
            <tr><td>重力</td><td>地球の1/6（1.62 m/s&sup2;）</td></tr>
            <tr><td>大気</td><td>ほぼ真空（10&sup{-12} Pa）</td></tr>
            <tr><td>日中温度</td><td>+127&deg;C（14.75日間）</td></tr>
            <tr><td>夜間温度</td><td>&minus;173&deg;C（14.75日間）</td></tr>
            <tr><td>1日の長さ</td><td>29.5地球日</td></tr>
            <tr><td>通信遅延</td><td>片道1.3秒（384,400km）</td></tr>
          </table>
        </div>
        <div class="ib ib-line" style="border-color:var(--c-warm); flex:1;">
          <h3>水氷資源</h3>
          <div class="t">南極・北極の永久影地帯に数百万トンの水氷が賦存。飲料水・農業用水・ロケット燃料の原料として月面基地の立地を決める最重要資源。PRIME-1実験で採掘技術を実証中。</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div class="ib ib-line" style="border-color:#C47D5A;">
          <h3>宇宙放射線</h3>
          <div class="t">磁気圏がなく銀河宇宙線と太陽粒子線が直接到達。長期滞在では発がん・中枢神経障害リスク。レゴリス遮蔽や居住モジュール設計が不可欠。太陽フレア時は緊急退避が必要。</div>
        </div>
        <div class="ib ib-line" style="border-color:#8B7355;">
          <h3>月面レゴリス</h3>
          <div class="t">微細で鋭角的な砂塵が静電気で付着。ナノスケール鉄が活性酸素を生成し吸入で肺障害リスク。アポロ飛行士も鼻腔充血を経験。推奨曝露限界 0.3 mg/m&sup3;。</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div class="ib ib-line" style="border-color:#6E7B7C;">
          <h3>心理的課題</h3>
          <div class="t">閉鎖空間での長期滞在による対人摩擦、単調さ、地球との隔絶感。29.5日周期の概日リズム乱れも加わり、メンタルヘルス維持が生命維持と同等に重要。ISS・南極越冬隊の知見が基盤。</div>
        </div>
        <div class="ib" style="flex:1; display:flex; flex-direction:column; justify-content:center; text-align:center; color:var(--c-muted); font-size:8pt; line-height:1.7;">
          <div style="font-size:28pt; font-weight:800; color:var(--c-warm); margin-bottom:2mm;">1/6 G</div>
          <div>月面の重力は地球の6分の1。<br>骨密度低下・筋萎縮が進行するが<br>ISSの微小重力よりは緩和される。</div>
        </div>
      </div>
    </div>
  </div>
  {ft(page)}
</div>
'''
    page += 1

    # ━━━ 3. HISTORY ━━━
    tl_data = [
        ('1959', 'Luna 2 — 人類初の月面到達（衝突）'),
        ('1966', 'Luna 9 — 初の軟着陸、月面写真の撮影に成功'),
        ('1969', '<strong>Apollo 11 — 人類初の月面歩行</strong>'),
        ('1972', 'Apollo 17 — 最後の有人ミッション。以後50年以上、人類は月面に立っていない'),
        ('2007-13', '月面探査の国際化 — かぐや（日）、Chandrayaan-1（印）、Chang\'e-1~3（中）'),
        ('2019', 'Chang\'e 4 — 人類初の月裏側着陸'),
        ('2023', 'Chandrayaan-3 南極着陸 / SLIM精密着陸（日本）'),
        ('2025', '商用月面着陸の幕開け — Firefly Blue Ghost成功、IM-2南極探査'),
        ('2026', 'Artemis II 月周回飛行完了。商用着陸が加速'),
        ('2028', '<strong class="hi">Artemis IV — Apollo以来の有人月面着陸（予定）</strong>'),
        ('2030s', 'Artemis Base Camp建設 / Lunar Cruiser投入 / ILRS基本モデル完成へ'),
    ]
    html += f'''
<div class="slide">
  <div class="rule"></div>
  <div class="si">
    <div class="ph">
      <div class="ph-kicker">History</div>
      <h2>月面基地に至る人類の歩み</h2>
      <div class="ph-sub">1959年の最初の月面到達から、2030年代の恒久基地建設へ。半世紀の空白を経て、再び月を目指す時代が始まった。</div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10mm; flex:1; align-content:start; padding-top:2mm;">
'''
    half = 6
    for col_data in [tl_data[:half], tl_data[half:]]:
        html += '      <div>\n'
        for yr, text in col_data:
            html += f'        <div class="tl"><div class="tl-y">{yr}</div><div class="tl-d" style="background:var(--c-warm);"></div><div class="tl-t">{text}</div></div>\n'
        html += '      </div>\n'
    html += f'''    </div>
  </div>
  {ft(page)}
</div>
'''
    page += 1

    # ━━━ 4. ROADMAPS + PROJECTS ━━━
    html += f'''
<div class="slide">
  <div class="rule"></div>
  <div class="si">
    <div class="ph">
      <div class="ph-kicker">Global Landscape</div>
      <h2>各国のロードマップと主要プロジェクト</h2>
      <div class="ph-sub">2025年は商用着陸が本格化し、2028年には半世紀ぶりの有人着陸が予定されている。政府機関と民間企業が並走する月面開発の全体像。</div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:3mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:2mm;">
        <div class="ib ib-line" style="border-color:var(--c-warm); flex:1;">
          <h4>米国 Artemis計画</h4>
          <div class="t"><strong>2026</strong> Artemis II 月周回完了<br><strong>2028</strong> <span class="hi">Artemis IV 有人着陸</span><br><strong>2029+</strong> 月面地表基地建設へ転換</div>
        </div>
        <div class="ib" style="flex:1;">
          <h4>SpaceX / Blue Origin</h4>
          <div class="t">Starship HLS — NASA主契約<br>Blue Moon Mk2 — 4名30日滞在</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2mm;">
        <div class="ib ib-line" style="border-color:#8B7355; flex:1;">
          <h4>中国 ILRS</h4>
          <div class="t"><strong>2028-29</strong> Chang'e-7/8<br><strong>2035</strong> <span class="hi">ILRS基本モデル完成</span><br>17ヶ国・50+機関が参加</div>
        </div>
        <div class="ib ib-line" style="border-color:#7E8B6D; flex:1;">
          <h4>日本 Lunar Cruiser</h4>
          <div class="t">Toyota共同開発・与圧ローバ<br>水素燃料電池・航続10,000km<br><strong>2030s初</strong> 月面投入</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2mm;">
        <div class="ib" style="flex:none;">
          <h4>商用着陸機（CLPS）</h4>
          <div class="t" style="font-size:7pt;"><strong>Intuitive Machines</strong> IM-2南極<br><strong>Firefly</strong> Blue Ghost成功<br><strong>Astrobotic</strong> Griffin 2026<br><strong>ispace</strong> APEX 1.0 2026</div>
        </div>
        <div class="ib" style="flex:1;">
          <h4>基地建設技術</h4>
          <div class="t" style="font-size:7pt;"><strong>ICON Project Olympus</strong><br>3D印刷建設（NASA $57M）<br><br><strong>Sierra Space LIFE</strong><br>拡張式高圧ハビタット</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2mm;">
        <div class="ib" style="flex:none;">
          <h4>欧州 ESA Moonlight</h4>
          <div class="t">月衛星通信+測位 5衛星<br><strong>2030</strong> 完全運用開始</div>
        </div>
        <div class="ib" style="flex:none;">
          <h4>インド / ロシア / 他</h4>
          <div class="t" style="font-size:7pt;">ISRO: 2040年有人着陸目標<br>Roscosmos: ILRS共同参加<br>UAE: Gateway参加宣言<br>韓国: 2032年着陸機計画</div>
        </div>
        <div class="ib" style="flex:1;">
          <h4>資源探査 ISRU</h4>
          <div class="t">NASA PRIME-1 水氷採掘<br>ILRS科学拠点（2035年）</div>
        </div>
      </div>
    </div>
  </div>
  {ft(page)}
</div>
'''
    page += 1

    # ━━━ CATEGORY SLIDES ━━━
    cat_num = 0
    for cat_key, cat_info in CATEGORIES.items():
        cat_num += 1
        cat_entries = by_cat.get(cat_key, [])
        cat_challenges = ch_by_cat.get(cat_key, [])
        color = cat_info['color']

        # Divider
        html += f'''
<div class="slide divider">
  <div class="rule" style="background:{color};"></div>
  <div class="div-num">{cat_num:02d}</div>
  <div class="si">
    <div class="div-kicker" style="color:{color};">CATEGORY {cat_num:02d}</div>
    <div class="div-title">{cat_info["ja"]}</div>
    <div class="div-desc">{cat_info["desc"]}。{len(cat_entries)}件のリサーチ事例を収録。</div>
'''
        if cat_challenges:
            html += '    <div class="div-challenges">\n'
            for ch in cat_challenges:
                sc = {'critical':'#C47D5A','high':'#8B7355','medium':'#A0896E','low':'#9CA3AF'}.get(ch.get('severity','medium'),'#9CA3AF')
                sl = SEVERITY_JA.get(ch.get('severity','medium'),'?')
                html += f'      <div class="div-ch"><span class="div-ch-sev" style="background:{sc};">{sl}</span><span class="tl-t"><strong>{ch["name_ja"]}</strong> &mdash; {truncate(ch.get("description",""),80)}</span></div>\n'
            html += '    </div>\n'
        html += f'  </div>\n  {ft(page)}\n</div>\n'
        page += 1

        # Cards
        html += f'''
<div class="slide">
  <div class="rule" style="background:{color};"></div>
  <div class="si">
    <div class="ph">
      <h2>{cat_info["ja"]}</h2>
      <div class="ph-sub">{len(cat_entries)}件の事例</div>
    </div>
    <div class="cg">
'''
        for e in cat_entries:
            trl = e.get('trl')
            org = truncate(e.get('source_org',''),12)
            etype = ENTRY_TYPE_JA.get(e.get('entry_type',''),'')
            html += f'      <div class="card">\n        <div class="card-top"><span class="b" style="background:{color};">{etype}</span>'
            if trl: html += f'<span class="b" style="background:{trl_color(trl)};">TRL{trl}</span>'
            if org: html += f'<span class="b-o">{org}</span>'
            html += f'</div>\n        <div class="card-title">{truncate(e["title"],38)}</div>\n'
            html += f'        <div class="card-desc">{truncate(e.get("summary",""),75)}</div>\n'
            mods = e.get('related_modules',[])
            if mods:
                html += '        <div class="card-foot">'
                for m in mods[:2]:
                    html += f'<span class="tag">{MODULES.get(m,{"ja":m}).get("ja",m)}</span>'
                html += '</div>\n'
            html += '      </div>\n'
        html += f'    </div>\n  </div>\n  {ft(page)}\n</div>\n'
        page += 1

    # ━━━ MODULE SLIDES ━━━
    for mk, mod in MODULES.items():
        ments = module_entries.get(mk, [])
        img_fmt, img_b64 = img_to_base64(mod.get('image',''))
        scored = sorted([(context_fit_score(e, mk), e) for e in ments], key=lambda x: x[0], reverse=True)
        featured = [e for _, e in scored[:2]]
        rest = [e for _, e in scored[2:]]

        html += f'''
<div class="slide">
  <div class="rule"></div>
  <div class="si">
    <div class="ph">
      <div class="ph-kicker">Module</div>
      <h2>{mod["ja"]}</h2>
      <div class="ph-sub">{mod["desc"]}</div>
    </div>
    <div class="mod-grid">
      <div class="mod-img">
'''
        if img_b64:
            html += f'        <img src="data:image/{img_fmt};base64,{img_b64}" alt="{mod["ja"]}">\n'
        html += f'        <div class="mod-img-cap">JAXA Space Life on the Moon &mdash; {mod.get("pdf_title","")}</div>\n      </div>\n      <div class="mod-right">\n'

        for fe in featured:
            cc = CATEGORIES.get(fe['category'],{}).get('color','#9CA3AF')
            cj = CATEGORIES.get(fe['category'],{}).get('ja','')
            trl = fe.get('trl')
            org = truncate(fe.get('source_org',''),15)
            etype = ENTRY_TYPE_JA.get(fe.get('entry_type',''),'')
            html += f'        <div class="mod-feat" style="border-color:{cc};">\n'
            html += f'          <h3>{truncate(fe["title"],38)}</h3>\n'
            html += f'          <p>{truncate(fe.get("summary",""),70)}</p>\n'
            html += f'          <div class="mod-feat-meta"><span class="b" style="background:{cc};">{cj}</span>'
            if trl: html += f'<span class="b" style="background:{trl_color(trl)};">TRL {trl}</span>'
            html += f'<span class="b-o">{etype}</span>'
            if org: html += f'<span class="b-o">{org}</span>'
            html += '</div>\n        </div>\n'

        if rest:
            html += f'        <div class="mod-rest">\n          <h4>OTHER RELATED &mdash; {len(rest)}件</h4>\n          <div class="mod-rest-list">\n'
            for re in rest[:8]:
                rc = CATEGORIES.get(re['category'],{}).get('color','#9CA3AF')
                rj = CATEGORIES.get(re['category'],{}).get('ja','')
                rtrl = re.get('trl')
                html += f'            <div class="mod-rest-item" style="--dot-c:{rc};"><span style="background:{rc};width:1mm;height:1mm;border-radius:50%;flex-shrink:0;margin-top:0.8mm;"></span><span><strong>{rj}</strong> {truncate(re["title"],22)}'
                if rtrl: html += f' TRL{rtrl}'
                html += '</span></div>\n'
            if len(rest) > 8:
                html += f'            <div class="mod-rest-item" style="color:var(--c-subtle);">+{len(rest)-8}件</div>\n'
            html += '          </div>\n        </div>\n'
        html += f'      </div>\n    </div>\n  </div>\n  {ft(page)}\n</div>\n'
        page += 1

    # ━━━ CLOSING ━━━
    html += f'''
<div class="slide cover">
  <div class="rule" style="background:var(--c-warm);"></div>
  <div class="si">
    <div class="c-kicker">Lunar Life Research Database</div>
    <div class="c-title" style="font-size:24pt;">月面生活リサーチDB</div>
    <div class="c-rule"></div>
    <div class="c-desc">
      本レポートはJAXA「Space Life on the Moon」企業向け資料をベースに、<br>
      月面生活のイメージをより具体的にするための世界中のリサーチを集積したものです。<br>
      追加のリサーチやアイディエーションにご活用ください。
    </div>
    <div class="c-meta">NPO法人ミラツク &mdash; {today}</div>
  </div>
</div>
'''

    html += '\n</body>\n</html>'
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Slides: {os.path.abspath(OUTPUT_PATH)} ({page} slides)')


if __name__ == '__main__':
    generate()
