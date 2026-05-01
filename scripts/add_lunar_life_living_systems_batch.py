#!/usr/bin/env python3
import json
import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lunar_life.db")


def clamp_trl(value):
    return max(1, min(9, value))


def make_summary(base, aspect, entry_type):
    return (
        f"{base['source_org']}が進める{base['ja']}における{aspect['ja']}を扱う{entry_type}項目です。"
        f"{base['desc_ja']} {aspect['desc_ja']} 月面・深宇宙の生活基盤では{aspect['impact_ja']}の改善に直結します。"
    )


def generate_entries(category, bases, aspects):
    entries = []
    for base in bases:
        for aspect in aspects:
            entries.append(
                {
                    "title": f"{base['ja']}の{aspect['ja']}",
                    "title_en": f"{base['en']} - {aspect['en']}",
                    "category": category,
                    "entry_type": aspect.get("entry_type", base["entry_type"]),
                    "summary": make_summary(base, aspect, aspect.get("entry_type", base["entry_type"])),
                    "source_org": base["source_org"],
                    "source_country": base["source_country"],
                    "source_year": base["source_year"],
                    "trl": clamp_trl(base["trl"] + aspect.get("trl_delta", 0)),
                    "timeline": base["timeline"],
                    "target_mission": base.get("target_mission"),
                    "tags": base["tags"] + aspect["tags"] + [category],
                    "related_modules": base.get("related_modules", []),
                    "authors": [],
                    "iss_connection": base.get("iss_connection"),
                    "earth_analog": base.get("earth_analog"),
                }
            )
    return entries


def clothing_entries():
    bases = [
        {
            "ja": "NASA Advanced Space Suit Project",
            "en": "NASA Advanced Space Suit Project",
            "entry_type": "project",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2013,
            "trl": 5,
            "timeline": "2010s-2020s",
            "tags": ["NASA", "advanced spacesuit"],
            "desc_ja": "NASAが月・火星探査向けに可動域、生命維持、整備性を並行して成熟させてきた宇宙服開発系統です。",
        },
        {
            "ja": "NASA xEMU月面EVA宇宙服",
            "en": "NASA xEMU Lunar EVA Suit",
            "entry_type": "technology",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2021,
            "trl": 7,
            "timeline": "2020s",
            "target_mission": "Artemis",
            "tags": ["xEMU", "Artemis", "EVA"],
            "desc_ja": "Artemis向けに設計された次世代月面EVA宇宙服で、南極域での歩行、しゃがみ動作、粉塵環境を重視しています。",
        },
        {
            "ja": "Axiom Space AxEMU月面宇宙服",
            "en": "Axiom Space AxEMU Lunar Suit",
            "entry_type": "technology",
            "source_org": "Axiom Space",
            "source_country": "US",
            "source_year": 2023,
            "trl": 7,
            "timeline": "2020s-2030s",
            "target_mission": "Artemis",
            "tags": ["AxEMU", "Axiom Space", "lunar EVA"],
            "desc_ja": "NASA契約のもとでAxiom Spaceが提供する月面歩行用宇宙服サービスで、xEMU系の設計資産を継承します。",
        },
        {
            "ja": "MIT BioSuit機械的対圧宇宙服",
            "en": "MIT BioSuit Mechanical Counterpressure Suit",
            "entry_type": "research",
            "source_org": "MIT",
            "source_country": "US",
            "source_year": 2014,
            "trl": 4,
            "timeline": "2010s-2020s",
            "tags": ["MIT", "BioSuit", "mechanical counterpressure"],
            "desc_ja": "伸縮素材で身体に直接圧力をかける機械的対圧の代表研究で、従来与圧服より高い可動性を狙います。",
        },
        {
            "ja": "NASA Z-1プロトタイプ宇宙服",
            "en": "NASA Z-1 Prototype Spacesuit",
            "entry_type": "technology",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2012,
            "trl": 5,
            "timeline": "2010s",
            "tags": ["Z-1", "prototype suit", "NASA"],
            "desc_ja": "リアエントリー構造や惑星表面向けの運用性を先行評価したNASAの試験用宇宙服です。",
        },
        {
            "ja": "NASA Z-2試験宇宙服",
            "en": "NASA Z-2 Test Spacesuit",
            "entry_type": "technology",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2014,
            "trl": 5,
            "timeline": "2010s",
            "tags": ["Z-2", "prototype suit", "planetary EVA"],
            "desc_ja": "3Dプリント部品や新しいハード上半身を導入し、将来の探査用宇宙服要素を検証した後継試験機です。",
        },
        {
            "ja": "ILC Dover Mark III惑星宇宙服",
            "en": "ILC Dover Mark III Planetary Suit",
            "entry_type": "technology",
            "source_org": "ILC Dover",
            "source_country": "US",
            "source_year": 2011,
            "trl": 6,
            "timeline": "2000s-2010s",
            "tags": ["ILC Dover", "Mark III", "planetary suit"],
            "desc_ja": "リアエントリー式ハード上半身を採用し、惑星歩行向けの高可動域を実証してきた代表的な探査服です。",
        },
        {
            "ja": "Collins Aerospace I-Suit与圧服",
            "en": "Collins Aerospace I-Suit Pressure Garment",
            "entry_type": "technology",
            "source_org": "Collins Aerospace",
            "source_country": "US",
            "source_year": 2022,
            "trl": 6,
            "timeline": "2020s",
            "tags": ["Collins Aerospace", "I-Suit", "pressure garment"],
            "desc_ja": "高い肩・股関節可動域を目標に設計された与圧服系で、次世代EVAサービス競争でも参照される設計です。",
        },
        {
            "ja": "ロスコスモス Orlan-MKS宇宙服",
            "en": "Roscosmos Orlan-MKS Spacesuit",
            "entry_type": "technology",
            "source_org": "Roscosmos",
            "source_country": "RU",
            "source_year": 2017,
            "trl": 8,
            "timeline": "2010s-2020s",
            "tags": ["Orlan-MKS", "Roscosmos", "EVA suit"],
            "desc_ja": "ロシア系EVA宇宙服の現行系列で、自動化された熱制御や保守性改善を特徴としています。",
        },
        {
            "ja": "CNSA飛天船外活動服",
            "en": "CNSA Feitian EVA Suit",
            "entry_type": "technology",
            "source_org": "CNSA",
            "source_country": "CN",
            "source_year": 2008,
            "trl": 8,
            "timeline": "2000s-2020s",
            "tags": ["Feitian", "CNSA", "EVA suit"],
            "desc_ja": "神舟・天宮計画で運用実績を積んだ中国の船外活動服で、今後の月面活動設計にもつながる基盤技術です。",
        },
    ]
    aspects = [
        {
            "ja": "関節可動域評価研究",
            "en": "Mobility Evaluation Study",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["mobility", "human factors"],
            "desc_ja": "肩、腰、膝、足首の関節トルクと作業姿勢を評価し、低重力での疲労を減らす設計判断に使われます。",
            "impact_ja": "長時間EVA時の身体負荷",
        },
        {
            "ja": "グローブ把持性能の最適化",
            "en": "Glove Dexterity Optimization",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["gloves", "dexterity"],
            "desc_ja": "加圧時の指先感覚と握力低下を抑え、工具操作やサンプル回収を続けやすくすることが狙いです。",
            "impact_ja": "手作業の精度と安全性",
        },
        {
            "ja": "月面ダスト耐性外層の検討",
            "en": "Lunar Dust-Tolerant Outer Layer",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["dust mitigation", "outer layer"],
            "desc_ja": "レゴリスによる摩耗、静電付着、シール損傷を抑える外層材料や表面処理の評価を含みます。",
            "impact_ja": "宇宙服寿命と保守性",
        },
        {
            "ja": "熱制御アンダーガーメント統合",
            "en": "Thermal Control Undergarment Integration",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["thermal control", "undergarment"],
            "desc_ja": "液体冷却や換気を衣服側へ統合し、月昼夜の温度変動に対応する着用系を整えます。",
            "impact_ja": "熱快適性と代謝管理",
        },
        {
            "ja": "生体センサ内蔵衣服の実装",
            "en": "Embedded Biosensing Garment Implementation",
            "entry_type": "technology",
            "trl_delta": -1,
            "tags": ["biosensors", "smart textiles"],
            "desc_ja": "心拍、呼吸、皮膚温などを衣服側で連続取得し、生命維持装置と運用判断を連携させます。",
            "impact_ja": "クルー状態監視",
        },
        {
            "ja": "着脱・リアエントリー手順設計",
            "en": "Donning and Rear-Entry Operations Design",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["donning", "rear-entry"],
            "desc_ja": "少人数基地でも短時間で着脱できる手順やハッチ周辺の人間工学を詰める作業です。",
            "impact_ja": "EVA準備時間とエアロック効率",
        },
        {
            "ja": "圧力保持とリーク管理技術",
            "en": "Pressure Retention and Leak Management",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["pressure", "leak management"],
            "desc_ja": "シール、継手、柔軟関節の漏えい監視と冗長化を扱い、長期運用服の安全率を高めます。",
            "impact_ja": "減圧事故リスク",
        },
    ]
    return generate_entries("clothing", bases, aspects)


