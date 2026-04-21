#!/usr/bin/env python3
"""Collect additional lunar life research entries via Claude API with web knowledge.

Generates 20 entries per category (200 total) covering deeper, more specific
research projects, technologies, and initiatives from around the world.
"""

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

MODULES = ["private_room", "kitchen_dining", "laboratory", "workspace",
           "medical_bay", "training_room", "courtyard", "plantation"]

# Each category has specific deep-dive topics to research
RESEARCH_TOPICS = {
    "food": [
        ("batch_a", "閉鎖環境での食料生産技術（水耕栽培、エアロポニクス、LED農業、微細藻類培養、食用昆虫養殖）に関する具体的なプロジェクトや技術"),
        ("batch_b", "宇宙食の心理学・文化的側面（食事の社会的機能、メニューの単調さ対策、各国の宇宙食開発、3Dフードプリンティング、発酵食品の宇宙応用）"),
    ],
    "water": [
        ("batch_a", "月面の水氷採掘技術（VIPER、PRIME-1、月極域探査、レゴリス加熱抽出、水電気分解）と水資源マッピング"),
        ("batch_b", "閉鎖環境水循環システム（膜蒸留、逆浸透、湿度回収、グレーウォーター処理、バイオリアクター水浄化）"),
    ],
    "hygiene": [
        ("batch_a", "宇宙での個人衛生技術（無水シャンプー、抗菌素材、衣類消臭・再利用、口腔衛生、レゴリスダスト除去）"),
        ("batch_b", "閉鎖環境の微生物管理（ISS微生物叢研究、プロバイオティクス環境、HEPA/光触媒空気清浄、廃棄物処理・リサイクル）"),
    ],
    "medical": [
        ("batch_a", "宇宙遠隔医療・自律医療（AI診断支援、遠隔手術ロボット、3Dバイオプリンティング、ポイントオブケア診断、宇宙薬理学）"),
        ("batch_b", "放射線防護・骨密度低下対策（薬物的対策、遺伝子治療、放射線シールド素材、宇宙飛行士の健康モニタリングウェアラブル）"),
    ],
    "exercise": [
        ("batch_a", "低重力環境での運動処方（抵抗運動装置、フライホイール、全身振動、VR運動、外骨格補助訓練）"),
        ("batch_b", "宇宙での身体機能維持研究（骨密度維持、筋萎縮予防、心血管デコンディショニング、前庭機能、リハビリプロトコル）"),
    ],
    "clothing": [
        ("batch_a", "次世代宇宙服技術（機械式与圧スーツ、自己修復素材、ダスト排除コーティング、スマートテキスタイル、月面用軽量EVAスーツ）"),
        ("batch_b", "船内衣服・テキスタイル技術（抗菌繊維、生分解性素材、3Dニッティング、圧縮着、温度調整素材）"),
    ],
    "communication": [
        ("batch_a", "月面通信インフラ（LunaNet、Moonlight、月面5G/LTE、光通信、中継衛星網、月面GPS）"),
        ("batch_b", "遠隔チームの心理・社会的コミュニケーション（通信遅延対策、非同期コミュニケーション、VRソーシャル、AI仲介対話、家族との接続性）"),
    ],
    "entertainment": [
        ("batch_a", "閉鎖環境でのレクリエーション技術（VR/AR体験、ゲームデザイン、音楽・楽器、芸術活動、スポーツ適応）"),
        ("batch_b", "心理的ウェルビーイング支援（自然映像シミュレーション、園芸療法、マインドフルネス技術、ペットロボット、文化活動プログラム）"),
    ],
    "sleep_habitat": [
        ("batch_a", "居住モジュール設計（インフレータブル構造、3Dプリント建築、レゴリス遮蔽、気密構造、モジュール連結、溶岩チューブ活用）"),
        ("batch_b", "睡眠環境・概日リズム管理（人工照明制御、サウンドスケープ、プライバシー確保、温湿度最適化、29.5日周期への適応）"),
    ],
    "work_environment": [
        ("batch_a", "月面作業支援技術（AR/MRヘッドセット、テレロボティクス、自律走行ローバー、建設用ロボット、レゴリス加工技術）"),
        ("batch_b", "人間工学・認知負荷管理（宇宙服内作業最適化、デジタルツイン、タスクスケジューリングAI、チームワーク支援、疲労管理）"),
    ],
}


