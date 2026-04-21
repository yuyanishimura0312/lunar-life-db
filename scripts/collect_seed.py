#!/usr/bin/env python3
"""Generate seed data for the Lunar Life Research Database using Claude API."""

import sqlite3
import json
import os
import subprocess
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')

def get_api_key():
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', 'ANTHROPIC_API_KEY', '-w'],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def call_claude(prompt, api_key):
    import urllib.request
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["content"][0]["text"]

CATEGORIES = [
    ("food", "食"),
    ("water", "水"),
    ("hygiene", "衛生"),
    ("medical", "医療"),
    ("exercise", "運動"),
    ("clothing", "衣服"),
    ("communication", "コミュニケーション"),
    ("entertainment", "娯楽"),
    ("sleep_habitat", "睡眠・住環境"),
    ("work_environment", "作業環境"),
]

MODULES = ["private_room", "kitchen_dining", "laboratory", "workspace",
           "medical_bay", "training_room", "courtyard", "plantation"]

def generate_prompt(category_en, category_ja):
    return f"""You are a space technology researcher. Generate exactly 5 research entries about "{category_ja}" ({category_en}) challenges and solutions for lunar surface living.

Context: This is for a database about lunar base life, based on JAXA's "Space Life on the Moon" research. The lunar base has these modules: private rooms, kitchen/dining, laboratory, workspace, medical bay, training room, courtyard (with plants), and plantation.

For each entry, provide a JSON object with these fields:
- "title": Japanese title (concise, descriptive)
- "title_en": English title
- "category": "{category_en}"
- "entry_type": one of "technology", "research", "project", "concept", "challenge", "case_study"
- "summary": 2-3 sentence Japanese summary of what this is and why it matters for lunar living
- "summary_en": English summary
- "description": Detailed Japanese description (3-5 paragraphs, covering the technology/research, its current status, relevance to lunar base life, and future outlook)
- "source_org": primary organization (e.g., "NASA", "ESA", "JAXA", "CNSA", "SpaceX", "MIT", etc.)
- "source_country": country code ("US", "EU", "JP", "CN", "international")
- "source_url": actual URL if known, otherwise null
- "source_year": year of latest development (integer)
- "trl": Technology Readiness Level 1-9
- "trl_note": brief Japanese explanation of the TRL assessment
- "timeline": "2020s", "2030s", "2040s", or "ongoing"
- "target_mission": e.g., "Artemis", "Gateway", "Lunar Base", "ISS", "CHAPEA"
- "related_modules": JSON array of relevant lunar base modules from {json.dumps(MODULES)}
- "tags": JSON array of 3-5 keyword tags in Japanese
- "keywords_ja": comma-separated Japanese keywords
- "keywords_en": comma-separated English keywords
- "iss_connection": how ISS experience relates (Japanese, 1-2 sentences, or null)
- "earth_analog": relevant Earth analog environments (Japanese, or null)

Include a diverse mix:
- At least one from a non-US/EU/JP source
- Mix of TRL levels (some basic research TRL 1-3, some proven TRL 7-9)
- Both near-term and long-term solutions
- Both high-tech and simple/practical approaches

Return ONLY a JSON array of exactly 5 objects. No markdown, no explanation."""


