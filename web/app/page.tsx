import Link from "next/link";
import Image from "next/image";
import { getEntries, getStats } from "@/lib/data";
import CategoryGrid from "@/components/CategoryGrid";
import EntryCard from "@/components/EntryCard";
import { SITE_IMAGES } from "@/lib/constants";

export default function HomePage() {
  const entries = getEntries();
  const stats = getStats();
  const recent = entries.slice(0, 6);

  return (
    <div>
      {/* Hero - Full bleed photo like JAXA booklet cover */}
      <section className="relative h-[70vh] min-h-[500px] flex items-center justify-center overflow-hidden">
        <Image
          src={SITE_IMAGES.hero}
          alt="Moon surface"
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-[#0B0F1A]" />
        <div className="relative z-10 text-center px-4">
          <p className="text-xs tracking-[0.4em] text-white/50 uppercase mb-6">
            Lunar Life Research Database
          </p>
          <h1 className="text-5xl md:text-6xl font-light mb-4 tracking-wide text-white">
            Space Life on the Moon
          </h1>
          <p className="text-sm text-white/60 max-w-lg mx-auto mb-2 font-light leading-relaxed">
            月面基地での生活を支える技術・研究・プロジェクトの世界
          </p>
          <p className="text-xs text-white/30 mb-12">
            Based on JAXA &ldquo;Space Life on the Moon&rdquo;
          </p>
          <div className="flex justify-center gap-16 text-sm">
            <div>
              <p className="text-4xl font-light text-white">{stats.total_entries}</p>
              <p className="text-[10px] text-white/40 mt-1 tracking-[0.2em] uppercase">Entries</p>
            </div>
            <div>
              <p className="text-4xl font-light text-white">{stats.total_organizations}</p>
              <p className="text-[10px] text-white/40 mt-1 tracking-[0.2em] uppercase">Organizations</p>
            </div>
            <div>
              <p className="text-4xl font-light text-white">10</p>
              <p className="text-[10px] text-white/40 mt-1 tracking-[0.2em] uppercase">Categories</p>
            </div>
            <div>
              <p className="text-4xl font-light text-white">{stats.total_challenges}</p>
              <p className="text-[10px] text-white/40 mt-1 tracking-[0.2em] uppercase">Challenges</p>
            </div>
          </div>
        </div>
      </section>

      {/* Categories - Photo cards */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-lg font-light text-text mb-1 tracking-wide">
          Life Categories
        </h2>
        <p className="text-xs text-text-muted mb-8">月面生活の10の課題領域</p>
        <CategoryGrid stats={stats} />
      </section>

      {/* Photo divider - ISS like JAXA booklet chapter break */}
      <section className="relative h-[300px] overflow-hidden">
        <Image
          src={SITE_IMAGES.moon_surface}
          alt="Lunar surface"
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent" />
        <div className="relative z-10 h-full flex items-center px-8 md:px-16 max-w-6xl mx-auto">
          <div>
            <p className="text-xs tracking-[0.3em] text-white/50 uppercase mb-3">Database</p>
            <h2 className="text-3xl font-light text-white tracking-wide mb-2">
              197 Research Entries
            </h2>
            <p className="text-sm text-white/60 font-light max-w-md">
              世界中の宇宙機関・大学・民間企業から収集した月面生活に関する技術・研究・プロジェクト
            </p>
          </div>
        </div>
      </section>

      {/* Recent entries */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="flex items-center justify-between mb-8">
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
