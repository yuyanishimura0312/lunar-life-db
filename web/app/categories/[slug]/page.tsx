import Link from "next/link";
import Image from "next/image";
import {
  getEntriesByCategory,
  getChallengesByCategory,
  getAllCategories,
} from "@/lib/data";
import { CATEGORY_CONFIG, CATEGORY_IMAGES } from "@/lib/constants";
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
  const img = CATEGORY_IMAGES[category];

  return (
    <div>
      {/* Photo header like JAXA booklet chapter page */}
      <section className="relative h-[280px] overflow-hidden">
        <Image
          src={img.url}
          alt={img.alt}
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-black/30" />
        <div
          className="absolute bottom-0 left-0 right-0 h-[4px]"
          style={{ backgroundColor: config.color }}
        />
        <div className="relative z-10 h-full flex flex-col justify-end px-8 md:px-16 pb-8 max-w-6xl mx-auto">
          <nav className="text-xs text-white/40 mb-3 tracking-wide">
            <Link href="/" className="hover:text-white/70 transition-colors">
              Home
            </Link>
            {" / "}
            <span className="text-white/70">{config.ja}</span>
          </nav>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-2 tracking-wide">
            {config.ja}
          </h1>
          <p className="text-sm text-white/50">
            {entries.length} entries / {challenges.length} challenges
          </p>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Challenges */}
        {challenges.length > 0 && (
          <section className="mb-10">
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
    </div>
  );
}
