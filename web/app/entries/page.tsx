import Image from "next/image";
import { getEntries } from "@/lib/data";
import { SITE_IMAGES } from "@/lib/constants";
import SearchAndFilters from "@/components/SearchAndFilters";

export default function EntriesPage() {
  const entries = getEntries();

  return (
    <div>
      {/* Photo header */}
      <section className="relative h-[200px] overflow-hidden">
        <Image
          src={SITE_IMAGES.earth_from_moon}
          alt="Earth from the Moon"
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-black/30" />
        <div className="relative z-10 h-full flex flex-col justify-end px-8 md:px-16 pb-6 max-w-6xl mx-auto">
          <h1 className="text-3xl font-light text-white mb-1 tracking-wide">Entries</h1>
          <p className="text-xs text-white/50">全{entries.length}件のエントリ</p>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <SearchAndFilters entries={entries} />
      </div>
    </div>
  );
}