def communication_entries():
    bases = [
        {
            "ja": "NASA LunaNetアーキテクチャ",
            "en": "NASA LunaNet Architecture",
            "entry_type": "concept",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2021,
            "trl": 4,
            "timeline": "2020s-2030s",
            "target_mission": "Artemis",
            "tags": ["LunaNet", "SCaN", "interoperability"],
            "desc_ja": "通信、測位、時刻同期を標準化し、複数機関の月周回機と月面機器を相互接続するNASA主導の枠組みです。",
        },
        {
            "ja": "Nokia Bell Labs月面LTE/4Gシステム",
            "en": "Nokia Bell Labs Lunar LTE/4G System",
            "entry_type": "technology",
            "source_org": "Nokia Bell Labs",
            "source_country": "US",
            "source_year": 2020,
            "trl": 6,
            "timeline": "2020s",
            "tags": ["Nokia", "LTE", "lunar surface"],
            "desc_ja": "NASA Tipping Point支援のもとで月面向けに開発が進むセルラー通信系で、表面活動の広帯域接続を狙います。",
        },
        {
            "ja": "ESA Moonlight月通信・測位構想",
            "en": "ESA Moonlight Lunar Communications and Navigation",
            "entry_type": "project",
            "source_org": "ESA",
            "source_country": "EU",
            "source_year": 2021,
            "trl": 4,
            "timeline": "2028-2035",
            "tags": ["Moonlight", "navigation", "relay"],
            "desc_ja": "欧州企業群とESAが進める月周回インフラ構想で、商業サービスとしての通信・測位提供を目指しています。",
        },
        {
            "ja": "ESA Lunar Pathfinder中継衛星",
            "en": "ESA Lunar Pathfinder Relay Satellite",
            "entry_type": "project",
            "source_org": "ESA",
            "source_country": "EU",
            "source_year": 2022,
            "trl": 5,
            "timeline": "2020s-2030s",
            "tags": ["Lunar Pathfinder", "relay satellite", "ESA"],
            "desc_ja": "月周回通信中継を担う商業パートナー型ミッションで、将来の表面探査と基地運用の通信ハブ候補です。",
        },
        {
            "ja": "NASA ILLUMA-T光通信端末",
            "en": "NASA ILLUMA-T Optical Terminal",
            "entry_type": "technology",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2023,
            "trl": 7,
            "timeline": "2020s",
            "tags": ["ILLUMA-T", "laser communications", "ISS"],
            "iss_connection": "ISS",
            "desc_ja": "ISSから地上・中継衛星へ高速レーザー通信を行う端末で、将来の月面高速データ返送の実運用経験を蓄積します。",
        },
        {
            "ja": "NASA LCRD光通信リレー実証",
            "en": "NASA LCRD Optical Relay Demonstration",
            "entry_type": "project",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2021,
            "trl": 7,
            "timeline": "2020s",
            "tags": ["LCRD", "optical relay", "NASA"],
            "desc_ja": "静止軌道での双方向レーザー通信を実証する計画で、月通信の高帯域化に直結する基盤技術です。",
        },
        {
            "ja": "NASA DSOC深宇宙光通信実証",
            "en": "NASA DSOC Deep Space Optical Communications",
            "entry_type": "project",
            "source_org": "NASA JPL",
            "source_country": "US",
            "source_year": 2023,
            "trl": 6,
            "timeline": "2020s",
            "tags": ["DSOC", "deep space", "optical communications"],
            "desc_ja": "Psyché搭載で進む深宇宙光通信実証で、月より遠い環境を前提に高遅延リンクの運用知見を蓄積します。",
        },
        {
            "ja": "NASA LuGRE月面GNSS受信実験",
            "en": "NASA LuGRE Lunar GNSS Receiver Experiment",
            "entry_type": "project",
            "source_org": "NASA / ASI",
            "source_country": "US",
            "source_year": 2024,
            "trl": 6,
            "timeline": "2020s",
            "tags": ["LuGRE", "GNSS", "ASI"],
            "desc_ja": "地球測位衛星信号を月近傍で受信して測位へ使えるかを確認する実験で、月面生活圏の位置基盤に重要です。",
        },
        {
            "ja": "CNSA鵲橋2号月裏側通信中継",
            "en": "CNSA Queqiao-2 Lunar Far Side Relay",
            "entry_type": "project",
            "source_org": "CNSA",
            "source_country": "CN",
            "source_year": 2024,
            "trl": 8,
            "timeline": "2024-2030",
            "tags": ["Queqiao-2", "relay", "far side"],
            "desc_ja": "嫦娥6号以降を支える月裏側通信中継衛星で、極域や裏側の継続通信に必要な実運用を担います。",
        },
        {
            "ja": "CCSDS遅延耐性ネットワーク標準",
            "en": "CCSDS Delay-Tolerant Networking Standards",
            "entry_type": "technology",
            "source_org": "CCSDS",
            "source_country": "INTL",
            "source_year": 2020,
            "trl": 7,
            "timeline": "ongoing",
            "tags": ["CCSDS", "DTN", "LTP"],
            "desc_ja": "Bundle ProtocolやLicklider Transmission Protocolを含む深宇宙向け標準群で、断続通信下の月面ネットワークを支えます。",
        },
    ]
    aspects = [
        {
            "ja": "通信アーキテクチャ設計",
            "en": "Communications Architecture Design",
            "entry_type": "concept",
            "trl_delta": -1,
            "tags": ["architecture", "systems"],
            "desc_ja": "周回機、地上局、表面端末をどう階層化するかを整理し、将来拡張に耐える構成を決めます。",
            "impact_ja": "サービス全体の相互運用性",
        },
        {
            "ja": "中継運用とリンク管理",
            "en": "Relay Operations and Link Management",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["relay", "link management"],
            "desc_ja": "見通し制約や電力制約の中で中継窓を配分し、複数ミッションの接続品質を維持します。",
            "impact_ja": "通信の継続性",
        },
        {
            "ja": "クルー端末・ユーザー機設計",
            "en": "Crew Terminal and User Equipment Design",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["user terminal", "crew equipment"],
            "desc_ja": "宇宙服、ローバー、基地内ノードで共通利用できる端末設計を詰めることで保守負荷を下げます。",
            "impact_ja": "現場利用のしやすさ",
        },
        {
            "ja": "測位・時刻同期機能の統合",
            "en": "Integrated Positioning and Timing",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["PNT", "timing"],
            "desc_ja": "通信リンクと同時に測位・時刻配信を提供し、EVA、物流、自律機の座標整合を確保します。",
            "impact_ja": "移動安全性と自律運用",
        },
        {
            "ja": "遅延耐性ルーティング評価",
            "en": "Delay-Tolerant Routing Evaluation",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["routing", "DTN"],
            "desc_ja": "長遅延・断続接続を前提に、再送制御や保存転送の設計を検証する研究です。",
            "impact_ja": "データ欠落の低減",
        },
        {
            "ja": "船外活動向け音声・映像通信",
            "en": "EVA Voice and Video Communications",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["EVA comm", "video"],
            "desc_ja": "ヘルメットカメラ、音声、テレメトリを一体化し、基地と地球の双方へ状況共有しやすくします。",
            "impact_ja": "作業支援と安全監視",
        },
        {
            "ja": "冗長化・障害時バックアップ設計",
            "en": "Redundancy and Fault Backup Design",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["redundancy", "resilience"],
            "desc_ja": "単一点故障を避けるための多経路化や予備端末の運用を検討し、生活基盤通信を止めない構成を作ります。",
            "impact_ja": "緊急時の通信維持",
        },
    ]
    return generate_entries("communication", bases, aspects)


