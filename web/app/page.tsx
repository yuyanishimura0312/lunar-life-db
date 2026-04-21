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
      {/* Hero */}
      <section
        className="py-16 px-4 text-center"
        style={{
          background:
            "linear-gradient(135deg, #faf8f5 0%, #F8CDAC30 50%, #faf8f5 100%)",
        }}
      >
        <h1
          className="text-3xl md:text-4xl font-bold mb-4"
          style={{ color: "var(--accent)" }}
        >
          月面生活リサーチDB
        </h1>
        <p className="text-text-muted max-w-2xl mx-auto mb-6">
          月面基地での生活課題と、それに応える世界中の技術・研究・プロジェクトを集めたデータベース。
          JAXA「Space Life on the Moon」をベースに構築。
        </p>
        <div className="flex justify-center gap-8 text-sm">
          <div>
            <p className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
              {stats.total_entries}
            </p>
            <p className="text-text-muted">エントリ</p>
          </div>
          <div>
            <p className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
              {stats.total_organizations}
            </p>
            <p className="text-text-muted">組織</p>
          </div>
          <div>
            <p className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
              10
            </p>
            <p className="text-text-muted">カテゴリ</p>
          </div>
          <div>
            <p className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
              {stats.total_challenges}
            </p>
            <p className="text-text-muted">課題</p>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-6xl mx-auto px-4 py-10">
        <h2 className="text-xl font-bold text-text mb-6">生活課題カテゴリ</h2>
        <CategoryGrid stats={stats} />
      </section>

      {/* Recent entries */}
      <section className="max-w-6xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-text">最新エントリ</h2>
          <Link href="/entries/" className="text-sm text-accent hover:underline">
            すべて見る →
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
