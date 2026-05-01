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

// NASA/public domain images for each category
export const CATEGORY_IMAGES: Record<Category, { url: string; alt: string; credit: string }> = {
  food: {
    url: "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&h=500&fit=crop",
    alt: "Space agriculture concept",
    credit: "NASA",
  },
  water: {
    url: "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=800&h=500&fit=crop",
    alt: "Lunar south pole ice",
    credit: "NASA",
  },
  hygiene: {
    url: "https://images.unsplash.com/photo-1457364559154-aa2644600ebb?w=800&h=500&fit=crop",
    alt: "Clean room environment",
    credit: "NASA",
  },
  medical: {
    url: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&h=500&fit=crop",
    alt: "Space medical equipment",
    credit: "NASA",
  },
  exercise: {
    url: "https://images.unsplash.com/photo-1541873676-a18131494184?w=800&h=500&fit=crop",
    alt: "Astronaut training",
    credit: "NASA",
  },
  clothing: {
    url: "https://images.unsplash.com/photo-1454789548928-9efd52dc4031?w=800&h=500&fit=crop",
    alt: "Spacesuit EVA",
    credit: "NASA",
  },
  communication: {
    url: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=500&fit=crop",
    alt: "Earth communications network from space",
    credit: "NASA",
  },
  entertainment: {
    url: "https://images.unsplash.com/photo-1462332420958-a05d1e002413?w=800&h=500&fit=crop",
    alt: "Stargazing from space",
    credit: "NASA",
  },
  sleep_habitat: {
    url: "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=800&h=500&fit=crop",
    alt: "Space station interior habitat",
    credit: "NASA",
  },
  work_environment: {
    url: "https://images.unsplash.com/photo-1517976487492-5750f3195933?w=800&h=500&fit=crop",
    alt: "Lunar surface work",
    credit: "NASA",
  },
};

// Hero and section images
export const SITE_IMAGES = {
  hero: "https://images.unsplash.com/photo-1522030299830-16b8d3d049fe?w=1920&h=800&fit=crop",
  moon_surface: "https://images.unsplash.com/photo-1532693322450-2cb5c511067d?w=1920&h=600&fit=crop",
  iss: "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1920&h=600&fit=crop",
  earth_from_moon: "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=1920&h=600&fit=crop",
};
