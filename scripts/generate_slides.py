#!/usr/bin/env python3
"""Generate a landscape A4 slide-style HTML report for Lunar Life Research DB.

Design: Miratuku CI, presentation-grade quality.
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

ENTRY_TYPE_JA = {
    'technology': '技術', 'research': '研究', 'project': 'PJ',
    'concept': '概念', 'regulation': '規制', 'challenge': '課題', 'case_study': '事例',
}
SEVERITY_JA = {'critical': '深刻', 'high': '高', 'medium': '中', 'low': '低'}
SEVERITY_COLOR = {'critical': '#DC8766', 'high': '#B07256', 'medium': '#F0A671', 'low': '#CEA26F'}

MODULE_CONTEXT = {
    'private_room': {'primary_cats': ['sleep_habitat', 'entertainment', 'communication'],
        'keywords': ['睡眠','プライバシー','概日','照明','個室','居住','サーカディアン','ベッド','安眠','音響','住環境','休息']},
    'kitchen_dining': {'primary_cats': ['food', 'water', 'entertainment'],
        'keywords': ['食','調理','栄養','食事','料理','培養肉','昆虫','水耕','発酵','食文化','キッチン','食料','社交']},
    'laboratory': {'primary_cats': ['work_environment', 'medical', 'hygiene'],
        'keywords': ['実験','研究','分析','ラボ','科学','検査','宇宙服','EVA','探査','レゴリス','試料','機器']},
    'workspace': {'primary_cats': ['work_environment', 'communication'],
        'keywords': ['作業','オフィス','仕事','AR','MR','ロボティクス','遠隔','デジタルツイン','認知','タスク','会議','協働']},
    'medical_bay': {'primary_cats': ['hygiene', 'water', 'medical'],
        'keywords': ['衛生','入浴','シャワー','洗濯','洗浄','水','浄化','殺菌','清潔','循環','排水','廃棄物','無水']},
    'training_room': {'primary_cats': ['entertainment', 'exercise', 'communication'],
        'keywords': ['娯楽','レクリエーション','VR','ゲーム','映画','音楽','スクリーン','イベント','文化','芸術','マインドフルネス']},
    'courtyard': {'primary_cats': ['exercise', 'entertainment', 'sleep_habitat'],
        'keywords': ['運動','スポーツ','トレーニング','筋力','骨密度','フィットネス','緑','植物','庭','散歩','体操','身体']},
    'plantation': {'primary_cats': ['food', 'water', 'hygiene'],
        'keywords': ['植物','栽培','農業','作物','LED','水耕','エアロポニクス','藻類','野菜','収穫','光合成','バイオ','食料生産']},
}

def context_fit_score(entry, module_key):
    ctx = MODULE_CONTEXT.get(module_key, {})
    score = 0.0
    primary_cats = ctx.get('primary_cats', [])
    cat = entry.get('category', '')
    if cat in primary_cats:
        score += (3 - primary_cats.index(cat)) * 10
    keywords = ctx.get('keywords', [])
    text = ((entry.get('title', '') or '') + ' ' + (entry.get('summary', '') or '')).lower()
    score += sum(1 for kw in keywords if kw.lower() in text) * 5
    mods = entry.get('related_modules', [])
    if len(mods) > 0:
        score += 3.0 / len(mods)
    score += (entry.get('trl') or 0) * 0.3
    return score

def img_to_base64(filename):
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
  font-family: "Hiragino Kaku Gothic ProN", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #1a1a1a; background: #d8d0c8;
  font-feature-settings: "palt";
}

/* ── Slide frame ── */
.slide {
  width: 297mm; height: 210mm; background: #fff;
  position: relative; overflow: hidden; margin: 0 auto;
}
@media screen { .slide { margin: 10mm auto; box-shadow: 0 4px 24px rgba(0,0,0,0.15); } }
.si { padding: 16mm 22mm 20mm; height: 100%; display: flex; flex-direction: column; }

/* ── Accent bar ── */
.ab { position: absolute; top: 0; left: 0; right: 0; height: 3mm; }
.ab-grad { background: linear-gradient(90deg, #F0A671 0%, #DC8766 25%, #B07256 50%, #966D5E 75%, #7A4033 100%); }

/* ── Footer ── */
.sf {
  position: absolute; bottom: 7mm; left: 22mm; right: 22mm;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 6.5pt; color: #B09A8A; letter-spacing: 0.05em;
}

/* ── Cover ── */
.cover .si { justify-content: center; align-items: center; text-align: center; }
.cover-bg {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 80%, #F8CDAC18 0%, transparent 60%),
              radial-gradient(ellipse at 20% 20%, #F0A67110 0%, transparent 40%);
}
.c-title { font-size: 34pt; font-weight: 900; color: #783c28; letter-spacing: 0.15em; margin-bottom: 6mm; position: relative; }
.c-sub { font-size: 13pt; color: #966D5E; letter-spacing: 0.08em; margin-bottom: 5mm; position: relative; }
.c-desc { font-size: 10pt; color: #6b5c52; max-width: 200mm; line-height: 1.8; position: relative; margin-bottom: 12mm; }
.c-meta { font-size: 8.5pt; color: #B09A8A; position: relative; letter-spacing: 0.05em; }
.c-line { width: 40mm; height: 0.5px; background: #CEA26F; margin: 0 auto 8mm; position: relative; }

/* ── Page header ── */
.ph { margin-bottom: 6mm; }
.ph h2 { font-size: 18pt; font-weight: 800; letter-spacing: 0.04em; }
.ph-sub { font-size: 9pt; color: #6b5c52; margin-top: 1.5mm; }
.ph-line { width: 20mm; height: 1.5px; margin-top: 3mm; }

/* ── Section divider ── */
.divider .si { justify-content: center; padding-left: 32mm; }
.div-num { font-size: 64pt; font-weight: 900; opacity: 0.07; position: absolute; right: 28mm; top: 50%; transform: translateY(-50%); }
.div-cat { font-size: 10pt; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 2mm; }
.div-title { font-size: 32pt; font-weight: 900; margin-bottom: 5mm; letter-spacing: 0.05em; }
.div-desc { font-size: 11pt; color: #6b5c52; max-width: 165mm; line-height: 1.7; }
.div-challenges { margin-top: 8mm; max-width: 210mm; }
.div-ch { display: flex; align-items: flex-start; gap: 3mm; margin-bottom: 2.5mm; font-size: 8.5pt; line-height: 1.5; }
.div-ch-badge { padding: 0.5mm 2.5mm; border-radius: 1.5mm; font-size: 6.5pt; font-weight: 700; color: #fff; flex-shrink: 0; margin-top: 0.5mm; }

/* ── Info box ── */
.ib { border-radius: 3mm; padding: 4mm; background: #fdfbf9; }
.ib-border { border: 1px solid #ebe4dc; }
.ib-accent { border-left: 3px solid; }
.ib h3 { font-size: 10pt; font-weight: 700; color: #783c28; margin-bottom: 2mm; }
.ib h4 { font-size: 8.5pt; font-weight: 700; color: #783c28; margin-bottom: 1.5mm; }
.ib p, .ib div.t { font-size: 7.5pt; line-height: 1.6; color: #4a4a4a; }
.ib table { width: 100%; font-size: 7.5pt; border-collapse: collapse; }
.ib td { padding: 1.5mm 1mm; border-bottom: 1px solid #f0ebe5; vertical-align: top; }
.ib td:first-child { font-weight: 600; color: #783c28; width: 32%; white-space: nowrap; }
.ib .hi { color: #DC8766; font-weight: 700; }

/* ── Timeline ── */
.tl-row { display: flex; align-items: flex-start; gap: 3mm; margin-bottom: 2mm; }
.tl-year { font-size: 9pt; font-weight: 800; width: 12mm; text-align: right; flex-shrink: 0; }
.tl-dot { width: 2.5mm; height: 2.5mm; border-radius: 50%; flex-shrink: 0; margin-top: 1.5mm; border: 1px solid #fff; }
.tl-text { font-size: 7.5pt; color: #4a4a4a; line-height: 1.5; flex: 1; }

/* ── Cards (5-col grid) ── */
.cg { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3mm; flex: 1; }
.card {
  border-radius: 3mm; padding: 3mm; display: flex; flex-direction: column;
  background: #fdfbf9; border: 1px solid #ebe4dc; overflow: hidden;
}
.card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-badges { display: flex; align-items: center; gap: 1.5mm; margin-bottom: 1.5mm; flex-wrap: wrap; }
.card-title { font-size: 8.5pt; font-weight: 700; line-height: 1.3; margin-bottom: 1.5mm; }
.card-desc { font-size: 7pt; color: #4a4a4a; line-height: 1.4; flex: 1; }
.card-foot { margin-top: auto; padding-top: 1.5mm; display: flex; flex-wrap: wrap; gap: 1mm; }

/* ── Badges ── */
.b { display: inline-block; padding: 0.4mm 2mm; border-radius: 1.5mm; font-size: 6.5pt; font-weight: 700; color: #fff; white-space: nowrap; }
.b-s { font-size: 5.5pt; padding: 0.3mm 1.5mm; }
.b-o { display: inline-block; padding: 0.3mm 2mm; border-radius: 1.5mm; font-size: 6.5pt; font-weight: 600; border: 0.5px solid; background: transparent; white-space: nowrap; }
.mt { display: inline-block; padding: 0.3mm 1.5mm; border-radius: 1mm; font-size: 5.5pt; background: #f0ebe5; color: #6b5c52; white-space: nowrap; }

/* ── Module slide ── */
.mod-layout { display: grid; grid-template-columns: 44% 1fr; gap: 5mm; height: 148mm; overflow: hidden; }
.mod-img { position: relative; border-radius: 3mm; overflow: hidden; background: #f0ebe5; }
.mod-img img { width: 100%; height: 100%; object-fit: cover; object-position: center 40%; }
.mod-img-label {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(transparent, rgba(26,26,26,0.7));
  color: #fff; padding: 6mm 3mm 2.5mm; font-size: 6.5pt; letter-spacing: 0.03em;
}
.mod-right { display: flex; flex-direction: column; gap: 2.5mm; height: 100%; overflow: hidden; }
.mod-feat {
  border-left: 3px solid; border-radius: 3mm; padding: 3.5mm; background: #fdfbf9;
}
.mod-feat-title { font-size: 9.5pt; font-weight: 700; line-height: 1.25; margin-bottom: 1mm; }
.mod-feat-desc { font-size: 7pt; color: #4a4a4a; line-height: 1.4; }
.mod-feat-meta { display: flex; gap: 1.5mm; align-items: center; margin-top: 1.5mm; flex-wrap: wrap; }
.mod-rest {
  flex: 1; border: 1px solid #ebe4dc; border-radius: 3mm; padding: 2.5mm; background: #fdfbf9; overflow: hidden;
}
.mod-rest h4 { font-size: 7pt; font-weight: 600; color: #B09A8A; margin-bottom: 1.5mm; letter-spacing: 0.03em; }
.mod-rest-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8mm; }
.mod-rest-item { display: flex; align-items: baseline; gap: 1mm; font-size: 6pt; line-height: 1.3; }
.mod-rest-dot { width: 1.2mm; height: 1.2mm; border-radius: 50%; flex-shrink: 0; margin-top: 0.8mm; }
"""

    # ─── HTML ───
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>月面生活リサーチレポート</title>
<style>{css}</style>
</head>
<body>
"""

    page = 1
    def ft(p):
        return f'<div class="sf"><span>NPO法人ミラツク / MIRA TUKU</span><span>月面生活リサーチレポート</span><span>{p}</span></div>'

    # ━━━ 1. COVER ━━━
    html += f"""