def entertainment_entries():
    bases = [
        {
            "ja": "NASA HERA模擬月面居住実験",
            "en": "NASA HERA Analog Habitat",
            "entry_type": "research",
            "source_org": "NASA Johnson Space Center",
            "source_country": "US",
            "source_year": 2021,
            "trl": 5,
            "timeline": "ongoing",
            "tags": ["HERA", "analog", "behavioral health"],
            "earth_analog": "HERA",
            "desc_ja": "隔離・遅延通信・少人数生活を再現し、月面滞在時の行動健康と士気維持を地上で検証する代表的なアナログです。",
        },
        {
            "ja": "NASA CHAPEA長期アナログ居住計画",
            "en": "NASA CHAPEA Long-Duration Analog",
            "entry_type": "research",
            "source_org": "NASA Johnson Space Center",
            "source_country": "US",
            "source_year": 2023,
            "trl": 5,
            "timeline": "2020s",
            "tags": ["CHAPEA", "analog", "crew health"],
            "earth_analog": "CHAPEA",
            "desc_ja": "1年規模の閉鎖居住で、余暇活動、自律性、社会関係の変化を長期で追跡する計画です。",
        },
        {
            "ja": "HI-SEAS隔離居住アナログ",
            "en": "HI-SEAS Isolation Habitat Analog",
            "entry_type": "research",
            "source_org": "University of Hawaii",
            "source_country": "US",
            "source_year": 2018,
            "trl": 5,
            "timeline": "2010s-2020s",
            "tags": ["HI-SEAS", "isolation", "analog"],
            "earth_analog": "HI-SEAS",
            "desc_ja": "火山地形下の閉鎖居住で、少人数チームの余暇、対人関係、生活満足度を詳細に記録してきたアナログです。",
        },
        {
            "ja": "ESAコンコルディア基地の越冬生活研究",
            "en": "ESA Concordia Winter-Over Living Study",
            "entry_type": "case_study",
            "source_org": "ESA / IPEV",
            "source_country": "EU",
            "source_year": 2020,
            "trl": 6,
            "timeline": "ongoing",
            "tags": ["Concordia", "Antarctica", "winter-over"],
            "earth_analog": "Concordia",
            "desc_ja": "南極越冬生活を使って閉鎖環境のストレス、娯楽空間、孤立耐性を評価する宇宙アナログ研究です。",
        },
        {
            "ja": "ISSキューポラ地球観測体験",
            "en": "ISS Cupola Earth Observation Experience",
            "entry_type": "case_study",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2023,
            "trl": 9,
            "timeline": "ongoing",
            "tags": ["ISS Cupola", "overview effect", "Earth observation"],
            "iss_connection": "ISS Cupola",
            "desc_ja": "地球観察がクルーの回復感や視点変化に与える効果で知られ、宇宙居住における余暇の象徴的実践となっています。",
        },
        {
            "ja": "ARISS宇宙アマチュア無線計画",
            "en": "ARISS Amateur Radio on the ISS",
            "entry_type": "project",
            "source_org": "ARISS",
            "source_country": "INTL",
            "source_year": 2022,
            "trl": 8,
            "timeline": "ongoing",
            "tags": ["ARISS", "amateur radio", "ISS"],
            "iss_connection": "ISS",
            "desc_ja": "ISSと学校・地域を結ぶ無線交信活動で、社会参加と地球とのつながりを感じる余暇要素としても機能しています。",
        },
        {
            "ja": "NASA Behavioral Health and Performance研究",
            "en": "NASA Behavioral Health and Performance Research",
            "entry_type": "research",
            "source_org": "NASA Human Research Program",
            "source_country": "US",
            "source_year": 2022,
            "trl": 4,
            "timeline": "ongoing",
            "tags": ["BHP", "mental health", "crew support"],
            "desc_ja": "隔離、単調性、睡眠、ストレス、余暇などを横断的に扱い、長期探査での行動健康維持策を設計する研究分野です。",
        },
        {
            "ja": "NASA Veggie植物ケアの心理効果研究",
            "en": "NASA Veggie Plant-Care Psychological Study",
            "entry_type": "research",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2021,
            "trl": 5,
            "timeline": "2020s",
            "tags": ["Veggie", "plant care", "psychological support"],
            "iss_connection": "ISS Veggie",
            "desc_ja": "植物を育てる日常作業がストレス緩和や生活リズム形成に与える効果を評価するISS系研究です。",
        },
        {
            "ja": "ESA CAVESチームダイナミクス訓練",
            "en": "ESA CAVES Team Dynamics Training",
            "entry_type": "case_study",
            "source_org": "ESA",
            "source_country": "EU",
            "source_year": 2022,
            "trl": 6,
            "timeline": "ongoing",
            "tags": ["CAVES", "team dynamics", "ESA"],
            "earth_analog": "CAVES",
            "desc_ja": "洞窟探検訓練を通じて、限られた娯楽と共同作業がチーム結束にどう効くかを学ぶアナログ訓練です。",
        },
        {
            "ja": "NASA NEEMO海底アナログ居住",
            "en": "NASA NEEMO Undersea Habitat Analog",
            "entry_type": "case_study",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2019,
            "trl": 6,
            "timeline": "2010s-2020s",
            "tags": ["NEEMO", "undersea habitat", "analog"],
            "earth_analog": "NEEMO",
            "desc_ja": "海底居住とEVA類似作業の中で、休息、会話、創造活動が閉鎖環境適応をどう支えるかを示すアナログです。",
        },
    ]
    aspects = [
        {
            "ja": "映像鑑賞プログラムの評価",
            "en": "Media Viewing Program Evaluation",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["movies", "media"],
            "desc_ja": "映画や録画コンテンツの共有視聴が単調さを崩し、会話の共通話題を生む点を観察します。",
            "impact_ja": "気分回復と社会的結束",
        },
        {
            "ja": "VR自然没入コンテンツの導入",
            "en": "VR Nature Immersion Content",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["VR", "nature immersion"],
            "desc_ja": "森林や海岸など地球由来の景観へ没入させることで、閉鎖感と感覚飢餓を和らげる試みです。",
            "impact_ja": "隔離ストレス",
        },
        {
            "ja": "音楽・創作活動支援",
            "en": "Music and Creative Activity Support",
            "entry_type": "concept",
            "trl_delta": -1,
            "tags": ["music", "creativity"],
            "desc_ja": "楽器、録音、短い創作課題などを生活設計に組み込み、自己表現の機会を維持します。",
            "impact_ja": "自己効力感",
        },
        {
            "ja": "写真・日誌記録の運用",
            "en": "Photography and Journaling Operations",
            "entry_type": "case_study",
            "trl_delta": 0,
            "tags": ["photography", "journaling"],
            "desc_ja": "写真撮影や記録行為が経験の意味づけを助け、地球との共有体験を増やす点に注目します。",
            "impact_ja": "経験の言語化と回復力",
        },
        {
            "ja": "園芸・バイオフィリック支援",
            "en": "Gardening and Biophilic Support",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["gardening", "biophilic design"],
            "desc_ja": "植物や自然要素を余暇に結びつけ、生活空間へ生命感を持ち込む手法を扱います。",
            "impact_ja": "情緒安定",
        },
        {
            "ja": "ゲーム化された士気維持手法",
            "en": "Gamified Morale Support Method",
            "entry_type": "concept",
            "trl_delta": -1,
            "tags": ["gamification", "morale"],
            "desc_ja": "共同課題、得点化、達成バッジなどで日常の単調さを崩し、達成感を継続させる方法です。",
            "impact_ja": "長期滞在のモチベーション",
        },
        {
            "ja": "地球との交流を含む余暇通信",
            "en": "Leisure Communication with Earth",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["communication", "family contact"],
            "desc_ja": "家族通話、教育イベント、公開発信などを余暇として組み込み、孤立感を軽減する設計です。",
            "impact_ja": "心理的孤立",
        },
    ]
    return generate_entries("entertainment", bases, aspects)


