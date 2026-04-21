#!/usr/bin/env python3
"""Initialize the Lunar Life Research Database."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'lunar_life.db')

SCHEMA = """
-- Core research entries
CREATE TABLE IF NOT EXISTS entries (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    title_en    TEXT,
    category    TEXT NOT NULL CHECK(category IN (
        'food', 'water', 'hygiene', 'medical', 'exercise',
        'clothing', 'communication', 'entertainment',
        'sleep_habitat', 'work_environment'
    )),
    entry_type  TEXT NOT NULL CHECK(entry_type IN (
        'technology', 'research', 'project', 'concept',
        'regulation', 'challenge', 'case_study'
    )),
    summary     TEXT,
    summary_en  TEXT,
    description TEXT,

    -- Source metadata
    source_org      TEXT,
    source_country  TEXT,
    source_url      TEXT,
    source_year     INTEGER,
    authors         TEXT,  -- JSON array

    -- Technology/maturity metadata
    trl             INTEGER CHECK(trl BETWEEN 1 AND 9),
    trl_note        TEXT,
    timeline        TEXT,
    target_mission  TEXT,

    -- Lunar base module linkage
    related_modules TEXT,  -- JSON array

    -- Tags & classification
    tags        TEXT,  -- JSON array
    keywords_ja TEXT,
    keywords_en TEXT,

    -- ISS connection
    iss_connection  TEXT,
    earth_analog    TEXT,

    -- Quality
    quality_score   TEXT DEFAULT 'draft' CHECK(quality_score IN (
        'draft', 'reviewed', 'verified', 'primary_source'
    )),
    is_enriched     INTEGER DEFAULT 0,
    image_url       TEXT,

    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- Bibliography and research sources
CREATE TABLE IF NOT EXISTS sources (
    id          TEXT PRIMARY KEY,
    entry_id    TEXT NOT NULL REFERENCES entries(id),
    source_type TEXT CHECK(source_type IN (
        'webpage', 'paper', 'report', 'news', 'patent', 'press_release', 'book'
    )),
    title       TEXT,
    url         TEXT,
    author      TEXT,
    year        INTEGER,
    doi         TEXT,
    notes       TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Cross-category connections
CREATE TABLE IF NOT EXISTS relations (
    id              TEXT PRIMARY KEY,
    source_entry_id TEXT NOT NULL REFERENCES entries(id),
    target_entry_id TEXT NOT NULL REFERENCES entries(id),
    relation_type   TEXT CHECK(relation_type IN (
        'enables', 'requires', 'supplements', 'replaces', 'conflicts_with', 'related'
    )),
    description     TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Lunar environment challenges
CREATE TABLE IF NOT EXISTS challenges (
    id              TEXT PRIMARY KEY,
    name_ja         TEXT NOT NULL,
    name_en         TEXT,
    category        TEXT NOT NULL,
    challenge_type  TEXT CHECK(challenge_type IN (
        'radiation', 'microgravity', 'dust', 'vacuum', 'thermal',
        'psychological', 'resource_scarcity', 'communication_delay',
        'isolation', 'confined_environment'
    )),
    description     TEXT,
    severity        TEXT CHECK(severity IN ('critical', 'high', 'medium', 'low')),
    iss_analog      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Research progress tracking
CREATE TABLE IF NOT EXISTS collection_log (
    id          TEXT PRIMARY KEY,
    category    TEXT,
    source_org  TEXT,
    query_used  TEXT,
    entries_added INTEGER DEFAULT 0,
    status      TEXT DEFAULT 'pending',
    notes       TEXT,
    run_at      TEXT DEFAULT (datetime('now'))
);

-- Full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
    title, title_en, summary, summary_en, description,
    source_org, tags, keywords_ja, keywords_en,
    content=entries, content_rowid=rowid,
    tokenize='unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
    INSERT INTO entries_fts(rowid, title, title_en, summary, summary_en, description,
        source_org, tags, keywords_ja, keywords_en)
    VALUES (new.rowid, new.title, new.title_en, new.summary, new.summary_en, new.description,
        new.source_org, new.tags, new.keywords_ja, new.keywords_en);
END;

CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
    INSERT INTO entries_fts(entries_fts, rowid, title, title_en, summary, summary_en, description,
        source_org, tags, keywords_ja, keywords_en)
    VALUES ('delete', old.rowid, old.title, old.title_en, old.summary, old.summary_en, old.description,
        old.source_org, old.tags, old.keywords_ja, old.keywords_en);
END;

CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
    INSERT INTO entries_fts(entries_fts, rowid, title, title_en, summary, summary_en, description,
        source_org, tags, keywords_ja, keywords_en)
    VALUES ('delete', old.rowid, old.title, old.title_en, old.summary, old.summary_en, old.description,
        old.source_org, old.tags, old.keywords_ja, old.keywords_en);
    INSERT INTO entries_fts(rowid, title, title_en, summary, summary_en, description,
        source_org, tags, keywords_ja, keywords_en)
    VALUES (new.rowid, new.title, new.title_en, new.summary, new.summary_en, new.description,
        new.source_org, new.tags, new.keywords_ja, new.keywords_en);
END;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category);
CREATE INDEX IF NOT EXISTS idx_entries_trl ON entries(trl);
CREATE INDEX IF NOT EXISTS idx_entries_source_org ON entries(source_org);
CREATE INDEX IF NOT EXISTS idx_entries_timeline ON entries(timeline);
CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_sources_entry ON sources(entry_id);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entry_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entry_id);
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.close()
    print(f"Database initialized at {os.path.abspath(DB_PATH)}")

    # Verify
    conn = sqlite3.connect(DB_PATH)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables: {', '.join(t[0] for t in tables)}")
    conn.close()

if __name__ == '__main__':
    init_db()
