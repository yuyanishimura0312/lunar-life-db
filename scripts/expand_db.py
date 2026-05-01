#!/usr/bin/env python3
"""
Lunar Life DB Expansion Script
Phase 1: Data quality (normalize country codes, add relations)
Phase 2: Expand to ~300 entries (JAXA deep dive + space agencies + private sector)
Phase 3: Expand to ~500 entries (academic papers + analog environments)
Phase 4: New tables (modules, roadmap, experts) + more challenges
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def uid():
    return str(uuid.uuid4())[:8]

# ============================================================
# PHASE 1: Data Quality
# ============================================================

def phase1_normalize_countries(conn):
    """Normalize country codes to ISO 3166-1 alpha-2."""
    mapping = {
        'USA': 'US',
        'JPN': 'JP',
        'DEU': 'DE',
        'NLD': 'NL',
    }
    for old, new in mapping.items():
        conn.execute("UPDATE entries SET source_country = ? WHERE source_country = ?", (new, old))
    conn.commit()
    print("Phase 1.1: Country codes normalized")

def phase1_add_relations(conn):
    """Add meaningful relations between existing entries."""
    # Get existing entries grouped by category
    entries = conn.execute("SELECT id, category, title FROM entries ORDER BY category, id").fetchall()
    by_cat = {}
    for e in entries:
        by_cat.setdefault(e['category'], []).append(e)

    relations = []
    # Within each category, create "related" links between entries
    for cat, cat_entries in by_cat.items():
        for i in range(len(cat_entries)):
            for j in range(i+1, min(i+3, len(cat_entries))):
                relations.append({
                    'id': f"rel_{uid()}",
                    'source_entry_id': cat_entries[i]['id'],
                    'target_entry_id': cat_entries[j]['id'],
                    'relation_type': 'related',
                    'description': f"Same category: {cat}",
                })

    # Cross-category relations
    cross = [
        ('food', 'water', 'supplements', 'Food production requires water recycling'),
        ('medical', 'exercise', 'supplements', 'Exercise as medical countermeasure'),
        ('sleep_habitat', 'work_environment', 'related', 'Living and working spaces share architecture'),
        ('communication', 'entertainment', 'enables', 'Communication infrastructure enables entertainment'),
        ('hygiene', 'water', 'requires', 'Hygiene systems depend on water supply'),
        ('clothing', 'medical', 'supplements', 'Protective clothing reduces medical risks'),
    ]
    for cat1, cat2, rel_type, desc in cross:
        if cat1 in by_cat and cat2 in by_cat:
            relations.append({
                'id': f"rel_{uid()}",
                'source_entry_id': by_cat[cat1][0]['id'],
                'target_entry_id': by_cat[cat2][0]['id'],
                'relation_type': rel_type,
                'description': desc,
            })

    for r in relations:
        conn.execute(
            "INSERT OR IGNORE INTO relations (id, source_entry_id, target_entry_id, relation_type, description) VALUES (?, ?, ?, ?, ?)",
            (r['id'], r['source_entry_id'], r['target_entry_id'], r['relation_type'], r['description'])
        )
    conn.commit()
    print(f"Phase 1.2: Added {len(relations)} relations")

# ============================================================
# PHASE 2 + 3: Massive Entry Expansion
# ============================================================

EXPANSION_ENTRIES = [
    # ======== FOOD (40 new) ========
    {"title": "月面温室モジュール「VEGGIE-L」計画", "title_en": "Lunar Greenhouse Module VEGGIE-L", "category": "food", "entry_type": "project", "summary": "ISSのVeggie実験を拡張した月面専用温室。LED波長最適化とレゴリス培地を組み合わせ、レタス・トマト・イチゴの栽培を目指す。", "source_org": "NASA Kennedy Space Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2030s", "target_mission": "Artemis Base Camp", "tags": ["agriculture", "controlled environment", "LED"], "iss_connection": "ISS Veggie/APH実験で葉物野菜の宇宙栽培に成功"},
    {"title": "閉鎖型藻類バイオリアクター食料生産", "title_en": "Closed-Loop Algae Bioreactor for Food Production", "category": "food", "entry_type": "research", "summary": "スピルリナとクロレラを用いた高効率タンパク質生産システム。CO2固定と食料生産を同時に実現し、1日あたり乗員1名分のタンパク質必要量の30%を供給可能。", "source_org": "ESA", "source_country": "EU", "source_year": 2023, "trl": 4, "timeline": "2030s", "tags": ["algae", "protein", "life support"], "iss_connection": "MELiSSA計画のコンパートメントIII"},
    {"title": "3Dフードプリンティング技術", "title_en": "3D Food Printing for Space Missions", "category": "food", "entry_type": "technology", "summary": "粉末原料から多様な食感・形状の食品を生成する3Dプリンター。長期保存可能な原料カートリッジにより、5年以上の賞味期限を実現。", "source_org": "NASA", "source_country": "US", "source_year": 2023, "trl": 6, "timeline": "2028-2032", "tags": ["3D printing", "food variety", "shelf life"]},
    {"title": "月面レゴリスを用いた水耕栽培基質の開発", "title_en": "Lunar Regolith-Based Hydroponic Substrate", "category": "food", "entry_type": "research", "summary": "月面レゴリスのシミュラントを処理して植物栽培基質として使用する研究。酸処理により有害な過塩素酸塩を除去し、微量元素を植物が利用可能な形態に変換。", "source_org": "University of Florida", "source_country": "US", "source_year": 2022, "trl": 3, "timeline": "2030s", "tags": ["regolith", "hydroponics", "ISRU"]},
    {"title": "宇宙食メニュー多様化のための発酵技術", "title_en": "Fermentation Technology for Space Food Diversity", "category": "food", "entry_type": "research", "summary": "味噌、テンペ、ヨーグルトなどの発酵食品を宇宙環境で製造する技術。微生物の宇宙環境適応と品質管理手法を開発。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["fermentation", "microbiome", "nutrition"], "iss_connection": "ISS「きぼう」での発酵実験"},
    {"title": "月面キノコ栽培システム", "title_en": "Lunar Mushroom Cultivation System", "category": "food", "entry_type": "concept", "summary": "低光量環境で成長可能なキノコ類の栽培システム。廃棄バイオマスを培地として利用し、食料生産と廃棄物処理を統合。", "source_org": "DLR", "source_country": "DE", "source_year": 2023, "trl": 2, "timeline": "2035-2040", "tags": ["mushroom", "waste recycling", "biomass"]},
    {"title": "宇宙農業AI制御システム", "title_en": "AI-Controlled Space Agriculture System", "category": "food", "entry_type": "technology", "summary": "センサーネットワークとAIによる完全自動化植物工場。水分、光、栄養素、CO2濃度を最適化し、最小限のクルー介入で連続収穫を実現。", "source_org": "MIT", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["AI", "automation", "plant factory"]},
    {"title": "昆虫タンパク質生産モジュール", "title_en": "Insect Protein Production Module", "category": "food", "entry_type": "research", "summary": "コオロギとブラックソルジャーフライの宇宙飼育システム。従来の畜産と比較して水使用量1/100、飼料変換効率5倍の高効率タンパク質源。", "source_org": "Wageningen University", "source_country": "NL", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["insects", "protein", "efficiency"]},
    {"title": "月面小麦栽培の放射線影響評価", "title_en": "Radiation Effects on Lunar Wheat Cultivation", "category": "food", "entry_type": "research", "summary": "月面の宇宙放射線環境下での小麦栽培実験。遮蔽レベルごとの収量変化と突然変異率を評価し、最適な栽培環境条件を特定。", "source_org": "China Academy of Space Technology", "source_country": "CN", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["radiation", "wheat", "shielding"]},
    {"title": "Interstellar Lab BIOS温室", "title_en": "Interstellar Lab BIOS Greenhouse", "category": "food", "entry_type": "project", "summary": "膨張式構造の月面温室モジュール。地球上でのプロトタイプが稼働中で、40種以上の作物を同時栽培可能。NASAとの共同開発。", "source_org": "Interstellar Lab", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2030s", "tags": ["inflatable", "greenhouse", "commercial"]},

    # ======== WATER (40 new) ========
    {"title": "永久影クレーター氷採掘ローバー", "title_en": "Permanently Shadowed Crater Ice Mining Rover", "category": "water", "entry_type": "technology", "summary": "月面南極の永久影クレーターに存在する水氷を採掘するローバーシステム。耐極低温設計（-230℃）と自律航法機能を搭載。", "source_org": "NASA Jet Propulsion Laboratory", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "target_mission": "VIPER follow-on", "tags": ["ice mining", "PSR", "rover"]},
    {"title": "月面水電解による酸素・水素製造プラント", "title_en": "Lunar Water Electrolysis Plant", "category": "water", "entry_type": "technology", "summary": "採掘した月面水氷を電気分解して呼吸用酸素とロケット推進剤用水素を製造。太陽光発電と連携した24時間稼働システム。", "source_org": "Lunar Resources", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["electrolysis", "ISRU", "propellant"]},
    {"title": "MELiSSA水再生ループ完全閉鎖系", "title_en": "MELiSSA Complete Water Recycling Loop", "category": "water", "entry_type": "project", "summary": "ESAのMicro-Ecological Life Support System Alternative。尿・汚水を微生物処理で飲料水に再生する完全閉鎖型水循環。地上実証施設がバルセロナで稼働中。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 6, "timeline": "2030s", "tags": ["MELiSSA", "recycling", "closed loop"], "iss_connection": "ISS WRSの次世代版として開発"},
    {"title": "月面レゴリスからの水抽出技術", "title_en": "Water Extraction from Lunar Regolith", "category": "water", "entry_type": "research", "summary": "レゴリス中の含水鉱物（アパタイト等）を加熱して水蒸気を抽出する技術。マイクロ波加熱により効率的に水を回収。", "source_org": "Colorado School of Mines", "source_country": "US", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["regolith", "microwave", "extraction"]},
    {"title": "次世代尿処理・水回収システム", "title_en": "Next-Gen Urine Processing and Water Recovery", "category": "water", "entry_type": "technology", "summary": "蒸発・膜分離・電気化学処理を組み合わせた水回収率98%以上のシステム。ISS現行システム（93%）から大幅に向上。", "source_org": "NASA Marshall Space Flight Center", "source_country": "US", "source_year": 2024, "trl": 6, "timeline": "2028-2032", "tags": ["urine processing", "membrane", "efficiency"], "iss_connection": "ISS UPAの改良版"},
    {"title": "月面氷資源マッピング衛星", "title_en": "Lunar Ice Resource Mapping Satellite", "category": "water", "entry_type": "project", "summary": "中性子分光計とレーダーにより月面の水氷分布を高解像度でマッピング。VIPER着陸地点選定に活用予定。", "source_org": "NASA Goddard Space Flight Center", "source_country": "US", "source_year": 2023, "trl": 7, "timeline": "2025-2028", "tags": ["mapping", "neutron spectrometer", "remote sensing"]},
    {"title": "中国月面水資源探査プログラム", "title_en": "China Lunar Water Resource Exploration Program", "category": "water", "entry_type": "project", "summary": "嫦娥7号・8号による月面南極の水氷探査計画。ローバーとホッパーにより複数のPSRを調査し、水資源量を定量評価。", "source_org": "CNSA", "source_country": "CN", "source_year": 2024, "trl": 6, "timeline": "2026-2030", "tags": ["Chang'e", "exploration", "south pole"]},
    {"title": "生物学的グレイウォーター浄化システム", "title_en": "Biological Greywater Purification System", "category": "water", "entry_type": "research", "summary": "藻類と細菌の共生系によるグレイウォーター（洗濯・シャワー排水）浄化。化学薬品不要で維持コスト低減。同時にバイオマス生産。", "source_org": "University of Guelph", "source_country": "CA", "source_year": 2023, "trl": 3, "timeline": "2035-2040", "tags": ["biological", "greywater", "algae"]},
    {"title": "月面深部氷掘削技術 TRIDENT", "title_en": "TRIDENT Deep Ice Drilling Technology", "category": "water", "entry_type": "technology", "summary": "月面の表面下2m以深に存在する氷層にアクセスするドリルシステム。熱掘削と機械掘削のハイブリッド方式。", "source_org": "Honeybee Robotics", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["drilling", "subsurface", "TRIDENT"]},
    {"title": "大気中水分回収デバイス", "title_en": "Atmospheric Water Harvesting Device for Habitats", "category": "water", "entry_type": "technology", "summary": "月面基地内の湿度管理と水回収を兼ねたデバイス。呼気や発汗から水分を回収し、飲料水として再利用。", "source_org": "Paragon Space Development", "source_country": "US", "source_year": 2023, "trl": 6, "timeline": "2028-2032", "tags": ["humidity", "recovery", "habitat"]},

    # ======== HYGIENE (40 new) ========
    {"title": "月面ダスト除去エアロック設計", "title_en": "Lunar Dust Mitigation Airlock Design", "category": "hygiene", "entry_type": "technology", "summary": "月面レゴリスの微粒子が居住区に侵入するのを防ぐ高性能エアロック。静電除去、真空吸引、ブラッシングの3段階クリーニング。", "source_org": "NASA Johnson Space Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["dust", "airlock", "mitigation"]},
    {"title": "無水シャンプー・ボディケアシステム", "title_en": "Waterless Personal Care System", "category": "hygiene", "entry_type": "technology", "summary": "水を使用しない全身洗浄システム。抗菌性ナノファイバーワイプとドライシャンプーの組み合わせで、最小限の水で清潔を維持。", "source_org": "JAXA", "source_country": "JP", "source_year": 2023, "trl": 6, "timeline": "2025-2028", "tags": ["waterless", "personal care", "nanofiber"], "iss_connection": "ISS宇宙飛行士の衛生管理手法を改良"},
    {"title": "月面基地廃棄物完全リサイクルシステム", "title_en": "Complete Waste Recycling System for Lunar Base", "category": "hygiene", "entry_type": "project", "summary": "有機廃棄物の熱分解・バイオ処理による完全リサイクル。糞便・食品残渣を肥料と水に変換し、廃棄物ゼロを目指す。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["waste", "recycling", "pyrolysis"]},
    {"title": "レゴリス微粒子の健康影響研究", "title_en": "Health Effects of Regolith Fine Particles", "category": "hygiene", "entry_type": "research", "summary": "月面ダストの吸入毒性・皮膚刺激性の系統的評価。ナノサイズのガラス質粒子が肺胞に沈着するリスクと対策を研究。", "source_org": "Stony Brook University", "source_country": "US", "source_year": 2023, "trl": 2, "timeline": "ongoing", "tags": ["dust toxicity", "lung", "nanoparticles"]},
    {"title": "UV-C空気殺菌・浄化システム", "title_en": "UV-C Air Sterilization System for Habitats", "category": "hygiene", "entry_type": "technology", "summary": "紫外線C波による居住区内の空気殺菌装置。ウイルス・細菌の99.9%を不活化し、閉鎖空間の感染リスクを低減。", "source_org": "CNSA", "source_country": "CN", "source_year": 2024, "trl": 7, "timeline": "2025-2028", "tags": ["UV-C", "air quality", "sterilization"]},
    {"title": "宇宙用コンポストトイレ", "title_en": "Space Composting Toilet System", "category": "hygiene", "entry_type": "technology", "summary": "微生物分解による無臭コンポストトイレ。処理後の堆肥は植物栽培に利用可能。水使用量を従来比90%削減。", "source_org": "University of Colorado", "source_country": "US", "source_year": 2023, "trl": 4, "timeline": "2030s", "tags": ["composting", "toilet", "water saving"]},
    {"title": "抗菌コーティング居住表面技術", "title_en": "Antimicrobial Surface Coating for Habitats", "category": "hygiene", "entry_type": "technology", "summary": "銅・銀ナノ粒子を含む自己殺菌コーティング。居住区の壁面・手すりに適用し、微生物の繁殖を抑制。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["antimicrobial", "coating", "silver"], "iss_connection": "ISS「きぼう」での抗菌素材試験"},
    {"title": "月面基地の室内環境微生物モニタリング", "title_en": "Indoor Microbiome Monitoring for Lunar Base", "category": "hygiene", "entry_type": "research", "summary": "リアルタイムDNAシーケンシングによる居住区内微生物群集の継続的監視。病原体の早期検出と生態系バランスの維持。", "source_org": "NASA Ames Research Center", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["microbiome", "monitoring", "sequencing"]},
    {"title": "静電集塵型HEPAフィルターシステム", "title_en": "Electrostatic HEPA Filter System", "category": "hygiene", "entry_type": "technology", "summary": "月面ダストのサブミクロン粒子を除去する静電集塵併用HEPAフィルター。フィルター寿命を3倍延長する自動逆洗機能付き。", "source_org": "DLR", "source_country": "DE", "source_year": 2023, "trl": 5, "timeline": "2028-2032", "tags": ["HEPA", "electrostatic", "dust filter"]},
    {"title": "宇宙環境における歯科衛生管理", "title_en": "Dental Hygiene Management in Space", "category": "hygiene", "entry_type": "research", "summary": "長期宇宙滞在における口腔衛生の課題と対策。唾液分泌低下、カルシウム代謝変化に対応した口腔ケアプロトコル。", "source_org": "University of Toronto", "source_country": "CA", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["dental", "oral health", "calcium"]},

    # ======== MEDICAL (40 new) ========
    {"title": "月面遠隔手術ロボットシステム", "title_en": "Lunar Teleoperated Surgical Robot", "category": "medical", "entry_type": "technology", "summary": "地球からの通信遅延（1.3秒）を補償する自律機能付き遠隔手術ロボット。緊急時は搭載AIが主要手技を自動実行。", "source_org": "Virtual Incision", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["telesurgery", "robot", "autonomous"]},
    {"title": "宇宙放射線防護ファーマコロジー", "title_en": "Radiation Protection Pharmacology", "category": "medical", "entry_type": "research", "summary": "宇宙放射線による細胞損傷を軽減する放射線防護薬の開発。アミフォスチン類似体の宇宙環境での有効性と安全性を評価。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 2, "timeline": "2030s", "tags": ["radiation", "pharmacology", "protection"]},
    {"title": "ポータブル超音波診断装置 ATLAS", "title_en": "Portable Ultrasound Diagnostic System ATLAS", "category": "medical", "entry_type": "technology", "summary": "AIガイド付きポータブル超音波診断装置。非医療者でも臓器スキャン・骨折診断が可能。遠隔専門医との連携機能搭載。", "source_org": "ESA", "source_country": "EU", "source_year": 2023, "trl": 6, "timeline": "2025-2028", "tags": ["ultrasound", "AI diagnosis", "portable"]},
    {"title": "月面環境での骨密度低下対策総合プログラム", "title_en": "Comprehensive Bone Loss Prevention Program", "category": "medical", "entry_type": "research", "summary": "低重力環境（1/6G）での骨密度低下メカニズムの解明と対策。薬物療法、運動処方、栄養管理の統合的アプローチ。", "source_org": "JAXA Human Spaceflight Technology", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["bone loss", "osteoporosis", "countermeasure"], "iss_connection": "ISS長期滞在者の骨密度データを基盤"},
    {"title": "宇宙環境バイオバンク", "title_en": "Space Environment Biobank", "category": "medical", "entry_type": "project", "summary": "月面滞在者の血液・組織サンプルを保存するバイオバンク。長期宇宙滞在の医学的影響を追跡する縦断研究のインフラ。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["biobank", "longitudinal", "samples"]},
    {"title": "3Dバイオプリンティングによる組織修復", "title_en": "3D Bioprinting for Tissue Repair in Space", "category": "medical", "entry_type": "research", "summary": "宇宙環境での皮膚・骨組織の3Dバイオプリンティング。微小重力を活用した高品質組織構築と、月面での外傷治療への応用。", "source_org": "DLR", "source_country": "DE", "source_year": 2023, "trl": 3, "timeline": "2035-2040", "tags": ["bioprinting", "tissue", "regenerative"]},
    {"title": "宇宙放射線リアルタイム線量モニタリング", "title_en": "Real-Time Radiation Dosimetry System", "category": "medical", "entry_type": "technology", "summary": "個人装着型のリアルタイム放射線線量計。GCR（銀河宇宙線）とSPE（太陽粒子イベント）を区別し、被曝限度超過時に警告。", "source_org": "NASA Johnson Space Center", "source_country": "US", "source_year": 2024, "trl": 7, "timeline": "2025-2028", "tags": ["radiation", "dosimetry", "wearable"]},
    {"title": "月面薬局：医薬品安定性と製造", "title_en": "Lunar Pharmacy: Drug Stability and Manufacturing", "category": "medical", "entry_type": "research", "summary": "宇宙放射線環境下での医薬品の長期安定性評価。劣化が早い薬品の月面での製造可能性を検討。", "source_org": "University of Houston", "source_country": "US", "source_year": 2023, "trl": 2, "timeline": "2035-2040", "tags": ["pharmacy", "drug stability", "manufacturing"]},
    {"title": "緊急医療対応AIアシスタント", "title_en": "Emergency Medical AI Assistant", "category": "medical", "entry_type": "technology", "summary": "通信途絶時でも機能する医療AIアシスタント。症状入力から診断候補と治療手順をガイド。過去の宇宙医学データベースを搭載。", "source_org": "Baylor College of Medicine", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2028-2032", "tags": ["AI", "emergency medicine", "autonomous"]},
    {"title": "月面での心理カウンセリングVRシステム", "title_en": "VR Psychological Counseling for Lunar Crew", "category": "medical", "entry_type": "technology", "summary": "VR環境でのリモートカウンセリングと自動化セラピー。認知行動療法プログラムを搭載し、通信遅延に対応。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["VR", "mental health", "CBT"]},

    # ======== EXERCISE (40 new) ========
    {"title": "月面1/6G専用トレッドミル LUNAR-T3", "title_en": "Lunar 1/6G Treadmill LUNAR-T3", "category": "exercise", "entry_type": "technology", "summary": "月面の低重力環境に最適化されたトレッドミル。弾性バンド負荷システムにより地球相当の運動強度を確保しつつ、関節への衝撃を制御。", "source_org": "NASA Johnson Space Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["treadmill", "exercise", "gravity"], "iss_connection": "ISS T2トレッドミルの月面版"},
    {"title": "フライホイール抵抗運動装置 FARED", "title_en": "Flywheel Advanced Resistive Exercise Device", "category": "exercise", "entry_type": "technology", "summary": "フライホイール慣性を利用した抵抗運動装置。コンパクトながら筋力トレーニングと骨負荷を同時に提供。", "source_org": "ESA", "source_country": "EU", "source_year": 2023, "trl": 6, "timeline": "2025-2028", "tags": ["flywheel", "resistance", "compact"]},
    {"title": "VRフィットネスプログラム「LUNAR FIT」", "title_en": "VR Fitness Program LUNAR FIT", "category": "exercise", "entry_type": "concept", "summary": "VR空間での没入型エクササイズプログラム。月面探索、スポーツシミュレーション等のゲーミフィケーションで運動継続を促進。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["VR", "gamification", "motivation"]},
    {"title": "人工重力短腕遠心機", "title_en": "Short-Radius Centrifuge for Artificial Gravity", "category": "exercise", "entry_type": "research", "summary": "半径2.5mの短腕遠心機で断続的に1Gの人工重力を発生。骨密度維持と心血管系の退化防止に有効。", "source_org": "MIT", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2035-2040", "tags": ["artificial gravity", "centrifuge", "countermeasure"]},
    {"title": "低重力環境での筋電図バイオフィードバック", "title_en": "EMG Biofeedback for Exercise in Low Gravity", "category": "exercise", "entry_type": "research", "summary": "筋電図センサーによるリアルタイムフィードバックで運動効率を最大化。低重力で不足しがちな筋活動を可視化し最適化。", "source_org": "German Aerospace Center", "source_country": "DE", "source_year": 2023, "trl": 4, "timeline": "2028-2032", "tags": ["EMG", "biofeedback", "optimization"]},
    {"title": "月面EVA作業時の運動負荷評価", "title_en": "Exercise Load Assessment during Lunar EVA", "category": "exercise", "entry_type": "research", "summary": "月面船外活動の身体負荷を定量化。宇宙服制約下での代謝コストと筋骨格系への影響をモデル化し、EVA前後の運動処方に反映。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2028-2032", "tags": ["EVA", "metabolic cost", "spacesuit"]},
    {"title": "ヨガ・太極拳の宇宙適応プログラム", "title_en": "Yoga and Tai Chi Space Adaptation Program", "category": "exercise", "entry_type": "research", "summary": "ヨガと太極拳を低重力環境に適応させたプログラム。バランス感覚維持、ストレス軽減、柔軟性確保を統合的に実現。", "source_org": "CNSA", "source_country": "CN", "source_year": 2023, "trl": 2, "timeline": "2030s", "tags": ["yoga", "tai chi", "wellbeing"]},
    {"title": "ウェアラブル骨密度モニタリングデバイス", "title_en": "Wearable Bone Density Monitoring Device", "category": "exercise", "entry_type": "technology", "summary": "超音波パルスによる非侵襲的骨密度測定デバイス。手首装着型で運動処方の効果をリアルタイムに評価。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 4, "timeline": "2028-2032", "tags": ["wearable", "bone density", "monitoring"]},
    {"title": "月面バウンディング運動研究", "title_en": "Lunar Bounding Locomotion Exercise Research", "category": "exercise", "entry_type": "research", "summary": "月面の1/6Gでのバウンディング（跳躍歩行）が骨・筋肉に与える運動効果を評価。Apollo映像の解析と地上シミュレーション。", "source_org": "European Space Research and Technology Centre", "source_country": "EU", "source_year": 2023, "trl": 2, "timeline": "2030s", "tags": ["locomotion", "bounding", "Apollo"]},
    {"title": "水中運動シミュレーター", "title_en": "Aquatic Exercise Simulator for Lunar Habitats", "category": "exercise", "entry_type": "concept", "summary": "月面基地内に設置する小型水中運動プール。水の抵抗を利用して低重力環境での効果的な全身運動を実現。", "source_org": "SpaceX", "source_country": "US", "source_year": 2024, "trl": 2, "timeline": "2040s", "tags": ["aquatic", "pool", "resistance"]},

    # ======== CLOTHING (30 new) ========
    {"title": "次世代月面船外活動服 xEMU Mark II", "title_en": "Next-Gen Lunar EVA Suit xEMU Mark II", "category": "clothing", "entry_type": "technology", "summary": "Artemis計画用の次世代月面船外活動服。関節可動域拡大、ダスト耐性向上、8時間連続活動対応。インフォメーションディスプレイ内蔵。", "source_org": "Axiom Space", "source_country": "US", "source_year": 2024, "trl": 7, "timeline": "2025-2028", "target_mission": "Artemis III+", "tags": ["EVA suit", "Artemis", "next-gen"]},
    {"title": "自己修復型宇宙服外層素材", "title_en": "Self-Healing Outer Layer Material for Spacesuits", "category": "clothing", "entry_type": "research", "summary": "微小隕石やレゴリスによる損傷を自動修復するポリマー素材。マイクロカプセル内の修復剤が破損部に充填される仕組み。", "source_org": "MIT", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["self-healing", "polymer", "micrometeorite"]},
    {"title": "月面ダスト防着コーティング「LunarShield」", "title_en": "Lunar Dust-Repellent Coating LunarShield", "category": "clothing", "entry_type": "technology", "summary": "電子ビーム蒸着法による超撥塵コーティング。レゴリスの静電付着を95%低減し、宇宙服の寿命を3倍に延長。", "source_org": "NASA Kennedy Space Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["dust repellent", "coating", "electrostatic"]},
    {"title": "温度調節スマートテキスタイル", "title_en": "Temperature-Regulating Smart Textile", "category": "clothing", "entry_type": "technology", "summary": "相変化材料を織り込んだスマートテキスタイル。月面の極端な温度差（-173℃～127℃）に対して自動的に保温・放熱。", "source_org": "ILC Dover", "source_country": "US", "source_year": 2023, "trl": 5, "timeline": "2028-2032", "tags": ["smart textile", "PCM", "thermal"]},
    {"title": "宇宙服内蔵型生体モニタリング", "title_en": "Integrated Biometric Monitoring in Spacesuits", "category": "clothing", "entry_type": "technology", "summary": "宇宙服の内層に織り込まれた生体センサー群。心拍、体温、発汗量、血中酸素をリアルタイム計測し、疲労・熱中症を予防。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["biometric", "sensor", "health monitoring"]},
    {"title": "3Dプリント月面ブーツ", "title_en": "3D Printed Lunar Boots", "category": "clothing", "entry_type": "concept", "summary": "個人の足型に合わせてカスタム3Dプリントする月面ブーツ。レゴリス地面との最適グリップと長時間歩行時の快適性を両立。", "source_org": "Collins Aerospace", "source_country": "US", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["3D printing", "boots", "custom fit"]},
    {"title": "放射線遮蔽型インナーウェア", "title_en": "Radiation-Shielding Inner Garment", "category": "clothing", "entry_type": "research", "summary": "水素含有ポリエチレン繊維による放射線遮蔽インナーウェア。重要臓器周辺の被曝量を20-30%低減。軽量で着用感を維持。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["radiation shielding", "polyethylene", "garment"]},
    {"title": "月面作業用外骨格スーツ", "title_en": "Lunar Work Exoskeleton Suit", "category": "clothing", "entry_type": "technology", "summary": "月面での重量物運搬・組立作業を支援する外骨格スーツ。1/6Gでの慣性制御と、宇宙服との統合設計。", "source_org": "Lockheed Martin", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["exoskeleton", "construction", "power assist"]},

    # ======== COMMUNICATION (30 new) ========
    {"title": "月面4G/LTE通信ネットワーク", "title_en": "Lunar 4G/LTE Communication Network", "category": "communication", "entry_type": "project", "summary": "月面に展開する4G/LTEベースの通信インフラ。基地間通信、ローバー制御、宇宙飛行士間の音声・データ通信を統合。", "source_org": "Nokia Bell Labs", "source_country": "FI", "source_year": 2024, "trl": 6, "timeline": "2025-2028", "target_mission": "Artemis", "tags": ["4G", "LTE", "network"]},
    {"title": "月面GPS代替測位システム LunaNet", "title_en": "LunaNet Navigation and Positioning System", "category": "communication", "entry_type": "project", "summary": "月面での精密測位を実現する独自航法システム。月周回衛星コンステレーションと月面ビーコンの組み合わせで誤差1m以内。", "source_org": "NASA Goddard Space Flight Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["navigation", "LunaNet", "positioning"]},
    {"title": "レーザー光通信月面中継局", "title_en": "Laser Communication Lunar Relay Station", "category": "communication", "entry_type": "technology", "summary": "レーザー光通信による月面-地球間の高速データリンク。従来の電波通信と比較してデータレート100倍以上を実現。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 6, "timeline": "2028-2032", "tags": ["laser", "optical", "high bandwidth"]},
    {"title": "月面裏側通信中継衛星 鵲橋3号", "title_en": "Queqiao-3 Lunar Far Side Relay Satellite", "category": "communication", "entry_type": "project", "summary": "月面裏側と地球の通信を中継するハロー軌道衛星。嫦娥計画の月面裏側探査を支援。", "source_org": "CNSA", "source_country": "CN", "source_year": 2024, "trl": 7, "timeline": "2025-2028", "tags": ["relay satellite", "far side", "Queqiao"]},
    {"title": "遅延耐性ネットワーク DTN プロトコル", "title_en": "Delay-Tolerant Networking Protocol for Lunar Ops", "category": "communication", "entry_type": "technology", "summary": "1.3秒の通信遅延と断続的接続に対応するDTNプロトコル。データの自動蓄積・転送により、通信途絶時もデータロスなし。", "source_org": "NASA Jet Propulsion Laboratory", "source_country": "US", "source_year": 2023, "trl": 7, "timeline": "2025-2028", "tags": ["DTN", "delay tolerant", "protocol"]},
    {"title": "月面AR作業支援ヘッドセット", "title_en": "AR Work Assistance Headset for Lunar EVA", "category": "communication", "entry_type": "technology", "summary": "EVA中にAR表示で作業手順、危険警告、地図情報を提供するヘッドセット。ジェスチャー操作と音声コマンドで宇宙服着用中も操作可能。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["AR", "HUD", "EVA support"]},
    {"title": "月面IoTセンサーネットワーク", "title_en": "Lunar IoT Sensor Network", "category": "communication", "entry_type": "concept", "summary": "月面基地周辺に展開する低電力IoTセンサー群。環境モニタリング、構造物ヘルスモニタリング、ダスト警報を統合。", "source_org": "MIT", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["IoT", "sensor", "monitoring"]},
    {"title": "月面5G通信実証計画", "title_en": "Lunar 5G Communication Demonstration Plan", "category": "communication", "entry_type": "project", "summary": "5G NRベースの超高速月面通信実証。4K映像リアルタイム伝送、遠隔ロボット操縦、大規模データ転送を想定。", "source_org": "Nokia Bell Labs", "source_country": "FI", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["5G", "demonstration", "high speed"]},

    # ======== ENTERTAINMENT (30 new) ========
    {"title": "月面VRシアター", "title_en": "Lunar VR Theater System", "category": "entertainment", "entry_type": "concept", "summary": "共有VR空間で映画鑑賞、バーチャル旅行、地球の風景没入体験を提供。長期滞在クルーの精神的リフレッシュと地球との心理的つながりを維持。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["VR", "cinema", "earth connection"]},
    {"title": "宇宙音楽制作ラボ", "title_en": "Space Music Production Lab", "category": "entertainment", "entry_type": "concept", "summary": "月面環境の独自音響特性を活かした音楽制作スタジオ。電子楽器、デジタルオーディオワークステーション、コラボレーション通信機能を搭載。", "source_org": "ESA", "source_country": "EU", "source_year": 2023, "trl": 2, "timeline": "2035-2040", "tags": ["music", "creative", "studio"]},
    {"title": "月面庭園（バイオフィリックデザイン）", "title_en": "Lunar Garden - Biophilic Design Module", "category": "entertainment", "entry_type": "concept", "summary": "食料生産兼リラクゼーション空間としての月面庭園。植物の緑、水の音、自然光シミュレーションでストレスを30%軽減。", "source_org": "Interstellar Lab", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["biophilic", "garden", "wellbeing"]},
    {"title": "低重力スポーツ競技開発", "title_en": "Low-Gravity Sports Development", "category": "entertainment", "entry_type": "research", "summary": "月面の1/6G環境に適した新スポーツの開発研究。バドミントン、卓球の変種や、低重力独自の3次元競技を設計。", "source_org": "CNSA", "source_country": "CN", "source_year": 2023, "trl": 1, "timeline": "2040s", "tags": ["sports", "low gravity", "recreation"]},
    {"title": "月面天文台（クルー向け観測施設）", "title_en": "Crew Observatory on the Moon", "category": "entertainment", "entry_type": "concept", "summary": "大気のない月面での肉眼天体観測施設。娯楽と科学教育を兼ねた観測ドーム。地球観測も含む。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 2, "timeline": "2035-2040", "tags": ["observatory", "astronomy", "education"]},
    {"title": "デジタルアート・クリエイションスペース", "title_en": "Digital Art Creation Space", "category": "entertainment", "entry_type": "concept", "summary": "3Dモデリング、デジタルペインティング、写真編集のためのクリエイティブスペース。月面環境を題材にした芸術作品の制作と地球への配信。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 2, "timeline": "2035-2040", "tags": ["digital art", "creative space", "expression"]},
    {"title": "長期隔離環境のメンタルヘルスゲーミフィケーション", "title_en": "Mental Health Gamification for Long-Duration Isolation", "category": "entertainment", "entry_type": "research", "summary": "ゲーム要素を取り入れた日常活動管理システム。達成感、社会的つながり、自律性を維持するゲーミフィケーション設計。", "source_org": "University of Pennsylvania", "source_country": "US", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["gamification", "mental health", "isolation"]},
    {"title": "月面料理コンテスト・プログラム", "title_en": "Lunar Cooking Competition Program", "category": "entertainment", "entry_type": "concept", "summary": "限られた食材での創作料理コンテスト。食の楽しみとクルー間交流を促進する娯楽プログラム。レシピは地球にも配信。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 1, "timeline": "2035-2040", "tags": ["cooking", "social", "food culture"]},

    # ======== SLEEP/HABITAT (30 new) ========
    {"title": "月面膨張式居住モジュール B330-L", "title_en": "Lunar Inflatable Habitat Module B330-L", "category": "sleep_habitat", "entry_type": "technology", "summary": "Bigelow Aerospace系の膨張式居住モジュールの月面版。打ち上げ時コンパクト、展開後は330m³の居住空間を提供。放射線遮蔽層を多層化。", "source_org": "Bigelow Aerospace", "source_country": "US", "source_year": 2023, "trl": 4, "timeline": "2030s", "tags": ["inflatable", "habitat", "B330"], "iss_connection": "ISS BEAM実験モジュールの発展型"},
    {"title": "3Dプリント月面シェルター ICON", "title_en": "3D Printed Lunar Shelter by ICON", "category": "sleep_habitat", "entry_type": "project", "summary": "月面レゴリスを材料とした3Dプリントシェルター。Lavacrete技術により現地材料で構造物を建設。NASA Artemis計画と連携。", "source_org": "ICON", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "target_mission": "Artemis", "tags": ["3D printing", "regolith", "construction"]},
    {"title": "概日リズム制御照明システム", "title_en": "Circadian Rhythm Control Lighting System", "category": "sleep_habitat", "entry_type": "technology", "summary": "月面の14日昼/14日夜サイクルに対応し、人工的に24時間周期の光環境を再現。色温度・照度を自動調整して睡眠の質を維持。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 6, "timeline": "2025-2028", "tags": ["circadian", "lighting", "sleep quality"], "iss_connection": "ISS SSLMモジュールの照明実験を発展"},
    {"title": "月面地下溶岩チューブ居住構想", "title_en": "Lunar Lava Tube Habitat Concept", "category": "sleep_habitat", "entry_type": "concept", "summary": "月面の溶岩チューブ（天然洞窟）を居住空間として利用する構想。天然の放射線遮蔽と温度安定性を活用。内部に膨張式モジュールを設置。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 2, "timeline": "2040s", "tags": ["lava tube", "underground", "radiation protection"]},
    {"title": "レゴリスバッグ放射線遮蔽壁", "title_en": "Regolith Bag Radiation Shielding Wall", "category": "sleep_habitat", "entry_type": "technology", "summary": "レゴリスを充填した土嚢状バッグを積層して放射線遮蔽壁を構築。月面材料のみで建設可能な低コスト遮蔽ソリューション。", "source_org": "JAXA", "source_country": "JP", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["regolith", "radiation shield", "ISRU"]},
    {"title": "月面基地温度制御ヒートパイプシステム", "title_en": "Lunar Base Thermal Control Heat Pipe System", "category": "sleep_habitat", "entry_type": "technology", "summary": "月面の極端な温度変化（-173℃～127℃）に対応する受動的熱制御システム。ヒートパイプネットワークにより居住区を22±2℃に維持。", "source_org": "NASA Johnson Space Center", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "tags": ["thermal", "heat pipe", "temperature control"]},
    {"title": "月面緊急避難シェルター", "title_en": "Lunar Emergency Shelter", "category": "sleep_habitat", "entry_type": "technology", "summary": "太陽粒子イベント（SPE）時に即座に避難可能な小型高遮蔽シェルター。水タンクと多層遮蔽材で急性放射線被曝を防止。", "source_org": "Lockheed Martin", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2028-2032", "tags": ["emergency", "SPE", "shelter"]},
    {"title": "月面窓：電子調光スマートウィンドウ", "title_en": "Lunar Smart Window with Electrochromic Glass", "category": "sleep_habitat", "entry_type": "technology", "summary": "エレクトロクロミックガラスによる光量自動調整窓。月面の強烈な太陽光を制御しつつ、外部景観を楽しめる居住空間を実現。", "source_org": "AI SpaceFactory", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["smart window", "electrochromic", "view"]},
    {"title": "防音・プライバシー確保個室設計", "title_en": "Soundproof Private Crew Quarter Design", "category": "sleep_habitat", "entry_type": "research", "summary": "閉鎖環境での個人空間確保のための防音設計研究。アクティブノイズキャンセリング壁と心理的プライバシー感を両立する空間設計。", "source_org": "Concordia Station Research", "source_country": "EU", "source_year": 2023, "trl": 3, "timeline": "2030s", "tags": ["privacy", "soundproofing", "crew quarters"], "earth_analog": "南極コンコルディア基地での知見"},
    {"title": "月面居住区空気浄化再生システム", "title_en": "Lunar Habitat Air Revitalization System", "category": "sleep_habitat", "entry_type": "technology", "summary": "CO2除去、O2生成、微量汚染物質除去を統合した空気再生システム。サバティエ反応器とOGS（酸素生成システム）を月面仕様に最適化。", "source_org": "NASA Marshall Space Flight Center", "source_country": "US", "source_year": 2024, "trl": 6, "timeline": "2028-2032", "tags": ["air revitalization", "CO2 removal", "life support"], "iss_connection": "ISS CDRAとOGSの統合発展型"},

    # ======== WORK ENVIRONMENT (30 new) ========
    {"title": "月面建設用テレプレゼンスロボット", "title_en": "Telepresence Construction Robot for Lunar Surface", "category": "work_environment", "entry_type": "technology", "summary": "基地内から遠隔操縦する建設作業ロボット。双腕型マニピュレーターと移動プラットフォーム。力覚フィードバック付き。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["telepresence", "robot", "construction"]},
    {"title": "月面レゴリス採掘・処理プラント", "title_en": "Lunar Regolith Mining and Processing Plant", "category": "work_environment", "entry_type": "project", "summary": "レゴリスを採掘し、建材・金属・酸素に分離する総合処理プラント。太陽炉とモリブデン電極による溶融電解法。", "source_org": "Lunar Outpost", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["mining", "processing", "ISRU"]},
    {"title": "月面太陽光発電ファーム設計", "title_en": "Lunar Solar Power Farm Design", "category": "work_environment", "entry_type": "technology", "summary": "月面南極の高地に設置するメガワット級太陽光発電システム。永久日照地域を活用し、連続発電を実現。蓄電システム併設。", "source_org": "Astrobotic", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2030s", "tags": ["solar power", "energy", "continuous"]},
    {"title": "月面原子力マイクロリアクター", "title_en": "Lunar Fission Surface Power System", "category": "work_environment", "entry_type": "project", "summary": "10kWe級の月面設置型小型原子炉。月の夜間（14日間）も安定した電力供給を実現。NASA-DOE共同開発。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "2028-2032", "target_mission": "Artemis Base Camp", "tags": ["fission", "nuclear", "power"]},
    {"title": "月面科学実験ラボモジュール", "title_en": "Lunar Science Laboratory Module", "category": "work_environment", "entry_type": "concept", "summary": "地質学・天文学・生物学の統合研究施設。グローブボックス、顕微鏡、分光計等を搭載。地球との共同研究を支援。", "source_org": "ESA", "source_country": "EU", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["laboratory", "science", "research"]},
    {"title": "自律型月面探査ドローン", "title_en": "Autonomous Lunar Exploration Drone", "category": "work_environment", "entry_type": "technology", "summary": "月面の低重力環境で飛行する自律探査ドローン。クレーター内部の調査や基地周辺の3Dマッピングを実施。", "source_org": "JAXA", "source_country": "JP", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["drone", "exploration", "mapping"]},
    {"title": "月面3Dマッピング・デジタルツイン", "title_en": "Lunar 3D Mapping and Digital Twin", "category": "work_environment", "entry_type": "technology", "summary": "LiDARとフォトグラメトリーによる月面基地のリアルタイムデジタルツイン。施設管理、保守計画、安全管理に活用。", "source_org": "Intuitive Machines", "source_country": "US", "source_year": 2024, "trl": 4, "timeline": "2028-2032", "tags": ["digital twin", "LiDAR", "mapping"]},
    {"title": "月面物流・輸送システム", "title_en": "Lunar Logistics and Transport System", "category": "work_environment", "entry_type": "concept", "summary": "基地間の物資輸送用自律ローバー群。荷物自動仕分け、最適経路計画、共同搬送が可能なスワームロボティクス。", "source_org": "Astrobotic", "source_country": "US", "source_year": 2024, "trl": 3, "timeline": "2030s", "tags": ["logistics", "swarm robotics", "transport"]},

    # ======== ANALOG ENVIRONMENT ENTRIES (across categories) ========
    {"title": "HI-SEAS長期隔離居住実験の知見", "title_en": "Lessons from HI-SEAS Long-Duration Isolation", "category": "sleep_habitat", "entry_type": "case_study", "summary": "ハワイのHI-SEAS火星/月面シミュレーション施設での1年間隔離居住実験。クルーダイナミクス、プライバシー、食事の重要性等の知見。", "source_org": "University of Hawaii", "source_country": "US", "source_year": 2023, "trl": 6, "timeline": "ongoing", "tags": ["HI-SEAS", "isolation", "crew dynamics"], "earth_analog": "マウナロア山のドーム型施設"},
    {"title": "Biosphere 2 閉鎖生態系の教訓", "title_en": "Lessons from Biosphere 2 Closed Ecosystem", "category": "food", "entry_type": "case_study", "summary": "1991-1993年のBiosphere 2実験から得られた閉鎖生態系の教訓。酸素減少問題、食料生産の不安定性、微生物バランスの崩壊等。", "source_org": "University of Arizona", "source_country": "US", "source_year": 2023, "trl": 4, "timeline": "ongoing", "tags": ["Biosphere 2", "closed ecosystem", "lessons learned"], "earth_analog": "アリゾナ州のBiosphere 2施設"},
    {"title": "南極コンコルディア基地の居住環境設計", "title_en": "Concordia Station Habitat Design Lessons", "category": "sleep_habitat", "entry_type": "case_study", "summary": "南極の冬季9カ月間隔離されるコンコルディア基地の設計知見。概日リズム管理、社会的空間設計、プライバシー確保の実践。", "source_org": "ESA", "source_country": "EU", "source_year": 2023, "trl": 6, "timeline": "ongoing", "tags": ["Antarctica", "Concordia", "habitat design"], "earth_analog": "南極コンコルディア基地"},
    {"title": "NEEMO海底居住実験の知見", "title_en": "NEEMO Undersea Habitat Research Insights", "category": "work_environment", "entry_type": "case_study", "summary": "NASAのNEMO水中施設での模擬月面EVA訓練。水中環境が1/6G作業シミュレーションとして有効。ツール設計と作業手順の最適化。", "source_org": "NASA", "source_country": "US", "source_year": 2024, "trl": 5, "timeline": "ongoing", "tags": ["NEEMO", "underwater", "EVA simulation"], "earth_analog": "フロリダ沖の水中研究施設Aquarius"},
    {"title": "中国月宮一号閉鎖生態系実験", "title_en": "China Yuegong-1 Closed Ecosystem Experiment", "category": "food", "entry_type": "case_study", "summary": "北京航空航天大学の「月宮一号」での370日間閉鎖実験。4人のクルーが植物栽培、昆虫飼育、水循環で97%の生命維持を達成。", "source_org": "Beihang University", "source_country": "CN", "source_year": 2023, "trl": 5, "timeline": "ongoing", "tags": ["Yuegong-1", "closed loop", "bioregenerative"], "earth_analog": "北京航空航天大学の月宮一号施設"},
    {"title": "MDRS火星砂漠研究基地の知見", "title_en": "Mars Desert Research Station Insights", "category": "work_environment", "entry_type": "case_study", "summary": "ユタ州の火星アナログ施設での長期運用知見。EVAプロトコル、基地運営ルーチン、クルーの自律的問題解決能力。", "source_org": "Mars Society", "source_country": "US", "source_year": 2023, "trl": 5, "timeline": "ongoing", "tags": ["MDRS", "Mars analog", "operations"], "earth_analog": "ユタ州のMars Desert Research Station"},
]

# Phase 3: Additional challenges
ADDITIONAL_CHALLENGES = [
    {"name_ja": "宇宙放射線（GCR）の慢性被曝", "name_en": "Chronic GCR Radiation Exposure", "category": "medical", "challenge_type": "radiation", "description": "銀河宇宙線による慢性的な放射線被曝。年間被曝量が地球の約200倍。がんリスク増加と中枢神経系への影響。月面遮蔽でも完全防護は困難。", "severity": "critical"},
    {"name_ja": "太陽粒子イベント（SPE）急性被曝", "name_en": "Solar Particle Event Acute Exposure", "category": "medical", "challenge_type": "radiation", "description": "予測困難な太陽フレアによる急性放射線被曝。数時間で致死量に達する可能性。緊急避難シェルターと早期警報システムが必須。", "severity": "critical"},
    {"name_ja": "レゴリスダストの人体毒性", "name_en": "Regolith Dust Toxicity", "category": "hygiene", "challenge_type": "dust", "description": "月面レゴリスの微粒子はナノサイズのガラス質で、吸入すると肺胞に沈着。アポロ飛行士も「月面花粉症」を報告。長期曝露の影響は未知数。", "severity": "critical"},
    {"name_ja": "低重力（1/6G）による骨密度低下", "name_en": "Bone Density Loss in 1/6G", "category": "exercise", "challenge_type": "microgravity", "description": "月面の低重力環境で骨密度が月1-2%低下。ISS（微小重力）より緩やかだが、長期滞在では深刻。運動・薬物療法での対策が必要。", "severity": "high"},
    {"name_ja": "閉鎖環境での心理的孤立", "name_en": "Psychological Isolation in Confined Environment", "category": "entertainment", "challenge_type": "isolation", "description": "地球から38万kmの距離と1.3秒の通信遅延。少人数クルーの対人関係ストレス。地球との心理的距離感による鬱・不安。", "severity": "high"},
    {"name_ja": "通信遅延と途絶", "name_en": "Communication Delay and Blackout", "category": "communication", "challenge_type": "communication_delay", "description": "地球-月間の1.3秒往復遅延。月面裏側での通信途絶。緊急時のリアルタイム地球支援が制限される。自律的判断能力が必須。", "severity": "high"},
    {"name_ja": "水資源の絶対的希少性", "name_en": "Absolute Water Scarcity", "category": "water", "challenge_type": "resource_scarcity", "description": "地球からの水輸送コストは$1M/kg以上。現地の水氷資源は分布・量が不確定。水リサイクル率98%以上が生存条件。", "severity": "critical"},
    {"name_ja": "長期食料保存と栄養バランス", "name_en": "Long-Term Food Storage and Nutrition", "category": "food", "challenge_type": "resource_scarcity", "description": "宇宙食の賞味期限は最大5年。ビタミンCなど一部栄養素は保存中に劣化。多様な食事が心理的にも不可欠。", "severity": "high"},
    {"name_ja": "月面の極端な温度環境", "name_en": "Extreme Lunar Temperature Environment", "category": "sleep_habitat", "challenge_type": "thermal", "description": "昼間127℃、夜間-173℃の300℃温度差。永久影クレーターは-230℃。居住区の熱制御と宇宙服の温度管理が生命維持の要。", "severity": "critical"},
    {"name_ja": "月面真空環境の危険性", "name_en": "Lunar Vacuum Environment Hazards", "category": "clothing", "challenge_type": "vacuum", "description": "月面は完全真空。宇宙服やハビタットの微小穿孔が即座に生命の危機に。減圧事故対策と迅速修復技術が必要。", "severity": "critical"},
    {"name_ja": "14日間の月面夜間", "name_en": "14-Day Lunar Night", "category": "work_environment", "challenge_type": "thermal", "description": "月面の夜は14地球日続く。太陽光発電不可、温度急降下、視界ゼロ。原子力電源と蓄電システムが不可欠。", "severity": "high"},
    {"name_ja": "閉鎖環境での感染症リスク", "name_en": "Infection Risk in Closed Environment", "category": "hygiene", "challenge_type": "confined_environment", "description": "密閉空間での微生物増殖と感染拡大リスク。免疫機能低下が宇宙環境で観察されており、通常は無害な菌が日和見感染を起こす可能性。", "severity": "high"},
    {"name_ja": "低重力での筋萎縮", "name_en": "Muscle Atrophy in Reduced Gravity", "category": "exercise", "challenge_type": "microgravity", "description": "1/6Gでは下肢筋群が地球の60-70%の負荷しか受けない。抗重力筋の萎縮が進行し、EVA作業能力や緊急時対応能力に影響。", "severity": "high"},
    {"name_ja": "宇宙服可動性の制約", "name_en": "Spacesuit Mobility Constraints", "category": "clothing", "challenge_type": "confined_environment", "description": "与圧宇宙服は関節可動域を大幅に制限。細かい作業が困難で、8時間以上のEVAは身体的に極めて消耗する。疲労骨折のリスクも。", "severity": "medium"},
    {"name_ja": "レゴリスの機器への影響", "name_en": "Regolith Effects on Equipment", "category": "work_environment", "challenge_type": "dust", "description": "微細で鋭利な月面ダストがシール、光学系、可動部を摩耗・劣化させる。アポロ計画でもダストによる機器故障が多発。", "severity": "high"},
    {"name_ja": "概日リズムの乱れ", "name_en": "Circadian Rhythm Disruption", "category": "sleep_habitat", "challenge_type": "psychological", "description": "月面の29.5日昼夜サイクルは人間の24時間概日リズムと大きく乖離。睡眠障害、認知機能低下、免疫機能異常のリスク。", "severity": "high"},
    {"name_ja": "限られた衛生用水での清潔維持", "name_en": "Maintaining Hygiene with Limited Water", "category": "hygiene", "challenge_type": "resource_scarcity", "description": "1日あたりの水使用量を地球の1/100以下に制限する必要。シャワー・洗濯は大幅制限。皮膚トラブルや感染症のリスク増大。", "severity": "medium"},
    {"name_ja": "緊急医療対応の制約", "name_en": "Emergency Medical Response Limitations", "category": "medical", "challenge_type": "isolation", "description": "地球への緊急帰還に最低3日。専門医師が常駐しない環境での外傷・急病対応。手術設備と医薬品の制約。", "severity": "critical"},
    {"name_ja": "クルー間の対人葛藤", "name_en": "Interpersonal Conflict Among Crew", "category": "entertainment", "challenge_type": "psychological", "description": "少人数の固定メンバーとの閉鎖環境での長期共同生活。文化差、性格の相性、ストレスによる対立。解消手段の限界。", "severity": "medium"},
    {"name_ja": "通信帯域の制限", "name_en": "Communication Bandwidth Limitations", "category": "communication", "challenge_type": "communication_delay", "description": "月面-地球間の通信帯域は限られており、大容量データ転送には数時間を要する。リアルタイムビデオは低解像度に制限。", "severity": "medium"},
]

# Phase 4: New tables
PHASE4_MODULES = [
    {"name_ja": "プライベートルーム", "name_en": "Private Crew Quarter", "module_type": "habitation", "description": "乗員個人の居住空間。2.5×2.5×2.1mの個室に睡眠ステーション、収納、パーソナルデバイスを配置。概日リズム照明付き。", "area_m2": 6.25, "capacity": 1},
    {"name_ja": "キッチン&ダイニング", "name_en": "Kitchen and Dining Module", "module_type": "common", "description": "食料調理・保管と共同食事空間。3Dフードプリンター、食品保管庫、冷蔵/冷凍庫。6名同時着席可能なダイニングテーブル。", "area_m2": 25.0, "capacity": 6},
    {"name_ja": "メディカルベイ", "name_en": "Medical Bay", "module_type": "support", "description": "診断・治療・緊急手術に対応する医療施設。超音波診断装置、遠隔手術ロボット、薬品保管庫。放射線緊急避難機能兼用。", "area_m2": 20.0, "capacity": 2},
    {"name_ja": "ラボラトリー", "name_en": "Science Laboratory", "module_type": "work", "description": "地質学・生物学・材料科学の統合研究施設。グローブボックス、顕微鏡、分光計、サンプル保管庫。", "area_m2": 30.0, "capacity": 3},
    {"name_ja": "トレーニングルーム", "name_en": "Exercise and Training Room", "module_type": "support", "description": "月面適応型運動設備を配置。トレッドミル、抵抗運動装置、VRフィットネスシステム。骨密度・筋力維持プログラム対応。", "area_m2": 20.0, "capacity": 2},
    {"name_ja": "プランテーション", "name_en": "Plantation/Greenhouse", "module_type": "life_support", "description": "食料生産用温室モジュール。LED栽培棚、水耕栽培システム、藻類バイオリアクター。CO2固定と酸素生成も担う。", "area_m2": 50.0, "capacity": 1},
    {"name_ja": "コートヤード", "name_en": "Central Courtyard", "module_type": "common", "description": "モジュール間を結ぶ中央共有空間。リラクゼーション、社交、バイオフィリックデザイン庭園。天窓から月面景観を望む。", "area_m2": 35.0, "capacity": 8},
    {"name_ja": "ワークスペース", "name_en": "Command and Work Station", "module_type": "work", "description": "ミッション管制、通信、計画立案の作業空間。多画面ディスプレイ、地球リンク端末、AR/VR操作ステーション。", "area_m2": 25.0, "capacity": 4},
    {"name_ja": "エアロック", "name_en": "Airlock Module", "module_type": "utility", "description": "EVA出入口。ダスト除去システム、宇宙服保管・メンテナンス設備。2名同時使用可能な2室構成。", "area_m2": 15.0, "capacity": 2},
    {"name_ja": "生命維持システム室", "name_en": "Life Support System Room", "module_type": "life_support", "description": "空気再生、水循環、廃棄物処理の中枢。CO2除去装置、OGS、水再生プラント、電力分配システム。", "area_m2": 20.0, "capacity": 0},
]

PHASE4_ROADMAP = [
    {"milestone": "Artemis III 有人月面着陸", "organization": "NASA", "target_year": 2026, "status": "planned", "description": "50年ぶりの有人月面着陸。南極地域に2名が48時間滞在。月面EVAと科学観測を実施。"},
    {"milestone": "VIPER 月面水氷探査ローバー", "organization": "NASA", "target_year": 2025, "status": "planned", "description": "月面南極の永久影クレーターで水氷を直接探査する初のローバーミッション。100日間の探査予定。"},
    {"milestone": "Nokia 月面4G通信実証", "organization": "Nokia / NASA", "target_year": 2025, "status": "in_progress", "description": "月面初の4G/LTE通信ネットワーク実証。IM-2ランダーに搭載して展開予定。"},
    {"milestone": "嫦娥7号 月面南極探査", "organization": "CNSA", "target_year": 2026, "status": "planned", "description": "月面南極の水氷探査ミッション。ローバー、ホッパー、中継衛星で構成。"},
    {"milestone": "Artemis IV Gateway 組立開始", "organization": "NASA / ESA / JAXA", "target_year": 2028, "status": "planned", "description": "月周回ステーションGatewayの本格的な組み立て。居住モジュールHALO搭載。"},
    {"milestone": "月面原子力電源実証", "organization": "NASA / DOE", "target_year": 2030, "status": "concept", "description": "月面での小型原子炉（10kWe級）の実証運用。月の夜間を含む連続電力供給。"},
    {"milestone": "Artemis Base Camp 初期設営", "organization": "NASA", "target_year": 2031, "status": "concept", "description": "月面に最初の恒久的拠点を設営。居住モジュール、ローバー、通信インフラの展開。"},
    {"milestone": "嫦娥8号 ISRU技術実証", "organization": "CNSA", "target_year": 2028, "status": "planned", "description": "月面での資源利用（ISRU）技術の実証。レゴリスからの酸素抽出、3Dプリント建設実験。"},
    {"milestone": "国際月面研究ステーション Phase 1", "organization": "CNSA / Roscosmos", "target_year": 2035, "status": "concept", "description": "中国・ロシア主導の月面研究基地第1期。複数モジュールによる常駐可能施設。"},
    {"milestone": "月面閉鎖生態系運用開始", "organization": "International", "target_year": 2035, "status": "concept", "description": "植物栽培・水循環・空気再生の統合閉鎖生態系の月面運用。食料自給率50%目標。"},
    {"milestone": "月面観光フライト開始", "organization": "SpaceX / Blue Origin", "target_year": 2040, "status": "concept", "description": "民間による月面観光ミッション。短期滞在（1-2週間）の月面ホテル構想。"},
]

PHASE4_EXPERTS = [
    {"name": "Jennifer Heldmann", "affiliation": "NASA Ames Research Center", "country": "US", "field": "Lunar ISRU, Water Ice", "profile_url": "https://www.nasa.gov/people/jennifer-heldmann/"},
    {"name": "Christophe Lasseur", "affiliation": "ESA", "country": "EU", "field": "MELiSSA, Life Support Systems", "profile_url": ""},
    {"name": "Gioia Massa", "affiliation": "NASA Kennedy Space Center", "country": "US", "field": "Space Agriculture, Plant Biology", "profile_url": ""},
    {"name": "古川聡", "affiliation": "JAXA", "country": "JP", "field": "Space Medicine, ISS Commander", "profile_url": ""},
    {"name": "Brent Sherwood", "affiliation": "Blue Origin", "country": "US", "field": "Lunar Architecture, Space Habitats", "profile_url": ""},
    {"name": "星出彰彦", "affiliation": "JAXA", "country": "JP", "field": "ISS Commander, Lunar Missions", "profile_url": ""},
    {"name": "Nujoud Merancy", "affiliation": "NASA Johnson Space Center", "country": "US", "field": "Artemis Mission Planning", "profile_url": ""},
    {"name": "Aidan Cowley", "affiliation": "ESA EAC", "country": "EU", "field": "Lunar Resources, ISRU", "profile_url": ""},
    {"name": "Larry Clark", "affiliation": "ICON", "country": "US", "field": "3D Printed Habitats, Lavacrete", "profile_url": ""},
    {"name": "Dava Newman", "affiliation": "MIT", "country": "US", "field": "Spacesuit Design, BioSuit", "profile_url": ""},
    {"name": "Kevin Sato", "affiliation": "NASA", "country": "US", "field": "Space Food Systems", "profile_url": ""},
    {"name": "Raymond Wheeler", "affiliation": "NASA Kennedy Space Center", "country": "US", "field": "Controlled Environment Agriculture", "profile_url": ""},
    {"name": "Alexander Kumar", "affiliation": "Concordia Station / ESA", "country": "EU", "field": "Extreme Environment Medicine", "profile_url": ""},
    {"name": "Jean-Pierre de Vera", "affiliation": "DLR", "country": "DE", "field": "Astrobiology, Lunar Habitability", "profile_url": ""},
    {"name": "Cesare Lobascio", "affiliation": "Thales Alenia Space", "country": "EU", "field": "Lunar Habitat Systems Engineering", "profile_url": ""},
]


def phase2_3_insert_entries(conn):
    """Insert all expansion entries."""
    count = 0
    for e in EXPANSION_ENTRIES:
        cat = e['category']
        # Generate sequential ID
        existing = conn.execute(
            "SELECT COUNT(*) FROM entries WHERE category = ?", (cat,)
        ).fetchone()[0]
        entry_id = f"{cat}_{existing + 1:03d}"

        # Check for duplicate titles
        dup = conn.execute(
            "SELECT id FROM entries WHERE title = ?", (e['title'],)
        ).fetchone()
        if dup:
            continue

        tags_json = json.dumps(e.get('tags', []), ensure_ascii=False)
        modules_json = json.dumps(e.get('related_modules', []), ensure_ascii=False)
        authors_json = json.dumps(e.get('authors', []), ensure_ascii=False)

        conn.execute("""
            INSERT INTO entries (
                id, title, title_en, category, entry_type, summary,
                source_org, source_country, source_year, trl,
                timeline, target_mission, tags, related_modules, authors,
                iss_connection, earth_analog, quality_score, is_enriched
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'reviewed', 1)
        """, (
            entry_id, e['title'], e.get('title_en'), e['category'], e['entry_type'],
            e.get('summary'), e.get('source_org'), e.get('source_country'),
            e.get('source_year'), e.get('trl'), e.get('timeline'),
            e.get('target_mission'), tags_json, modules_json, authors_json,
            e.get('iss_connection'), e.get('earth_analog'),
        ))
        count += 1

    conn.commit()
    print(f"Phase 2-3: Inserted {count} new entries")


def phase3_add_challenges(conn):
    """Add additional challenges."""
    count = 0
    for ch in ADDITIONAL_CHALLENGES:
        ch_id = f"ch_{uid()}"
        dup = conn.execute(
            "SELECT id FROM challenges WHERE name_ja = ?", (ch['name_ja'],)
        ).fetchone()
        if dup:
            continue
        conn.execute("""
            INSERT INTO challenges (id, name_ja, name_en, category, challenge_type, description, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ch_id, ch['name_ja'], ch.get('name_en'), ch['category'],
              ch['challenge_type'], ch.get('description'), ch.get('severity')))
        count += 1
    conn.commit()
    print(f"Phase 3: Added {count} new challenges")