<div class="slide cover">
  <div class="ab ab-grad"></div>
  <div class="cover-bg"></div>
  <div class="si">
    <div class="c-title">月面生活リサーチレポート</div>
    <div class="c-line"></div>
    <div class="c-sub">Space Life on the Moon</div>
    <div class="c-desc">
      月面基地での暮らしに必要な技術と知見を<br>
      世界中の研究・プロジェクトから集め、整理したレポート
    </div>
    <div class="c-meta">NPO法人ミラツク &nbsp;&mdash;&nbsp; {today}</div>
  </div>
</div>
"""
    page += 1

    # ━━━ 2. LUNAR ENVIRONMENT ━━━
    html += f"""
<div class="slide">
  <div class="ab ab-grad"></div>
  <div class="si">
    <div class="ph">
      <h2 style="color:#783c28;">月面環境</h2>
      <div class="ph-sub">人が暮らすために理解すべき月の条件</div>
      <div class="ph-line" style="background:#783c28;"></div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:5mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div class="ib ib-border" style="flex:none;">
          <h3>基本物理環境</h3>
          <table>
            <tr><td>重力</td><td>地球の1/6（約1.62 m/s²）</td></tr>
            <tr><td>大気</td><td>ほぼ真空（10⁻¹² Pa）— 保圧ハビタット必須</td></tr>
            <tr><td>日中温度</td><td>+127°C（14.75日間継続）</td></tr>
            <tr><td>夜間温度</td><td>&minus;173°C（14.75日間継続）</td></tr>
            <tr><td>1日の長さ</td><td>29.5地球日（約708時間）</td></tr>
            <tr><td>地球との距離</td><td>約384,400km（通信遅延 片道1.3秒）</td></tr>
          </table>
        </div>
        <div class="ib ib-accent" style="border-color:#CEA26F; flex:1;">
          <h3 style="color:#CEA26F;">水氷資源</h3>
          <div class="t">月の南極・北極の永久影地帯に数百万トンの水氷が賦存すると推定。飲料水・農業用水・ロケット燃料（水素+酸素）の原料として、月面基地の立地を決定づける最重要資源。NASAのVIPERローバやPRIME-1実験で採掘技術の実証が進行中。</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:3mm;">
        <div class="ib ib-accent" style="border-color:#DC8766;">
          <h3 style="color:#DC8766;">宇宙放射線</h3>
          <div class="t">地球のような磁気圏が存在せず、銀河宇宙線と太陽粒子線が直接到達。長期滞在では発がんリスク・中枢神経障害が懸念される。居住モジュールの遮蔽設計やレゴリスを利用したシールド構造が不可欠。太陽フレア時は緊急退避が必要。</div>
        </div>
        <div class="ib ib-accent" style="border-color:#B07256;">
          <h3 style="color:#B07256;">月面レゴリス（ダスト）</h3>
          <div class="t">月面を覆う微細な砂塵は鋭角的で、静電気により帯電しあらゆる表面に付着する。ナノスケール鉄が活性酸素を生成し、吸入すると肺・中枢神経に障害リスク。アポロ飛行士も鼻腔充血・くしゃみを経験。推奨曝露限界 0.3 mg/m³。</div>
        </div>
        <div class="ib ib-accent" style="border-color:#966D5E; flex:1;">
          <h3 style="color:#966D5E;">心理的課題</h3>
          <div class="t">閉鎖空間での長期滞在による心理的負荷。対人摩擦、単調さ、地球との隔絶感、概日リズムの乱れ（29.5日周期）が重なり、メンタルヘルスの維持が生命維持と同等に重要。ISS・南極越冬隊の知見が基盤となる。</div>
        </div>
      </div>
    </div>
  </div>
  {ft(page)}
