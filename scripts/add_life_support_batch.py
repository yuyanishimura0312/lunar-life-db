#!/usr/bin/env python3
import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lunar_life.db")


def make_entry(
    title,
    title_en,
    category,
    entry_type,
    source_org,
    source_country,
    source_year,
    trl,
    timeline,
    tags,
    detail,
    impact,
    target_mission=None,
    related_modules=None,
    authors=None,
    iss_connection=None,
    earth_analog=None,
):
    summary = (
        f"{source_org}が進める{title_en}に関する{entry_type}項目です。"
        f"{detail} 月面拠点での{impact}に役立つ知見として参照されています。"
    )
    return {
        "title": title,
        "title_en": title_en,
        "category": category,
        "entry_type": entry_type,
        "summary": summary,
        "source_org": source_org,
        "source_country": source_country,
        "source_year": source_year,
        "trl": trl,
        "timeline": timeline,
        "target_mission": target_mission,
        "tags": tags,
        "related_modules": related_modules or [],
        "authors": authors or [],
        "iss_connection": iss_connection,
        "earth_analog": earth_analog,
    }


def build_food_entries():
    entries = []
    add = entries.append
    category = "food"

    items = [
        ("Veggieレッドロメインレタス栽培", "Veggie Red Romaine Lettuce Growth", "research", "NASA", "US", 2015, 8, "ongoing", ["Veggie", "lettuce", "ISS"], "ISSのVeggie装置で赤ロメインレタスを育成し、収穫後の微生物安全性と食味評価まで実施しました。", "生鮮野菜の供給"),
        ("Veggieアウトレジャスレタス試験", "Veggie Outredgeous Lettuce Trial", "research", "NASA", "US", 2014, 7, "completed", ["Veggie", "Outredgeous", "crop trial"], "宇宙用LED条件下でOutredgeous系統の生育性能を評価した初期の代表試験です。", "作物選抜"),
        ("Veggieミズナ栽培実験", "Veggie Mizuna Cultivation Experiment", "research", "NASA", "US", 2016, 7, "completed", ["Veggie", "mizuna", "leafy greens"], "葉物野菜として生育が早いミズナを用い、収穫サイクルと風味の変化を比較しました。", "短期栽培メニューの拡充"),
        ("Veggieジニア開花実験", "Veggie Zinnia Flowering Experiment", "research", "NASA", "US", 2016, 6, "completed", ["Veggie", "zinnia", "flowering"], "食用ではないジニアを使って開花制御と病害対応を検証し、のちの果菜栽培の運用知見を蓄積しました。", "栽培運用の安定化"),
        ("Plant Habitat-03ラディッシュ栽培", "Plant Habitat-03 Radish Experiment", "research", "NASA", "US", 2020, 8, "completed", ["APH", "radish", "Plant Habitat-03"], "APHで20日余りのラディッシュ栽培を行い、根菜の可食部形成と栄養成分を解析しました。", "根菜の導入"),
        ("Plant Habitat-04ハッチチリ栽培", "Plant Habitat-04 Hatch Chile Pepper Experiment", "research", "NASA", "US", 2021, 8, "completed", ["APH", "pepper", "Plant Habitat-04"], "果菜類として初めて本格的に唐辛子を栽培し、開花、結実、味覚満足度まで確認しました。", "嗜好性の高い作物供給"),
        ("XROOTS宇宙水耕栽培システム", "XROOTS Space Hydroponic System", "technology", "NASA", "US", 2021, 6, "ongoing", ["XROOTS", "hydroponics", "roots"], "土壌を使わず液相と気相を切り替える根域制御で、水と空気の供給効率を高める技術です。", "省資源栽培"),
        ("PONDS受動型軌道栄養供給システム", "Passive Orbital Nutrient Delivery System", "technology", "NASA", "US", 2021, 6, "ongoing", ["PONDS", "nutrients", "passive"], "ポンプ依存を減らした受動型の栄養液供給手法で、小型宇宙植物実験の運用性を改善します。", "低保守化"),
        ("APEX-07宇宙種子発芽研究", "APEX-07 Space Seed Germination Study", "research", "NASA", "US", 2013, 5, "completed", ["APEX", "germination", "Arabidopsis"], "シロイヌナズナを用いて微小重力が発芽初期と細胞壁応答に与える影響を調べました。", "栽培基礎生理の理解"),
        ("Seedling Growth微小重力植物応答実験", "Seedling Growth Plant Response Study", "research", "NASA", "US", 2014, 6, "completed", ["Seedling Growth", "roots", "ISS"], "苗の根とシュートの方向性を観察し、低重力での成長シグナル変化を比較しました。", "重力依存性の把握"),
        ("Seedling Growth-2光屈性比較試験", "Seedling Growth-2 Phototropism Study", "research", "NASA", "US", 2017, 6, "completed", ["Seedling Growth-2", "phototropism", "Arabidopsis"], "光刺激と重力刺激の相互作用を切り分け、低重力での植物形態形成を解析しました。", "環境制御アルゴリズムの改善"),
        ("Advanced Plant Habitat綿花栽培試験", "Advanced Plant Habitat Cotton Growth Trial", "research", "NASA", "US", 2021, 7, "completed", ["APH", "cotton", "fiber crop"], "綿花を使って長期開花作物の生育管理とストレス耐性応答を観察しました。", "多用途作物の選定"),
        ("APHデュワーフトマト栽培", "APH Dwarf Tomato Cultivation", "research", "NASA", "US", 2023, 7, "ongoing", ["APH", "tomato", "fruit crop"], "小型トマト品種を対象に果実生産、受粉支援、香味保持を検証する系統試験です。", "果菜類の安定生産"),
        ("ISS小麦成長チャンバー研究", "ISS Wheat Growth Chamber Study", "research", "NASA", "US", 2003, 5, "completed", ["wheat", "growth chamber", "ISS"], "宇宙ステーション時代初期の小麦栽培研究で、穀物系作物の閉鎖環境適応を評価しました。", "主食候補の検討"),
        ("CELSS小麦・大豆統合試験", "CELSS Wheat and Soybean Integration Test", "research", "University of Arizona", "US", 1997, 4, "completed", ["CELSS", "wheat", "soybean"], "Controlled Ecological Life Support System研究の一環として穀物と豆類の組み合わせ生産を検証しました。", "完全食料系の設計"),
        ("University of Arizona月惑星温室研究", "University of Arizona Lunar Greenhouse Study", "project", "University of Arizona", "US", 2007, 5, "ongoing", ["Lunar Greenhouse", "CEA", "Arizona"], "月面・火星向け温室構想として、閉鎖環境農業と居住系の統合設計を続けています。", "月面温室の設計最適化"),
        ("EDEN ISS温室制御アーキテクチャ", "EDEN ISS Greenhouse Control Architecture", "technology", "DLR", "DE", 2018, 7, "ongoing", ["EDEN ISS", "greenhouse", "control"], "南極実証温室で用いられた環境制御、衛生管理、遠隔運用の統合アーキテクチャです。", "遠隔植物工場運用"),
        ("MELiSSA Higher Plant Compartment", "MELiSSA Higher Plant Compartment", "technology", "ESA", "EU", 2019, 6, "ongoing", ["MELiSSA", "higher plants", "bioregenerative"], "MELiSSAの高等植物区画で食料生産とCO2固定を同時に担う構成を検証しています。", "閉鎖循環食料生産"),
        ("MELiSSA微細藻類コンパートメント", "MELiSSA Microalgae Compartment", "technology", "ESA", "EU", 2019, 6, "ongoing", ["MELiSSA", "microalgae", "spirulina"], "藻類を使って食料とガス交換を兼ねるユニットとして設計され、再生型生命維持の核を成します。", "高効率タンパク供給"),
        ("Lunar Palace 1閉鎖生態系食料試験", "Lunar Palace 1 Closed Ecosystem Food Trial", "project", "Beihang University", "CN", 2018, 6, "completed", ["Lunar Palace 1", "closed ecosystem", "China"], "105日と370日の長期閉鎖試験で植物由来食料の供給と廃棄物循環を検証しました。", "長期自給体制の構築"),
        ("BIOS-3閉鎖生態系食料研究", "BIOS-3 Closed Ecological Food Research", "project", "Institute of Biophysics SB RAS", "RU", 1972, 5, "completed", ["BIOS-3", "closed ecosystem", "Soviet"], "ソ連時代の閉鎖生態系施設で藻類と作物による食料・空気再生を試みた古典的研究です。", "長期閉鎖系の基礎設計"),
        ("Biosphere 2食料自給ケーススタディ", "Biosphere 2 Food Self-Sufficiency Case Study", "case_study", "Biosphere 2", "US", 1991, 4, "completed", ["Biosphere 2", "food", "analog"], "大規模閉鎖環境での食料生産の難しさと栄養不足リスクを示した代表例として引用されています。", "月面農業のリスク評価"),
        ("Eu:CROPIS尿素肥料循環実証", "Eu:CROPIS Urine Fertilizer Demonstration", "project", "DLR", "DE", 2018, 5, "completed", ["Eu:CROPIS", "fertilizer", "biocycle"], "人工重力条件と尿由来栄養塩利用を組み合わせた小型衛星実証で、循環型栽培を試しました。", "養分循環"),
        ("BioNutrientsオンデマンド栄養素生産", "BioNutrients On-Demand Nutrient Production", "technology", "NASA", "US", 2020, 5, "ongoing", ["BioNutrients", "fermentation", "nutrition"], "微生物発酵で長期ミッション中に栄養補助成分を必要時に生産する構想です。", "栄養補完"),
        ("Aleph Farms ISS培養肉実証", "Aleph Farms ISS Cultivated Meat Demonstration", "project", "Aleph Farms / 3D Bioprinting Solutions", "IL", 2019, 4, "completed", ["cultivated meat", "ISS", "protein"], "ISS上で牛細胞を培養し、宇宙環境での細胞ベース食料生産の成立性を示しました。", "動物性タンパクの現地生産"),
        ("ESA Spirulina宇宙利用研究", "ESA Spirulina Space Utilization Study", "research", "ESA", "EU", 2018, 5, "ongoing", ["spirulina", "microalgae", "protein"], "スピルリナを高タンパク・高ビタミン食材として扱い、閉鎖系での培養条件を検討しています。", "高密度栄養供給"),
        ("DLRシアノバクテリアCyBLiSS研究", "CyBLiSS Cyanobacteria Study", "research", "University of Bremen", "DE", 2020, 4, "completed", ["CyBLiSS", "cyanobacteria", "regolith"], "シアノバクテリアをレゴリスシミュラント上で育成し、食料・酸素・バイオ資材源としての利用可能性を評価しました。", "現地資源利用型生産"),
        ("Wageningenレゴリスシミュラント作物栽培", "Wageningen Regolith Simulant Crop Cultivation", "research", "Wageningen University & Research", "NL", 2016, 4, "completed", ["regolith simulant", "crop cultivation", "WUR"], "月・火星模擬土壌で食用作物を栽培し、重金属蓄積と収量の関係を調べました。", "土壌利用の安全評価"),
        ("NASA宇宙食官能評価プログラム", "NASA Space Food Sensory Evaluation Program", "research", "NASA Johnson Space Center", "US", 2018, 8, "ongoing", ["sensory", "menu fatigue", "space food"], "長期保存後の味、香り、食感の変化を継続評価し、メニュー疲労の低減につなげています。", "食事満足度の維持"),
        ("NASA 5年保存宇宙食安定性研究", "NASA Five-Year Shelf Life Study", "research", "NASA", "US", 2017, 8, "ongoing", ["shelf life", "nutrition", "packaging"], "探査ミッション向けに5年保存を前提とした栄養劣化と包装性能の追跡試験です。", "長期備蓄"),
        ("NASA熱安定化宇宙食技術", "NASA Thermostabilized Space Food Technology", "technology", "NASA", "US", 2016, 9, "ongoing", ["thermostabilized", "processing", "space food"], "高温殺菌で安全性を確保しつつ常温長期保存を可能にする代表的な宇宙食加工法です。", "安全な保存食供給"),
        ("NASAフリーズドライ宇宙食技術", "NASA Freeze-Dried Space Food Technology", "technology", "NASA", "US", 2016, 9, "ongoing", ["freeze-dried", "dehydration", "space food"], "質量を抑えながら保存性を高める乾燥技術で、飲料や果物系メニューに広く使われます。", "輸送質量の削減"),
        ("NASA照射肉宇宙食技術", "NASA Irradiated Meat Space Food Technology", "technology", "NASA", "US", 2016, 9, "ongoing", ["irradiated meat", "sterilization", "protein"], "高タンパク食品の微生物安全性を維持するための照射処理技術として探査食に組み込まれています。", "安全なたんぱく源確保"),
        ("NASAレトルトパウチ包装研究", "NASA Retort Pouch Packaging Study", "technology", "NASA", "US", 2018, 8, "ongoing", ["retort pouch", "packaging", "barrier film"], "酸素・水蒸気バリアを確保する多層パウチ設計で、長期保存食の品質を支えます。", "包装信頼性の向上"),
        ("JAXA宇宙日本食メニュー開発", "JAXA Space Japanese Food Menu Development", "project", "JAXA", "JP", 2019, 9, "ongoing", ["JAXA", "Japanese food", "menu"], "日本企業と共同で和食の保存性と食べやすさを両立した認証メニューを拡充しています。", "文化的受容性の向上"),
        ("CSA microgreens宇宙栽培研究", "CSA Microgreens Space Cultivation Study", "research", "Canadian Space Agency", "CA", 2022, 4, "ongoing", ["microgreens", "CSA", "fresh food"], "短期間で収穫可能なマイクログリーンを対象に、栄養価と運用負荷のバランスを調べています。", "即応性の高い生鮮供給"),
        ("CNES閉鎖環境パン製造概念", "CNES Closed-Environment Breadmaking Concept", "concept", "CNES", "FR", 2021, 3, "ongoing", ["bread", "processing", "CNES"], "粉体飛散や発酵管理の制約を踏まえ、閉鎖環境向けに再設計したパン製造の概念検討です。", "主食加工の多様化"),
        ("BeeHex宇宙3Dフードプリンティング", "BeeHex 3D Food Printing for Space", "technology", "BeeHex", "US", 2019, 5, "ongoing", ["3D food printing", "BeeHex", "custom nutrition"], "個人ごとの栄養要求に合わせて食材を積層する食品プリント技術としてNASA関連研究で注目されました。", "個別化食"),
        ("ESA閉鎖環境発酵食品研究", "ESA Fermented Foods in Closed Habitats", "research", "ESA", "EU", 2022, 4, "ongoing", ["fermentation", "microbiome", "closed habitat"], "発酵による保存性向上と腸内環境改善を狙い、味噌やヨーグルト類似食品の可能性を調べています。", "栄養と嗜好の両立"),
        ("KSC食用菌類宇宙栽培評価", "KSC Edible Mushroom Space Cultivation Assessment", "research", "NASA Kennedy Space Center", "US", 2022, 3, "ongoing", ["mushroom", "fungi", "KSC"], "菌糸体ベースの高効率食料としてキノコ栽培の閉鎖環境適応を評価しています。", "副産物利用型食料生産"),
        ("USDA-NASA宇宙作物品種選定", "NASA-USDA Space Crop Variety Screening", "research", "NASA / USDA", "US", 2021, 4, "ongoing", ["variety screening", "USDA", "crop breeding"], "低背性、短周期、高栄養の品種を比較し、探査ミッション向け作物リストを絞り込んでいます。", "作物ポートフォリオ最適化"),
        ("Purdue宇宙LED光レシピ研究", "Purdue Space LED Recipe Study", "research", "Purdue University", "US", 2021, 4, "ongoing", ["LED", "light recipe", "Purdue"], "波長比と日長が収量、色、栄養価に与える影響を系統的に計測しています。", "省電力栽培"),
        ("Cornell宇宙受粉支援研究", "Cornell Assisted Pollination in Space Study", "research", "Cornell University", "US", 2022, 3, "ongoing", ["pollination", "fruit crops", "Cornell"], "果菜類栽培で必要となる手動・機械的受粉方法の比較検討です。", "果実収量の安定化"),
        ("ISS植物微生物安全性評価", "ISS Plant Microbial Safety Assessment", "research", "NASA", "US", 2016, 7, "ongoing", ["microbial safety", "fresh produce", "ISS"], "宇宙で育てた可食植物の表面微生物を評価し、生食の安全基準づくりに使われています。", "食中毒リスク低減"),
        ("NASA宇宙食ビタミンC劣化追跡", "NASA Vitamin C Degradation Tracking in Space Foods", "research", "NASA", "US", 2020, 7, "ongoing", ["vitamin C", "nutrition stability", "shelf life"], "長期保存中に失われやすいビタミンCの保持対策を重点的に分析しています。", "欠乏症予防"),
        ("NASA宇宙食オメガ3保持研究", "NASA Omega-3 Retention Study for Space Foods", "research", "NASA", "US", 2020, 6, "ongoing", ["omega-3", "lipid oxidation", "nutrition"], "脂質酸化の進みやすい食品で必須脂肪酸をどこまで保持できるかを評価しています。", "心血管・認知機能支援"),
        ("JAXA宇宙米飯加工研究", "JAXA Space Rice Processing Study", "research", "JAXA", "JP", 2018, 7, "ongoing", ["rice", "processing", "JAXA"], "粘着性や飛散防止を考慮した米飯加工技術を日本食メニュー向けに最適化しています。", "主食の実装"),
        ("ISRO宇宙食チャパティ開発", "ISRO Space Chapati Development", "project", "ISRO", "IN", 2023, 5, "ongoing", ["ISRO", "chapati", "crew food"], "インド有人宇宙飛行を見据え、地域食文化に合う保存食メニューとしてチャパティ系食品を研究しています。", "多国籍クルー対応"),
        ("ESA宇宙向けダックウィード研究", "ESA Duckweed for Space Food Study", "research", "ESA", "EU", 2023, 4, "ongoing", ["duckweed", "protein", "fast growth"], "高速成長で可食タンパク源となるウキクサ類の閉鎖環境栽培を検討しています。", "超短周期食材の活用"),
        ("NASA single-cell protein概念評価", "NASA Single-Cell Protein Concept Assessment", "concept", "NASA", "US", 2022, 3, "ongoing", ["single-cell protein", "microbial food", "concept"], "酵母や細菌を原料とする単細胞タンパクの宇宙利用性を比較する概念評価です。", "非常時食料の確保"),
        ("TUM宇宙昆虫タンパク研究", "TUM Insect Protein for Space Study", "research", "Technical University of Munich", "DE", 2022, 3, "ongoing", ["insect protein", "mealworm", "TUM"], "ミールワームなどの昆虫を高効率タンパク源として閉鎖環境で育成する可能性を調べています。", "資源効率の高いタンパク生産"),
        ("MIT宇宙アクアポニクス概念", "MIT Space Aquaponics Concept", "concept", "MIT", "US", 2021, 2, "ongoing", ["aquaponics", "MIT", "closed loop"], "魚類養殖と水耕栽培を結ぶ循環食料系の概念で、水と栄養の再利用を重視しています。", "複合型食料生産"),
        ("NASA宇宙食品HACCP運用", "NASA HACCP for Space Food Operations", "technology", "NASA", "US", 2019, 8, "ongoing", ["HACCP", "food safety", "operations"], "宇宙食製造と搭載運用における危害要因分析と重要管理点管理の実装です。", "衛生管理の標準化"),
        ("KSC宇宙作物塩ストレス評価", "KSC Space Crop Salt Stress Assessment", "research", "NASA Kennedy Space Center", "US", 2022, 3, "ongoing", ["salt stress", "crop resilience", "KSC"], "再生水利用を想定し、塩濃度変動に強い作物を選抜する研究です。", "再生水との適合性向上"),
        ("NASA宇宙作物ナトリウム管理研究", "NASA Sodium Management for Space Crops", "research", "NASA", "US", 2021, 3, "ongoing", ["sodium", "crop nutrition", "hydroponics"], "栄養液中のナトリウム蓄積が植物品質に及ぼす影響を追跡しています。", "閉鎖循環栽培の安定化"),
        ("ESA宇宙作物フェノール化合物研究", "ESA Phenolic Compounds in Space Crops Study", "research", "ESA", "EU", 2022, 3, "ongoing", ["phenolics", "nutritional quality", "ESA"], "低重力・高放射線ストレスで変化する抗酸化成分の含有量を評価しています。", "機能性食品化"),
        ("NASA宇宙食メニュー疲労研究", "NASA Menu Fatigue Study", "research", "NASA Human Research Program", "US", 2019, 7, "ongoing", ["menu fatigue", "behavioral health", "food systems"], "長期滞在で同じメニューを反復した際の摂食量低下と心理影響を調べる研究です。", "食欲維持"),
        ("DLR月面温室リモート運用研究", "DLR Remote Lunar Greenhouse Operations Study", "research", "DLR", "DE", 2021, 5, "ongoing", ["remote ops", "greenhouse", "DLR"], "通信遅延を含む遠隔農業運用の手順と故障対応を実証温室で検証しています。", "少人数運用"),
        ("NASA作物残渣バイオマス利用概念", "NASA Crop Residue Biomass Utilization Concept", "concept", "NASA", "US", 2022, 2, "ongoing", ["biomass", "residue", "circular food"], "非可食部を堆肥化、飼料化、材料化する循環利用の概念整理です。", "廃棄物最小化"),
        ("UCLA宇宙味覚個別化研究", "UCLA Personalized Taste in Space Study", "research", "UCLA", "US", 2023, 2, "ongoing", ["taste", "personalization", "UCLA"], "味覚変化と嗜好差を踏まえた個別メニュー提案の可能性を探る研究です。", "摂食量最適化"),
        ("NASA食用花宇宙栽培研究", "NASA Edible Flowers in Space Study", "research", "NASA", "US", 2022, 2, "ongoing", ["edible flowers", "crew morale", "horticulture"], "見た目や香りの多様性が心理面に与える効果を重視した食用花栽培の検討です。", "食体験の改善"),
        ("ESA宇宙向け根菜収穫性研究", "ESA Root Crop Harvestability Study", "research", "ESA", "EU", 2022, 2, "ongoing", ["root crops", "harvest", "ESA"], "根菜類の洗浄、切断、保存手順まで含めた運用性を評価しています。", "主食補完作物の導入"),
        ("NASA月面食品物流モデル", "NASA Lunar Food Logistics Model", "concept", "NASA", "US", 2021, 3, "ongoing", ["logistics", "food stock", "mission planning"], "現地生産と地球補給を組み合わせた在庫モデルで、欠品と過剰輸送の両方を抑える考え方です。", "補給計画の最適化"),
        ("Space Food Systems Laboratory探査食設計", "Space Food Systems Laboratory Exploration Diet Design", "research", "NASA Johnson Space Center", "US", 2021, 8, "ongoing", ["SFSL", "diet design", "exploration"], "探査ミッション向けに保存性、調理性、栄養密度を総合設計する実務研究です。", "長期探査食の設計"),
        ("NASA宇宙作物微量栄養素強化研究", "NASA Micronutrient Enrichment of Space Crops", "research", "NASA", "US", 2023, 3, "ongoing", ["micronutrients", "biofortification", "crops"], "鉄やビタミン類を強化した作物系統の検討で、長期滞在中の栄養欠乏を防ぐ狙いがあります。", "栄養密度向上"),
        ("JAXA発酵大豆宇宙食品研究", "JAXA Fermented Soy Space Food Study", "research", "JAXA", "JP", 2022, 4, "ongoing", ["soy", "fermentation", "JAXA"], "大豆ベース食品を発酵で高機能化し、保存性と嗜好性を両立する研究です。", "植物性タンパク利用"),
        ("NASA宇宙作物収穫後処理研究", "NASA Post-Harvest Processing for Space Crops", "research", "NASA", "US", 2022, 4, "ongoing", ["post-harvest", "processing", "fresh food"], "収穫後の洗浄、切断、簡易包装まで含めた運用工程を整備する研究です。", "生鮮食品の衛生供給"),
        ("ESA食料・酸素共生設計概念", "ESA Food and Oxygen Co-Design Concept", "concept", "ESA", "EU", 2021, 3, "ongoing", ["bioregenerative", "co-design", "ESA"], "植物・藻類を食料と空気再生の両方に使う共生設計の考え方です。", "システム統合"),
        ("NASA宇宙作物心理効果研究", "NASA Psychological Benefits of Crop Care Study", "research", "NASA Human Research Program", "US", 2022, 3, "ongoing", ["behavioral health", "crop care", "crew"], "植物の世話がストレス低減と生活リズム維持に与える影響を評価しています。", "メンタルヘルス支援"),
        ("CNSA月面食料再生生態系概念", "CNSA Lunar Bioregenerative Food Ecosystem Concept", "concept", "CNSA", "CN", 2023, 3, "ongoing", ["CNSA", "bioregenerative", "lunar base"], "中国の月面拠点構想で検討される再生型食料系の概念で、植物・微生物・廃棄物循環を一体化します。", "自給率向上"),
    ]

    for item in items:
        add(
            make_entry(
                item[0],
                item[1],
                category,
                item[2],
                item[3],
                item[4],
                item[5],
                item[6],
                item[7],
                item[8],
                detail=item[9],
                impact=item[10],
            )
        )

    assert len(entries) == 70
    return entries


