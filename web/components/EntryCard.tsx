import Link from "next/link";
import type { Entry } from "@/lib/types";
import { CATEGORY_CONFIG, ENTRY_TYPE_JA, TRL_COLOR } from "@/lib/constants";

export default function EntryCard({ entry }: { entry: Entry }) {
  const cat = CATEGORY_CONFIG[entry.category];

  return (
    <Link
      href={`/entries/${entry.id}/`}
      className="block bg-bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow no-underline group"
    >
      <div className="flex items-start gap-2 mb-2">
        <span
          className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white shrink-0"
          style={{ backgroundColor: cat.color }}
        >
          {cat.ja}
        </span>
        {entry.trl && (
          <span
            className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white shrink-0"
            style={{ backgroundColor: TRL_COLOR(entry.trl) }}
          >
            TRL {entry.trl}
          </span>
        )}
        {entry.entry_type && (
          <span className="inline-block px-2 py-0.5 rounded text-xs bg-gray-100 text-text-muted shrink-0">
            {ENTRY_TYPE_JA[entry.entry_type]}
          </span>
        )}
      </div>

      <h3 className="text-base font-semibold text-text group-hover:text-accent transition-colors mb-1 line-clamp-2">
        {entry.title}
      </h3>

      {entry.summary && (
        <p className="text-sm text-text-muted line-clamp-2 mb-2">
          {entry.summary}
        </p>
      )}

      <div className="flex items-center gap-3 text-xs text-text-muted">
        {entry.source_org && <span>{entry.source_org}</span>}
        {entry.source_year && <span>{entry.source_year}</span>}
        {entry.timeline && <span>{entry.timeline}</span>}
      </div>
    </Link>
  );
}