</div>
"""
    page += 1

    # ━━━ 3. HISTORY TIMELINE ━━━
    milestones = [
        ('1959', '#F0A671', 'Luna 2 — 人類初の月面到達（衝突）', ''),
        ('1966', '#F0A671', 'Luna 9 — 初の軟着陸、月面写真の撮影に成功', ''),
        ('1969', '#DC8766', 'Apollo 11 — 人類初の月面歩行（アームストロング、オルドリン）', ''),
        ('1972', '#DC8766', 'Apollo 17 — 最後の有人月面ミッション。以後50年以上、人類は月面に立っていない', ''),
        ('2007-13', '#B07256', '月面探査の国際化 — かぐや（日）、Chandrayaan-1（印）、Chang\'e-1~3（中）', ''),
        ('2019', '#B07256', 'Chang\'e 4 — 人類初の月の裏側への着陸に成功', ''),
        ('2023', '#966D5E', 'Chandrayaan-3 南極着陸成功 / SLIM精密着陸（日本）', ''),
        ('2025', '#966D5E', '商用月面着陸の幕開け — Firefly Blue Ghost成功、IM-2南極探査', ''),
        ('2026', '#7A4033', 'Artemis II 月周回飛行完了。商用着陸が加速', ''),
        ('2028', '#7A4033', 'Artemis IV — Apollo 17以来の有人月面着陸（予定）', 'hi'),
        ('2030s', '#7A4033', 'Artemis Base Camp建設、Lunar Cruiser投入、ILRS基本モデル完成へ', ''),
    ]
    html += f"""