def build_water_entries():
    entries = []
    add = entries.append
    category = "water"

    items = [
        ("Lunar Prospector中性子分光水素探査", "Lunar Prospector Neutron Spectrometer Hydrogen Survey", category, "research", "NASA", "US", 1998, 9, "completed", ["Lunar Prospector", "neutron spectrometer", "hydrogen"], "中性子データから極域地下に水素濃集域があることを示し、月面水探査の方向性を決定づけました。", "極域資源探査"),
        ("Clementine双基地レーダー水氷解析", "Clementine Bistatic Radar Ice Analysis", category, "research", "NASA / DoD", "US", 1994, 8, "completed", ["Clementine", "radar", "ice"], "月極域反射特性から水氷の可能性をめぐる初期議論を生んだ解析です。", "遠隔探査手法の確立"),
        ("Mini-SAR月極域レーダー偏波観測", "Mini-SAR Polarimetric Radar Observation", category, "research", "ISRO / NASA", "IN", 2009, 8, "completed", ["Mini-SAR", "polarimetry", "ice"], "偏波比解析で永久影クレーター内の氷様シグナルを抽出しました。", "水氷候補地点の絞り込み"),
        ("LRO LEND水素マッピング", "LRO LEND Hydrogen Mapping", category, "research", "NASA", "US", 2009, 8, "ongoing", ["LRO", "LEND", "hydrogen"], "月周回軌道から中性子観測を行い、水素分布の全球地図を更新しました。", "着陸候補地評価"),
        ("LRO LAMP紫外分光水氷検出", "LRO LAMP Ultraviolet Ice Detection", category, "research", "NASA", "US", 2010, 8, "ongoing", ["LAMP", "ultraviolet", "ice"], "紫外反射分光で永久影領域の表層氷存在を推定する観測です。", "低温トラップ評価"),
        ("LRO Diviner極低温コールドトラップ解析", "LRO Diviner Cold Trap Analysis", category, "research", "NASA", "US", 2010, 8, "ongoing", ["Diviner", "cold trap", "temperature"], "表面温度分布から氷が長期安定に存在しうるコールドトラップ領域を抽出しました。", "採掘候補地評価"),
        ("LunaH-Map月極域中性子観測", "LunaH-Map Polar Neutron Observation", category, "project", "Arizona State University / NASA", "US", 2022, 6, "ongoing", ["LunaH-Map", "CubeSat", "neutron"], "超低高度から南極域の水素分布を高解像度で測るCubeSat計画です。", "局所資源探査"),
        ("Lunar Flashlight近赤外レーザー氷探索", "Lunar Flashlight Near-Infrared Laser Ice Search", category, "project", "NASA JPL", "US", 2022, 6, "ongoing", ["Lunar Flashlight", "laser", "ice"], "能動レーザー照射で永久影領域表層の氷シグナルを探る小型衛星実証です。", "低コスト探査"),
        ("Lunar Trailblazer月面水分布観測", "Lunar Trailblazer Global Water Mapping", category, "project", "Caltech / NASA", "US", 2022, 6, "ongoing", ["Lunar Trailblazer", "mapping", "orbiter"], "赤外分光と熱観測を組み合わせ、時間変動を含む月面水分布の把握を目指します。", "資源マップ整備"),
        ("VIPER TRIDENTドリル", "VIPER TRIDENT Drill", category, "technology", "Honeybee Robotics / NASA", "US", 2023, 7, "ongoing", ["VIPER", "TRIDENT", "drill"], "1m級掘削で揮発性物質の深さ分布を取得する月面氷探査用ドリルです。", "地下氷直接確認"),
        ("VIPER MSolo質量分析計", "VIPER MSolo Mass Spectrometer", category, "technology", "NASA", "US", 2023, 7, "ongoing", ["VIPER", "MSolo", "mass spectrometer"], "掘削試料の加熱放出ガスを分析し、水や揮発性成分の種類を識別します。", "資源品位評価"),
        ("VIPER NIRVSS揮発性分光器", "VIPER NIRVSS Spectrometer", category, "technology", "NASA Ames Research Center", "US", 2023, 7, "ongoing", ["VIPER", "NIRVSS", "spectrometer"], "近赤外分光で表層の水・鉱物・温度情報を同時取得する機器です。", "氷分布推定"),
        ("VIPER NSS中性子分光装置", "VIPER NSS Neutron Spectrometer System", category, "technology", "NASA", "US", 2023, 7, "ongoing", ["VIPER", "NSS", "neutron"], "移動しながら地下の水素濃度変化を測れるローバー搭載中性子計です。", "走行型資源マッピング"),
        ("PROSPECT PROSEED試料処理系", "PROSPECT PROSEED Sample Processing System", category, "technology", "ESA", "EU", 2021, 6, "ongoing", ["PROSPECT", "PROSEED", "sample processing"], "掘削試料を加熱し揮発成分を分析系へ導く処理モジュールです。", "ISRU前段評価"),
        ("PROSPECT ProSPA分析ラボ", "PROSPECT ProSPA Analysis Laboratory", category, "technology", "ESA", "EU", 2021, 6, "ongoing", ["PROSPECT", "ProSPA", "volatile analysis"], "掘削した月面物質中の水と揮発性分子をその場分析する小型ラボです。", "揮発性資源の定量"),
        ("Luna-27揮発性資源探査", "Luna-27 Volatile Resource Investigation", category, "project", "Roscosmos / ESA", "RU", 2021, 5, "planned", ["Luna-27", "ESA", "volatiles"], "月面極域で水と揮発性物質を直接測る着陸探査計画として位置づけられています。", "極域資源の地上真値取得"),
        ("Chandrayaan-1 M3月面水分光観測", "Chandrayaan-1 M3 Water Spectral Observation", category, "research", "ISRO / NASA", "IN", 2009, 9, "completed", ["M3", "Chandrayaan-1", "spectroscopy"], "月面広域にOH/H2O吸収帯を確認し、世界的に月面水研究を加速させました。", "全球水分布の把握"),
        ("LCROSS Cabeus噴出物分析", "LCROSS Cabeus Ejecta Analysis", category, "research", "NASA", "US", 2009, 9, "completed", ["LCROSS", "Cabeus", "ejecta"], "衝突噴出物から水氷を直接検出し、極域資源の実在性を強く支持しました。", "掘削価値の検証"),
        ("SOFIA 6ミクロン分子水検出", "SOFIA 6-Micron Molecular Water Detection", category, "research", "NASA / DLR", "US", 2020, 9, "completed", ["SOFIA", "6 micron", "molecular water"], "OHではなく分子状H2Oを識別できる波長帯で観測し、月面表層水の議論を進めました。", "水状態の識別"),
        ("Chang'e 5月面粒子中OH分析", "Chang'e 5 Hydroxyl Analysis in Lunar Samples", category, "research", "Chinese Academy of Sciences", "CN", 2022, 6, "ongoing", ["Chang'e 5", "samples", "OH"], "持ち帰り試料を用いて太陽風起源のOH形成に関する実験室分析が進められています。", "形成メカニズム解明"),
        ("ISS Water Recovery System", "ISS Water Recovery System", category, "technology", "NASA", "US", 2008, 9, "ongoing", ["WRS", "ISS", "recycling"], "尿、凝縮水、衛生系排水を再生して飲用水に戻す現行宇宙水循環の基幹システムです。", "高自給率生活"),
        ("ISS Urine Processor Assembly", "ISS Urine Processor Assembly", category, "technology", "NASA", "US", 2008, 9, "ongoing", ["UPA", "urine", "distillation"], "蒸気圧縮蒸留で尿から回収可能な水分を取り出す装置です。", "廃水再利用"),
        ("ISS Water Processor Assembly", "ISS Water Processor Assembly", category, "technology", "NASA", "US", 2008, 9, "ongoing", ["WPA", "filtration", "catalytic oxidation"], "多段ろ過と触媒酸化で各種排水を飲用レベルまで浄化する装置です。", "飲料水の確保"),
        ("ISS Total Organic Carbon Analyzer", "ISS Total Organic Carbon Analyzer", category, "technology", "NASA", "US", 2009, 8, "ongoing", ["TOCA", "water quality", "monitoring"], "軌道上で水中有機物濃度を測り、水質悪化を早期に検出する分析装置です。", "水質監視"),
        ("ISS Multifiltration Bed System", "ISS Multifiltration Bed System", category, "technology", "NASA", "US", 2010, 8, "ongoing", ["multifiltration", "sorbent", "water"], "イオン交換樹脂や吸着材で微量汚染物質を除去する浄化ステージです。", "微量汚染管理"),
        ("ISS Catalytic Reactor水酸化処理", "ISS Catalytic Reactor Water Oxidation", category, "technology", "NASA", "US", 2010, 8, "ongoing", ["catalytic reactor", "oxidation", "water"], "残留有機物を高温触媒で分解し、再生水の最終安全性を高めます。", "長期浄化安定性"),
        ("Brine Processor Assembly", "Brine Processor Assembly", category, "technology", "NASA", "US", 2021, 7, "ongoing", ["BPA", "brine", "water recovery"], "尿処理残渣から追加で水を回収し、閉鎖系の総回収率をさらに高める装置です。", "回収率向上"),
        ("Oxygen Generation Assembly水電解", "Oxygen Generation Assembly", category, "technology", "NASA", "US", 2007, 9, "ongoing", ["OGA", "electrolysis", "oxygen"], "再生水を電気分解して呼吸用酸素を作り出すISSの主要ECLSS装置です。", "水と空気の統合管理"),
        ("Sabatier反応器水回収", "Sabatier Reactor Water Recovery", category, "technology", "NASA", "US", 2010, 8, "ongoing", ["Sabatier", "CO2 reduction", "water"], "二酸化炭素と水素からメタンと水を生成し、酸素系と連携して水利用効率を高めます。", "閉鎖循環率向上"),
        ("Bosch反応閉鎖系概念", "Bosch Reaction Closed-Loop Concept", category, "concept", "NASA", "US", 2021, 3, "ongoing", ["Bosch reaction", "closed loop", "concept"], "CO2から固体炭素と水を得る完全閉鎖型候補として再評価されている概念です。", "長期探査向け循環強化"),
        ("蒸気圧縮蒸留宇宙水再生技術", "Vapor Compression Distillation for Space Water Recovery", category, "technology", "NASA", "US", 2012, 8, "ongoing", ["vapor compression distillation", "water recovery", "ISS"], "限られたエネルギーで尿由来水分を効率回収する蒸留方式です。", "省エネ再生"),
        ("膜蒸留宇宙廃水再生研究", "Membrane Distillation for Space Wastewater", category, "research", "KIST", "KR", 2022, 4, "ongoing", ["membrane distillation", "wastewater", "KIST"], "ファウリング耐性に優れる膜蒸留を閉鎖環境水再生へ適用する研究です。", "メンテナンス性向上"),
        ("順浸透式宇宙水処理概念", "Forward Osmosis Space Water Treatment Concept", category, "concept", "NASA", "US", 2021, 3, "ongoing", ["forward osmosis", "water treatment", "concept"], "低圧条件で駆動できる膜分離法として探査向け適用性が検討されています。", "低電力浄化"),
        ("電気脱イオン宇宙水質仕上げ技術", "Electrodeionization Water Polishing for Space Systems", category, "technology", "ESA", "EU", 2022, 3, "ongoing", ["electrodeionization", "water polishing", "ESA"], "イオン性不純物を連続除去し、飲用規格へ仕上げる後段処理技術です。", "高純度水供給"),
        ("銀イオン宇宙水バイオ制御", "Silver Ion Biocontrol in Space Water Systems", category, "technology", "Roscosmos", "RU", 2015, 8, "ongoing", ["silver ions", "biocide", "water"], "ロシア系宇宙機で用いられてきた銀イオン系殺菌管理の知見です。", "配管内微生物制御"),
        ("ヨウ素系宇宙水殺菌管理", "Iodine-Based Water Biocide Management", category, "technology", "NASA", "US", 2014, 8, "ongoing", ["iodine", "biocide", "potable water"], "NASA系で使われてきたヨウ素殺菌管理とその除去手順に関する運用技術です。", "飲料水衛生"),
        ("宇宙水配管バイオフィルム対策研究", "Biofilm Control in Space Water Plumbing Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["biofilm", "plumbing", "water"], "閉鎖循環水システム内で形成されるバイオフィルムの抑制法を評価しています。", "長期信頼性"),
        ("月面レゴリス加熱昇華水抽出", "Thermal Sublimation Water Extraction from Lunar Regolith", category, "technology", "NASA", "US", 2022, 4, "ongoing", ["regolith", "sublimation", "ISRU"], "含水レゴリスを加熱して揮発分を回収する最も基本的なISRU水抽出プロセスです。", "現地水製造"),
        ("イルメナイト水素還元水生成", "Ilmenite Hydrogen Reduction Water Production", category, "technology", "NASA", "US", 2021, 4, "ongoing", ["ilmenite", "hydrogen reduction", "ISRU"], "イルメナイト中の酸素を水素還元で取り出し、水や酸素を得る古典的ISRU手法です。", "資源変換"),
        ("炭熱還元月面酸素・水資源概念", "Carbothermal Reduction for Lunar Oxygen and Water Resources", category, "concept", "NASA", "US", 2021, 3, "ongoing", ["carbothermal", "oxygen", "ISRU"], "高温処理で酸素資源を得る概念で、水系と組み合わせた資源循環も検討されます。", "ISRU多角化"),
        ("マイクロ波月面氷抽出研究", "Microwave Extraction of Lunar Ice Study", category, "research", "University of Central Florida", "US", 2020, 3, "ongoing", ["microwave", "ice extraction", "UCF"], "レゴリス内部を局所加熱して氷や吸着水を抽出する方法を評価しています。", "採掘効率向上"),
        ("月面永久影クレーター採氷ロボット概念", "Permanently Shadowed Region Ice Mining Robot Concept", category, "concept", "NASA", "US", 2022, 3, "ongoing", ["PSR", "mining robot", "concept"], "超低温環境での掘削、搬送、昇華回収を統合するロボット概念です。", "極域採掘自動化"),
        ("Honeybee Robotics PlanetVac含水レゴリス採取", "PlanetVac Hydrated Regolith Sampling", category, "technology", "Honeybee Robotics", "US", 2021, 6, "ongoing", ["PlanetVac", "sampling", "regolith"], "ガス流で表層試料を回収する採取技術で、水分分析前処理に向いています。", "低質量試料取得"),
        ("ispace月面水資源データサービス構想", "ispace Lunar Water Resource Data Service", category, "concept", "ispace", "JP", 2023, 3, "ongoing", ["ispace", "resource data", "commercial"], "探査データを商業利用につなげる水資源情報サービスの構想です。", "民間ISRU市場形成"),
        ("ESA Moonlight水資源通信支援構想", "ESA Moonlight Support for Lunar Resource Operations", category, "concept", "ESA", "EU", 2023, 3, "ongoing", ["Moonlight", "resource ops", "communications"], "極域水資源オペレーションを支える通信・測位基盤として位置づけられています。", "採掘運用の継続性"),
        ("JAXA水再生型与圧ローバー給水設計", "JAXA Closed-Loop Water Design for Pressurized Rover", category, "concept", "JAXA", "JP", 2022, 3, "ongoing", ["JAXA", "rover", "water loop"], "長期走行ローバー内での飲料水、衛生水、回収水の管理構想です。", "移動生活圏の自給性"),
        ("NASA水分活量制御包装研究", "NASA Water Activity Control Packaging Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["water activity", "food-water interface", "packaging"], "保存食の水分活量管理を通じて水資源と食品品質の両方を最適化する研究です。", "全体資源管理"),
        ("月面水物流バッファタンク概念", "Lunar Water Logistics Buffer Tank Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["buffer tank", "logistics", "water"], "採掘地点、基地、移動車両の間で水を中継貯蔵するインフラ概念です。", "供給安定化"),
        ("NASA可搬型月面水品質分析器", "Portable Lunar Water Quality Analyzer", category, "technology", "NASA", "US", 2023, 3, "ongoing", ["portable analyzer", "water quality", "lunar"], "現地抽出水に含まれる塩類や微粒子を迅速評価する携行分析器の概念です。", "現場判定"),
        ("ESA過塩素酸塩混入水処理研究", "ESA Perchlorate-Contaminated Water Treatment Study", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["perchlorate", "treatment", "ESA"], "有害塩類が混入した場合の除去法とシステム影響を検討しています。", "水安全性の確保"),
        ("NASA低重力気液分離給水研究", "NASA Low-Gravity Phase Separation for Water Systems", category, "research", "NASA Glenn Research Center", "US", 2021, 4, "ongoing", ["phase separation", "low gravity", "water"], "低重力下で気泡と液体を確実に分離する流体管理研究です。", "再生系安定運転"),
        ("JPL水氷安定性時間変動モデル", "JPL Temporal Stability Model of Lunar Ice", category, "research", "NASA JPL", "US", 2022, 3, "ongoing", ["ice stability", "model", "JPL"], "温度と照明変動を考慮して極域氷の長期安定性をシミュレートしています。", "採掘持続性評価"),
        ("NASA月面水採掘エネルギー収支研究", "NASA Lunar Water Mining Energy Balance Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["energy balance", "water mining", "ISRU"], "採掘、輸送、精製、貯蔵に必要な総エネルギーを試算する研究です。", "採算性評価"),
        ("CSA低温配管凍結防止研究", "CSA Cryogenic Plumbing Freeze Prevention Study", category, "research", "Canadian Space Agency", "CA", 2023, 2, "ongoing", ["cryogenic plumbing", "freeze prevention", "CSA"], "極域の低温環境で水配管が凍結しないための熱設計を検討しています。", "インフラ信頼性"),
        ("NASA月面氷サンプルコンテナ設計", "NASA Lunar Ice Sample Container Design", category, "technology", "NASA", "US", 2023, 3, "ongoing", ["sample container", "ice", "cryogenic"], "昇華損失を抑えて氷試料を搬送するための低温容器設計です。", "試料保全"),
        ("ESA閉鎖環境グレイウォーター再利用研究", "ESA Greywater Reuse in Closed Habitats", category, "research", "ESA", "EU", 2021, 4, "ongoing", ["greywater", "reuse", "closed habitat"], "手洗い・調理由来のグレイウォーターを衛生的に再利用する条件を評価しています。", "再利用範囲の拡大"),
        ("NASA再生水味覚受容性研究", "NASA Palatability of Recycled Water Study", category, "research", "NASA", "US", 2020, 6, "ongoing", ["palatability", "recycled water", "crew"], "安全性だけでなく、飲み続けやすさの観点から再生水の感覚評価を行っています。", "飲水量確保"),
        ("NASA水回収率98パーセント化研究", "NASA 98 Percent Water Recovery Study", category, "research", "NASA", "US", 2021, 6, "ongoing", ["98 percent", "water recovery", "exploration"], "探査ミッションで必要とされる98%以上の総回収率実現に向けた統合研究です。", "補給依存低減"),
        ("月面氷電解燃料製造概念", "Lunar Ice Electrolysis Propellant Production Concept", category, "concept", "NASA", "US", 2022, 3, "ongoing", ["electrolysis", "propellant", "ISRU"], "採掘水を分解して酸素・水素推進剤へ転換する月面インフラ構想です。", "生命維持と輸送の両立"),
        ("NASA水循環故障診断デジタルツイン", "NASA Digital Twin for Water Loop Fault Diagnosis", category, "technology", "NASA", "US", 2023, 3, "ongoing", ["digital twin", "fault diagnosis", "water loop"], "センサーデータとモデルを結んで故障を予兆検知する運用支援技術です。", "保守省人化"),
        ("DLR宇宙植物工場給液最適化研究", "DLR Nutrient and Water Delivery Optimization Study", category, "research", "DLR", "DE", 2021, 4, "ongoing", ["plant factory", "water delivery", "DLR"], "植物工場系での給液制御を調整し、食料生産と水消費を両立させる研究です。", "食料系との統合"),
        ("NASA極域水輸送ローバー概念", "NASA Polar Water Hauler Rover Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["rover", "water hauling", "polar"], "採掘地点から基地まで氷や再生水を輸送する専用ローバーの概念です。", "基地補給"),
        ("ESA水再生システム微量金属管理", "ESA Trace Metal Control in Water Recovery Systems", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["trace metals", "water recovery", "ESA"], "長期循環で蓄積しうる微量金属の監視と除去条件を整理しています。", "長期毒性の低減"),
        ("NASA月面採水・浄化統合モジュール", "NASA Integrated Lunar Water Harvesting and Purification Module", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["integrated module", "harvesting", "purification"], "採掘、昇華、凝縮、ろ過を一体化した小規模実証モジュールの考え方です。", "初期拠点の立ち上げ"),
        ("JAXA月面水利用シナリオ研究", "JAXA Lunar Water Utilization Scenario Study", category, "research", "JAXA", "JP", 2023, 2, "ongoing", ["JAXA", "scenario", "water utilization"], "飲料、衛生、農業、推進剤の各用途に対する配分シナリオを比較しています。", "資源配分最適化"),
        ("PRIME-1月面氷採掘技術実証", "Polar Resources Ice Mining Experiment 1", category, "project", "NASA", "US", 2024, 6, "ongoing", ["PRIME-1", "drill", "IM-2"], "月着陸機に搭載されるドリルと質量分析計で、氷資源利用技術を前哨実証する計画です。", "初期ISRU実証"),
        ("RESOLVE揮発性資源探査パッケージ", "Regolith and Environment Science and Oxygen and Lunar Volatile Extraction", category, "project", "NASA", "US", 2019, 5, "completed", ["RESOLVE", "volatiles", "oxygen"], "月面揮発性物質の探査と資源化を統合的に扱う旧世代の実証パッケージです。", "後続ISRU計画の基礎"),
        ("Resource Prospector水氷ローバー計画", "Resource Prospector Rover Mission", category, "project", "NASA", "US", 2018, 5, "cancelled", ["Resource Prospector", "rover", "ice"], "中止されたものの、極域氷探査ローバー構想としてVIPER以前の重要な設計蓄積を残しました。", "探査要件の先行整理"),
        ("Water Walls居住区水シールド概念", "Water Walls Habitat Shielding Concept", category, "concept", "NASA", "US", 2015, 3, "ongoing", ["Water Walls", "shielding", "storage"], "貯蔵水を生活資源と放射線遮蔽の両方に使う居住設計概念です。", "水資源の多目的利用"),
        ("NASA毛細管流体水管理研究", "NASA Capillary Fluidics for Water Management Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["capillary fluidics", "water management", "NASA"], "低重力でポンプ依存を減らすため、毛細管現象を活用した水移送手法を研究しています。", "信頼性の高い流体制御"),
    ]

    for item in items:
        add(make_entry(*item[:10], detail=item[10], impact=item[11]))

    assert len(entries) == 70
    return entries


def build_hygiene_entries():
    entries = []
    add = entries.append
    category = "hygiene"

    items = [
        ("ISS Waste and Hygiene Compartment", "ISS Waste and Hygiene Compartment", category, "technology", "NASA / Roscosmos", "US", 2000, 9, "ongoing", ["WHC", "toilet", "ISS"], "ISSロシア区画で長期運用される基幹トイレで、宇宙衛生設備の実運用知見を提供しています。", "排泄衛生の維持"),
        ("Universal Waste Management System", "Universal Waste Management System", category, "technology", "NASA", "US", 2020, 8, "ongoing", ["UWMS", "toilet", "waste"], "小型化と操作性改善を図った次世代トイレで、Artemis系居住設備の前段技術です。", "月面衛生設備の標準化"),
        ("Heat Melt Compactor廃棄物処理", "Heat Melt Compactor Waste Processing", category, "technology", "NASA", "US", 2014, 6, "completed", ["HMC", "trash", "volume reduction"], "ごみを加熱圧縮して体積を減らし、水分回収も狙う廃棄物処理装置です。", "廃棄物管理"),
        ("Trash-to-Gas廃棄物ガス化研究", "Trash-to-Gas Waste Gasification Study", category, "research", "NASA Ames Research Center", "US", 2016, 4, "ongoing", ["trash-to-gas", "gasification", "waste"], "固形廃棄物からメタンなどを得て資源化する研究で、衛生負荷の低減にもつながります。", "廃棄物資源化"),
        ("MATISS抗菌表面実験", "MATISS Antimicrobial Surface Experiment", category, "research", "CNES / ESA", "FR", 2016, 7, "ongoing", ["MATISS", "surface", "microbes"], "ISS表面に付着する微生物の広がりを可視化し、抗菌素材の効果を比較しました。", "表面衛生管理"),
        ("Microbial Tracking-1", "Microbial Tracking-1", category, "research", "NASA", "US", 2015, 7, "completed", ["Microbial Tracking", "ISS", "microbiome"], "ISS内の表面・空気・水の微生物叢を遺伝学的に調べた初期大規模調査です。", "微生物監視"),
        ("Microbial Tracking-2", "Microbial Tracking-2", category, "research", "NASA", "US", 2017, 7, "completed", ["Microbial Tracking-2", "ISS", "microbiome"], "滞在期間や環境条件による微生物叢の変化を追跡し、衛生管理策改善に役立てました。", "長期変動把握"),
        ("ISS Microbial Observatory", "ISS Microbial Observatory", category, "research", "NASA", "US", 2021, 6, "ongoing", ["microbial observatory", "ISS", "monitoring"], "定常的な微生物環境監視の枠組みとして運用されるISS衛生研究群です。", "定期衛生評価"),
        ("Biofilms宇宙表面形成研究", "Biofilms in Space Surface Formation Study", category, "research", "NASA", "US", 2020, 5, "ongoing", ["biofilm", "surface", "ISS"], "閉鎖環境表面でのバイオフィルム形成挙動を観察し、除去法を探る研究です。", "腐食と感染リスク低減"),
        ("Bacterial Adhesion and Corrosion Study", "Bacterial Adhesion and Corrosion Study", category, "research", "NASA", "US", 2019, 5, "ongoing", ["adhesion", "corrosion", "microbes"], "微生物付着が金属腐食や表面劣化に与える影響を評価しました。", "設備衛生と保全"),
        ("Electrodynamic Dust Shield", "Electrodynamic Dust Shield", category, "technology", "NASA Kennedy Space Center", "US", 2022, 7, "ongoing", ["EDS", "dust", "electrostatic"], "透明電極に交流電場を与えて月面ダストを払い落とす代表的な除塵技術です。", "ダスト衛生対策"),
        ("Lotus Coating宇宙防汚表面", "Lotus Coating for Space Antifouling Surfaces", category, "technology", "ESA", "EU", 2021, 4, "ongoing", ["coating", "dust", "antifouling"], "超撥水・低付着表面でダストや汚れの滞留を抑える表面設計です。", "清掃負荷軽減"),
        ("LADTAG月面ダスト曝露限界研究", "LADTAG Lunar Dust Exposure Limit Study", category, "research", "NASA", "US", 2019, 4, "ongoing", ["LADTAG", "dust toxicity", "exposure"], "月面ダストの許容曝露限界を定めるため、吸入毒性データを整理した研究群です。", "健康保護基準の設定"),
        ("Lunar Airborne Dust Toxicity Study", "Lunar Airborne Dust Toxicity Study", category, "research", "NASA", "US", 2010, 4, "completed", ["dust toxicity", "inhalation", "Apollo"], "アポロ由来の健康懸念を受け、粒径と表面反応性を重視して毒性を評価しました。", "吸入リスク評価"),
        ("JSC-1Aレゴリス皮膚刺激評価", "JSC-1A Regolith Skin Irritation Assessment", category, "research", "NASA", "US", 2021, 3, "ongoing", ["JSC-1A", "skin irritation", "regolith"], "模擬レゴリスが皮膚バリアへ与える刺激性をin vitroで調べる研究です。", "接触衛生リスク低減"),
        ("月面ダスト眼刺激性評価", "Lunar Dust Ocular Irritation Assessment", category, "research", "NASA", "US", 2021, 3, "ongoing", ["ocular irritation", "dust", "safety"], "眼表面への刺激と洗浄手順の有効性を確認する衛生安全研究です。", "眼の衛生保護"),
        ("Suitportダスト隔離概念", "Suitport Dust Isolation Concept", category, "concept", "NASA", "US", 2020, 4, "ongoing", ["suitport", "dust isolation", "airlock"], "スーツを居住区外壁に接続し、ダストを内部へ持ち込まない考え方です。", "室内清浄度維持"),
        ("Suitlock衛生エアロック概念", "Suitlock Hygiene Airlock Concept", category, "concept", "NASA", "US", 2020, 4, "ongoing", ["suitlock", "airlock", "hygiene"], "簡易エアロック内でスーツ汚染を局所管理する居住設計の概念です。", "ダスト侵入抑制"),
        ("Apollo月面ダストハウスキーピング教訓", "Apollo Lunar Dust Housekeeping Lessons", category, "case_study", "NASA", "US", 1972, 8, "completed", ["Apollo", "dust", "housekeeping"], "アポロ船内でのダスト付着、臭気、清掃困難の経験は月面衛生設計の出発点です。", "運用教訓の継承"),
        ("ISS HEPA空気ろ過衛生運用", "ISS HEPA Air Filtration Operations", category, "technology", "NASA", "US", 2001, 9, "ongoing", ["HEPA", "air filtration", "ISS"], "微粒子と微生物負荷を抑えるためのISS空気ろ過システム運用です。", "室内空気衛生"),
        ("TiO2光触媒空気浄化研究", "TiO2 Photocatalytic Air Purification Study", category, "research", "JAXA", "JP", 2020, 4, "ongoing", ["TiO2", "photocatalysis", "air"], "光触媒で臭気や有機汚染物を分解する閉鎖環境向け浄化法です。", "空気質改善"),
        ("UV-C表面殺菌装置", "UV-C Surface Disinfection Unit", category, "technology", "NASA", "US", 2021, 5, "ongoing", ["UV-C", "surface disinfection", "hygiene"], "接触頻度の高い表面を短時間で殺菌する装置として検討されています。", "感染予防"),
        ("UV-C空気ダクト殺菌システム", "UV-C Duct Air Sterilization System", category, "technology", "ESA", "EU", 2022, 4, "ongoing", ["UV-C", "air duct", "sterilization"], "空調ダクト内で微生物増殖を抑える衛生設備です。", "空気系微生物制御"),
        ("銅合金抗菌タッチサーフェス研究", "Copper Alloy Antimicrobial Touch Surface Study", category, "research", "ESA", "EU", 2021, 4, "ongoing", ["copper", "touch surface", "antimicrobial"], "手が触れる部材に抗菌性金属を適用し、汚染伝播を減らす研究です。", "接触感染抑制"),
        ("銀系抗菌繊維宇宙居住研究", "Silver Antimicrobial Textiles for Space Habitats", category, "research", "JAXA", "JP", 2020, 4, "ongoing", ["silver textiles", "clothing hygiene", "JAXA"], "衣服や寝具に抗菌繊維を使い、洗濯頻度低減と臭気抑制を狙います。", "個人衛生維持"),
        ("無水ボディワイプ宇宙衛生技術", "Waterless Body Wipe Hygiene Technology", category, "technology", "NASA", "US", 2018, 8, "ongoing", ["body wipes", "waterless", "personal hygiene"], "水使用を抑えつつ全身清拭を可能にする個人衛生用品です。", "節水型清潔維持"),
        ("無水シャンプー宇宙運用", "No-Rinse Shampoo for Space Operations", category, "technology", "NASA", "US", 2018, 8, "ongoing", ["shampoo", "no-rinse", "personal hygiene"], "すすぎ不要で頭皮衛生を維持する宇宙向け洗浄製品です。", "毛髪衛生"),
        ("宇宙用歯磨き・口腔衛生手順", "Space Toothbrushing and Oral Hygiene Procedure", category, "technology", "NASA", "US", 2019, 8, "ongoing", ["oral hygiene", "toothbrushing", "ISS"], "飲み込み可能な歯磨き手順や飛散しにくい用品で口腔衛生を保つ運用です。", "口腔健康維持"),
        ("宇宙用ひげ剃り粒子回収装置", "Space Shaving Particle Capture System", category, "technology", "NASA", "US", 2017, 7, "ongoing", ["shaving", "particle capture", "grooming"], "毛髪飛散を防ぐ吸引付きひげ剃り運用で、異物拡散を抑えます。", "清掃負荷低減"),
        ("宇宙洗濯機概念研究", "Space Washing Machine Concept Study", category, "concept", "Procter & Gamble / NASA", "US", 2023, 3, "ongoing", ["laundry", "P&G", "concept"], "月・火星向けに超低水使用の洗濯技術を模索する共同概念研究です。", "衣類衛生の長期化"),
        ("宇宙衣類再着用臭気管理研究", "Odor Management for Extended Clothing Reuse", category, "research", "NASA", "US", 2022, 3, "ongoing", ["odor", "clothing reuse", "hygiene"], "洗濯困難な環境で衣類を長期間再着用する際の臭気管理を調べています。", "消耗品削減"),
        ("閉鎖環境手指衛生プロトコル", "Hand Hygiene Protocol for Closed Environments", category, "technology", "CDC / NASA", "US", 2021, 5, "ongoing", ["hand hygiene", "protocol", "closed habitat"], "水とアルコール系消毒剤の使い分けを含む閉鎖環境向け手指衛生手順です。", "感染症予防"),
        ("アルコールベース手指消毒宇宙適用研究", "Alcohol-Based Hand Rub Use in Space Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["hand rub", "disinfection", "space"], "蒸気管理や皮膚乾燥も含めて手指消毒剤の宇宙適用性を評価しています。", "清潔保持"),
        ("宇宙用創傷洗浄衛生キット", "Space Wound Cleaning Hygiene Kit", category, "technology", "NASA", "US", 2022, 4, "ongoing", ["wound care", "cleaning kit", "medical hygiene"], "けが発生時に衛生的な洗浄と被覆を行うための消耗品パッケージです。", "二次感染防止"),
        ("月面居住区清掃動線設計", "Lunar Habitat Cleaning Flow Design", category, "concept", "NASA", "US", 2022, 3, "ongoing", ["cleaning flow", "habitat", "concept"], "汚染区域と清潔区域を分け、清掃動線を短くする居住区レイアウト概念です。", "日常衛生の効率化"),
        ("ESA閉鎖環境臭気センサー研究", "ESA Closed-Habitat Odor Sensor Study", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["odor sensor", "ESA", "air quality"], "臭気源を早期に検知し、衛生問題や設備異常の前兆として扱う研究です。", "快適性と保全性向上"),
        ("ISSごみ保管衛生管理", "ISS Trash Stowage Hygiene Management", category, "technology", "NASA", "US", 2019, 7, "ongoing", ["trash stowage", "odor", "microbes"], "船内に一時保管する廃棄物の臭気と微生物増殖を抑える運用管理です。", "船内衛生維持"),
        ("月面生ごみ乾燥安定化概念", "Lunar Organic Waste Dry Stabilization Concept", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["organic waste", "drying", "stabilization"], "生ごみを乾燥・安定化して臭気や腐敗を抑える衛生処理の考え方です。", "衛生負荷低減"),
        ("NASA湿式ワイプ包装殺菌設計", "NASA Sterile Packaging Design for Wet Wipes", category, "technology", "NASA", "US", 2020, 5, "ongoing", ["wet wipes", "sterile packaging", "hygiene"], "長期保存下でも微生物増殖を防ぐ個包装設計の研究です。", "消耗品安全性"),
        ("宇宙用女性衛生用品運用研究", "Space Menstrual Hygiene Operations Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["menstrual hygiene", "operations", "NASA"], "女性クルーの長期滞在に必要な衛生用品、廃棄、収納の運用を整理した研究です。", "包摂的衛生設計"),
        ("UWMS女性クルー適合性評価", "UWMS Female Crew Usability Assessment", category, "research", "NASA", "US", 2020, 6, "completed", ["UWMS", "female crew", "ergonomics"], "従来設備の課題を踏まえて操作性と衛生性を検証した評価です。", "設備利用性向上"),
        ("ロシアASUトイレ衛生運用", "Russian ASU Toilet Hygiene Operations", category, "technology", "Roscosmos", "RU", 2015, 8, "ongoing", ["ASU", "toilet", "Mir heritage"], "ミールから継承されたロシア系宇宙トイレの運用知見です。", "冗長衛生設備の確保"),
        ("月面ダストブラシング前処理手順", "Lunar Dust Brushing Pre-Entry Procedure", category, "technology", "NASA", "US", 2022, 4, "ongoing", ["dust brushing", "pre-entry", "procedure"], "エアロック入域前にスーツ表面を機械的に除塵する手順の標準化です。", "居住区保護"),
        ("NASA静電掃除ツール概念", "NASA Electrostatic Cleaning Tool Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["electrostatic cleaning", "tool", "concept"], "床面や機器表面の微粒子を電場で回収する清掃ツール概念です。", "粉塵除去の省力化"),
        ("月面ダスト対応シール材研究", "Dust-Tolerant Seal Material Study", category, "research", "NASA Glenn Research Center", "US", 2021, 4, "ongoing", ["seals", "dust tolerant", "materials"], "ダスト侵入下でも気密と清掃性を保つシール材の評価です。", "衛生隔離性能の維持"),
        ("月面エアロック床材防塵研究", "Dust-Controlling Airlock Flooring Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["flooring", "airlock", "dust"], "粒子を捕捉しやすく清掃しやすい床材構成を検討しています。", "内部拡散抑制"),
        ("NASAハウスダスト粒子モニタ研究", "NASA Habitat Dust Particle Monitoring Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["particle monitor", "dust", "habitat"], "室内浮遊粒子濃度を常時計測して清掃や換気タイミングを決める研究です。", "衛生監視自動化"),
        ("ISS空気サンプラー微生物評価", "ISS Air Sampler Microbial Assessment", category, "research", "NASA", "US", 2020, 5, "ongoing", ["air sampler", "microbes", "ISS"], "空中微生物負荷を把握し、閉鎖環境の空気衛生を評価する運用です。", "空気感染リスクの把握"),
        ("ISS表面サンプラー衛生監視", "ISS Surface Sampler Hygiene Monitoring", category, "research", "NASA", "US", 2020, 5, "ongoing", ["surface sampler", "hygiene", "ISS"], "接触面から拭き取り採取して表面清浄度を追跡しています。", "清掃品質管理"),
        ("NASA水回収系微生物バリア研究", "Microbial Barrier Study for Water Recovery Hardware", category, "research", "NASA", "US", 2021, 4, "ongoing", ["microbial barrier", "water hardware", "NASA"], "衛生と水カテゴリをまたぐ境界領域として、再生水機器の微生物侵入抑制を検討しています。", "複合衛生管理"),
        ("月面居住区消臭材吸着研究", "Lunar Habitat Deodorant Adsorbent Study", category, "research", "JAXA", "JP", 2022, 3, "ongoing", ["deodorant", "adsorbent", "JAXA"], "アンモニアや揮発性有機物を吸着する消臭材の長期性能を評価しています。", "生活快適性向上"),
        ("宇宙用リネン交換周期最適化", "Space Linen Replacement Cycle Optimization", category, "research", "NASA", "US", 2021, 3, "ongoing", ["linen", "replacement cycle", "hygiene"], "限られた洗濯能力を前提にタオルや寝具の交換周期を最適化する研究です。", "消耗品管理"),
        ("ESA閉鎖環境皮膚マイクロバイオーム研究", "ESA Skin Microbiome in Closed Habitats Study", category, "research", "ESA", "EU", 2023, 3, "ongoing", ["skin microbiome", "closed habitat", "ESA"], "隔離環境での皮膚常在菌変化を調べ、個人衛生用品設計に反映します。", "皮膚健康維持"),
        ("NASA創傷ドレッシング滅菌包装研究", "NASA Sterile Wound Dressing Packaging Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["wound dressing", "sterile packaging", "NASA"], "長期保存中の無菌性維持を重視した創傷被覆材の包装研究です。", "応急衛生の信頼性向上"),
        ("宇宙用爪切り飛散防止器具", "Space Nail Clipper Debris Containment Tool", category, "technology", "NASA", "US", 2018, 8, "ongoing", ["grooming", "nail clipper", "containment"], "切断片の飛散を防ぐ小型日用品で、異物管理の代表例です。", "微小異物の抑制"),
        ("NASA閉鎖環境殺菌剤適合性研究", "Disinfectant Compatibility in Closed Environments Study", category, "research", "NASA", "US", 2021, 3, "ongoing", ["disinfectant", "material compatibility", "NASA"], "殺菌剤が機器材質や空気質へ与える副作用まで含めて評価する研究です。", "安全な衛生運用"),
        ("JAXA宇宙歯科衛生パッケージ研究", "JAXA Space Dental Hygiene Package Study", category, "research", "JAXA", "JP", 2021, 3, "ongoing", ["dental hygiene", "JAXA", "oral care"], "閉鎖環境での歯周ケアと口腔衛生維持を目的にした用品群の研究です。", "医療負荷の予防"),
        ("NASA靴底ダスト持ち込み低減研究", "NASA Boot Sole Dust Carry-In Reduction Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["boots", "dust carry-in", "NASA"], "床面への粒子移送を減らす靴底構造や清掃方法を比較しています。", "居住区清浄度の維持"),
        ("CSA閉鎖環境シャワー代替設計", "CSA Shower Alternative Design for Closed Habitats", category, "concept", "Canadian Space Agency", "CA", 2023, 2, "ongoing", ["shower alternative", "CSA", "closed habitat"], "水を大量消費しない全身洗浄代替システムの設計概念です。", "節水型個人衛生"),
        ("月面トイレ前処理薬剤研究", "Lunar Toilet Pretreatment Chemistry Study", category, "research", "NASA", "US", 2021, 3, "ongoing", ["pretreatment", "chemistry", "toilet"], "配管腐食や臭気を抑えつつ回収系へ適合する薬剤処方を検討しています。", "廃液衛生管理"),
        ("ISS換気口粉塵清掃手順", "ISS Vent Cleaning Procedure for Dust Control", category, "technology", "NASA", "US", 2019, 8, "ongoing", ["vent cleaning", "dust control", "ISS"], "通風阻害と微生物蓄積を防ぐ定期清掃手順です。", "空調衛生の維持"),
        ("NASA閉鎖環境殺虫・防虫概念", "NASA Pest Prevention Concept for Closed Habitats", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["pest prevention", "closed habitat", "concept"], "植物栽培導入時の害虫持ち込みと拡散を抑える衛生概念です。", "農業系衛生保全"),
        ("ESA表面清浄度スワブ迅速判定研究", "ESA Rapid Swab Assessment for Surface Cleanliness", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["swab", "rapid assessment", "ESA"], "ATP測定などを使って清掃後の表面清浄度を短時間判定する研究です。", "清掃品質の即時確認"),
        ("NASAウェットトラッシュ脱水研究", "NASA Wet Trash Dewatering Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["wet trash", "dewatering", "NASA"], "湿ったごみから水分を抜いて腐敗と臭気を抑える研究です。", "衛生負荷低減"),
        ("閉鎖環境共有器具消毒プロトコル", "Shared Equipment Disinfection Protocol", category, "technology", "NASA", "US", 2021, 4, "ongoing", ["shared equipment", "disinfection", "protocol"], "運動器具や調理器具など共有物品の消毒頻度と手順を定めた運用です。", "交差汚染防止"),
        ("ISS床面粒子回収掃除機運用", "ISS Vacuum Particle Recovery Operations", category, "technology", "NASA", "US", 2018, 8, "ongoing", ["vacuum", "particle recovery", "ISS"], "浮遊粒子やダストを吸引回収する日常清掃の基礎運用です。", "ハウスキーピング維持"),
        ("BOSSバイオフィルム宇宙形成実験", "Biofilm Organisms Surfing Space", category, "research", "NASA", "US", 2019, 6, "completed", ["BOSS", "biofilm", "ISS"], "微小重力でのバイオフィルム形成速度と構造変化を調べた代表的なISS実験です。", "表面衛生対策の高度化"),
        ("MATISS-2抗菌素材追跡試験", "MATISS-2 Antimicrobial Materials Follow-Up", category, "research", "CNES / ESA", "FR", 2020, 6, "completed", ["MATISS-2", "materials", "surface hygiene"], "抗菌・防汚素材の長期挙動を追加評価し、接触面設計へ反映した追跡試験です。", "持続的な清浄度維持"),
        ("WetLab-2微生物迅速同定", "WetLab-2 Rapid Microbial Identification", category, "technology", "NASA", "US", 2016, 7, "ongoing", ["WetLab-2", "microbial ID", "ISS"], "船内でDNA解析を行い、微生物汚染を地上帰還なしに迅速同定できる技術です。", "衛生対応の即応化"),
        ("MinION船内遺伝子解析衛生監視", "MinION Onboard Genetic Sequencing for Hygiene Monitoring", category, "technology", "NASA", "US", 2016, 7, "ongoing", ["MinION", "sequencing", "hygiene monitoring"], "ポータブルシーケンサーを使って閉鎖環境の微生物変化を詳細監視する運用です。", "微生物監視の高度化"),
    ]

    for item in items:
        add(make_entry(*item[:10], detail=item[10], impact=item[11]))

    assert len(entries) == 70
    return entries


def build_medical_entries():
    entries = []
    add = entries.append
    category = "medical"

    items = [
        ("NASA Human Research Program", "NASA Human Research Program", category, "project", "NASA", "US", 2005, 9, "ongoing", ["HRP", "space medicine", "NASA"], "長期宇宙滞在の主要健康リスクを体系化し、医学研究を束ねる中核プログラムです。", "医学リスク低減"),
        ("NASA CIPHER統合宇宙医学プロトコル", "NASA CIPHER Integrated Space Medicine Protocol", category, "project", "NASA", "US", 2023, 7, "ongoing", ["CIPHER", "integrated protocol", "crew health"], "複数分野の測定を同じ被験者に統合し、宇宙滞在後の全身変化をつなげて理解する計画です。", "全身影響の統合理解"),
        ("NASA Twins Study", "NASA Twins Study", category, "case_study", "NASA", "US", 2019, 9, "completed", ["Twins Study", "omics", "long-duration"], "同一遺伝背景の双子を比較し、長期宇宙滞在が遺伝子発現や免疫、認知に与える影響を示しました。", "個別化医療の基礎"),
        ("NASA Space Omics", "NASA Space Omics", category, "research", "NASA", "US", 2020, 6, "ongoing", ["Space Omics", "genomics", "multiomics"], "宇宙環境応答をゲノム、転写、代謝レベルで解析する研究群です。", "バイオマーカー探索"),
        ("GeneLab宇宙生物データ基盤", "NASA GeneLab", category, "technology", "NASA", "US", 2015, 8, "ongoing", ["GeneLab", "omics", "database"], "宇宙生命科学データを統合公開し、放射線や微小重力の健康影響研究を支えています。", "再解析と知見統合"),
        ("NSRL宇宙放射線模擬施設", "NASA Space Radiation Laboratory", category, "technology", "Brookhaven National Laboratory / NASA", "US", 2003, 9, "ongoing", ["NSRL", "radiation", "facility"], "銀河宇宙線や太陽粒子イベントを模擬し、放射線医学研究の基盤となる施設です。", "放射線対策開発"),
        ("BioSentinel深宇宙放射線生物実証", "BioSentinel Deep Space Radiation Biology Mission", category, "project", "NASA Ames Research Center", "US", 2022, 6, "ongoing", ["BioSentinel", "radiation", "bioscience"], "深宇宙放射線が生体へ与える影響を酵母モデルで測る月近傍ミッションです。", "深宇宙医学データ取得"),
        ("Matroshka人体等価線量計測", "Matroshka Human Phantom Dosimetry", category, "research", "DLR / ESA / Roscosmos", "DE", 2004, 8, "ongoing", ["Matroshka", "dosimetry", "phantom"], "人体ファントムで各臓器相当位置の線量を測り、被ばく評価モデルを改善しました。", "臓器線量評価"),
        ("DOSIS 3D放射線線量分布研究", "DOSIS 3D Radiation Mapping", category, "research", "ESA", "EU", 2012, 7, "completed", ["DOSIS 3D", "radiation", "ISS"], "ISS内部での線量空間分布を細かく測定し、居住区ごとの差を可視化しました。", "遮蔽設計"),
        ("ALTEA脳・眼放射線観測", "ALTEA Brain and Eye Radiation Observation", category, "research", "ASI / NASA", "IT", 2006, 7, "completed", ["ALTEA", "neurology", "radiation"], "宇宙飛行士が感じる光視症と高エネルギー粒子通過の関係を調べました。", "神経影響理解"),
        ("SANS宇宙関連神経眼症候群研究", "Spaceflight Associated Neuro-Ocular Syndrome Research", category, "research", "NASA", "US", 2017, 7, "ongoing", ["SANS", "vision", "neuro-ocular"], "長期滞在で起こる視神経・眼球形態変化の原因と対策を探る重要研究領域です。", "視機能保護"),
        ("Ocular Health宇宙眼圧研究", "Space Ocular Health and Intraocular Pressure Study", category, "research", "NASA", "US", 2021, 5, "ongoing", ["ocular health", "intraocular pressure", "NASA"], "体液移動と眼圧変化の関係を追跡し、SANS対策へつなげています。", "眼科リスク管理"),
        ("rHEALTH ONE軌道上血液分析", "rHEALTH ONE On-Orbit Blood Analysis", category, "technology", "rHEALTH", "US", 2021, 6, "ongoing", ["rHEALTH ONE", "blood analysis", "diagnostics"], "少量血液から複数の血球・炎症指標を測れる小型分析器です。", "早期診断"),
        ("i-STAT宇宙臨床分析運用", "i-STAT Clinical Analyzer in Space Operations", category, "technology", "Abbott / NASA", "US", 2000, 8, "ongoing", ["i-STAT", "clinical chemistry", "ISS"], "血液ガスや電解質を船内で迅速測定する臨床分析器の運用事例です。", "ベッドサイド検査"),
        ("Butterfly iQ宇宙超音波評価", "Butterfly iQ Space Ultrasound Assessment", category, "technology", "Butterfly Network / NASA", "US", 2022, 5, "ongoing", ["Butterfly iQ", "ultrasound", "portable"], "手持ち型超音波装置を宇宙環境に適用し、遠隔指導診断の可能性を広げています。", "携帯診断能力"),
        ("Axiom Space tele-ultrasound実証", "Axiom Space Tele-Ultrasound Demonstration", category, "project", "Axiom Space", "US", 2023, 5, "ongoing", ["tele-ultrasound", "Axiom", "remote care"], "地上医師の支援を受けながらクルー自身が超音波検査を行う実証です。", "自律医療支援"),
        ("Autonomous Medical Officer Support", "Autonomous Medical Officer Support", category, "technology", "NASA", "US", 2018, 5, "ongoing", ["AMOS", "decision support", "medical AI"], "通信遅延下で乗員が医療判断できるよう手順提示を行う支援システムです。", "自律医療強化"),
        ("Smart Medical Checklist", "Smart Medical Checklist", category, "technology", "NASA", "US", 2019, 5, "ongoing", ["checklist", "decision support", "medical"], "症状と処置手順を状況に応じて切り替える電子チェックリストです。", "ヒューマンエラー低減"),
        ("Exploration Medical Capability", "Exploration Medical Capability", category, "project", "NASA", "US", 2020, 6, "ongoing", ["ExMC", "exploration medicine", "capability"], "月・火星探査で必要な医療機器、薬剤、運用の要件を整理する計画です。", "探査医療設計"),
        ("Integrated Medical Model", "Integrated Medical Model", category, "technology", "NASA", "US", 2014, 7, "ongoing", ["IMM", "risk model", "medical"], "ミッション中に起こりうる疾患と必要資源を統計的に見積もるリスクモデルです。", "医療備蓄最適化"),
        ("Trauma POD宇宙外傷処置概念", "Trauma POD Space Trauma Care Concept", category, "concept", "NASA", "US", 2022, 3, "ongoing", ["trauma", "pod", "concept"], "外傷時に必要な器具と手順を一体化した小型処置環境の概念です。", "緊急医療対応"),
        ("NEEMO遠隔医療実証", "NEEMO Telemedicine Demonstration", category, "project", "NASA", "US", 2011, 6, "completed", ["NEEMO", "telemedicine", "analog"], "海底居住アナログで通信制約下の遠隔医療手順を検証しました。", "月面遅延通信医療"),
        ("HERA医学運用評価", "HERA Medical Operations Assessment", category, "research", "NASA", "US", 2021, 5, "ongoing", ["HERA", "medical ops", "analog"], "閉鎖環境での診断、投薬、チーム内医療役割分担を評価しています。", "小規模クルー運用"),
        ("CHAPEA健康モニタリング計画", "CHAPEA Health Monitoring Program", category, "research", "NASA", "US", 2023, 5, "ongoing", ["CHAPEA", "health monitoring", "analog"], "長期隔離アナログで睡眠、ストレス、代謝、診療手順を統合監視しています。", "長期滞在医学"),
        ("Astroskin生体計測シャツ", "Astroskin Biometric Shirt", category, "technology", "Hexoskin / Canadian Space Agency", "CA", 2020, 7, "ongoing", ["Astroskin", "wearables", "biometrics"], "心拍、呼吸、皮膚温などを連続測定する着衣型モニタリング機器です。", "日常健康監視"),
        ("Echo心血管超音波宇宙研究", "Echo Cardiovascular Ultrasound Study", category, "research", "NASA", "US", 2015, 7, "ongoing", ["cardiovascular", "ultrasound", "Echo"], "心機能と血流動態の変化を超音波で追う長期滞在研究です。", "循環器リスク把握"),
        ("Vascular Aging宇宙血管老化研究", "Vascular Aging in Space Study", category, "research", "JAXA / NASA", "JP", 2020, 5, "ongoing", ["vascular aging", "arteries", "JAXA"], "宇宙滞在が血管硬化や内皮機能に与える影響を調べています。", "循環器疾患予防"),
        ("MARROW骨髄脂肪蓄積研究", "MARROW Bone Marrow Adipose Study", category, "research", "NASA", "US", 2021, 6, "ongoing", ["MARROW", "bone marrow", "metabolism"], "微小重力で骨髄脂肪が増える現象を追跡し、骨・代謝障害との関係を見ています。", "骨代謝障害理解"),
        ("Microgravity and Osteoporosis対比研究", "Microgravity and Osteoporosis Comparative Study", category, "research", "ESA", "EU", 2021, 4, "ongoing", ["osteoporosis", "bone loss", "ESA"], "宇宙骨量減少を地上の骨粗鬆症モデルと比較して治療候補を探る研究です。", "地上医療連携"),
        ("Kidney Stone宇宙腎結石研究", "Spaceflight Kidney Stone Risk Study", category, "research", "NASA", "US", 2018, 7, "ongoing", ["kidney stone", "renal", "NASA"], "骨吸収や脱水に伴う腎結石リスクを追跡し、食事と投薬対策を評価しています。", "泌尿器リスク管理"),
        ("IMMUNO宇宙免疫機能研究", "Spaceflight Immune Function Study", category, "research", "NASA", "US", 2019, 6, "ongoing", ["immune", "latency", "stress"], "宇宙滞在で免疫応答が変化し、潜伏ウイルス再活性化が起こる仕組みを調べています。", "感染症予防"),
        ("Microbiome宇宙腸内細菌研究", "Spaceflight Gut Microbiome Study", category, "research", "NASA", "US", 2020, 5, "ongoing", ["microbiome", "gut", "crew health"], "腸内細菌叢の変化と免疫・代謝・気分の関連を解析しています。", "全身健康管理"),
        ("Tissue Chips in Space", "Tissue Chips in Space", category, "research", "NIH / NASA", "US", 2019, 6, "ongoing", ["tissue chips", "organs", "NIH"], "ヒト組織チップで宇宙環境が臓器機能へ与える影響を調べる実験群です。", "病態機序解明"),
        ("BioFabrication Facility", "BioFabrication Facility", category, "technology", "Techshot / NASA", "US", 2019, 6, "ongoing", ["bioprinting", "BioFabrication Facility", "ISS"], "微小重力を利用した3D生体組織プリント装置として運用されています。", "再生医療研究"),
        ("3D BioFabrication装置月面医療応用概念", "3D Biofabrication for Lunar Medical Use Concept", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["bioprinting", "lunar medical", "concept"], "将来的に組織修復材料を現地製造する医療支援概念です。", "補給依存低減"),
        ("PharmaSat薬剤反応小型衛星実験", "PharmaSat Drug Response Nanosatellite Experiment", category, "research", "NASA Ames Research Center", "US", 2009, 7, "completed", ["PharmaSat", "drug response", "microbiology"], "宇宙環境での薬剤反応や微生物増殖を小型衛星で検証した先行実験です。", "宇宙薬理学の基礎"),
        ("ISS薬剤安定性追跡研究", "ISS Pharmaceutical Stability Tracking Study", category, "research", "NASA", "US", 2019, 6, "ongoing", ["pharmaceutical stability", "ISS", "shelf life"], "放射線と長期保存が医薬品有効成分へ与える影響を継続評価しています。", "医薬備蓄の信頼性"),
        ("個別化薬物動態宇宙研究", "Personalized Pharmacokinetics in Space Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["pharmacokinetics", "personalized medicine", "NASA"], "体液移動や代謝変化が薬物動態に及ぼす影響を個人差込みで解析しています。", "適切な投薬設計"),
        ("NASA宇宙薬局概念", "NASA Space Pharmacy Concept", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["space pharmacy", "medication", "concept"], "長期探査で必要な薬剤の備蓄、代替、製造まで見据えた概念整理です。", "医療継続性の確保"),
        ("NASAオンデマンド医薬品生産研究", "NASA On-Demand Pharmaceutical Production Study", category, "research", "NASA", "US", 2023, 3, "ongoing", ["on-demand pharma", "biomanufacturing", "NASA"], "微生物や細胞を用いて必要時に薬剤成分を生産する可能性を評価しています。", "薬剤不足対策"),
        ("Stanford遠隔医療遅延通信研究", "Stanford Delayed Telemedicine Study", category, "research", "Stanford University", "US", 2021, 3, "ongoing", ["telemedicine", "latency", "Stanford"], "地球-月間の通信遅延が診断と処置支援へ与える影響を検証しました。", "月面遠隔医療設計"),
        ("M7遠隔超音波誘導研究", "M7 Remote Guided Ultrasound Study", category, "research", "NASA", "US", 2005, 7, "completed", ["M7", "remote guidance", "ultrasound"], "非専門家でも地上支援を受けて超音波検査を実施できることを示した研究です。", "自律診断能力の向上"),
        ("ADUM自律超音波診断研究", "Autonomous Diagnostic Ultrasound in Microgravity Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["autonomous ultrasound", "diagnostics", "NASA"], "AI支援下での自律超音波手技を探る近年の研究方向です。", "通信遅延耐性向上"),
        ("ESA低重力前庭医学研究", "ESA Vestibular Medicine in Altered Gravity Study", category, "research", "ESA", "EU", 2021, 4, "ongoing", ["vestibular", "motion sickness", "ESA"], "前庭系の適応と宇宙酔いの医学的対処を調べる研究です。", "作業適応促進"),
        ("Motion Sickness宇宙酔い薬理研究", "Space Motion Sickness Pharmacology Study", category, "research", "NASA", "US", 2020, 4, "ongoing", ["motion sickness", "pharmacology", "NASA"], "制吐薬の効果と副作用を探査ミッション条件に合わせて再評価しています。", "初期滞在の作業性向上"),
        ("ESA睡眠医療モニタリング研究", "ESA Sleep Medicine Monitoring Study", category, "research", "ESA", "EU", 2022, 4, "ongoing", ["sleep medicine", "monitoring", "ESA"], "概日リズムの乱れと睡眠不足が全身健康へ与える影響を臨床的に追跡しています。", "疲労医療管理"),
        ("NASA心理支援VR医療研究", "NASA VR Support for Behavioral Health Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["behavioral health", "VR", "NASA"], "隔離ストレスや不安を軽減するVR介入の医療的効果を調べています。", "精神衛生支援"),
        ("Cognitive Assessment Toolkit for Spaceflight", "Cognitive Assessment Toolkit for Spaceflight", category, "technology", "NASA", "US", 2017, 6, "ongoing", ["cognition", "assessment", "behavioral"], "認知速度や注意機能の変化を簡便に測るツール群です。", "認知低下の早期検知"),
        ("WinSCAT認知評価ツール", "WinSCAT Cognitive Assessment Tool", category, "technology", "NASA", "US", 2004, 8, "ongoing", ["WinSCAT", "cognitive assessment", "NASA"], "長年使われてきた宇宙飛行士向け認知機能スクリーニングツールです。", "安全運用支援"),
        ("ISS聴覚健康モニタリング", "ISS Hearing Health Monitoring", category, "research", "NASA", "US", 2019, 5, "ongoing", ["hearing", "acoustics", "ISS"], "機械騒音環境が聴覚や疲労へ与える影響を評価する研究です。", "感覚器保護"),
        ("NASA閉鎖環境感染症隔離概念", "NASA Infection Isolation Concept for Closed Habitats", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["infection isolation", "closed habitat", "concept"], "感染症発生時に限られた空間でどう隔離するかを整理した概念検討です。", "アウトブレイク抑制"),
        ("CSA骨折固定宇宙医療キット研究", "CSA Fracture Stabilization Kit Study", category, "research", "Canadian Space Agency", "CA", 2023, 2, "ongoing", ["fracture", "medical kit", "CSA"], "限られた資材で骨折を固定する手技と器材の最適化研究です。", "外傷初期対応"),
        ("NASA宇宙心電図遠隔監視", "NASA Remote ECG Monitoring in Space", category, "technology", "NASA", "US", 2021, 6, "ongoing", ["ECG", "remote monitoring", "NASA"], "長期滞在中の不整脈や負荷変化を継続監視する心電図運用です。", "循環器異常の早期検知"),
        ("NASA超小型血液化学分析研究", "NASA Miniaturized Blood Chemistry Analysis Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["blood chemistry", "miniaturized", "NASA"], "少量サンプルで多項目測定できる機器の月面適用を評価しています。", "省資源診断"),
        ("ESA閉鎖環境抗菌薬耐性研究", "ESA Antimicrobial Resistance in Closed Habitats Study", category, "research", "ESA", "EU", 2023, 3, "ongoing", ["antimicrobial resistance", "closed habitat", "ESA"], "閉鎖環境で耐性菌がどう変化するかを衛生・医療の両面から解析しています。", "感染制御"),
        ("NASA免疫再活性化ウイルス監視", "NASA Latent Virus Reactivation Monitoring", category, "research", "NASA", "US", 2020, 5, "ongoing", ["latent virus", "immune", "NASA"], "ヘルペスウイルス再活性化などを指標に免疫低下を監視しています。", "健康状態把握"),
        ("JAXA iPS細胞宇宙医学研究", "JAXA iPS Cell Space Medicine Study", category, "research", "JAXA", "JP", 2022, 4, "ongoing", ["iPS", "cell biology", "JAXA"], "再生医療や病態モデルへの応用を見据え、宇宙での幹細胞挙動を調べています。", "先端医療基盤の拡張"),
        ("Tissue Regeneration in Space", "Tissue Regeneration in Space", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["tissue regeneration", "space biology", "ESA"], "創傷治癒や組織修復に宇宙環境が与える影響を調べる研究です。", "外傷回復知見"),
        ("NASA月面医療デジタルツイン概念", "NASA Lunar Medical Digital Twin Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["digital twin", "medical", "lunar"], "生体データとリスクモデルを組み合わせ、個人ごとの医療予測を行う構想です。", "予防医療強化"),
        ("Artemis Medical Kit Architecture", "Artemis Medical Kit Architecture", category, "concept", "NASA", "US", 2023, 3, "ongoing", ["Artemis", "medical kit", "architecture"], "限られた容積と重量で必要医療資材を構成する探査キット設計です。", "初期月面運用の安全性"),
        ("NASA月面医療搬送手順研究", "NASA Lunar Casualty Transport Procedure Study", category, "research", "NASA", "US", 2023, 2, "ongoing", ["casualty transport", "lunar surface", "NASA"], "宇宙服着用下で負傷者を搬送する手順と負荷を評価しています。", "救急対応能力"),
        ("ESA長期放射線防護薬研究", "ESA Radioprotective Pharmaceuticals Study", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["radioprotective", "pharmaceuticals", "ESA"], "被ばく障害を軽減する薬剤候補の探索と投与タイミング研究です。", "放射線医療対策"),
        ("NASA小型MRI概念研究", "NASA Compact MRI Concept Study", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["compact MRI", "diagnostics", "concept"], "大型装置が置けない探査拠点向けに、局所診断特化の小型MRI概念が検討されています。", "高度画像診断の将来展望"),
        ("NASA音響診断支援研究", "NASA Acoustic Diagnostic Support Study", category, "research", "NASA", "US", 2021, 3, "ongoing", ["acoustic diagnostics", "decision support", "NASA"], "呼吸音や機器音を含む音響データから健康異常を見つける研究です。", "非侵襲診断の拡張"),
        ("NASA宇宙救急手順XR訓練", "NASA XR Training for Emergency Medical Procedures", category, "technology", "NASA", "US", 2023, 3, "ongoing", ["XR", "medical training", "NASA"], "拡張現実で処置手順を重ねて示し、非専門家の緊急医療対応を支援します。", "処置品質向上"),
        ("CNSA月面拠点医療自律運用概念", "CNSA Autonomous Medical Operations for Lunar Base Concept", category, "concept", "CNSA", "CN", 2023, 2, "ongoing", ["CNSA", "autonomous medicine", "lunar base"], "中国の月面拠点文脈で議論される、自律診療比率を高める医療運用概念です。", "遅延通信下の医療継続"),
        ("Fluid Shifts体液移動研究", "Fluid Shifts Study", category, "research", "NASA", "US", 2015, 7, "completed", ["Fluid Shifts", "headward fluid shift", "NASA"], "頭側への体液移動が脳・眼・循環系へ与える影響を多面的に測定した代表研究です。", "SANSと循環変化の理解"),
        ("Cognition宇宙認知機能研究", "Cognition in Space Study", category, "research", "NASA", "US", 2019, 6, "ongoing", ["Cognition", "neurobehavioral", "NASA"], "長期滞在が注意、速度、感情認識などへ与える影響を標準化タスクで追跡しています。", "認知リスク管理"),
        ("Immunity Assay免疫機能評価", "Immunity Assay Study", category, "research", "NASA", "US", 2020, 5, "ongoing", ["Immunity Assay", "immune function", "NASA"], "船内で免疫細胞機能を簡便に把握する検査法の成立性を調べる研究です。", "免疫低下の早期検出"),
        ("Vascular Echo血管超音波研究", "Vascular Echo Study", category, "research", "NASA", "US", 2021, 5, "ongoing", ["Vascular Echo", "ultrasound", "vascular"], "血管構造と血流変化を超音波で継続評価し、動脈系リスクを定量化しています。", "循環器健康の追跡"),
    ]

    for item in items:
        add(make_entry(*item[:10], detail=item[10], impact=item[11]))

    assert len(entries) == 70
    return entries


def build_exercise_entries():
    entries = []
    add = entries.append
    category = "exercise"

    items = [
        ("TVISトレッドミル運動対策", "Treadmill with Vibration Isolation System", category, "technology", "NASA", "US", 2001, 9, "completed", ["TVIS", "treadmill", "ISS"], "ISS初期の主要ランニング装置で、骨格系負荷維持の基礎運用を担いました。", "有酸素運動の確保"),
        ("COLBERTトレッドミル", "Combined Operational Load Bearing External Resistance Treadmill", category, "technology", "NASA", "US", 2009, 9, "ongoing", ["COLBERT", "treadmill", "running"], "ハーネスで荷重を与えながら走行できるISS後継トレッドミルです。", "骨・筋負荷維持"),
        ("T2トレッドミル運動処方", "T2 Treadmill Exercise Prescription", category, "research", "NASA", "US", 2012, 8, "ongoing", ["T2", "exercise prescription", "ISS"], "走行時間、強度、荷重設定の最適化を続ける実務研究です。", "持久力維持"),
        ("CEVIS自転車エルゴメーター", "Cycle Ergometer with Vibration Isolation System", category, "technology", "NASA", "US", 2001, 9, "ongoing", ["CEVIS", "cycle ergometer", "ISS"], "心肺負荷を与える定番装置で、トレッドミルや抵抗運動と組み合わせて使われます。", "循環器機能維持"),
        ("iRED抵抗運動装置", "Interim Resistive Exercise Device", category, "technology", "NASA", "US", 2002, 8, "completed", ["iRED", "resistance", "ISS"], "ARED導入前に使われた抵抗運動装置で、筋力維持の重要性を示しました。", "筋萎縮対策"),
        ("ARED先進抵抗運動装置", "Advanced Resistive Exercise Device", category, "technology", "NASA", "US", 2009, 9, "ongoing", ["ARED", "resistance", "ISS"], "最大600ポンド級の負荷を模擬できるISSの主力抵抗運動装置です。", "筋骨格維持"),
        ("AREDスクワット負荷研究", "ARED Squat Loading Study", category, "research", "NASA", "US", 2018, 7, "ongoing", ["ARED", "squat", "bone loading"], "スクワット負荷設定と骨密度維持効果の関係を細かく評価しています。", "下肢骨量維持"),
        ("AREDデッドリフト処方研究", "ARED Deadlift Prescription Study", category, "research", "NASA", "US", 2018, 7, "ongoing", ["ARED", "deadlift", "exercise"], "後鎖筋群の維持を狙った処方の有効性を検討した研究です。", "全身筋力維持"),
        ("SPRINT高強度短時間運動研究", "SPRINT High-Intensity Interval Exercise Study", category, "research", "NASA", "US", 2016, 8, "ongoing", ["SPRINT", "HIIT", "ISS"], "運動時間を短縮しつつ同等以上の生理効果を得る高強度プロトコル研究です。", "時間効率の向上"),
        ("Integrated Resistance and Aerobic Training Study", "Integrated Resistance and Aerobic Training Study", category, "research", "NASA", "US", 2016, 8, "completed", ["integrated training", "aerobic", "resistance"], "抵抗運動と有酸素運動を統合したときの最適配分を評価しました。", "運動計画の最適化"),
        ("MARES筋骨格研究装置", "Muscle Atrophy Research and Exercise System", category, "technology", "ESA", "EU", 2007, 8, "ongoing", ["MARES", "muscle", "ESA"], "高精度トルク測定で神経筋機能を評価できる欧州の研究装置です。", "筋機能評価"),
        ("Flywheel宇宙抵抗運動研究", "Flywheel Resistance Exercise in Space Study", category, "research", "ESA", "EU", 2021, 5, "ongoing", ["flywheel", "resistance", "ESA"], "慣性負荷型装置を低重力運動対策として使う可能性を検討しています。", "装置小型化"),
        ("FAREDフライホイール抵抗装置", "Flywheel Advanced Resistive Exercise Device", category, "technology", "ESA", "EU", 2022, 4, "ongoing", ["FARED", "flywheel", "device"], "機械的質量を増やさず高負荷を得る慣性型抵抗装置コンセプトです。", "省質量運動装置"),
        ("Skinsuit重力負荷対策", "Gravity Loading Countermeasure Skinsuit", category, "technology", "King's College London / ESA", "GB", 2017, 6, "ongoing", ["Skinsuit", "loading", "ESA"], "身体軸方向に連続荷重を与え、脊柱伸長や姿勢変化を抑える衣類型対策です。", "受動的負荷付与"),
        ("Penguin Suitロシア負荷スーツ", "Penguin Suit Russian Loading Garment", category, "technology", "Roscosmos", "RU", 1980, 8, "ongoing", ["Penguin Suit", "loading suit", "Russia"], "弾性コードで体幹と四肢に軸圧を与える古典的な宇宙用負荷スーツです。", "受動的運動補助"),
        ("Chibis LBNP循環・運動補助", "Chibis Lower Body Negative Pressure System", category, "technology", "Roscosmos", "RU", 1990, 8, "ongoing", ["Chibis", "LBNP", "circulation"], "下半身陰圧を利用して体液再分配を補正し、運動対策と組み合わせて使われます。", "起立耐性維持"),
        ("LBNPトレッドミル研究", "LBNP Treadmill Study", category, "research", "NASA", "US", 2020, 4, "ongoing", ["LBNP", "treadmill", "exercise"], "陰圧を使ってより自然な荷重走行を実現する運動研究です。", "月面重力模擬"),
        ("短腕遠心機人工重力運動研究", "Short-Arm Centrifuge Artificial Gravity Exercise Study", category, "research", "DLR / ESA", "DE", 2022, 5, "ongoing", ["centrifuge", "artificial gravity", "DLR"], "遠心機と自転車運動を組み合わせ、骨・循環系を同時刺激する研究です。", "複合対策の高効率化"),
        ("AGBRESA人工重力ベッドレスト試験", "AGBRESA Artificial Gravity Bed Rest Study", category, "research", "DLR / ESA / NASA", "DE", 2019, 6, "completed", ["AGBRESA", "bed rest", "artificial gravity"], "頭低位ベッドレストで人工重力の有効性を検討した大規模共同研究です。", "月面対策の地上検証"),
        ("Envihabベッドレスト運動対策研究", "Envihab Bed Rest Exercise Countermeasure Study", category, "research", "DLR", "DE", 2021, 5, "ongoing", ["Envihab", "bed rest", "exercise"], "長期臥床で宇宙類似の身体変化を作り、運動処方を評価しています。", "対策比較"),
        ("MEDESベッドレスト抵抗運動研究", "MEDES Bed Rest Resistance Exercise Study", category, "research", "MEDES Institute for Space Medicine", "FR", 2021, 5, "ongoing", ["MEDES", "bed rest", "resistance"], "欧州の宇宙医学ベッドレスト施設で抵抗運動の防護効果を調べています。", "地上アナログ評価"),
        ("Dry Immersion運動対策試験", "Dry Immersion Exercise Countermeasure Trial", category, "research", "Institute of Biomedical Problems", "RU", 2020, 5, "ongoing", ["dry immersion", "exercise", "IBMP"], "短期間で強い脱荷重状態を再現するドライイマージョンで対策法を検証しています。", "急性脱調対策"),
        ("ARGOS部分免荷歩行システム", "Active Response Gravity Offload System", category, "technology", "NASA Johnson Space Center", "US", 2012, 7, "ongoing", ["ARGOS", "partial gravity", "gait"], "部分重力歩行を地上で再現し、月面歩行やリハビリ訓練に使われる装置です。", "月面歩行訓練"),
        ("Pogo月面歩行バイオメカ研究", "Lunar Bounding Biomechanics Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["bounding", "biomechanics", "lunar gait"], "1/6G相当でのバウンディング歩行が関節負荷とエネルギー消費に与える影響を測定しています。", "歩行様式の最適化"),
        ("EVA運動負荷代謝研究", "EVA Metabolic Load Study", category, "research", "NASA", "US", 2020, 5, "ongoing", ["EVA", "metabolism", "exercise"], "宇宙服での移動や作業が生理的運動負荷としてどの程度かを評価しています。", "作業処方の最適化"),
        ("VR運動動機づけ宇宙研究", "VR Exercise Motivation in Space Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["VR", "motivation", "exercise"], "単調になりがちな運動継続率を上げるため、没入型環境の効果を検討しています。", "アドヒアランス向上"),
        ("Astroskin運動負荷モニタリング", "Astroskin Exercise Load Monitoring", category, "technology", "Canadian Space Agency", "CA", 2021, 6, "ongoing", ["Astroskin", "exercise monitoring", "wearable"], "運動中の心拍や換気量を連続取得し、処方調整に活用する計測です。", "個別化処方"),
        ("MIT心拍変動運動回復研究", "MIT Heart Rate Variability Recovery Study", category, "research", "MIT", "US", 2022, 3, "ongoing", ["HRV", "recovery", "exercise"], "自律神経指標を用いて運動回復度を推定する研究です。", "オーバートレーニング防止"),
        ("NASA骨吸収マーカーと運動研究", "Bone Resorption Markers and Exercise Study", category, "research", "NASA", "US", 2019, 6, "ongoing", ["bone markers", "exercise", "NASA"], "尿・血液マーカーと運動負荷の関係から骨保護効果を評価しています。", "骨量減少抑制"),
        ("NASA筋タンパク同化応答研究", "Muscle Protein Synthesis Response Study", category, "research", "NASA", "US", 2020, 5, "ongoing", ["muscle protein", "anabolism", "exercise"], "抵抗運動が筋タンパク同化シグナルをどこまで維持できるかを分析しています。", "筋萎縮防止"),
        ("bisphosphonate併用運動研究", "Bisphosphonate Plus Exercise Study", category, "research", "NASA", "US", 2013, 7, "completed", ["bisphosphonate", "exercise", "bone"], "薬剤と運動を併用して骨密度低下を抑える複合対策研究です。", "骨保護の強化"),
        ("電気筋刺激運動補助研究", "Neuromuscular Electrical Stimulation Support Study", category, "research", "ESA", "EU", 2022, 4, "ongoing", ["NMES", "electrical stimulation", "ESA"], "運動量が不足する場面で筋刺激を補助的に用いる可能性を検討しています。", "補完的筋維持"),
        ("Galileo振動運動対策研究", "Galileo Vibration Exercise Countermeasure Study", category, "research", "DLR", "DE", 2021, 4, "ongoing", ["vibration", "Galileo", "countermeasure"], "全身振動刺激を骨・筋対策に用いる欧州研究の一つです。", "短時間刺激対策"),
        ("Jumping Device月面跳躍運動研究", "Jumping Device for Lunar Exercise Study", category, "research", "ESA", "EU", 2023, 3, "ongoing", ["jumping", "plyometrics", "ESA"], "低重力環境での跳躍運動を骨刺激源として使う研究です。", "高インパクト代替"),
        ("Rowing Ergometer宇宙適用概念", "Space Rowing Ergometer Concept", category, "concept", "NASA", "US", 2022, 2, "ongoing", ["rowing", "ergometer", "concept"], "全身運動を小さな占有体積で行う代替装置概念です。", "装置多様化"),
        ("Compact Resistive Device月面小型装置構想", "Compact Resistive Device for Lunar Use Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["compact", "resistance", "lunar"], "初期拠点向けに低質量・低容積の抵抗運動装置を構想する研究です。", "初期基地での運動確保"),
        ("Lunar Cruiser車内運動維持概念", "Exercise Maintenance Concept for Lunar Cruiser", category, "concept", "JAXA / Toyota", "JP", 2022, 2, "ongoing", ["Lunar Cruiser", "exercise", "JAXA"], "長期移動型居住で最低限の運動を確保するための車内運動概念です。", "移動生活時の健康維持"),
        ("NASA運動アドヒアランス行動研究", "NASA Exercise Adherence Behavior Study", category, "research", "NASA Human Research Program", "US", 2021, 4, "ongoing", ["adherence", "behavior", "exercise"], "多忙なミッション中に運動を継続する要因と阻害要因を分析しています。", "運動継続率向上"),
        ("ISS運動後回復栄養研究", "ISS Post-Exercise Recovery Nutrition Study", category, "research", "NASA", "US", 2021, 4, "ongoing", ["recovery nutrition", "ISS", "exercise"], "運動後のタンパク質や電解質補給が回復と適応に与える効果を評価しています。", "回復最適化"),
        ("NASA前庭適応と運動研究", "Vestibular Adaptation and Exercise Study", category, "research", "NASA", "US", 2020, 4, "ongoing", ["vestibular", "exercise", "adaptation"], "前庭適応の初期段階でどの運動が安全かを検討する研究です。", "転倒リスク低減"),
        ("ESA筋電バイオフィードバック運動研究", "EMG Biofeedback Exercise Study", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["EMG", "biofeedback", "ESA"], "筋活動の可視化でフォームと出力を最適化する訓練法です。", "運動効率向上"),
        ("MARES神経筋疲労計測研究", "MARES Neuromuscular Fatigue Measurement Study", category, "research", "ESA", "EU", 2021, 5, "ongoing", ["MARES", "fatigue", "neuromuscular"], "運動前後の力発揮と疲労特性を詳細に測る研究です。", "負荷調整の精密化"),
        ("ISS足底荷重モニタ研究", "ISS Plantar Load Monitoring Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["plantar load", "monitoring", "NASA"], "トレッドミル走行時の足底荷重を計測し、骨刺激量を推定しています。", "荷重最適化"),
        ("JAXA低重力歩行リハビリ研究", "JAXA Reduced-Gravity Gait Rehabilitation Study", category, "research", "JAXA", "JP", 2021, 3, "ongoing", ["JAXA", "gait", "rehabilitation"], "帰還後の歩行再適応と月面歩行訓練の両方を見据えた研究です。", "移動機能維持"),
        ("NASA月面作業前コンディショニング研究", "NASA Pre-EVA Conditioning Study for Lunar Surface Work", category, "research", "NASA", "US", 2023, 2, "ongoing", ["conditioning", "EVA", "lunar"], "作業前に行う短時間ウォームアップがパフォーマンスへ与える影響を調べています。", "作業能率向上"),
        ("ESA人工重力自転車運動研究", "Artificial Gravity Cycling Study", category, "research", "ESA", "EU", 2021, 4, "ongoing", ["artificial gravity", "cycling", "ESA"], "遠心機内での自転車運動が循環・筋骨格系へ与える複合刺激を評価しています。", "一体型対策"),
        ("NASA宇宙運動処方AI支援概念", "AI-Assisted Exercise Prescription for Space Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["AI", "exercise prescription", "concept"], "日々の計測値から負荷量を自動調整する運動処方支援の概念です。", "個別化トレーニング"),
        ("Bed Rest SPRINT地上検証", "Bed Rest Validation of SPRINT Protocol", category, "research", "NASA", "US", 2018, 6, "completed", ["bed rest", "SPRINT", "validation"], "地上アナログで短時間高強度処方の有効性を事前確認した研究です。", "宇宙運動処方の裏付け"),
        ("ISSカーフレイズ骨刺激研究", "ISS Calf Raise Bone Loading Study", category, "research", "NASA", "US", 2021, 3, "ongoing", ["calf raise", "bone loading", "ISS"], "下腿部への重点負荷が踵骨や脛骨刺激に与える効果を調べています。", "末梢骨保護"),
        ("NASA体幹安定化運動研究", "NASA Core Stabilization Exercise Study", category, "research", "NASA", "US", 2021, 3, "ongoing", ["core", "stabilization", "NASA"], "脊柱伸長や腰部不快感対策として体幹運動の価値を評価しています。", "腰痛予防"),
        ("ESA脊柱伸長対策運動研究", "ESA Spinal Elongation Countermeasure Exercise Study", category, "research", "ESA", "EU", 2022, 3, "ongoing", ["spine", "elongation", "ESA"], "微小重力で生じる脊柱伸長への対策として運動と負荷衣類を比較しています。", "脊柱健康維持"),
        ("NASA月面重力トレッドミル設計概念", "NASA Lunar Gravity Treadmill Design Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["treadmill", "1/6G", "concept"], "月面での部分重力条件に合わせて荷重機構を再設計する概念です。", "月面専用処方"),
        ("NASA運動器具メンテナンス予知保全研究", "Predictive Maintenance for Exercise Hardware Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["maintenance", "exercise hardware", "NASA"], "センサーで装置摩耗を予測し、故障前に保守する研究です。", "運動継続性の確保"),
        ("CSA遠隔運動コーチング研究", "CSA Remote Exercise Coaching Study", category, "research", "Canadian Space Agency", "CA", 2022, 3, "ongoing", ["coaching", "remote support", "CSA"], "地上運動専門家の助言を限られた通信でどう伝えるかを検討しています。", "フォーム改善"),
        ("NASA運動と認知機能相関研究", "Exercise and Cognitive Function Correlation Study", category, "research", "NASA", "US", 2020, 4, "ongoing", ["cognition", "exercise", "NASA"], "運動量が注意や気分に与える影響を追跡し、行動健康と結び付けています。", "総合パフォーマンス維持"),
        ("ESA低重力骨盤底筋研究", "ESA Pelvic Floor Exercise in Reduced Gravity Study", category, "research", "ESA", "EU", 2023, 2, "ongoing", ["pelvic floor", "reduced gravity", "ESA"], "低重力で見落とされがちな骨盤底筋群への影響を調べる新しい研究です。", "全身機能の偏り是正"),
        ("NASAロボティック運動補助研究", "Robotic Exercise Assistance Study", category, "research", "NASA", "US", 2023, 2, "ongoing", ["robotics", "exercise assistance", "NASA"], "小型ロボット機構で負荷制御や安全補助を行う将来装置研究です。", "装置自律化"),
        ("NASA短時間運動最小有効量研究", "Minimum Effective Dose of Exercise Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["minimum dose", "exercise", "NASA"], "限られたミッション時間で必要最低限の運動量を見積もる研究です。", "運用時間節約"),
        ("JAXA帰還後再適応運動プログラム", "JAXA Post-Flight Reconditioning Program", category, "project", "JAXA", "JP", 2020, 7, "ongoing", ["reconditioning", "JAXA", "post-flight"], "宇宙飛行後の筋力、平衡、持久力回復を支える運動再適応プログラムです。", "再適応支援"),
        ("NASA女性宇宙飛行士運動処方研究", "Exercise Prescription Study for Female Astronauts", category, "research", "NASA", "US", 2023, 2, "ongoing", ["female astronauts", "exercise", "NASA"], "体格差やホルモン要因を考慮した運動処方の最適化を進めています。", "個別化の精度向上"),
        ("CNSA月面クルー運動生理研究", "CNSA Lunar Crew Exercise Physiology Study", category, "research", "CNSA", "CN", 2023, 2, "ongoing", ["CNSA", "exercise physiology", "lunar"], "中国の月面拠点文脈で低重力下の運動生理と対策装置を検討する研究です。", "多国間知見の拡張"),
        ("NASA月面基地フィットネスモジュール概念", "NASA Lunar Base Fitness Module Concept", category, "concept", "NASA", "US", 2023, 2, "ongoing", ["fitness module", "lunar base", "concept"], "限られた空間に複数機能の運動装置をまとめる月面拠点向け概念です。", "居住区設計統合"),
        ("NASA Exercise Countermeasures Project", "NASA Exercise Countermeasures Project", category, "project", "NASA", "US", 2010, 8, "ongoing", ["Exercise Countermeasures", "project", "NASA"], "宇宙飛行中の筋骨格・心肺機能低下を抑える装置と処方を統括する実務プロジェクトです。", "総合対策の継続改善"),
        ("Functional Task Test運動機能評価", "Functional Task Test", category, "research", "NASA", "US", 2017, 6, "ongoing", ["Functional Task Test", "performance", "NASA"], "着陸後や長期滞在後に必要となる立位・移動・荷物運搬能力を評価する試験です。", "実任務能力の確認"),
        ("RVE抵抗振動運動ベッドレスト試験", "Resistive Vibration Exercise Bed Rest Trial", category, "research", "DLR", "DE", 2010, 6, "completed", ["RVE", "vibration", "bed rest"], "抵抗運動と振動刺激を組み合わせたベッドレスト対策の有効性を検証しました。", "地上対策比較"),
        ("Sledge Jump System骨刺激研究", "Sledge Jump System Bone Loading Study", category, "research", "DLR", "DE", 2021, 4, "ongoing", ["Sledge Jump", "bone loading", "DLR"], "短時間の跳躍刺激で骨・腱へ高インパクトを与える地上研究です。", "骨刺激の効率化"),
        ("NASAハーネス快適性運動研究", "NASA Treadmill Harness Comfort Study", category, "research", "NASA", "US", 2020, 4, "ongoing", ["harness", "treadmill", "comfort"], "荷重付与ハーネスの痛みや圧迫を減らし、運動継続性を高める研究です。", "アドヒアランス改善"),
        ("ESA月面EVA前ウォームアップ概念", "ESA Pre-EVA Warm-Up Concept for Lunar Missions", category, "concept", "ESA", "EU", 2023, 2, "ongoing", ["warm-up", "EVA", "ESA"], "低重力作業前に短時間で身体を活性化する準備運動の概念整理です。", "作業中のけが予防"),
        ("NASA部分重力スクワット研究", "NASA Partial Gravity Squat Study", category, "research", "NASA", "US", 2022, 3, "ongoing", ["partial gravity", "squat", "NASA"], "1/6G条件でどの程度の追加負荷が必要かをスクワット動作で調べています。", "月面専用負荷設定"),
        ("JAXA前庭・平衡再訓練運動研究", "JAXA Vestibular and Balance Retraining Exercise Study", category, "research", "JAXA", "JP", 2021, 3, "ongoing", ["vestibular", "balance", "JAXA"], "帰還後や低重力適応期の平衡機能低下に対する再訓練運動を研究しています。", "転倒と酔いの低減"),
    ]

    for item in items:
        add(make_entry(*item[:10], detail=item[10], impact=item[11]))

    assert len(entries) == 70
    return entries


def load_entries():
    entries = []
    entries.extend(build_food_entries())
    entries.extend(build_water_entries())
    entries.extend(build_hygiene_entries())
    entries.extend(build_medical_entries())
    entries.extend(build_exercise_entries())
    return entries


def next_id(conn, category):
    row = conn.execute(
        "SELECT id FROM entries WHERE category = ? ORDER BY CAST(SUBSTR(id, INSTR(id, '_') + 1) AS INTEGER) DESC LIMIT 1",
        (category,),
    ).fetchone()
    if not row:
        return f"{category}_001"
    last_num = int(row[0].split("_")[-1])
    return f"{category}_{last_num + 1:03d}"


def insert_entries(conn, entries):
    existing_titles = {row[0] for row in conn.execute("SELECT title FROM entries")}
    staged_titles = set()
    inserted = 0
    skipped = 0

    for entry in entries:
        title = entry["title"]
        if title in existing_titles or title in staged_titles:
            skipped += 1
            continue

        entry_id = next_id(conn, entry["category"])
        conn.execute(
            """
            INSERT INTO entries (
                id, title, title_en, category, entry_type, summary,
                source_org, source_country, source_year, trl,
                timeline, target_mission, tags, related_modules, authors,
                iss_connection, earth_analog, quality_score, is_enriched
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'reviewed', 1)
            """,
            (
                entry_id,
                entry["title"],
                entry["title_en"],
                entry["category"],
                entry["entry_type"],
                entry["summary"],
                entry["source_org"],
                entry["source_country"],
                entry["source_year"],
                entry["trl"],
                entry["timeline"],
                entry["target_mission"],
                json.dumps(entry["tags"], ensure_ascii=False),
                json.dumps(entry["related_modules"], ensure_ascii=False),
                json.dumps(entry["authors"], ensure_ascii=False),
                entry["iss_connection"],
                entry["earth_analog"],
            ),
        )
        staged_titles.add(title)
        inserted += 1

    conn.commit()
    return inserted, skipped


def print_category_counts(conn):
    print("Category counts:")
    for category, count in conn.execute(
        """
        SELECT category, COUNT(*)
        FROM entries
        WHERE category IN ('food', 'water', 'hygiene', 'medical', 'exercise')
        GROUP BY category
        ORDER BY category
        """
    ):
        print(f"  {category}: {count}")


def main():
    entries = load_entries()
    conn = sqlite3.connect(DB_PATH)
    inserted, skipped = insert_entries(conn, entries)
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    print(f"Prepared entries: {len(entries)}")
    print(f"Inserted: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print(f"Total entries: {total}")
    print_category_counts(conn)
    conn.close()


if __name__ == "__main__":
    main()