def insert_entries(entries, category_en):
    conn = sqlite3.connect(DB_PATH)
    count = 0
    for i, entry in enumerate(entries):
        entry_id = f"{category_en}_{i+1:03d}"
        try:
            conn.execute("""
                INSERT OR IGNORE INTO entries (
                    id, title, title_en, category, entry_type,
                    summary, summary_en, description,
                    source_org, source_country, source_url, source_year,
                    trl, trl_note, timeline, target_mission,
                    related_modules, tags, keywords_ja, keywords_en,
                    iss_connection, earth_analog, is_enriched
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                entry_id,
                entry.get("title", ""),
                entry.get("title_en", ""),
                category_en,
                entry.get("entry_type", "technology"),
                entry.get("summary", ""),
                entry.get("summary_en", ""),
                entry.get("description", ""),
                entry.get("source_org", ""),
                entry.get("source_country", ""),
                entry.get("source_url"),
                entry.get("source_year"),
                entry.get("trl"),
                entry.get("trl_note", ""),
                entry.get("timeline", ""),
                entry.get("target_mission", ""),
                json.dumps(entry.get("related_modules", []), ensure_ascii=False),
                json.dumps(entry.get("tags", []), ensure_ascii=False),
                entry.get("keywords_ja", ""),
                entry.get("keywords_en", ""),
                entry.get("iss_connection"),
                entry.get("earth_analog"),
            ))
            count += 1
        except Exception as e:
            print(f"  Error inserting {entry_id}: {e}")
    conn.commit()
    conn.close()
    return count


def main():
    api_key = get_api_key()
    if not api_key:
        print("Error: Could not retrieve Anthropic API key from keychain")
        return

    total = 0
    for category_en, category_ja in CATEGORIES:
        print(f"\nGenerating entries for {category_ja} ({category_en})...")
        prompt = generate_prompt(category_en, category_ja)

        try:
            response = call_claude(prompt, api_key)
            # Parse JSON from response
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            entries = json.loads(text)

            if not isinstance(entries, list):
                print(f"  Error: Expected list, got {type(entries)}")
                continue

            count = insert_entries(entries, category_en)
            total += count
            print(f"  Inserted {count} entries")

            # Rate limiting
            time.sleep(1)

        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
            print(f"  Response preview: {response[:200]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Insert seed challenges
    insert_seed_challenges()

    print(f"\nTotal entries inserted: {total}")

    # Verify
    conn = sqlite3.connect(DB_PATH)
    for cat_en, cat_ja in CATEGORIES:
        count = conn.execute("SELECT COUNT(*) FROM entries WHERE category=?", (cat_en,)).fetchone()[0]
        print(f"  {cat_ja}: {count} entries")
    conn.close()


def insert_seed_challenges():
    """Insert lunar environment challenges from JAXA PDF."""
    challenges = [
        ("ch_001", "宇宙放射線被曝", "Space radiation exposure", "medical",
         "radiation", "月面では地球磁場による防護がなく、銀河宇宙線や太陽粒子線に直接曝される。長期滞在では発がんリスクや中枢神経障害が懸念される。",
         "critical", "ISS乗組員は約6ヶ月で地上の約100倍の放射線を浴びる"),
        ("ch_002", "低重力環境（1/6G）", "Low gravity (1/6G)", "exercise",
         "microgravity", "月面の重力は地球の約1/6。骨密度低下、筋萎縮、心血管機能の変化が生じる。ISSの微小重力よりはましだが、長期的影響は未知。",
         "high", "ISS乗組員は月1-2%の骨密度低下を経験"),
        ("ch_003", "月面レゴリスの有害性", "Lunar regolith toxicity", "hygiene",
         "dust", "月面のレゴリスは微細で鋭角的な粒子で、吸入すると肺損傷を引き起こす可能性がある。帯電性が高く、機器や宇宙服に付着しやすい。",
         "critical", "アポロ飛行士が報告した「月の匂い」と呼吸器症状"),
        ("ch_004", "閉鎖空間での心理的ストレス", "Psychological stress in confinement", "entertainment",
         "psychological", "限られた空間で少人数が長期間生活することによる心理的負荷。対人関係の摩擦、単調さ、地球との隔絶感が問題となる。",
         "high", "ISS6ヶ月ミッション、南極越冬隊での報告"),
        ("ch_005", "水資源の制約", "Water resource limitations", "water",
         "resource_scarcity", "月面での水は極めて貴重な資源。飲料水、衛生用水、農業用水のすべてを限られた資源で賄う必要がある。",
         "critical", "ISS ECLSSは尿を含む水の93%以上をリサイクル"),
        ("ch_006", "通信遅延と地球との隔絶", "Communication delay and isolation", "communication",
         "communication_delay", "地球-月間の通信遅延は約1.3秒（片道）。リアルタイム会話は可能だが、自律的な意思決定能力が必要。",
         "medium", "ISS乗組員はリアルタイム通信が可能"),
        ("ch_007", "極端な温度差", "Extreme temperature variations", "sleep_habitat",
         "thermal", "月面は日中+127°C、夜間-173°Cという極端な温度差がある。居住モジュールの断熱と温度管理が不可欠。",
         "high", "ISS外部は-157°Cから+121°Cの範囲"),
        ("ch_008", "食料の自給自足", "Food self-sufficiency", "food",
         "resource_scarcity", "地球からの補給に依存しない食料生産体制の構築が必要。閉鎖環境での農業、栄養バランス、食の心理的満足度の確保が課題。",
         "high", "ISS Veggie/APH実験での少量栽培"),
        ("ch_009", "真空環境", "Vacuum environment", "work_environment",
         "vacuum", "月面は事実上真空（大気圧の10^-12）。船外活動時の宇宙服依存、減圧事故のリスク、エアロック設計の重要性。",
         "critical", None),
        ("ch_010", "閉鎖環境での衛生管理", "Hygiene in closed environment", "hygiene",
         "confined_environment", "微生物叢の管理、廃棄物処理、空気清浄が閉鎖環境の健康を左右する。抗菌素材や紫外線殺菌の活用が必要。",
         "high", "ISS内の微生物モニタリングと空気浄化システム"),
    ]

    conn = sqlite3.connect(DB_PATH)
    for ch in challenges:
        conn.execute("""
            INSERT OR IGNORE INTO challenges (id, name_ja, name_en, category,
                challenge_type, description, severity, iss_analog)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ch)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
    print(f"\nInserted {count} challenges")
    conn.close()


if __name__ == '__main__':
    main()