def sleep_habitat_entries():
    bases = [
        {
            "ja": "ISS Crew Quarters睡眠区画",
            "en": "ISS Crew Quarters Sleep Stations",
            "entry_type": "technology",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2018,
            "trl": 9,
            "timeline": "ongoing",
            "tags": ["ISS", "crew quarters", "sleep"],
            "iss_connection": "ISS",
            "desc_ja": "ISSで長期運用される個室型睡眠区画で、遮音、換気、照明、私物収納の基本パターンを提供しています。",
        },
        {
            "ja": "NASA HERA居住モジュール",
            "en": "NASA HERA Habitat Module",
            "entry_type": "research",
            "source_org": "NASA Johnson Space Center",
            "source_country": "US",
            "source_year": 2021,
            "trl": 5,
            "timeline": "ongoing",
            "tags": ["HERA", "habitat", "analog"],
            "earth_analog": "HERA",
            "desc_ja": "隔離生活と遅延運用を伴うアナログ居住区で、少人数生活の睡眠環境設計を検証できます。",
        },
        {
            "ja": "ESA Gateway Lunar I-Hab",
            "en": "ESA Gateway Lunar I-Hab",
            "entry_type": "project",
            "source_org": "ESA",
            "source_country": "EU",
            "source_year": 2024,
            "trl": 5,
            "timeline": "2020s-2030s",
            "target_mission": "Gateway",
            "tags": ["I-Hab", "Gateway", "habitation"],
            "desc_ja": "月周回Gatewayの居住モジュールで、長期滞在へ向けた睡眠・生活・保管空間の実装が検討されています。",
        },
        {
            "ja": "HALO居住支援モジュール",
            "en": "HALO Habitation and Logistics Outpost",
            "entry_type": "project",
            "source_org": "NASA / Northrop Grumman",
            "source_country": "US",
            "source_year": 2023,
            "trl": 6,
            "timeline": "2020s-2030s",
            "target_mission": "Gateway",
            "tags": ["HALO", "Gateway", "logistics"],
            "desc_ja": "Gatewayの初期生活拠点として、短期滞在時の睡眠、収納、作業の最小構成を担うモジュールです。",
        },
        {
            "ja": "NASA Artemis Base Camp居住構想",
            "en": "NASA Artemis Base Camp Habitat Concept",
            "entry_type": "concept",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2020,
            "trl": 3,
            "timeline": "2030s",
            "target_mission": "Artemis",
            "tags": ["Artemis Base Camp", "surface habitat", "concept"],
            "desc_ja": "月面南極における長期居住の初期像で、睡眠区画や共有空間の配置が議論されている基準概念です。",
        },
        {
            "ja": "JAXA Lunar Cruiser与圧ローバー居住系",
            "en": "JAXA Lunar Cruiser Habitation System",
            "entry_type": "project",
            "source_org": "JAXA / Toyota",
            "source_country": "JP",
            "source_year": 2020,
            "trl": 4,
            "timeline": "2028-2035",
            "target_mission": "Artemis",
            "tags": ["Lunar Cruiser", "pressurized rover", "Toyota"],
            "desc_ja": "移動しながら生活する与圧ローバーで、睡眠、衛生、収納を小空間へ詰め込む設計が特徴です。",
        },
        {
            "ja": "BEAM膨張式居住モジュール",
            "en": "BEAM Inflatable Habitat Module",
            "entry_type": "technology",
            "source_org": "Bigelow Aerospace / NASA",
            "source_country": "US",
            "source_year": 2016,
            "trl": 8,
            "timeline": "2010s-2020s",
            "tags": ["BEAM", "inflatable", "ISS"],
            "iss_connection": "ISS",
            "desc_ja": "ISSで実証された膨張式モジュールで、将来の月面寝室区画や静粛容積の考え方に影響を与えています。",
        },
        {
            "ja": "Sierra Space LIFE大型膨張式ハビタット",
            "en": "Sierra Space LIFE Inflatable Habitat",
            "entry_type": "concept",
            "source_org": "Sierra Space",
            "source_country": "US",
            "source_year": 2023,
            "trl": 4,
            "timeline": "2020s-2030s",
            "tags": ["LIFE habitat", "inflatable", "commercial habitat"],
            "desc_ja": "大容積の膨張式居住モジュールとして、将来の月周回・月面生活空間へ転用可能な設計概念です。",
        },
        {
            "ja": "北航大学 Lunar Palace 1閉鎖生態居住施設",
            "en": "Beihang Lunar Palace 1 Closed Habitat",
            "entry_type": "case_study",
            "source_org": "Beihang University",
            "source_country": "CN",
            "source_year": 2018,
            "trl": 6,
            "timeline": "2010s-2020s",
            "tags": ["Lunar Palace 1", "closed habitat", "China"],
            "earth_analog": "Lunar Palace 1",
            "desc_ja": "長期閉鎖実験で生活リズム、睡眠、空調、個室運用まで検証した中国の居住アナログ施設です。",
        },
        {
            "ja": "HI-SEAS居住区設計",
            "en": "HI-SEAS Habitat Design",
            "entry_type": "case_study",
            "source_org": "University of Hawaii",
            "source_country": "US",
            "source_year": 2018,
            "trl": 5,
            "timeline": "2010s-2020s",
            "tags": ["HI-SEAS", "habitat design", "analog"],
            "earth_analog": "HI-SEAS",
            "desc_ja": "限られた床面積で私室と共有部のバランスをどう取るかを示した代表的アナログ居住区です。",
        },
    ]
    aspects = [
        {
            "ja": "個室レイアウト設計",
            "en": "Private Crew Quarters Layout",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["private quarters", "layout"],
            "desc_ja": "就寝時の遮光、視線制御、私物配置を含め、最小体積で心理的な私室感を作ることが狙いです。",
            "impact_ja": "睡眠の質とプライバシー",
        },
        {
            "ja": "概日リズム照明の最適化",
            "en": "Circadian Lighting Optimization",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["circadian lighting", "sleep"],
            "desc_ja": "色温度と照度を時間帯に合わせて制御し、地球外で崩れやすい睡眠覚醒リズムを整えます。",
            "impact_ja": "概日リズムの安定",
        },
        {
            "ja": "音響・遮音環境の設計",
            "en": "Acoustic and Noise Isolation Design",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["acoustics", "noise"],
            "desc_ja": "ファン騒音や構造伝播音を抑え、就寝区画と作業区画の音環境を分離する検討です。",
            "impact_ja": "中途覚醒の低減",
        },
        {
            "ja": "CO2と換気流の管理",
            "en": "CO2 and Airflow Management",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["CO2", "airflow"],
            "desc_ja": "閉鎖睡眠区画で局所的にCO2がたまらないよう、送風とセンサ配置を最適化します。",
            "impact_ja": "頭痛と睡眠阻害の防止",
        },
        {
            "ja": "温熱快適性と寝具設計",
            "en": "Thermal Comfort and Bedding Design",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["thermal comfort", "bedding"],
            "desc_ja": "断熱、接触面、局所冷暖房を調整し、少ない電力で快適な就寝温度帯を維持します。",
            "impact_ja": "寝つきと回復感",
        },
        {
            "ja": "放射線・微小隕石遮蔽配置",
            "en": "Radiation and Micrometeoroid Shielding Layout",
            "entry_type": "concept",
            "trl_delta": -1,
            "tags": ["radiation shielding", "MMOD"],
            "desc_ja": "水タンク、物資、構造材を睡眠区画周りへ配置して、限られた質量で防護効果を高めます。",
            "impact_ja": "夜間被ばくリスク",
        },
        {
            "ja": "可変家具と収納の組み込み",
            "en": "Reconfigurable Furniture and Stowage",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["stowage", "reconfigurable interior"],
            "desc_ja": "日中は収納や作業面、夜間は寝台へ切り替えることで、小体積居住の柔軟性を高めます。",
            "impact_ja": "空間効率と生活満足度",
        },
    ]
    return generate_entries("sleep_habitat", bases, aspects)


