import { getEntries } from "@/lib/data";
import SearchAndFilters from "@/components/SearchAndFilters";

export default function EntriesPage() {
  const entries = getEntries();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-text mb-6">エントリ一覧</h1>
      <SearchAndFilters entries={entries} />
    </div>
  );
}
