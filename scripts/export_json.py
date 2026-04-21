#!/usr/bin/env python3
"""Export SQLite data to JSON files for the Next.js dashboard."""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data')

CATEGORIES = {
    'food': '食',
    'water': '水',
    'hygiene': '衛生',
    'medical': '医療',
    'exercise': '運動',
    'clothing': '衣服',
    'communication': 'コミュニケーション',
    'entertainment': '娯楽',
    'sleep_habitat': '睡眠・住環境',
    'work_environment': '作業環境',
}


def export():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Export entries with sources
    entries_raw = conn.execute("""
        SELECT * FROM entries ORDER BY category, id
    """).fetchall()

    entries = []
    for row in entries_raw:
        entry = dict(row)
        # Parse JSON fields
        for field in ['related_modules', 'tags', 'authors']:
            if entry.get(field):
                try:
                    entry[field] = json.loads(entry[field])
                except (json.JSONDecodeError, TypeError):
                    entry[field] = []
            else:
                entry[field] = []

        # Attach sources
        sources = conn.execute(
            "SELECT * FROM sources WHERE entry_id = ?", (entry['id'],)
        ).fetchall()
        entry['sources'] = [dict(s) for s in sources]
        entries.append(entry)

    # Export challenges
    challenges_raw = conn.execute("SELECT * FROM challenges ORDER BY category").fetchall()
    challenges = [dict(c) for c in challenges_raw]

    # Export relations
    relations_raw = conn.execute("SELECT * FROM relations").fetchall()
    relations = [dict(r) for r in relations_raw]

    # Build stats
    stats = {
        'total_entries': len(entries),
        'total_challenges': len(challenges),
        'by_category': {},
        'by_source_org': {},
        'by_trl': {},
        'by_timeline': {},
        'by_entry_type': {},
        'by_country': {},
        'organizations': set(),
    }

    for entry in entries:
        cat = entry['category']
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

        org = entry.get('source_org', 'Unknown') or 'Unknown'
        stats['by_source_org'][org] = stats['by_source_org'].get(org, 0) + 1
        stats['organizations'].add(org)

        trl = entry.get('trl')
        if trl:
            trl_key = str(trl)
            stats['by_trl'][trl_key] = stats['by_trl'].get(trl_key, 0) + 1

        timeline = entry.get('timeline', 'unknown') or 'unknown'
        stats['by_timeline'][timeline] = stats['by_timeline'].get(timeline, 0) + 1

        etype = entry.get('entry_type', 'unknown') or 'unknown'
        stats['by_entry_type'][etype] = stats['by_entry_type'].get(etype, 0) + 1

        country = entry.get('source_country', 'unknown') or 'unknown'
        stats['by_country'][country] = stats['by_country'].get(country, 0) + 1

    stats['total_organizations'] = len(stats['organizations'])
    stats['organizations'] = sorted(list(stats['organizations']))

    # Category details with challenge counts
    stats['categories'] = {}
    for cat_en, cat_ja in CATEGORIES.items():
        cat_challenges = [c for c in challenges if c['category'] == cat_en]
        stats['categories'][cat_en] = {
            'name_ja': cat_ja,
            'entry_count': stats['by_category'].get(cat_en, 0),
            'challenge_count': len(cat_challenges),
        }

    # Write files
    entries_path = os.path.join(DATA_DIR, 'entries.json')
    with open(entries_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(entries)} entries to {entries_path}")

    challenges_path = os.path.join(DATA_DIR, 'challenges.json')
    with open(challenges_path, 'w', encoding='utf-8') as f:
        json.dump(challenges, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(challenges)} challenges to {challenges_path}")

    stats_path = os.path.join(DATA_DIR, 'stats.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Exported stats to {stats_path}")

    conn.close()


if __name__ == '__main__':
    export()