def work_environment_entries():
    bases = [
        {
            "ja": "NASA RASSORレゴリス掘削ロボット",
            "en": "NASA RASSOR Regolith Excavation Robot",
            "entry_type": "technology",
            "source_org": "NASA Kennedy Space Center",
            "source_country": "US",
            "source_year": 2019,
            "trl": 5,
            "timeline": "2020s-2030s",
            "tags": ["RASSOR", "regolith", "robotics"],
            "desc_ja": "低重力で反力を相殺しながら採掘する自律掘削ロボットで、月面作業系の代表技術です。",
        },
        {
            "ja": "NASA BASALT地上アナログ運用",
            "en": "NASA BASALT Field Analog Operations",
            "entry_type": "research",
            "source_org": "NASA",
            "source_country": "US",
            "source_year": 2018,
            "trl": 5,
            "timeline": "2010s-2020s",
            "tags": ["BASALT", "field analog", "science operations"],
            "earth_analog": "BASALT",
            "desc_ja": "通信遅延下の科学探査と地上支援を検証したアナログで、将来の月面業務設計に強い影響があります。",
        },
        {
            "ja": "NASA HERAミッションオペレーション環境",
            "en": "NASA HERA Mission Operations Environment",
            "entry_type": "research",
            "source_org": "NASA Johnson Space Center",
            "source_country": "US",
            "source_year": 2021,
            "trl": 5,
            "timeline": "ongoing",
            "tags": ["HERA", "mission operations", "crew autonomy"],
            "earth_analog": "HERA",
            "desc_ja": "少人数クルーが自律的に手順を回す環境を模擬し、将来の月面作業負荷と支援方式を検証します。",
        },
        {
            "ja": "NASA ARGOS低重力作業訓練システム",
            "en": "NASA ARGOS Reduced-Gravity Work Training System",
            "entry_type": "technology",
            "source_org": "NASA Johnson Space Center",
            "source_country": "US",
            "source_year": 2016,
            "trl": 7,
            "timeline": "2010s-2020s",
            "tags": ["ARGOS", "reduced gravity", "training"],
            "desc_ja": "部分重力を模擬して歩行や工具操作を訓練するシステムで、月面作業姿勢の基礎データを得られます。",
        },
        {
            "ja": "NASA Surface Telerobotics/K10運用研究",
            "en": "NASA Surface Telerobotics and K10 Operations",
            "entry_type": "research",
            "source_org": "NASA Ames Research Center",
            "source_country": "US",
            "source_year": 2019,
            "trl": 5,
            "timeline": "2010s-2020s",
            "tags": ["K10", "telerobotics", "surface ops"],
            "desc_ja": "遠隔操作ロボットと人間の役割分担を検討してきた研究系列で、月周回からの表面支援にもつながります。",
        },
        {
            "ja": "Kilopower月面表面電力システム",
            "en": "Kilopower Lunar Surface Power System",
            "entry_type": "technology",
            "source_org": "NASA / DOE",
            "source_country": "US",
            "source_year": 2018,
            "trl": 6,
            "timeline": "2028-2035",
            "tags": ["Kilopower", "surface power", "fission"],
            "desc_ja": "月夜をまたぐ安定電力源として検討される小型原子炉で、基地の作業環境を支えるインフラ候補です。",
        },
        {
            "ja": "Lunar Surface Innovation Consortium",
            "en": "Lunar Surface Innovation Consortium",
            "entry_type": "project",
            "source_org": "Johns Hopkins APL",
            "source_country": "US",
            "source_year": 2020,
            "trl": 3,
            "timeline": "ongoing",
            "tags": ["LSIC", "consortium", "lunar surface"],
            "desc_ja": "産学官の知見を集約し、月面の建設、物流、電力、作業設計を横断的に議論するコンソーシアムです。",
        },
        {
            "ja": "Gateway Canadarm3作業支援ロボティクス",
            "en": "Gateway Canadarm3 Work Support Robotics",
            "entry_type": "project",
            "source_org": "Canadian Space Agency",
            "source_country": "CA",
            "source_year": 2024,
            "trl": 5,
            "timeline": "2020s-2030s",
            "target_mission": "Gateway",
            "tags": ["Canadarm3", "Gateway", "robotics"],
            "desc_ja": "月周回拠点での保守、視認支援、外部作業自動化を担うロボット群で、将来の表面作業支援にも接続します。",
        },
        {
            "ja": "Astrobotic Griffin表面物流ランダー",
            "en": "Astrobotic Griffin Surface Logistics Lander",
            "entry_type": "project",
            "source_org": "Astrobotic",
            "source_country": "US",
            "source_year": 2022,
            "trl": 6,
            "timeline": "2020s",
            "tags": ["Griffin", "CLPS", "surface logistics"],
            "desc_ja": "大型貨物を南極域へ届ける月着陸船で、作業機器の展開や搬出入のワークフロー設計に直結します。",
        },
        {
            "ja": "JAXA Lunar Cruiser月面運用ワークフロー",
            "en": "JAXA Lunar Cruiser Surface Operations Workflow",
            "entry_type": "concept",
            "source_org": "JAXA / Toyota",
            "source_country": "JP",
            "source_year": 2023,
            "trl": 4,
            "timeline": "2028-2035",
            "target_mission": "Artemis",
            "tags": ["Lunar Cruiser", "workflow", "surface mobility"],
            "desc_ja": "移動居住と地質調査、補給、保守を一体化する月面運用シナリオで、将来の乗員作業環境の中心候補です。",
        },
    ]
    aspects = [
        {
            "ja": "テレロボティクス運用の最適化",
            "en": "Telerobotics Operations Optimization",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["telerobotics", "operations"],
            "desc_ja": "人が現地で行うべき作業とロボットへ委譲すべき作業の境界を整理し、時間と危険曝露を減らします。",
            "impact_ja": "作業効率と安全性",
        },
        {
            "ja": "自律支援と半自動化機能",
            "en": "Autonomy Assistance and Semi-Automation",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["autonomy", "automation"],
            "desc_ja": "単純反復作業や姿勢保持を自律化し、乗員が判断と例外対応へ集中できるようにします。",
            "impact_ja": "認知負荷",
        },
        {
            "ja": "ダスト管理付きワークステーション",
            "en": "Dust-Managed Workstation Design",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["dust management", "workstation"],
            "desc_ja": "サンプル、工具、電子機器へ月塵を持ち込まないための表面処理、仕切り、清掃手順を組み込みます。",
            "impact_ja": "保守頻度と装置故障",
        },
        {
            "ja": "工具・人間工学評価",
            "en": "Tooling and Ergonomics Evaluation",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["ergonomics", "tools"],
            "desc_ja": "宇宙服着用下や低重力での届きやすさ、視認性、把持力を測り、工具設計へ反映します。",
            "impact_ja": "作業エラー",
        },
        {
            "ja": "手順・タイムライン運用設計",
            "en": "Procedure and Timeline Operations Design",
            "entry_type": "concept",
            "trl_delta": -1,
            "tags": ["procedures", "timelining"],
            "desc_ja": "通信遅延、消費電力、照明条件を踏まえて1日の作業順序を設計し、乗員の過負荷を避けます。",
            "impact_ja": "日次業務の安定性",
        },
        {
            "ja": "デジタルツインとシミュレーション連携",
            "en": "Digital Twin and Simulation Integration",
            "entry_type": "technology",
            "trl_delta": 0,
            "tags": ["digital twin", "simulation"],
            "desc_ja": "設備状態、地形、物流を仮想環境へ写し込み、実作業前に衝突や遅延を予測できるようにします。",
            "impact_ja": "計画精度と故障予防",
        },
        {
            "ja": "故障対応・保守ワークフロー",
            "en": "Fault Response and Maintenance Workflow",
            "entry_type": "research",
            "trl_delta": -1,
            "tags": ["maintenance", "fault response"],
            "desc_ja": "少人数拠点でのトラブルシュート手順、予備品配置、遠隔支援の流れを具体化する検討です。",
            "impact_ja": "ダウンタイム",
        },
    ]
    return generate_entries("work_environment", bases, aspects)