<div class="slide">
  <div class="ab ab-grad"></div>
  <div class="si">
    <div class="ph">
      <h2 style="color:#783c28;">月面基地に至る人類の歩み</h2>
      <div class="ph-sub">1959年の最初の月面到達から、2030年代の恒久基地建設へ</div>
      <div class="ph-line" style="background:#783c28;"></div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8mm; flex:1; align-content:start;">
"""
    half = 6
    for col, sl in enumerate([milestones[:half], milestones[half:]]):
        html += '      <div style="display:flex; flex-direction:column; gap:0;">\n'
        for yr, color, text, cls in sl:
            tcls = ' class="hi"' if cls == 'hi' else ''
            html += f"""        <div class="tl-row">
          <div class="tl-year" style="color:{color};">{yr}</div>
          <div class="tl-dot" style="background:{color};"></div>
          <div class="tl-text"{tcls}>{text}</div>
        </div>\n"""
        html += '      </div>\n'
    html += f"""    </div>
  </div>
  {ft(page)}
</div>
"""
    page += 1

    # ━━━ 4. ROADMAPS + PROJECTS (merged) ━━━
    html += f"""
<div class="slide">
  <div class="ab ab-grad"></div>
  <div class="si">
    <div class="ph">
      <h2 style="color:#783c28;">各国のロードマップと主要プロジェクト</h2>
      <div class="ph-sub">政府宇宙機関と民間企業が並走する月面開発。2025年は商用着陸が本格化し、2028年には半世紀ぶりの有人着陸が予定されている</div>
      <div class="ph-line" style="background:#783c28;"></div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:3mm; flex:1;">
      <div style="display:flex; flex-direction:column; gap:2.5mm;">
        <div class="ib ib-accent" style="border-color:#DC8766; flex:1;">
          <h4 style="color:#DC8766;">米国 — Artemis計画</h4>
          <div class="t">
            <strong>2026</strong> Artemis II 月周回（完了）<br>
            <strong>2028</strong> <span class="hi">Artemis IV 有人着陸</span><br>
            <strong>2029+</strong> 月面地表基地建設へ転換
          </div>
        </div>
        <div class="ib ib-border" style="flex:1;">
          <h4>SpaceX Starship HLS</h4>
          <div class="t">NASA主契約。Block 3仕様で2028年初着陸予定</div>
        </div>
        <div class="ib ib-border" style="flex:1;">
          <h4>Blue Origin Blue Moon</h4>
          <div class="t">最大4名乗員、30日滞在対応の有人着陸機</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2.5mm;">
        <div class="ib ib-accent" style="border-color:#B07256; flex:1;">
          <h4 style="color:#B07256;">中国 — ILRS</h4>
          <div class="t">
            <strong>2028-29</strong> Chang'e-7/8<br>
            <strong>2035</strong> <span class="hi">ILRS基本モデル完成</span><br>
            17ヶ国・50+研究機関が参加
          </div>
        </div>
        <div class="ib ib-accent" style="border-color:#966D5E; flex:1;">
          <h4 style="color:#966D5E;">日本 — Lunar Cruiser</h4>
          <div class="t">
            Toyota共同開発の与圧ローバ<br>
            水素燃料電池・航続10,000km<br>
            <strong>2030s初</strong> 月面投入・Artemis統合
          </div>
        </div>
        <div class="ib ib-accent" style="border-color:#CEA26F; flex:1;">
          <h4 style="color:#CEA26F;">欧州 — ESA Moonlight</h4>
          <div class="t">月衛星通信+測位 5衛星網<br><strong>2030</strong> 完全運用開始</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2.5mm;">
        <div class="ib ib-border" style="flex:none;">
          <h4>商用月面着陸（CLPS）</h4>
          <div class="t" style="font-size:7pt;">
            <strong>Intuitive Machines</strong> IM-2南極探査<br>
            <strong>Firefly</strong> Blue Ghost成功（2025.3）<br>
            <strong>Astrobotic</strong> Griffin（南極、2026）<br>
            <strong>ispace</strong> APEX 1.0（裏側、2026）
          </div>
        </div>
        <div class="ib ib-border" style="flex:1;">
          <h4>基地建設技術</h4>
          <div class="t" style="font-size:7pt;">
            <strong>ICON Project Olympus</strong><br>レーザー月壌溶融3D印刷（NASA $57M契約）<br><br>
            <strong>Sierra Space LIFE</strong><br>拡張式高圧ハビタット
          </div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:2.5mm;">
        <div class="ib ib-border" style="flex:none;">
          <h4>インド — ISRO</h4>
          <div class="t">Chandrayaan-3成功（2023）<br><strong>2040</strong> 有人月面着陸目標</div>
        </div>
        <div class="ib ib-border" style="flex:none;">
          <h4>ロシア — Roscosmos</h4>
          <div class="t">Luna-27~30 段階的探査<br>ILRS共同参加（中国と連携）</div>
        </div>
        <div class="ib ib-border" style="flex:none;">
          <h4>UAE・韓国</h4>
          <div class="t">UAE: Gateway参加宣言<br>韓国: 2032年着陸機ミッション</div>
        </div>
        <div class="ib ib-border" style="flex:1;">
          <h4>資源探査・ISRU</h4>
          <div class="t">NASA PRIME-1 水氷採掘実験<br>ILRS科学拠点（2035年）</div>
        </div>
      </div>
    </div>
  </div>
  {ft(page)}
