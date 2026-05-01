import type { Category, EntryType } from "./types";

export const CATEGORY_CONFIG: Record<
  Category,
  { ja: string; color: string; icon: string }
> = {
  food: { ja: "食", color: "#4CAF50", icon: "utensils" },
  water: { ja: "水", color: "#42A5F5", icon: "droplet" },
  hygiene: { ja: "衛生", color: "#AB47BC", icon: "sparkles" },
  medical: { ja: "医療", color: "#EF5350", icon: "heart-pulse" },
  exercise: { ja: "運動", color: "#FF7043", icon: "dumbbell" },
  clothing: { ja: "衣服", color: "#78909C", icon: "shirt" },
  communication: { ja: "通信", color: "#29B6F6", icon: "radio" },
  entertainment: { ja: "娯楽", color: "#FFCA28", icon: "gamepad" },
  sleep_habitat: { ja: "睡眠・住環境", color: "#5C6BC0", icon: "moon" },
  work_environment: { ja: "作業環境", color: "#8D6E63", icon: "wrench" },
};

export const ENTRY_TYPE_JA: Record<EntryType, string> = {
  technology: "技術",
  research: "研究",
  project: "プロジェクト",
  concept: "コンセプト",
  regulation: "規制・基準",
  challenge: "課題",
  case_study: "事例研究",
};

export const TRL_LABELS: Record<number, string> = {
  1: "基本原理の観察",
  2: "技術コンセプトの定式化",
  3: "実験的な概念実証",
  4: "実験室環境での検証",
  5: "関連環境での検証",
  6: "関連環境での実証",
  7: "運用環境での実証",
  8: "システム完成・適格性確認",
  9: "運用実証済み",
};

export const TRL_STAGE = (trl: number): string => {
  if (trl <= 3) return "基礎研究";
  if (trl <= 6) return "技術実証";
  return "実用化";
};

export const TRL_COLOR = (trl: number): string => {
  if (trl <= 3) return "#EF5350"; // early research - red
  if (trl <= 6) return "#FFA726"; // demonstration - orange
  return "#66BB6A"; // operational - green
};

export const MODULE_JA: Record<string, string> = {
  private_room: "プライベートルーム",
  kitchen_dining: "キッチン&ダイニング",
  laboratory: "ラボラトリー",
  workspace: "ワークスペース",
  medical_bay: "メディカルベイ",
  training_room: "トレーニングルーム",
  courtyard: "コートヤード",
  plantation: "プランテーション",
};

export const ALL_CATEGORIES = Object.keys(CATEGORY_CONFIG) as Category[];
