import Link from "next/link";
import type { Entry } from "@/lib/types";
import { CATEGORY_CONFIG, ENTRY_TYPE_JA, TRL_COLOR } from "@/lib/constants";

export default function EntryCard({ entry }: { entry: Entry }) {
  const cat = CATEGORY_CONFIG[entry.category];

  return (
    <Link
      href={`/entries/${entry.id}/`}
      className="block bg-bg-card border border-border rounded-lg p-5 hover:border-accent/40 transition-all no-underline group"
    >
      <div className="flex items-start gap-2 mb-3">
        <span
          className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white/90 shrink-0"
          style={{ backgroundColor: cat.color }}
        >
          {cat.ja}
        </span>
        {entry.trl && (
          <span
            className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white/90 shrink-0"
            style={{ backgroundColor: TRL_COLOR(entry.trl) }}
          >
            TRL {entry.trl}
          </span>
        )}
        {entry.entry_type && (
          <span className="inline-block px-2 py-0.5 rounded text-xs bg-bg-surface text-text-muted shrink-0">
            {ENTRY_TYPE_JA[entry.entry_type]}
          </span>
        )}
        {entry.quality_score === "verified" && (
          <span className="inline-block px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-400 shrink-0">
            Verified
          </span>
        )}
      </div>

      <h3 className="text-base font-medium text-text group-hover:text-accent transition-colors mb-2 line-clamp-2">
        {entry.title}
      </h3>

      {entry.summary && (
        <p className="text-sm text-text-muted line-clamp-2 mb-3 font-light leading-relaxed">
          {entry.summary}
        </p>
      )}

      <div className="flex items-center gap-3 text-xs text-text-muted/70">
        {entry.source_org && <span>{entry.source_org}</span>}
        {entry.source_year && <span>{entry.source_year}</span>}
        {entry.timeline && <span>{entry.timeline}</span>}
      </div>
    </Link>
  );
}
