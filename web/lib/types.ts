export interface Entry {
  id: string;
  title: string;
  title_en: string | null;
  category: Category;
  entry_type: EntryType;
  summary: string | null;
  summary_en: string | null;
  description: string | null;
  source_org: string | null;
  source_country: string | null;
  source_url: string | null;
  source_year: number | null;
  authors: string[];
  trl: number | null;
  trl_note: string | null;
  timeline: string | null;
  target_mission: string | null;
  related_modules: string[];
  tags: string[];
  keywords_ja: string | null;
  keywords_en: string | null;
  iss_connection: string | null;
  earth_analog: string | null;
  quality_score: string;
  is_enriched: number;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  sources: Source[];
}

export interface Source {
  id: string;
  entry_id: string;
  source_type: string | null;
  title: string | null;
  url: string | null;
  author: string | null;
  year: number | null;
  doi: string | null;
  notes: string | null;
}

export interface Challenge {
  id: string;
  name_ja: string;
  name_en: string | null;
  category: string;
  challenge_type: string;
  description: string | null;
  severity: string | null;
  iss_analog: string | null;
}

export type Category =
  | "food"
  | "water"
  | "hygiene"
  | "medical"
  | "exercise"
  | "clothing"
  | "communication"
  | "entertainment"
  | "sleep_habitat"
  | "work_environment";

export type EntryType =
  | "technology"
  | "research"
  | "project"
  | "concept"
  | "regulation"
  | "challenge"
  | "case_study";

export interface Stats {
  total_entries: number;
  total_challenges: number;
  total_organizations: number;
  organizations: string[];
  by_category: Record<string, number>;
  by_source_org: Record<string, number>;
  by_trl: Record<string, number>;
  by_timeline: Record<string, number>;
  by_entry_type: Record<string, number>;
  by_country: Record<string, number>;
  categories: Record<
    string,
    { name_ja: string; entry_count: number; challenge_count: number }
  >;
}
