import Link from "next/link";
import { getEntries, getStats } from "@/lib/data";
import CategoryGrid from "@/components/CategoryGrid";
import EntryCard from "@/components/EntryCard";

export default function HomePage() {
  const entries = getEntries();
  const stats = getStats();
  const recent = entries.slice(0, 6);

  return (
    <div>
      {/* Hero - Space themed */}
      <section className="star-field py-24 px-4 text-center"
        style={{
          background: "linear-gradient(180deg, #060a14 0%, #0B0F1A 40%, #141929 100%)",
        }}
      >
        <p className="text-xs tracking-[0.3em] text-text-muted uppercase mb-4">
          Lunar Life Research Database
        </p>
        <h1 className="text-4xl md:text-5xl font-light mb-3 tracking-wide text-white">
          Space Life on the Moon
        </h1>
        <p className="text-sm text-text-muted max-w-xl mx-auto mb-2 font-light">
          月面基地での生活を支える技術・研究・プロジェクトの世界
        </p>
        <p className="text-xs text-text-muted/60 mb-10">
          JAXA「Space Life on the Moon」をベースに構築
        </p>
        <div className="flex justify-center gap-12 text-sm">
          <div>
            <p className="text-3xl font-light text-white">
              {stats.total_entries}
            </p>
            <p className="text-xs text-text-muted mt-1 tracking-wider uppercase">Entries</p>
          </div>
          <div>
            <p className="text-3xl font-light text-white">
              {stats.total_organizations}
            </p>
            <p className="text-xs text-text-muted mt-1 tracking-wider uppercase">Organizations</p>
          </div>
          <div>
            <p className="text-3xl font-light text-white">10</p>
            <p className="text-xs text-text-muted mt-1 tracking-wider uppercase">Categories</p>
          </div>
          <div>
            <p className="text-3xl font-light text-white">
              {stats.total_challenges}
            </p>
            <p className="text-xs text-text-muted mt-1 tracking-wider uppercase">Challenges</p>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-lg font-light text-text mb-1 tracking-wide">
          Life Categories
        </h2>
        <p className="text-xs text-text-muted mb-6">月面生活の10の課題領域</p>
        <CategoryGrid stats={stats} />
      </section>

      {/* Recent entries */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-light text-text tracking-wide">
              Recent Entries
            </h2>
            <p className="text-xs text-text-muted">最新のエントリ</p>
          </div>
          <Link href="/entries/" className="text-sm text-accent hover:underline">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recent.map((entry) => (
            <EntryCard key={entry.id} entry={entry} />
          ))}
        </div>
      </section>
    </div>
  );
}
