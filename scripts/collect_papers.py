#!/usr/bin/env python3
"""Collect lunar life research entries from academic papers via Claude API.

Generates structured entries based on real published papers about
lunar habitation, space life sciences, and related topics.
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

# Academic research topics grouped by category
PAPER_TOPICS = {
    "food": "lunar agriculture, closed ecological life support food, space crop production, bioregenerative food systems",
    "water": "lunar water ice extraction, ISRU water, closed-loop water recycling spacecraft, membrane distillation space",
    "hygiene": "spacecraft microbiome, space hygiene, lunar dust toxicology, closed habitat waste management",
    "medical": "space medicine telemedicine, radiation countermeasures spaceflight, bone loss microgravity pharmaceutical, autonomous surgery space",
    "exercise": "exercise countermeasures spaceflight, resistive exercise microgravity, bone density preservation astronaut",
    "clothing": "planetary spacesuit design, mechanical counter-pressure suit, smart textiles space, lunar dust resistant materials",
    "communication": "delay-tolerant networking space, lunar communication architecture, psychological isolation communication crew",
    "entertainment": "recreation confined environments, virtual reality space habitat, psychological well-being long-duration spaceflight",
    "sleep_habitat": "circadian rhythm space, sleep quality microgravity, lunar habitat design, 3D printed lunar structure, inflatable habitat",
    "work_environment": "augmented reality space maintenance, telerobotics lunar surface, human factors extravehicular activity, cognitive workload space",
}


def generate_prompt(category_en, paper_topics):
    return f"""You are a space science academic researcher. Based on your knowledge of published research literature (2015-2025), generate exactly 5 database entries about research papers and their findings relevant to lunar surface living.

Research area: {paper_topics}
Category: {category_en}

For each entry, create a structured record based on REAL published papers or well-known research programs. Include:
- Actual paper titles, authors, and journals where possible
- Real DOIs or arXiv IDs if known
- Genuine research findings and their implications for lunar habitation

Provide a JSON array with these fields per entry:
- "title": Japanese title describing the research finding
- "title_en": English title (can be the paper title)
- "category": "{category_en}"
- "entry_type": "research"
- "summary": 2-3 sentence Japanese summary of the finding and its lunar relevance
- "summary_en": English summary
- "description": Detailed Japanese description (research methodology, key findings, implications for lunar base design, 3-4 paragraphs)
- "source_org": lead institution
- "source_country": country code
- "source_url": DOI URL or null
- "source_year": publication year
- "authors": JSON array of author names
- "trl": estimated TRL 1-9
- "trl_note": Japanese TRL assessment
- "timeline": when findings could be applied
- "target_mission": relevant mission
- "related_modules": JSON array from {json.dumps(MODULES)}
- "tags": JSON array of 3-5 Japanese tags
- "keywords_ja": comma-separated Japanese keywords
- "keywords_en": comma-separated English keywords
- "iss_connection": ISS relevance (Japanese, or null)
- "earth_analog": Earth analog (Japanese, or null)
- "paper_doi": DOI string if known, else null
- "paper_journal": journal name if known

Return ONLY a JSON array. No markdown."""


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
                    authors,
                    trl, trl_note, timeline, target_mission,
                    related_modules, tags, keywords_ja, keywords_en,
                    iss_connection, earth_analog, is_enriched
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                entry_id,
                entry.get("title", ""),
                entry.get("title_en", ""),
                category_en,
                entry.get("entry_type", "research"),
                entry.get("summary", ""),
                entry.get("summary_en", ""),
                entry.get("description", ""),
                entry.get("source_org", ""),
                entry.get("source_country", ""),
                entry.get("source_url") or entry.get("paper_doi"),
                entry.get("source_year"),
                json.dumps(entry.get("authors", []), ensure_ascii=False),
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

            # Also insert source record if DOI available
            doi = entry.get("paper_doi")
            journal = entry.get("paper_journal")
            if doi or journal:
                source_id = f"src_{entry_id}"
                conn.execute("""
                    INSERT OR IGNORE INTO sources (id, entry_id, source_type, title, url, author, year, doi)
                    VALUES (?, ?, 'paper', ?, ?, ?, ?, ?)
                """, (
                    source_id, entry_id,
                    entry.get("title_en", ""),
                    f"https://doi.org/{doi}" if doi else None,
                    ", ".join(entry.get("authors", [])),
                    entry.get("source_year"),
                    doi,
                ))

        except Exception as e:
            print(f"  Error inserting {entry_id}: {e}")

    conn.commit()
    conn.close()
    return count


def main():
    api_key = get_api_key()
    if not api_key:
        print("Error: Could not retrieve Anthropic API key")
        return

    total = 0
    for category_en, topics in PAPER_TOPICS.items():
        print(f"\nCollecting papers for {category_en}...")
        start_num = get_next_id(category_en)
        prompt = generate_prompt(category_en, topics)

        try:
            response = call_claude(prompt, api_key)
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            entries = json.loads(text)

            if not isinstance(entries, list):
                print(f"  Error: Expected list")
                continue

            count = insert_entries(entries, category_en, start_num)
            total += count
            print(f"  Inserted {count} paper entries")
            time.sleep(1)

        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal paper entries inserted: {total}")

    conn = sqlite3.connect(DB_PATH)
    total_all = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    sources_count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    print(f"Total entries: {total_all}, Total sources: {sources_count}")
    conn.close()


if __name__ == '__main__':
    main()