</div>
"""
    page += 1

    # ━━━ CATEGORY SLIDES ━━━
    cat_num = 0
    for cat_key, cat_info in CATEGORIES.items():
        cat_num += 1
        cat_entries = by_cat.get(cat_key, [])
        cat_challenges = ch_by_cat.get(cat_key, [])
        color = cat_info['color']

        # Divider slide
        html += f"""
<div class="slide divider">
  <div class="ab" style="background:{color};"></div>
  <div class="div-num" style="color:{color};">{cat_num:02d}</div>
  <div class="si">
    <div class="div-cat" style="color:{color};">CATEGORY {cat_num:02d}</div>
    <div class="div-title" style="color:{color};">{cat_info['ja']}</div>
    <div class="div-desc">{cat_info['desc']}<br>{len(cat_entries)}件のエントリ</div>
"""
        if cat_challenges:
            html += '    <div class="div-challenges">\n'
            html += '      <div style="font-size:8.5pt;font-weight:700;color:#6b5c52;margin-bottom:2mm;">月面環境の主要課題</div>\n'
            for ch in cat_challenges:
                sc = SEVERITY_COLOR.get(ch.get('severity', 'medium'), '#999')
                sl = SEVERITY_JA.get(ch.get('severity', 'medium'), '?')
                html += f'      <div class="div-ch"><span class="div-ch-badge" style="background:{sc};">{sl}</span><span style="color:#4a4a4a;"><strong>{ch["name_ja"]}</strong> — {truncate(ch.get("description",""), 80)}</span></div>\n'
            html += '    </div>\n'
        html += f'  </div>\n  {ft(page)}\n</div>\n'
        page += 1

        # Cards slide
        html += f"""
