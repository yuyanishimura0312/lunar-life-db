import type { Entry, Challenge, Stats, Category } from "./types";
import { CATEGORY_CONFIG } from "./constants";

// These will be populated by export_json.py
let entriesData: Entry[] = [];
let challengesData: Challenge[] = [];
let statsData: Stats | null = null;

try {
  entriesData = require("../src/data/entries.json");
} catch {
  entriesData = [];
}

try {
  challengesData = require("../src/data/challenges.json");
} catch {
  challengesData = [];
}

try {
  statsData = require("../src/data/stats.json");
} catch {
  statsData = null;
}

export function getEntries(): Entry[] {
  return entriesData;
}

export function getEntry(id: string): Entry | undefined {
  return entriesData.find((e) => e.id === id);
}

export function getEntriesByCategory(category: Category): Entry[] {
  return entriesData.filter((e) => e.category === category);
}

export function getChallenges(): Challenge[] {
  return challengesData;
}

export function getChallengesByCategory(category: Category): Challenge[] {
  return challengesData.filter((c) => c.category === category);
}

export function getStats(): Stats {
  if (statsData) return statsData;
  // Fallback: compute from entries
  const by_category: Record<string, number> = {};
  const by_source_org: Record<string, number> = {};
  const orgs = new Set<string>();
  for (const e of entriesData) {
    by_category[e.category] = (by_category[e.category] || 0) + 1;
    const org = e.source_org || "Unknown";
    by_source_org[org] = (by_source_org[org] || 0) + 1;
    orgs.add(org);
  }
  return {
    total_entries: entriesData.length,
    total_challenges: challengesData.length,
    total_organizations: orgs.size,
    organizations: [...orgs].sort(),
    by_category,
    by_source_org,
    by_trl: {},
    by_timeline: {},
    by_entry_type: {},
    by_country: {},
    categories: Object.fromEntries(
      Object.entries(CATEGORY_CONFIG).map(([k, v]) => [
        k,
        {
          name_ja: v.ja,
          entry_count: by_category[k] || 0,
          challenge_count: challengesData.filter((c) => c.category === k)
            .length,
        },
      ])
    ),
  };
}

export function getAllEntryIds(): string[] {
  return entriesData.map((e) => e.id);
}

export function getAllCategories(): Category[] {
  return Object.keys(CATEGORY_CONFIG) as Category[];
}
