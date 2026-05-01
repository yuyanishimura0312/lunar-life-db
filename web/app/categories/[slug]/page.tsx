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
  critical: { label: "Critical", color: "#EF5350" },
  high: { label: "High", color: "#FF7043" },
  medium: { label: "Medium", color: "#FFA726" },
  low: { label: "Low", color: "#66BB6A" },
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
        <h1 className="text-2xl font-light text-text mb-4">
          Category not found
        </h1>
        <Link href="/" className="text-accent hover:underline">
          Back to Home
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
        className="rounded-lg p-6 mb-8 border border-border"
        style={{ backgroundColor: config.color + "08" }}
      >
        <nav className="text-xs text-text-muted mb-4 tracking-wide">
          <Link href="/" className="hover:text-accent transition-colors">
            Home
          </Link>
          {" / "}
          <span className="text-text">{config.ja}</span>
        </nav>
        <h1 className="text-2xl font-light text-text mb-2 tracking-wide">
          <span
            className="inline-block w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: config.color }}
          />
          {config.ja}
        </h1>
        <p className="text-sm text-text-muted">
          {entries.length} entries / {challenges.length} challenges
        </p>
      </div>

      {/* Challenges */}
      {challenges.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-light text-text mb-4 tracking-wide">Lunar Challenges</h2>
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
                      className="px-2 py-0.5 rounded text-xs font-medium text-white/90"
                      style={{ backgroundColor: sev.color }}
                    >
                      {sev.label}
                    </span>
                    <h3 className="text-sm font-medium text-text">
                      {ch.name_ja}
                    </h3>
                  </div>
                  {ch.description && (
                    <p className="text-sm text-text-muted line-clamp-3 font-light">
                      {ch.description}
                    </p>
                  )}
                  {ch.iss_analog && (
                    <p className="text-xs text-text-muted/70 mt-2">
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
        <h2 className="text-lg font-light text-text mb-4 tracking-wide">
          Entries
        </h2>
        <SearchAndFilters entries={entries} initialCategory={category} />
      </section>
    </div>
  );
}