<div class="slide">
  <div class="ab" style="background:{color};"></div>
  <div class="si">
    <div class="ph">
      <h2 style="color:{color};">{cat_info['ja']}</h2>
      <div class="ph-sub">事例一覧 — {len(cat_entries)}件</div>
      <div class="ph-line" style="background:{color};"></div>
    </div>
    <div class="cg">
"""
        for e in cat_entries:
            trl = e.get('trl')
            org = truncate(e.get('source_org', ''), 10) or ''
            etype = ENTRY_TYPE_JA.get(e.get('entry_type', ''), '')
            mods = e.get('related_modules', [])

            html += f'      <div class="card">\n        <div class="card-badges">\n          <span class="b b-s" style="background:{color};">{etype}</span>\n'
            if trl:
                html += f'          <span class="b b-s" style="background:{trl_color(trl)};">TRL{trl}</span>\n'
            if org:
                html += f'          <span class="b-o b-s" style="border-color:#B09A8A;color:#B09A8A;">{org}</span>\n'
            html += f'        </div>\n        <div class="card-title">{truncate(e["title"], 40)}</div>\n'
            html += f'        <div class="card-desc">{truncate(e.get("summary", ""), 80)}</div>\n'
            html += '        <div class="card-foot">\n'
            for m in mods[:3]:
                html += f'          <span class="mt">{MODULES.get(m, {"ja": m}).get("ja", m)}</span>\n'
            html += '        </div>\n      </div>\n'

        html += f'    </div>\n  </div>\n  {ft(page)}\n</div>\n'
        page += 1

    # ━━━ MODULE SLIDES ━━━
    for mk, mod in MODULES.items():
        ments = module_entries.get(mk, [])
        img_fmt, img_b64 = img_to_base64(mod.get('image', ''))

        scored = [(context_fit_score(e, mk), e) for e in ments]
        scored.sort(key=lambda x: x[0], reverse=True)
        featured = [e for _, e in scored[:2]]
        rest = [e for _, e in scored[2:]]

        html += f"""