def generate_prompt(category_en, topic_desc, existing_titles):
    return f"""You are a space technology researcher with deep expertise in lunar habitation systems.
Generate exactly 10 research entries about the following topic for a lunar life database:

Topic: {topic_desc}
Category: {category_en}

IMPORTANT: Do NOT duplicate these existing entries:
{json.dumps(existing_titles, ensure_ascii=False)}

Focus on REAL, verifiable projects, technologies, and research initiatives. Include:
- Specific NASA/ESA/JAXA/CNSA/SpaceX/Blue Origin/university programs
- Named technologies and systems with their actual development status
- Published research findings and their implications
- International collaborations and commercial ventures
- Both cutting-edge and practical/low-tech solutions

For each entry, provide a JSON object with these fields:
- "title": Japanese title (specific and descriptive - include the name of the project/technology)
- "title_en": English title
- "category": "{category_en}"
- "entry_type": one of "technology", "research", "project", "concept", "challenge", "case_study"
- "summary": 2-3 sentence Japanese summary
- "summary_en": English summary
- "description": Detailed Japanese description (3-5 paragraphs)
- "source_org": primary organization
- "source_country": country code ("US", "EU", "JP", "CN", "KR", "IN", "AE", "international")
- "source_url": actual URL if known, otherwise null
- "source_year": year of latest development (integer)
- "trl": Technology Readiness Level 1-9
- "trl_note": brief Japanese TRL assessment
- "timeline": "2020s", "2030s", "2040s", or "ongoing"
- "target_mission": specific mission name
- "related_modules": JSON array from {json.dumps(MODULES)}
- "tags": JSON array of 3-5 Japanese keyword tags
- "keywords_ja": comma-separated Japanese keywords
- "keywords_en": comma-separated English keywords
- "iss_connection": ISS relevance (Japanese, 1-2 sentences, or null)
- "earth_analog": Earth analog environments (Japanese, or null)

Return ONLY a JSON array of exactly 10 objects. No markdown, no explanation."""


def get_existing_titles(category_en):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT title FROM entries WHERE category = ?", (category_en,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_next_id(category_en):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id FROM entries WHERE category = ? ORDER BY id DESC LIMIT 1",
        (category_en,)
    ).fetchall()
    conn.close()
    if rows:
        num = int(rows[0][0].split('_')[-1])
        return num + 1
    return 1


def insert_entries(entries, category_en, start_num):
    conn = sqlite3.connect(DB_PATH)
    count = 0
    for i, entry in enumerate(entries):
        entry_id = f"{category_en}_{start_num + i:03d}"
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
    for category_en, batches in RESEARCH_TOPICS.items():
        existing_titles = get_existing_titles(category_en)
        start_num = get_next_id(category_en)

        for batch_name, topic_desc in batches:
            print(f"\n[{category_en}/{batch_name}] {topic_desc[:50]}...")

            prompt = generate_prompt(category_en, topic_desc, existing_titles)

            try:
                response = call_claude(prompt, api_key)
                text = response.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0]
                entries = json.loads(text)

                if not isinstance(entries, list):
                    print(f"  Error: Expected list, got {type(entries)}")
                    continue

                count = insert_entries(entries, category_en, start_num)
                total += count
                start_num += len(entries)
                existing_titles.extend([e.get("title", "") for e in entries])
                print(f"  Inserted {count} entries (total for {category_en}: {len(existing_titles)})")

                time.sleep(1)  # rate limit

            except json.JSONDecodeError as e:
                print(f"  JSON parse error: {e}")
                print(f"  Response preview: {response[:200]}")
            except Exception as e:
                print(f"  Error: {e}")

    print(f"\nTotal new entries inserted: {total}")

    # Summary
    conn = sqlite3.connect(DB_PATH)
    total_all = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    print(f"Total entries in database: {total_all}")
    for cat in RESEARCH_TOPICS:
        count = conn.execute("SELECT COUNT(*) FROM entries WHERE category=?", (cat,)).fetchone()[0]
        print(f"  {cat}: {count}")
    conn.close()


if __name__ == '__main__':
    main()
