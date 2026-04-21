import Link from "next/link";
import {
  getEntriesByCategory,
  getChallengesByCategory,
  getAllCategories,
} from "@/lib/data";
import { CATEGORY_CONFIG } from "@/lib/constants";
import type { Category } from "@/lib/types";
import SearchAndFilters from "@/components/SearchAndFilters";

export function generateStaticParams() {
  return getAllCategories().map((slug) => ({ slug }));
}

const SEVERITY_JA: Record<string, { label: string; color: string }> = {
  critical: { label: "深刻", color: "#DC8766" },
  high: { label: "高", color: "#B07256" },
  medium: { label: "中", color: "#F0A671" },
  low: { label: "低", color: "#CEA26F" },
};

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = slug as Category;
  const config = CATEGORY_CONFIG[category];

  if (!config) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-text mb-4">
          カテゴリが見つかりません
        </h1>
        <Link href="/" className="text-accent hover:underline">
          ホームに戻る
        </Link>
      </div>
    );
  }

  const entries = getEntriesByCategory(category);
  const challenges = getChallengesByCategory(category);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div
        className="rounded-lg p-6 mb-8"
        style={{ backgroundColor: config.color + "15" }}
      >
        <nav className="text-sm text-text-muted mb-4">
          <Link href="/" className="hover:underline">
            ホーム
          </Link>
          {" / "}
          <span className="text-text">{config.ja}</span>
        </nav>
        <h1 className="text-2xl font-bold text-text mb-2">
          <span
            className="inline-block w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: config.color }}
          />
          {config.ja}
        </h1>
        <p className="text-sm text-text-muted">
          {entries.length}件のエントリ / {challenges.length}件の課題
        </p>
      </div>

      {/* Challenges */}
      {challenges.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-bold text-text mb-4">月面環境の課題</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {challenges.map((ch) => {
              const sev = SEVERITY_JA[ch.severity || "medium"];
              return (
                <div
                  key={ch.id}
                  className="bg-bg-card border border-border rounded-lg p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="px-2 py-0.5 rounded text-xs font-medium text-white"
                      style={{ backgroundColor: sev.color }}
                    >
                      {sev.label}
                    </span>
                    <h3 className="text-sm font-semibold text-text">
                      {ch.name_ja}
                    </h3>
                  </div>
                  {ch.description && (
                    <p className="text-sm text-text-muted line-clamp-3">
                      {ch.description}
                    </p>
                  )}
                  {ch.iss_analog && (
                    <p className="text-xs text-text-muted mt-2">
                      ISS: {ch.iss_analog}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Entries */}
      <section>
        <h2 className="text-lg font-bold text-text mb-4">
          エントリ一覧
        </h2>
        <SearchAndFilters entries={entries} initialCategory={category} />
      </section>
    </div>
  );
}
