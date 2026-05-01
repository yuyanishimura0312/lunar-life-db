import { getEntries } from "@/lib/data";
import SearchAndFilters from "@/components/SearchAndFilters";

export default function EntriesPage() {
  const entries = getEntries();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-light text-text mb-1 tracking-wide">Entries</h1>
      <p className="text-xs text-text-muted mb-6">全{entries.length}件のエントリ</p>
      <SearchAndFilters entries={entries} />
    </div>
  );
}
