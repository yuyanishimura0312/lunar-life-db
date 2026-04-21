import Link from "next/link";
import { getEntry, getAllEntryIds, getEntriesByCategory } from "@/lib/data";
import {
  CATEGORY_CONFIG,
  ENTRY_TYPE_JA,
  TRL_LABELS,
  TRL_COLOR,
  TRL_STAGE,
  MODULE_JA,
} from "@/lib/constants";
import EntryCard from "@/components/EntryCard";
import type { Category } from "@/lib/types";

export function generateStaticParams() {
  return getAllEntryIds().map((id) => ({ id }));
}

export default async function EntryDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const entry = getEntry(id);

  if (!entry) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-text mb-4">
          エントリが見つかりません
        </h1>
        <Link href="/entries/" className="text-accent hover:underline">
          一覧に戻る
        </Link>
      </div>
    );
  }

  const cat = CATEGORY_CONFIG[entry.category];
  const related = getEntriesByCategory(entry.category as Category)
    .filter((e) => e.id !== entry.id)
    .slice(0, 3);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-text-muted mb-6">
        <Link href="/" className="hover:underline">
          ホーム
        </Link>
        {" / "}
        <Link href="/entries/" className="hover:underline">
          エントリ一覧
        </Link>
        {" / "}
        <Link
          href={`/categories/${entry.category}/`}
          className="hover:underline"
        >
          {cat.ja}
        </Link>
        {" / "}
        <span className="text-text">{entry.title}</span>
      </nav>

      {/* Header */}
      <div
        className="rounded-lg p-6 mb-6"
        style={{ backgroundColor: cat.color + "15" }}
      >
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span
            className="px-3 py-1 rounded text-sm font-medium text-white"
            style={{ backgroundColor: cat.color }}
          >
            {cat.ja}
          </span>
          {entry.trl && (
            <span
              className="px-3 py-1 rounded text-sm font-medium text-white"
              style={{ backgroundColor: TRL_COLOR(entry.trl) }}
            >
              TRL {entry.trl} - {TRL_STAGE(entry.trl)}
            </span>
          )}
          <span className="px-3 py-1 rounded text-sm bg-white/60 text-text-muted">
            {ENTRY_TYPE_JA[entry.entry_type]}
          </span>
        </div>
        <h1 className="text-2xl font-bold text-text mb-2">{entry.title}</h1>
        {entry.title_en && (
          <p className="text-sm text-text-muted">{entry.title_en}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="md:col-span-2 space-y-6">
          {/* Summary */}
          {entry.summary && (
            <div className="bg-bg-card border border-border rounded-lg p-5">
              <h2 className="text-sm font-medium text-text-muted mb-2">
                概要
              </h2>
              <p className="text-text leading-relaxed">{entry.summary}</p>
            </div>
          )}

          {/* Description */}
          {entry.description && (
            <div className="bg-bg-card border border-border rounded-lg p-5">
              <h2 className="text-sm font-medium text-text-muted mb-2">
                詳細
              </h2>
              <div className="text-text leading-relaxed whitespace-pre-line">
                {entry.description}
              </div>
            </div>
          )}

          {/* ISS Connection */}
          {entry.iss_connection && (
            <div className="bg-bg-card border border-border rounded-lg p-5">
              <h2 className="text-sm font-medium text-text-muted mb-2">
                ISS経験との関連
              </h2>
              <p className="text-text leading-relaxed">
                {entry.iss_connection}
              </p>
            </div>
          )}

          {/* Earth Analog */}
          {entry.earth_analog && (
            <div className="bg-bg-card border border-border rounded-lg p-5">
              <h2 className="text-sm font-medium text-text-muted mb-2">
                地上アナログ環境
              </h2>
              <p className="text-text leading-relaxed">{entry.earth_analog}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Metadata */}
          <div className="bg-bg-card border border-border rounded-lg p-4 space-y-3">
            {entry.source_org && (
              <div>
                <p className="text-xs text-text-muted">組織</p>
                <p className="text-sm font-medium text-text">
                  {entry.source_org}
                </p>
              </div>
            )}
            {entry.source_country && (
              <div>
                <p className="text-xs text-text-muted">国</p>
                <p className="text-sm text-text">{entry.source_country}</p>
              </div>
            )}
            {entry.source_year && (
              <div>
                <p className="text-xs text-text-muted">年</p>
                <p className="text-sm text-text">{entry.source_year}</p>
              </div>
            )}
            {entry.trl && (
              <div>
                <p className="text-xs text-text-muted">
                  技術成熟度 (TRL {entry.trl})
                </p>
                <p className="text-sm text-text">{TRL_LABELS[entry.trl]}</p>
                {entry.trl_note && (
                  <p className="text-xs text-text-muted mt-1">
                    {entry.trl_note}
                  </p>
                )}
              </div>
            )}
            {entry.timeline && (
              <div>
                <p className="text-xs text-text-muted">タイムライン</p>
                <p className="text-sm text-text">{entry.timeline}</p>
              </div>
            )}
            {entry.target_mission && (
              <div>
                <p className="text-xs text-text-muted">対象ミッション</p>
                <p className="text-sm text-text">{entry.target_mission}</p>
              </div>
            )}
            {entry.source_url && (
              <div>
                <a
                  href={entry.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-accent hover:underline"
                >
                  ソースを見る →
                </a>
              </div>
            )}
          </div>

          {/* Related modules */}
          {entry.related_modules && entry.related_modules.length > 0 && (
            <div className="bg-bg-card border border-border rounded-lg p-4">
              <p className="text-xs text-text-muted mb-2">
                関連する月面基地モジュール
              </p>
              <div className="flex flex-wrap gap-1">
                {entry.related_modules.map((mod) => (
                  <span
                    key={mod}
                    className="px-2 py-1 rounded text-xs bg-gray-100 text-text-muted"
                  >
                    {MODULE_JA[mod] || mod}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {entry.tags && entry.tags.length > 0 && (
            <div className="bg-bg-card border border-border rounded-lg p-4">
              <p className="text-xs text-text-muted mb-2">タグ</p>
              <div className="flex flex-wrap gap-1">
                {entry.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 rounded text-xs"
                    style={{
                      backgroundColor: cat.color + "20",
                      color: cat.color,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related entries */}
      {related.length > 0 && (
        <section className="mt-10">
          <h2 className="text-lg font-bold text-text mb-4">
            同じカテゴリのエントリ
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {related.map((e) => (
              <EntryCard key={e.id} entry={e} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