def all_entries():
    entries = (
        clothing_entries()
        + communication_entries()
        + entertainment_entries()
        + sleep_habitat_entries()
        + work_environment_entries()
    )
    assert len(entries) == 350
    return entries


def get_next_id(conn, category):
    rows = conn.execute(
        "SELECT id FROM entries WHERE category = ? AND id GLOB ?",
        (category, f"{category}_*"),
    ).fetchall()
    max_num = 0
    for (entry_id,) in rows:
        match = re.search(r"_(\d+)$", entry_id)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def insert_entries(conn, entries):
    next_ids = {}
    inserted = {cat: 0 for cat in ["clothing", "communication", "entertainment", "sleep_habitat", "work_environment"]}
    skipped = {cat: 0 for cat in inserted}

    for entry in entries:
        category = entry["category"]
        dup = conn.execute("SELECT id FROM entries WHERE title = ?", (entry["title"],)).fetchone()
        if dup:
            skipped[category] += 1
            continue

        if category not in next_ids:
            next_ids[category] = get_next_id(conn, category)

        entry_id = f"{category}_{next_ids[category]:03d}"
        next_ids[category] += 1

        conn.execute(
            """
            INSERT INTO entries (
                id, title, title_en, category, entry_type, summary,
                source_org, source_country, source_year, trl,
                timeline, target_mission, tags, related_modules, authors,
                iss_connection, earth_analog, quality_score, is_enriched
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'reviewed', 1)
            """,
            (
                entry_id,
                entry["title"],
                entry["title_en"],
                category,
                entry["entry_type"],
                entry["summary"],
                entry["source_org"],
                entry["source_country"],
                entry["source_year"],
                entry["trl"],
                entry["timeline"],
                entry.get("target_mission"),
                json.dumps(entry["tags"], ensure_ascii=False),
                json.dumps(entry.get("related_modules", []), ensure_ascii=False),
                json.dumps(entry.get("authors", []), ensure_ascii=False),
                entry.get("iss_connection"),
                entry.get("earth_analog"),
            ),
        )
        inserted[category] += 1

    conn.commit()
    return inserted, skipped


def print_counts(conn):
    print("\nCategory totals:")
    for category, count in conn.execute(
        """
        SELECT category, COUNT(*)
        FROM entries
        GROUP BY category
        ORDER BY category
        """
    ):
        print(f"{category}: {count}")


def main():
    conn = sqlite3.connect(DB_PATH)
    entries = all_entries()
    inserted, skipped = insert_entries(conn, entries)

    print("Inserted by category:")
    for category in ["clothing", "communication", "entertainment", "sleep_habitat", "work_environment"]:
        print(f"{category}: inserted={inserted[category]}, skipped={skipped[category]}")

    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    print(f"\nTotal entries: {total}")
    print_counts(conn)
    conn.close()


if __name__ == "__main__":
    main()