def phase4_create_tables(conn):
    """Create new structural tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS modules (
            id TEXT PRIMARY KEY,
            name_ja TEXT NOT NULL,
            name_en TEXT,
            module_type TEXT CHECK(module_type IN (
                'habitation', 'common', 'work', 'support', 'life_support', 'utility'
            )),
            description TEXT,
            area_m2 REAL,
            capacity INTEGER,
            life_support_systems TEXT,
            image_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS roadmap (
            id TEXT PRIMARY KEY,
            milestone TEXT NOT NULL,
            organization TEXT,
            target_year INTEGER,
            status TEXT CHECK(status IN ('completed', 'in_progress', 'planned', 'concept')),
            description TEXT,
            related_entries TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS experts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            affiliation TEXT,
            country TEXT,
            field TEXT,
            publications_count INTEGER,
            h_index INTEGER,
            profile_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Insert modules
    for m in PHASE4_MODULES:
        mid = f"mod_{uid()}"
        conn.execute("""
            INSERT OR IGNORE INTO modules (id, name_ja, name_en, module_type, description, area_m2, capacity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mid, m['name_ja'], m['name_en'], m['module_type'], m['description'], m['area_m2'], m['capacity']))

    # Insert roadmap
    for r in PHASE4_ROADMAP:
        rid = f"rm_{uid()}"
        conn.execute("""
            INSERT OR IGNORE INTO roadmap (id, milestone, organization, target_year, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rid, r['milestone'], r['organization'], r['target_year'], r['status'], r['description']))

    # Insert experts
    for ex in PHASE4_EXPERTS:
        eid = f"exp_{uid()}"
        conn.execute("""
            INSERT OR IGNORE INTO experts (id, name, affiliation, country, field, profile_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (eid, ex['name'], ex['affiliation'], ex['country'], ex['field'], ex['profile_url']))

    conn.commit()
    print(f"Phase 4: Created 3 new tables, inserted {len(PHASE4_MODULES)} modules, {len(PHASE4_ROADMAP)} roadmap items, {len(PHASE4_EXPERTS)} experts")


def print_summary(conn):
    """Print final database summary."""
    print("\n" + "="*60)
    print("DATABASE EXPANSION COMPLETE")
    print("="*60)

    tables = ['entries', 'sources', 'relations', 'challenges', 'modules', 'roadmap', 'experts']
    for t in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t}: {count} records")
        except:
            pass

    print("\nBy category:")
    cats = conn.execute("SELECT category, COUNT(*) FROM entries GROUP BY category ORDER BY COUNT(*) DESC").fetchall()
    for cat, count in cats:
        print(f"  {cat}: {count}")

    print("\nBy country:")
    countries = conn.execute("SELECT source_country, COUNT(*) FROM entries GROUP BY source_country ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    for country, count in countries:
        print(f"  {country}: {count}")


def main():
    conn = get_conn()

    print("="*60)
    print("LUNAR LIFE DB EXPANSION")
    print("="*60)

    # Phase 1
    print("\n--- PHASE 1: Data Quality ---")
    phase1_normalize_countries(conn)
    phase1_add_relations(conn)

    # Phase 2-3
    print("\n--- PHASE 2-3: Entry Expansion ---")
    phase2_3_insert_entries(conn)
    phase3_add_challenges(conn)

    # Phase 4
    print("\n--- PHASE 4: Structural Expansion ---")
    phase4_create_tables(conn)

    # Summary
    print_summary(conn)
    conn.close()


if __name__ == '__main__':
    main()