<div class="slide">
  <div class="ab ab-grad"></div>
  <div class="si">
    <div class="ph">
      <h2 style="color:#783c28;">{mod['ja']}</h2>
      <div class="ph-sub">{mod['desc']} — {len(ments)}件の関連事例</div>
      <div class="ph-line" style="background:#783c28;"></div>
    </div>
    <div class="mod-layout">
      <div class="mod-img">
"""
        if img_b64:
            html += f'        <img src="data:image/{img_fmt};base64,{img_b64}" alt="{mod["ja"]}">\n'
        html += f'        <div class="mod-img-label">JAXA「Space Life on the Moon」— {mod.get("pdf_title", mod["ja"])}</div>\n'
        html += '      </div>\n      <div class="mod-right">\n'

        for fe in featured:
            cat_c = CATEGORIES.get(fe['category'], {}).get('color', '#999')
            cat_j = CATEGORIES.get(fe['category'], {}).get('ja', '')
            trl = fe.get('trl')
            org = truncate(fe.get('source_org', ''), 15) or ''
            etype = ENTRY_TYPE_JA.get(fe.get('entry_type', ''), '')
            html += f'        <div class="mod-feat" style="border-color:{cat_c};">\n'
            html += f'          <div class="mod-feat-title" style="color:{cat_c};">{truncate(fe["title"], 40)}</div>\n'
            html += f'          <div class="mod-feat-desc">{truncate(fe.get("summary", ""), 75)}</div>\n'
            html += f'          <div class="mod-feat-meta"><span class="b b-s" style="background:{cat_c};">{cat_j}</span>'
            if trl:
                html += f'<span class="b b-s" style="background:{trl_color(trl)};">TRL {trl}</span>'
            html += f'<span class="b-o b-s" style="border-color:#B09A8A;color:#B09A8A;">{etype}</span>'
            if org:
                html += f'<span style="font-size:6pt;color:#B09A8A;">{org}</span>'
            html += '</div>\n        </div>\n'

        if rest:
            html += f'        <div class="mod-rest">\n          <h4>その他の関連事例（{len(rest)}件）</h4>\n          <div class="mod-rest-grid">\n'
            for re in rest[:8]:
                rc = CATEGORIES.get(re['category'], {}).get('color', '#999')
                rj = CATEGORIES.get(re['category'], {}).get('ja', '')
                rtrl = re.get('trl')
                rtrl_s = f' TRL{rtrl}' if rtrl else ''
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:{rc};"></span><span><strong>{rj}</strong> {truncate(re["title"], 22)}{rtrl_s}</span></div>\n'
            if len(rest) > 8:
                html += f'            <div class="mod-rest-item"><span class="mod-rest-dot" style="background:#ccc;"></span><span style="color:#B09A8A;">他 {len(rest)-8}件</span></div>\n'
            html += '          </div>\n        </div>\n'

        html += f'      </div>\n    </div>\n  </div>\n  {ft(page)}\n</div>\n'
        page += 1

    # ━━━ CLOSING ━━━
    html += f"""
<div class="slide cover">
  <div class="ab ab-grad"></div>
  <div class="cover-bg"></div>
  <div class="si">
    <div class="c-title" style="font-size:26pt;">月面生活リサーチDB</div>
    <div class="c-line"></div>
    <div class="c-sub" style="font-size:11pt;">Lunar Life Research Database</div>
    <div class="c-desc" style="margin-top:5mm;">
      本レポートはJAXA「Space Life on the Moon」企業向け資料をベースに、<br>
      月面生活のイメージをより具体的にするための世界中のリサーチを集積したものです。<br>
      追加のリサーチやアイディエーションにご活用ください。
    </div>
    <div class="c-meta">NPO法人ミラツク / MIRA TUKU &nbsp;&mdash;&nbsp; {today}</div>
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
